"""DeepSeek AI 出题服务：按章节智能生成题目。"""

import json
import random
import traceback
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI

from app.core.config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    AI_GENERATE_BATCH_SIZE, MIN_QUESTIONS_THRESHOLD,
)
from app.models.question import Question


# 难度中文映射
DIFFICULTY_MAP = {
    "easy": "简单（基础概念和直接计算，适合刚学习本节内容的学生）",
    "medium": "中等（需要一定思考和灵活运用知识点，适合巩固提升）",
    "hard": "困难（综合性强，需要多步推理或跨知识点应用，适合拔高训练）",
}


def _build_prompt(subject: str, chapter: str, difficulty: str,
                  question_types: List[str], count: int) -> str:
    """构造AI出题的prompt。"""
    type_desc = []
    if "choice" in question_types:
        type_desc.append(
            '选择题(type="choice"): 必须有4个选项A/B/C/D，options字段为JSON字符串如 '
            '\'{"A":"选项A内容","B":"选项B内容","C":"选项C内容","D":"选项D内容"}\'，'
            'answer字段为正确选项字母如"A"'
        )
    if "fill_blank" in question_types:
        type_desc.append(
            '填空题(type="fill_blank"): 题干中用"____"表示填空位置，'
            'options字段为null，answer字段为标准答案文本'
        )

    types_str = "、".join(type_desc)
    diff_desc = DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MAP["medium"])

    prompt = f"""你是一位经验丰富的初中{subject}教师，请严格按照以下要求出题：

【学科】{subject}
【章节】{chapter}
【难度】{diff_desc}
【题型】{types_str}
【数量】共{count}道题

要求：
1. 所有题目必须紧密围绕"{chapter}"这一章节的核心知识点，不得超出该章节范围
2. 题目表述清晰准确，符合初中教学大纲和考试标准
3. 难度必须严格符合所选难度等级
4. 每道题必须有详细的解析(explanation字段)，说明解题思路和涉及的知识点
5. 选择题的四个选项应具有合理的干扰性，避免一眼就能排除的选项
6. 填空题答案要简洁明确
7. 如果有多种题型，请均匀分配数量

请以严格的JSON数组格式返回，不要包含任何多余文字、解释或markdown标记。
每个题目的结构如下：
[
  {{
    "type": "choice或fill_blank",
    "content": "题目内容",
    "options": "{{\\"A\\":\\"..\\",\\"B\\":\\"..\\",\\"C\\":\\"..\\",\\"D\\":\\"..\\"}}" 或 null,
    "answer": "正确答案",
    "explanation": "详细解析"
  }}
]

只返回JSON数组，不要有其他内容。"""

    return prompt


def generate_questions_with_ai(
    subject: str,
    chapter: str,
    difficulty: str,
    question_types: List[str],
    count: int,
) -> List[dict]:
    """调用DeepSeek API生成题目。

    Args:
        subject: 学科
        chapter: 章节名称
        difficulty: 难度 easy/medium/hard
        question_types: 题型列表 ["choice", "fill_blank"]
        count: 生成数量

    Returns:
        解析后的题目字典列表
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API Key 未配置，请检查 .env 文件")

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )

    prompt = _build_prompt(subject, chapter, difficulty, question_types, count)

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的初中教育题库生成器，只输出合法的JSON数据。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    content = response.choices[0].message.content.strip()

    # 尝试提取JSON（处理可能的markdown包裹）
    if content.startswith("```"):
        lines = content.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            elif line.startswith("```") and in_block:
                break
            elif in_block:
                json_lines.append(line)
        content = "\n".join(json_lines)

    questions = json.loads(content)

    # 校验和标准化
    valid_questions = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if "content" not in q or "answer" not in q:
            continue
        q_type = q.get("type", "choice")
        if q_type not in question_types:
            q_type = question_types[0]

        # 确保选择题有options
        if q_type == "choice" and not q.get("options"):
            continue

        # 标准化options字段
        options = q.get("options")
        if options and isinstance(options, dict):
            options = json.dumps(options, ensure_ascii=False)

        valid_questions.append({
            "type": q_type,
            "content": q["content"],
            "options": options,
            "answer": str(q["answer"]),
            "explanation": q.get("explanation", ""),
        })

    return valid_questions


def get_or_generate_questions(
    db: Session,
    subject: str,
    chapter: str,
    difficulty: str = "medium",
    question_types: Optional[List[str]] = None,
    count: int = 10,
) -> List[Question]:
    """智能出题入口：优先从数据库抽题，不够则调用AI补充。

    Args:
        db: 数据库会话
        subject: 学科
        chapter: 章节名称
        difficulty: 难度
        question_types: 题型列表
        count: 需要的题目数量

    Returns:
        题目模型列表
    """
    if question_types is None:
        question_types = ["choice", "fill_blank"]

    # 1. 从数据库查询现有题目
    query = db.query(Question).filter(
        Question.subject == subject,
        Question.chapter == chapter,
        Question.difficulty == difficulty,
    )
    if len(question_types) == 1:
        query = query.filter(Question.type == question_types[0])
    else:
        query = query.filter(Question.type.in_(question_types))

    existing = query.all()
    existing_count = len(existing)

    # 2. 如果数据库题目充足，随机抽取
    if existing_count >= count:
        return random.sample(existing, count)

    # 3. 题目不够，调用AI补充
    need = max(count - existing_count, AI_GENERATE_BATCH_SIZE)
    try:
        ai_questions = generate_questions_with_ai(
            subject, chapter, difficulty, question_types, need
        )
    except Exception as e:
        traceback.print_exc()
        # AI生成失败时，返回现有题目（可能不足count道）
        if existing:
            return existing
        raise ValueError(f"AI出题失败且数据库中无可用题目: {str(e)}")

    # 4. 将AI生成的题目存入数据库
    new_questions = []
    for q_data in ai_questions:
        q = Question(
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            type=q_data["type"],
            content=q_data["content"],
            options=q_data.get("options"),
            answer=q_data["answer"],
            explanation=q_data.get("explanation", ""),
            points=3 if difficulty == "easy" else (5 if difficulty == "medium" else 8),
            source="ai",
        )
        db.add(q)
        new_questions.append(q)

    db.commit()
    for q in new_questions:
        db.refresh(q)

    # 5. 合并现有+新生成的题目，随机抽取
    all_questions = existing + new_questions
    if len(all_questions) >= count:
        return random.sample(all_questions, count)
    return all_questions
