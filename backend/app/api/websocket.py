"""
WebSocket Handler - WebSocket 处理器
"""

import socketio
from loguru import logger
from typing import Dict, Any

# 创建 Socket.IO 服务器
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[
        "http://localhost:16000",
        "http://127.0.0.1:16000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    logger=True,
    engineio_logger=True,
)

# 存储活跃的订阅
active_subscriptions: Dict[str, set] = {}  # exp_id -> set of sid


@sio.event
async def connect(sid, environ):
    """客户端连接事件"""
    logger.info(f"Client connected: {sid}")
    await sio.emit("connected", {"sid": sid, "message": "Connected to RL-GridWorld-3D server"}, to=sid)


@sio.event
async def disconnect(sid):
    """客户端断开事件"""
    logger.info(f"Client disconnected: {sid}")
    # 清理订阅
    for exp_id in list(active_subscriptions.keys()):
        if sid in active_subscriptions[exp_id]:
            active_subscriptions[exp_id].discard(sid)
            if not active_subscriptions[exp_id]:
                del active_subscriptions[exp_id]


@sio.event
async def subscribe(sid, data):
    """订阅实验更新"""
    exp_id = data.get("exp_id")
    if exp_id:
        if exp_id not in active_subscriptions:
            active_subscriptions[exp_id] = set()
        active_subscriptions[exp_id].add(sid)
        logger.info(f"Client {sid} subscribed to experiment {exp_id}")
        await sio.emit("subscribed", {"exp_id": exp_id, "status": "subscribed"}, to=sid)


@sio.event
async def unsubscribe(sid, data):
    """取消订阅"""
    exp_id = data.get("exp_id")
    if exp_id and exp_id in active_subscriptions:
        active_subscriptions[exp_id].discard(sid)
        logger.info(f"Client {sid} unsubscribed from experiment {exp_id}")
        await sio.emit("unsubscribed", {"exp_id": exp_id, "status": "unsubscribed"}, to=sid)


@sio.event
async def ping(sid, data):
    """心跳检测"""
    await sio.emit("pong", {"timestamp": data.get("timestamp")}, to=sid)


# 服务端推送函数（供算法服务调用）
async def emit_iteration_update(exp_id: str, data: Dict[str, Any]):
    """
    推送迭代更新

    data 结构:
    {
        "episode": int,
        "step": int,
        "state": str,
        "action": str,
        "reward": float,
        "q_values": List[float],
        "v_values": List[float],
        "policy": List[str]
    }
    """
    if exp_id in active_subscriptions:
        for sid in active_subscriptions[exp_id]:
            await sio.emit("iteration_update", {"exp_id": exp_id, **data}, to=sid)


async def emit_episode_complete(exp_id: str, data: Dict[str, Any]):
    """
    推送回合完成

    data 结构:
    {
        "episode": int,
        "total_reward": float,
        "steps": int
    }
    """
    if exp_id in active_subscriptions:
        for sid in active_subscriptions[exp_id]:
            await sio.emit("episode_complete", {"exp_id": exp_id, **data}, to=sid)


async def emit_experiment_complete(exp_id: str, data: Dict[str, Any]):
    """
    推送实验完成

    data 结构:
    {
        "final_policy": List[str],
        "final_values": List[float],
        "total_episodes": int,
        "converged": bool
    }
    """
    if exp_id in active_subscriptions:
        for sid in active_subscriptions[exp_id]:
            await sio.emit("experiment_complete", {"exp_id": exp_id, **data}, to=sid)


async def emit_error(exp_id: str, code: int, message: str):
    """推送错误通知"""
    if exp_id in active_subscriptions:
        for sid in active_subscriptions[exp_id]:
            await sio.emit("error", {"exp_id": exp_id, "code": code, "message": message}, to=sid)
