# 1. 启动后端 (终端窗口 1)
cd /Users/senor/online_learning_platform
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 启动前端 (终端窗口 2)
cd /Users/senor/online_learning_platform/frontend
npm run dev

# 3. 访问系统
# 打开浏览器访问: http://127.0.0.1:5173



1. 加入一个章节管理
2. 章节表加入查询
3. 研究数据库是啥样的
4. 扩充一下题型（单选，填空）
5. 题分成难易程度
6. 抽题考虑难度
