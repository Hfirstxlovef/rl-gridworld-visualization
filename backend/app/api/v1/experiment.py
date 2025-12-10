"""
Experiment API - 实验管理接口
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/experiment", tags=["Experiment"])


class ExperimentType(str, Enum):
    """实验类型枚举"""
    BASIC = "basic"
    WINDY = "windy"
    CLIFF = "cliff"


class ExperimentStatus(str, Enum):
    """实验状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IterationRecord(BaseModel):
    """迭代记录"""
    episode: int
    step: int
    state: str
    action: str
    reward: float
    q_value: Optional[float] = None
    v_value: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ExperimentDetail(BaseModel):
    """实验详情"""
    id: str
    name: str
    type: ExperimentType
    algorithm: str
    config: Dict[str, Any]
    status: ExperimentStatus
    created_at: datetime
    iterations: List[IterationRecord] = []


class ExperimentListResponse(BaseModel):
    """实验列表响应"""
    experiments: List[ExperimentDetail]
    total: int
    page: int
    size: int


# 内存存储
experiment_store: Dict[str, ExperimentDetail] = {}


@router.get("", response_model=ExperimentListResponse)
async def list_experiments(
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=10, ge=1, le=100, description="每页数量"),
):
    """获取实验列表"""
    all_experiments = list(experiment_store.values())
    total = len(all_experiments)

    start = (page - 1) * size
    end = start + size
    experiments = all_experiments[start:end]

    return ExperimentListResponse(
        experiments=experiments,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{exp_id}", response_model=ExperimentDetail)
async def get_experiment(exp_id: str):
    """获取实验详情"""
    if exp_id not in experiment_store:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    return experiment_store[exp_id]


@router.delete("/{exp_id}")
async def delete_experiment(exp_id: str):
    """删除实验"""
    if exp_id not in experiment_store:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    del experiment_store[exp_id]
    return {"status": "deleted", "exp_id": exp_id}
