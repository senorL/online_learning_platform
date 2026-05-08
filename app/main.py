"""初中生在线学习平台 — FastAPI 应用入口。"""

import os
import json

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.database import engine, SessionLocal
from app.models import (
    User, Course, Chapter, Video, Question,
    Enrollment, WrongQuestion, StudyRecord, StudyProgress,
)
from app.database import Base
from app.core.security import hash_password
from app.routers import auth, users, courses, questions, wrong_questions, ranking, admin

# ---- 创建 FastAPI 应用 ----
app = FastAPI(
    title="初中生在线学习平台",
    description="学-练-测-改 闭环学习系统",
    version="2.0.0",
)

# ---- 跨域中间件 ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 注册路由 ----
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(questions.router)
app.include_router(wrong_questions.router)
app.include_router(ranking.router)
app.include_router(admin.router)

# ---- 自动创建数据库表 ----
Base.metadata.create_all(bind=engine)




@app.on_event("startup")
def startup_event():
    """启动时自动初始化管理员账号。"""
    db = SessionLocal()
    try:
        # 自动创建管理员
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            ))
            db.commit()
            print("--- 管理员账号 admin/admin123 初始化成功 ---")
    except Exception as e:
        print(f"!!! 启动初始化失败: {e} !!!")
        db.rollback()
    finally:
        db.close()


@app.get("/api/health")
def health_check() -> dict:
    """健康检查接口。"""
    return {"code": 200, "data": {"status": "ok"}, "message": "服务运行正常"}