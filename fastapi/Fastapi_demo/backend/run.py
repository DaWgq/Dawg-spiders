"""统一启动入口 (生产部署用)。

宝塔面板 Python 项目管理器 / Supervisor / 本机后台运行都可以直接执行:
    python run.py

等价于: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)