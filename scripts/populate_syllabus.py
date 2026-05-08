import os
import json
import sqlite3
import re

# 数据库路径
DB_PATH = "learning_platform.db"
TIKU_PATH = "tiku.json"
README_PATH = "README.md"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def parse_readme():
    """解析 README.md 获取课程、章节结构。"""
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    syllabus = []
    current_subject = None
    current_course = None
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 主学科 (## 数学)
        subject_match = re.match(r"^##\s+(.+)$", line)
        if subject_match:
            current_subject = subject_match.group(1).strip()
            continue
            
        # 课程/年级册 (### 七年级上册)
        course_match = re.match(r"^###\s+(.+)$", line)
        if course_match:
            current_course = {
                "subject": current_subject,
                "name": course_match.group(1).strip(),
                "chapters": []
            }
            syllabus.append(current_course)
            continue
            
        # 章节或小节
        if current_course:
            # 简单认为非标题行就是章节内容
            current_course["chapters"].append(line)
            
    return syllabus

def load_tiku():
    """加载现有的题库。"""
    if not os.path.exists(TIKU_PATH):
        return {}
    with open(TIKU_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("初中题库", {})

def populate():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("--- 清理旧数据 ---")
    cursor.execute("DELETE FROM courses")
    cursor.execute("DELETE FROM chapters")
    cursor.execute("DELETE FROM questions")
    conn.commit()

    syllabus = parse_readme()
    tiku = load_tiku()

    course_id_map = {} # (subject, name) -> id
    
    print("--- 导入课程和章节 ---")
    for course_info in syllabus:
        subject = course_info["subject"]
        course_name = course_info["name"]
        
        # 插入课程
        cursor.execute(
            "INSERT INTO courses (name, subject, grade) VALUES (?, ?, ?)",
            (f"{subject} - {course_name}", subject, course_name)
        )
        course_id = cursor.lastrowid
        
        print(f"导入课程: {subject} - {course_name} (ID: {course_id})")
        
        # 插入章节
        for idx, chapter_title in enumerate(course_info["chapters"]):
            cursor.execute(
                "INSERT INTO chapters (course_id, title, sort_order) VALUES (?, ?, ?)",
                (course_id, chapter_title, idx)
            )
            chapter_id = cursor.lastrowid
            
            # 为每个章节生成两道题目
            # 1. 尝试从 tiku.json 中找匹配学科的题目
            questions_pool = tiku.get(subject, [])
            
            for q_idx in range(2):
                if questions_pool:
                    # 循环使用题库中的题目
                    template_q = questions_pool[(idx * 2 + q_idx) % len(questions_pool)]
                    
                    q_type = "choice" if template_q.get("题型") == "选择题" else (
                        "fill_blank" if template_q.get("题型") == "填空题" else "essay"
                    )
                    
                    cursor.execute(
                        """
                        INSERT INTO questions (
                            course_id, subject, chapter, type, content, 
                            options, answer, explanation, points
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            course_id, subject, chapter_title, q_type,
                            template_q["题目"],
                            json.dumps(template_q.get("选项", {}), ensure_ascii=False) if template_q.get("选项") else None,
                            template_q["答案"],
                            template_q.get("解析"),
                            5
                        )
                    )
                else:
                    # 如果该学科没有题库，生成通用题目
                    cursor.execute(
                        """
                        INSERT INTO questions (
                            course_id, subject, chapter, type, content, 
                            answer, explanation, points
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            course_id, subject, chapter_title, "essay",
                            f"请简述关于 '{chapter_title}' 的核心知识点。",
                            "详见教材相关章节。",
                            "考察学生对基础知识的掌握程度。",
                            5
                        )
                    )

    conn.commit()
    print("--- 数据库迁移完成 ---")
    conn.close()

if __name__ == "__main__":
    populate()
