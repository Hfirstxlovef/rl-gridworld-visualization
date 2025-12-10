"""
Logging Configuration - 日志配置
"""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """配置日志系统"""

    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )

    # 添加文件输出
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")

    return logger


# 导出配置好的 logger
app_logger = logger
