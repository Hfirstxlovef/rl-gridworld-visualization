"""
Environment Model - 环境数据模型
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.sql import func
from app.db.session import Base


class Environment(Base):
    """环境表"""
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    env_id = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # basic, windy, cliff
    grid_size = Column(Integer, nullable=False, default=4)
    config = Column(JSON, nullable=False, default={})
    status = Column(String(20), default="created")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Experiment(Base):
    """实验表"""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # basic, windy, cliff
    algorithm = Column(String(20), nullable=False)  # dp, sarsa, qlearning
    config = Column(JSON, nullable=False, default={})
    status = Column(String(20), default="created")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Iteration(Base):
    """迭代记录表"""
    __tablename__ = "iterations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, nullable=False, index=True)
    episode = Column(Integer, nullable=False)
    step = Column(Integer, nullable=False)
    state = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)
    reward = Column(Float, nullable=False)
    q_value = Column(Float)
    v_value = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())
