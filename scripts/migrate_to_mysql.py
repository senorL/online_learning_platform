import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 确保能导入 app 包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models import (
    User, Course, Chapter, Video, Question, Enrollment,
    WrongQuestion, StudyRecord, StudyProgress
)

# SQLite 引擎 (旧数据源)
sqlite_engine = create_engine("sqlite:///./learning_platform.db", connect_args={"check_same_thread": False})
SqliteSession = sessionmaker(bind=sqlite_engine)

# MySQL 引擎 (新数据源，读取环境变量)
print(f"Connecting to MySQL: {SQLALCHEMY_DATABASE_URL}")
mysql_engine = create_engine(SQLALCHEMY_DATABASE_URL)
MysqlSession = sessionmaker(bind=mysql_engine)

def migrate_data():
    # 1. 在 MySQL 中创建所有表结构
    print("Creating tables in MySQL...")
    Base.metadata.drop_all(mysql_engine)
    Base.metadata.create_all(mysql_engine)
    print("Tables created.")

    # 2. 按外键依赖顺序迁移表数据
    tables_to_migrate = [
        User,        # 独立
        Course,      # 独立
        Chapter,     # 依赖 Course
        Video,       # 依赖 Chapter
        Question,    # 依赖 Course
        Enrollment,  # 依赖 User, Course
        WrongQuestion, # 依赖 User, Question
        StudyRecord,   # 依赖 User
        StudyProgress  # 依赖 User, Video
    ]

    sqlite_db = SqliteSession()
    mysql_db = MysqlSession()

    try:
        # 清空 MySQL 防止主键冲突 (可选，这里假设是空库)
        # 逐个表迁移数据
        for model in tables_to_migrate:
            print(f"Migrating table: {model.__tablename__}...")
            
            # 从 SQLite 读取所有数据
            records = sqlite_db.query(model).all()
            print(f"  Found {len(records)} records.")
            
            if not records:
                continue
                
            # 将每个对象转化为字典（排除不需要的状态属性）
            for record in records:
                # 复制属性，忽略 SQLAlchemy 内部状态
                data = {c.name: getattr(record, c.name) for c in model.__table__.columns}
                
                # 检查 MySQL 中是否已存在
                # 这里假设主键为 'id'
                exists = mysql_db.query(model).filter_by(id=data['id']).first()
                if not exists:
                    new_record = model(**data)
                    mysql_db.add(new_record)
            
            # 提交当前表的修改
            mysql_db.commit()
            print(f"  Migrated {model.__tablename__} successfully.")
            
        print("\nAll data migrated successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        mysql_db.rollback()
    finally:
        sqlite_db.close()
        mysql_db.close()

if __name__ == "__main__":
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        print("Error: DATABASE_URL is still pointing to sqlite. Please check your .env file.")
        sys.exit(1)
        
    migrate_data()
