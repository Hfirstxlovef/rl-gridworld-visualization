#!/bin/bash
# RL-GridWorld-3D 启动脚本

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  RL-GridWorld-3D 启动脚本"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 未安装"
    exit 1
fi

# 检查Node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 未安装"
    exit 1
fi

# 启动后端
echo ""
echo "[1/2] 启动后端服务..."
cd "$PROJECT_ROOT/backend"

# 检查依赖
if [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "  提示: 建议使用虚拟环境"
fi

# 后台启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  后端PID: $BACKEND_PID"
echo "  API文档: http://localhost:8000/docs"

# 等待后端启动
sleep 2

# 启动前端
echo ""
echo "[2/2] 启动前端服务..."
cd "$PROJECT_ROOT/frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "  安装依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "  前端PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo "  启动完成!"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "=========================================="

# 等待并清理
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
