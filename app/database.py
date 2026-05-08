import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# 读取环境变量，默认回退到 SQLite 保持兼容
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning_platform.db")

engine_args = {}
# SQLite 特有的配置
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    # MySQL 配置
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20
    engine_args["pool_recycle"] = 3600

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有数据库模型类的基类
Base = declarative_base()