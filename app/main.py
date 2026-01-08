import os
import json
import datetime
from datetime import datetime as dt, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette.middleware.cors import CORSMiddleware

# 导入本地模块
from . import models, schemas, database

app = FastAPI(title="中学生在线学习平台")

# 必须在接口之前配置跨域，否则前端无法访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自动创建数据库表结构
models.Base.metadata.create_all(bind=database.engine)

# 安全与加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-very-secret-key-for-project"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- 1. 预定义初始课程数据 [cite: 9, 15] ---
# 确保在 startup_event 调用之前定义
INITIAL_COURSES = [
    {"title": "中考数学复习全集", "subject": "数学",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1qE411H7Uv"},
    {"title": "分子动理论", "subject": "物理",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1Mb421n7nB"},
    {"title": "初中化学公开课", "subject": "化学",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1wb411x78e"},
    {"title": "七年级地理上册", "subject": "地理",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1ni4y1u7qn"},
    {"title": "初中生物基础课", "subject": "生物",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1n94y1g7XG"},
    {"title": "零基础英语拯救计划", "subject": "英语",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1wt411G7QY"},
    {"title": "七年级道法名师课", "subject": "道法",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1K4KyzNEVJ"},
    {"title": "初中语文全题型讲解", "subject": "语文",
     "video_url": "https://player.bilibili.com/player.html?bvid=BV1jc411c7CS"},
]


# --- 2. 核心依赖函数 ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = dt.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user: raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="登录已过期")


# --- 3. 启动初始化逻辑：自动填充数据 [cite: 14, 15] ---
@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    try:
        # A. 自动创建管理员
        if not db.query(models.User).filter(models.User.username == "admin").first():
            db.add(models.User(username="admin", hashed_password=pwd_context.hash("admin123"), role="admin"))
            print("--- 管理员账号 admin/admin123 初始化成功 ---")

        # B. 初始化课程
        if db.query(models.Course).count() == 0:
            for course in INITIAL_COURSES:
                db.add(models.Course(**course))
            db.commit()
            print(f"--- 成功导入 {len(INITIAL_COURSES)} 门学科视频资源 ---")

        # C. 自动载入题库
        if db.query(models.Question).count() == 0:
            tiku_path = os.path.join(os.path.dirname(__file__), "..", "tiku.json")
            if os.path.exists(tiku_path):
                with open(tiku_path, 'r', encoding='utf-8') as f:
                    tiku_data = json.load(f)["初中题库"]
                    q_count = 0
                    for sub, qs in tiku_data.items():
                        for q in qs:
                            db.add(models.Question(
                                subject=sub,
                                content=q["题目"],
                                options=json.dumps(q.get("选项", {}), ensure_ascii=False),
                                answer=q["答案"]
                            ))
                            q_count += 1
                    db.commit()
                    print(f"--- 成功从 JSON 导入 {q_count} 道试题 ---")
            else:
                print(f"!!! 错误：未在 {tiku_path} 找到题库文件 !!!")
    except Exception as e:
        print(f"!!! 启动初始化失败: {e} !!!")
    finally:
        db.close()


# --- 4. 接口实现 ---

@app.post("/register", response_model=schemas.UserOut, tags=["用户"])
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """[cite: 8] 用户注册"""
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = models.User(username=user_in.username, hashed_password=pwd_context.hash(user_in.password),
                           grade=user_in.grade)
    db.add(new_user);
    db.commit();
    db.refresh(new_user)
    return new_user


@app.post("/login", tags=["用户"])
def login(credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    """[cite: 8] 用户登录"""
    db_user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not db_user or not pwd_context.verify(credentials.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = create_access_token(data={"sub": db_user.username, "role": db_user.role, "id": db_user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "username": db_user.username,
        "grade": db_user.grade,
        "avatar": db_user.avatar
    }

@app.put("/my/profile")
def update_profile(new_data: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. 修改个人信息
    current_user.grade = new_data.get("grade")
    current_user.hashed_password = pwd_context.hash(new_data.get("password")) if new_data.get("password") else current_user.hashed_password
    current_user.avatar = new_data.get("avatar")
    # 2. 存入数据库
    db.commit()
    return {"message": "更新成功", "grade": current_user.grade, "username": current_user.username, "avatar": current_user.avatar}

@app.get("/courses/{subject}", tags=["课程"])
def get_courses(subject: str, db: Session = Depends(get_db)):
    """[cite: 9] 获取课程视频"""
    return db.query(models.Course).filter(models.Course.subject == subject).all()


@app.get("/questions/{subject}", tags=["测试"])
def get_questions(subject: str, db: Session = Depends(get_db)):
    """[cite: 10] 获取题目列表"""
    return db.query(models.Question).filter(models.Question.subject == subject).all()


@app.post("/questions/submit", tags=["测试"])
def submit(submission: schemas.AnswerSubmit, db: Session = Depends(get_db),
           current: models.User = Depends(get_current_user)):
    """[cite: 10, 11, 12] 提交答案并处理错题与打卡"""
    q = db.query(models.Question).filter(models.Question.id == submission.question_id).first()
    is_correct = submission.user_answer.strip() == q.answer.strip()
    if not is_correct:
        db.add(models.WrongQuestion(user_id=current.id, question_id=q.id))
    record = db.query(models.StudyRecord).filter(models.StudyRecord.user_id == current.id,
                                                 models.StudyRecord.date == datetime.date.today()).first()
    if record:
        record.count += 1
    else:
        db.add(models.StudyRecord(user_id=current.id, count=1))
    db.commit()
    return {"is_correct": is_correct, "correct_answer": q.answer}


@app.get("/my/heatmap", tags=["统计"])
def get_heatmap(current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """[cite: 12] 获取打卡热力图数据"""
    records = db.query(models.StudyRecord).filter(models.StudyRecord.user_id == current.id).all()
    return {str(r.date): r.count for r in records}


@app.get("/my/mistakes", tags=["错题"])
def get_mistakes(current: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """[cite: 11] 获取我的错题本"""
    return db.query(models.Question).join(models.WrongQuestion,
                                          models.Question.id == models.WrongQuestion.question_id).filter(
        models.WrongQuestion.user_id == current.id).all()