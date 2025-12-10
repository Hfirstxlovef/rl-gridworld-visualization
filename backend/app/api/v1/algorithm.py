"""
Algorithm API - 算法控制接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio

router = APIRouter(prefix="/algorithm", tags=["Algorithm"])


class AlgorithmType(str, Enum):
    """算法类型枚举"""
    DP = "dp"  # 动态规划
    SARSA = "sarsa"  # Sarsa
    QLEARNING = "qlearning"  # Q-Learning


class AlgorithmStatus(str, Enum):
    """算法状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class StartAlgorithmRequest(BaseModel):
    """启动算法请求"""
    env_id: str = Field(..., description="环境ID")
    algorithm: AlgorithmType = Field(..., description="算法类型")
    params: Optional[Dict[str, Any]] = Field(default=None, description="算法参数")


class AlgorithmParams(BaseModel):
    """算法参数"""
    gamma: float = Field(default=1.0, ge=0, le=1, description="折扣因子")
    alpha: float = Field(default=0.5, ge=0, le=1, description="学习率")
    epsilon: float = Field(default=0.1, ge=0, le=1, description="探索率")
    theta: float = Field(default=1e-6, gt=0, description="收敛阈值")
    max_episodes: int = Field(default=500, ge=1, description="最大回合数")
    max_steps: int = Field(default=100, ge=1, description="每回合最大步数")


class AlgorithmResponse(BaseModel):
    """算法响应"""
    exp_id: str
    env_id: str
    algorithm: AlgorithmType
    status: AlgorithmStatus
    params: Dict[str, Any]


class AlgorithmProgressResponse(BaseModel):
    """算法进度响应"""
    exp_id: str
    status: AlgorithmStatus
    current_episode: int
    total_episodes: int
    current_step: int
    progress_percent: float


# 内存中存储实验实例
experiments: Dict[str, Dict] = {}
exp_counter = 0


@router.post("/start", response_model=AlgorithmResponse)
async def start_algorithm(request: StartAlgorithmRequest):
    """
    启动算法训练

    - **env_id**: 环境ID
    - **algorithm**: 算法类型 (dp/sarsa/qlearning)
    - **params**: 算法参数
    """
    global exp_counter
    exp_counter += 1
    exp_id = f"exp_{exp_counter}"

    # 默认参数
    default_params = AlgorithmParams().model_dump()
    if request.params:
        default_params.update(request.params)

    exp_data = {
        "exp_id": exp_id,
        "env_id": request.env_id,
        "algorithm": request.algorithm,
        "status": AlgorithmStatus.RUNNING,
        "params": default_params,
        "current_episode": 0,
        "total_episodes": default_params["max_episodes"],
        "current_step": 0,
    }

    experiments[exp_id] = exp_data

    return AlgorithmResponse(**exp_data)


@router.post("/stop")
async def stop_algorithm(exp_id: str):
    """停止算法训练"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    experiments[exp_id]["status"] = AlgorithmStatus.PAUSED
    return {"status": "stopped", "exp_id": exp_id}


@router.post("/resume")
async def resume_algorithm(exp_id: str):
    """恢复算法训练"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    experiments[exp_id]["status"] = AlgorithmStatus.RUNNING
    return {"status": "resumed", "exp_id": exp_id}


@router.post("/reset")
async def reset_algorithm(exp_id: str):
    """重置算法"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    experiments[exp_id]["status"] = AlgorithmStatus.IDLE
    experiments[exp_id]["current_episode"] = 0
    experiments[exp_id]["current_step"] = 0
    return {"status": "reset", "exp_id": exp_id}


@router.get("/status/{exp_id}", response_model=AlgorithmProgressResponse)
async def get_algorithm_status(exp_id: str):
    """查询算法状态"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp = experiments[exp_id]
    progress = (exp["current_episode"] / exp["total_episodes"]) * 100 if exp["total_episodes"] > 0 else 0

    return AlgorithmProgressResponse(
        exp_id=exp_id,
        status=exp["status"],
        current_episode=exp["current_episode"],
        total_episodes=exp["total_episodes"],
        current_step=exp["current_step"],
        progress_percent=progress,
    )


@router.get("", response_model=List[AlgorithmResponse])
async def list_experiments():
    """列出所有实验"""
    return [AlgorithmResponse(**exp) for exp in experiments.values()]
