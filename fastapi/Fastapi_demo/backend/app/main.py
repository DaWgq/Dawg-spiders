import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import auth, books, circulation, dashboard, readers
from .seed import ensure_defaults

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 表结构由 sql/library_management.sql 创建; 这里兜底建表并补齐默认数据
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ensure_defaults(db)
        finally:
            db.close()
    except Exception as exc:  # 数据库不可用时不影响应用启动
        logger.warning("初始化数据库失败(应用仍会启动): %s", exc)
    yield


app = FastAPI(
    title="图书管理系统 API",
    description="基于 FastAPI + MySQL 的图书管理系统后端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# 允许跨域 (前后端分离开发环境)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(books.router, prefix="/api/books", tags=["图书"])
app.include_router(readers.router, prefix="/api/readers", tags=["读者"])
app.include_router(circulation.router, prefix="/api/circulation", tags=["借阅流通"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])


@app.get("/api/health", tags=["系统"], summary="健康检查")
def health_check():
    return {"status": "ok", "service": "图书管理系统 API"}