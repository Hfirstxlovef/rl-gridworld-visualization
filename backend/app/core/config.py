"""
Application Configuration - 应用配置管理
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""

    # 项目基本信息
    PROJECT_NAME: str = "RL-GridWorld-3D"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "强化学习 Grid World 3D 可视化交互平台"

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 16210
    DEBUG: bool = True

    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:16000",
        "http://127.0.0.1:16000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/rl_gridworld.db"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/app.log"

    # 实验数据目录
    EXPERIMENTS_DIR: str = "data/experiments"
    LOGS_DIR: str = "data/logs"

    # Grid World 默认配置
    DEFAULT_GRID_SIZE: int = 4
    MAX_GRID_SIZE: int = 20
    MIN_GRID_SIZE: int = 3

    # 算法默认参数
    DEFAULT_GAMMA: float = 1.0  # 折扣因子
    DEFAULT_ALPHA: float = 0.5  # 学习率
    DEFAULT_EPSILON: float = 0.1  # 探索率
    DEFAULT_THETA: float = 1e-6  # 收敛阈值

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


def get_project_root() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
