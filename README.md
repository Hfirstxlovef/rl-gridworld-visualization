# RL-GridWorld-3D

强化学习 Grid World 3D 可视化交互平台

## 项目简介

本项目是一个交互式3D可视化平台，用于强化学习经典Grid World问题的教学与实验。通过3D立体可视化、实时交互控制、算法对比分析等功能，提升强化学习的教学效果和研究效率。

### 支持的实验场景

| 实验 | 环境 | 算法 | 说明 |
|------|------|------|------|
| 实验一 | Basic Gridworld (4×4) | 动态规划 (策略迭代/值迭代) | 状态值函数与策略评估 |
| 实验二 | Windy Gridworld (7×10) | SARSA | 有风环境下的TD学习 |
| 实验三 | Cliff Walking (4×12) | SARSA vs Q-Learning | On-policy与Off-policy对比 |

## 功能特性

- **3D可视化**: 网格世界立体渲染，值函数热力图，策略箭头显示
- **实时交互**: 参数调节，算法控制，视角切换
- **多种算法**: 策略评估、策略迭代、值迭代、SARSA、Q-Learning
- **学习曲线**: 收敛曲线图表，回合奖励统计
- **数据导出**: XML格式日志记录，符合实验要求
- **教学模式**: 分步演示，关键概念高亮

## 技术栈

### 前端
- React 18 + TypeScript
- Three.js / React Three Fiber (3D渲染)
- Ant Design (UI组件)
- Recharts (图表)
- Zustand (状态管理)

### 后端
- FastAPI (Python 3.10+)
- NumPy (数值计算)
- SQLAlchemy + SQLite (数据存储)
- lxml (XML导出)

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- npm 或 yarn

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd 实验4-强化学习

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 启动服务

```bash
# 终端1: 启动后端
cd backend
uvicorn app.main:app --reload --port 8000

# 终端2: 启动前端
cd frontend
npm run dev
```

访问 http://localhost:5173 查看应用。

## 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/v1/         # REST API路由
│   │   │   ├── algorithm.py    # 算法控制API
│   │   │   ├── environment.py  # 环境管理API
│   │   │   └── export.py       # 数据导出API
│   │   ├── services/
│   │   │   ├── algorithm/      # 算法实现
│   │   │   │   ├── dp_solver.py    # 动态规划
│   │   │   │   └── td_solver.py    # TD算法
│   │   │   ├── environment/    # 环境模型
│   │   │   │   ├── basic_grid.py   # 基础网格
│   │   │   │   ├── windy_grid.py   # 有风网格
│   │   │   │   └── cliff_walking.py # 悬崖行走
│   │   │   └── export/         # 导出模块
│   │   └── schemas/            # 数据模型
│   ├── tests/                  # 单元测试
│   └── requirements.txt
│
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/         # 布局组件
│   │   │   ├── Scene3D/        # 3D场景组件
│   │   │   └── Charts/         # 图表组件
│   │   ├── hooks/              # 自定义Hooks
│   │   ├── store/              # 状态管理
│   │   ├── services/           # API服务
│   │   └── types/              # 类型定义
│   └── package.json
│
└── README.md
```

## API文档

启动后端后访问: http://localhost:8000/docs

### 主要接口

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/v1/environment | 创建环境 |
| GET | /api/v1/environment/{id} | 获取环境状态 |
| POST | /api/v1/algorithm/start | 启动算法 |
| POST | /api/v1/algorithm/run-sync | 同步执行算法 |
| GET | /api/v1/export/xml/{id} | 导出XML日志 |

## 使用说明

### 1. 选择实验类型

在左侧控制面板选择:
- **Basic Gridworld**: 4×4网格，用于学习DP算法
- **Windy Gridworld**: 7×10网格，体验风力影响
- **Cliff Walking**: 4×12网格，对比SARSA与Q-Learning

### 2. 配置参数

- **DP算法**: 折扣因子γ、收敛阈值θ
- **TD算法**: 学习率α、探索率ε、最大回合数

### 3. 运行算法

点击"开始训练"按钮，观察:
- 3D场景中的值函数变化（颜色/高度）
- 策略箭头的演化
- 右侧面板的收敛曲线

### 4. 导出结果

点击"导出XML"保存实验日志，用于实验报告。

## 测试

```bash
# 运行后端测试
cd backend
pytest tests/ -v

# 运行前端类型检查
cd frontend
npx tsc --noEmit
```

## 算法说明

### 动态规划 (DP)

- **策略评估**: 给定策略π，计算状态值函数V^π(s)
- **策略迭代**: 交替进行策略评估和策略改进
- **值迭代**: 直接迭代贝尔曼最优方程

### 时序差分 (TD)

- **SARSA**: On-policy, Q(S,A) ← Q(S,A) + α[R + γQ(S',A') - Q(S,A)]
- **Q-Learning**: Off-policy, Q(S,A) ← Q(S,A) + α[R + γmax_a Q(S',a) - Q(S,A)]

## 参考资料

1. Sutton & Barto《强化学习导论（第2版）》
2. [Three.js文档](https://threejs.org/docs)
3. [FastAPI文档](https://fastapi.tiangolo.com)

## 许可证

MIT License
