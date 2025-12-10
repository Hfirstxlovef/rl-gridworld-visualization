"""
RL-GridWorld-3D Backend Application
强化学习 Grid World 3D 可视化交互平台 - 主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
import os

from app.core.config import settings
from app.core.logger import setup_logging, app_logger
from app.api.v1 import environment, algorithm, experiment, export
from app.api.websocket import sio

# 初始化日志
setup_logging()

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(environment.router, prefix=settings.API_V1_PREFIX)
app.include_router(algorithm.router, prefix=settings.API_V1_PREFIX)
app.include_router(experiment.router, prefix=settings.API_V1_PREFIX)
app.include_router(export.router, prefix=settings.API_V1_PREFIX)

# 集成 Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    app_logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    app_logger.info(f"API docs available at http://{settings.HOST}:{settings.PORT}/docs")
    app_logger.info(f"WebSocket endpoint: ws://{settings.HOST}:{settings.PORT}/socket.io/")

    # 确保数据目录存在
    os.makedirs(settings.EXPERIMENTS_DIR, exist_ok=True)
    os.makedirs(settings.LOGS_DIR, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    app_logger.info("Shutting down application...")


@app.get("/", tags=["Root"])
async def root():
    """根路径 - 健康检查"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
    }


# 用于直接运行
if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
