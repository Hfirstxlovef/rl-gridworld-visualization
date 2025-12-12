/**
 * 实验状态管理 Store
 * 使用 Zustand 进行轻量级状态管理
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  EnvironmentConfig,
  AlgorithmConfig,
  AlgorithmResult,
  IterationRecord,
  GridCell,
  Position,
  TrainingStats,
  VisualizationSettings,
  AlgorithmType,
  Action,
  IterationSnapshot
} from '../types';

// 实验Store状态接口
interface ExperimentStore {
  // 环境状态
  envId: string | null;
  envConfig: EnvironmentConfig;
  gridSize: number;
  grid: GridCell[][];
  terminalStates: number[];

  // 算法状态
  expId: string | null;
  algorithm: AlgorithmType;
  algorithmConfig: AlgorithmConfig;
  isRunning: boolean;
  isPaused: boolean;
  progress: number;

  // 结果数据
  valueFunction: number[];
  policy: number[][];
  policyArrows: Record<number, string[]>;
  currentIteration: number;
  history: IterationRecord[];
  convergenceHistory: { iteration: number; maxDelta: number; avgValue: number }[];
  result: AlgorithmResult | null;

  // TD算法数据
  episodeRewards: number[];
  episodeLengths: number[];
  successRate: number;
  avgReward: number;

  // Agent状态
  agentState: number | null;
  agentPosition: Position | null;

  // 训练统计
  stats: TrainingStats;

  // 可视化设置
  visualization: VisualizationSettings;

  // 播放控制状态
  iterationSnapshots: IterationSnapshot[];
  playbackIndex: number;
  isPlaying: boolean;
  playbackSpeed: number;  // ms/帧

  // Actions - 环境
  setEnvId: (id: string) => void;
  setEnvConfig: (config: Partial<EnvironmentConfig>) => void;
  setGridSize: (size: number) => void;
  initializeGrid: (size: number) => void;
  updateGridCell: (state: number, updates: Partial<GridCell>) => void;

  // Actions - 算法
  setExpId: (id: string) => void;
  setAlgorithm: (algo: AlgorithmType) => void;
  setAlgorithmConfig: (config: Partial<AlgorithmConfig>) => void;
  setRunning: (running: boolean) => void;
  setPaused: (paused: boolean) => void;
  setProgress: (progress: number) => void;

  // Actions - 结果
  setValueFunction: (values: number[]) => void;
  setPolicy: (policy: number[][]) => void;
  setPolicyArrows: (arrows: Record<number, string[]>) => void;
  setCurrentIteration: (iteration: number) => void;
  addIterationRecord: (record: IterationRecord) => void;
  addConvergencePoint: (point: { iteration: number; maxDelta: number; avgValue: number }) => void;
  setConvergenceHistory: (history: { iteration: number; maxDelta: number; avgValue: number }[]) => void;
  setResult: (result: AlgorithmResult) => void;
  clearHistory: () => void;

  // Actions - TD数据
  setTDData: (data: { episodeRewards?: number[]; episodeLengths?: number[]; successRate?: number; avgReward?: number }) => void;

  // Actions - Agent
  setAgentState: (state: number | null) => void;
  moveAgent: (action: Action) => void;

  // Actions - 可视化
  setVisualization: (settings: Partial<VisualizationSettings>) => void;

  // Actions - 播放控制
  setIterationSnapshots: (snapshots: IterationSnapshot[]) => void;
  setPlaybackIndex: (index: number) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  playAnimation: () => void;
  pauseAnimation: () => void;
  stepForward: () => void;
  stepBackward: () => void;
  seekTo: (index: number) => void;
  applySnapshot: (index: number) => void;

  // Actions - 重置
  reset: () => void;
  resetAlgorithm: () => void;
}

// 默认环境配置
const defaultEnvConfig: EnvironmentConfig = {
  type: 'basic',
  gridSize: 4,
  stepReward: -1.0,
  terminalReward: 0.0,
  gamma: 1.0
};

// 默认算法配置
const defaultAlgorithmConfig: AlgorithmConfig = {
  algorithm: 'policy_iteration',
  gamma: 1.0,
  theta: 1e-6,
  maxIterations: 1000,
  learningRate: 0.1,
  epsilon: 0.1,
  maxEpisodes: 500
};

// 默认可视化设置
const defaultVisualization: VisualizationSettings = {
  showValueHeatmap: true,
  showPolicyArrows: true,
  showGrid: true,
  showAgent: true,
  animationSpeed: 50,
  cameraMode: 'orbit',
  colorScheme: 'blue-red'
};

// 默认统计数据
const defaultStats: TrainingStats = {
  currentEpisode: 0,
  totalEpisodes: 0,
  currentStep: 0,
  totalReward: 0,
  avgReward: 0,
  successRate: 0,
  bestPathLength: 0
};

// 初始化网格
function createInitialGrid(size: number): GridCell[][] {
  const grid: GridCell[][] = [];
  const terminalStates = [0, size * size - 1];

  for (let row = 0; row < size; row++) {
    const rowCells: GridCell[] = [];
    for (let col = 0; col < size; col++) {
      const state = row * size + col;
      const isTerminal = terminalStates.includes(state);

      rowCells.push({
        state,
        row,
        col,
        type: isTerminal ? 'terminal' : 'normal',
        value: 0,
        qValues: [0, 0, 0, 0],
        policy: [0.25, 0.25, 0.25, 0.25],
        bestActions: []
      });
    }
    grid.push(rowCells);
  }

  return grid;
}

// 创建Store
export const useExperimentStore = create<ExperimentStore>()(
  devtools(
    (set, get) => ({
      // 初始状态
      envId: null,
      envConfig: defaultEnvConfig,
      gridSize: 4,
      grid: createInitialGrid(4),
      terminalStates: [0, 15],

      expId: null,
      algorithm: 'policy_iteration',
      algorithmConfig: defaultAlgorithmConfig,
      isRunning: false,
      isPaused: false,
      progress: 0,

      valueFunction: new Array(16).fill(0),
      policy: new Array(16).fill(null).map(() => [0.25, 0.25, 0.25, 0.25]),
      policyArrows: {},
      currentIteration: 0,
      history: [],
      convergenceHistory: [],
      result: null,

      episodeRewards: [],
      episodeLengths: [],
      successRate: 0,
      avgReward: 0,

      agentState: null,
      agentPosition: null,

      stats: defaultStats,
      visualization: defaultVisualization,

      // 播放控制初始状态
      iterationSnapshots: [],
      playbackIndex: 0,
      isPlaying: false,
      playbackSpeed: 250,  // 默认250ms/帧（细粒度快照，快些播放）

      // 环境Actions
      setEnvId: (id) => set({ envId: id }),

      setEnvConfig: (config) => set((state) => ({
        envConfig: { ...state.envConfig, ...config }
      })),

      setGridSize: (size) => {
        const grid = createInitialGrid(size);
        const terminalStates = [0, size * size - 1];
        set({
          gridSize: size,
          grid,
          terminalStates,
          valueFunction: new Array(size * size).fill(0),
          policy: new Array(size * size).fill(null).map(() => [0.25, 0.25, 0.25, 0.25])
        });
      },

      initializeGrid: (size) => {
        const grid = createInitialGrid(size);
        set({ grid, gridSize: size });
      },

      updateGridCell: (state, updates) => set((store) => {
        const size = store.gridSize;
        const row = Math.floor(state / size);
        const col = state % size;
        const newGrid = [...store.grid];
        newGrid[row] = [...newGrid[row]];
        newGrid[row][col] = { ...newGrid[row][col], ...updates };
        return { grid: newGrid };
      }),

      // 算法Actions
      setExpId: (id) => set({ expId: id }),

      setAlgorithm: (algo) => set({ algorithm: algo }),

      setAlgorithmConfig: (config) => set((state) => ({
        algorithmConfig: { ...state.algorithmConfig, ...config }
      })),

      setRunning: (running) => set({ isRunning: running }),

      setPaused: (paused) => set({ isPaused: paused }),

      setProgress: (progress) => set({ progress }),

      // 结果Actions
      setValueFunction: (values) => {
        const { gridSize, grid } = get();
        const newGrid = grid.map((row, rowIdx) =>
          row.map((cell, colIdx) => {
            const state = rowIdx * gridSize + colIdx;
            return { ...cell, value: values[state] || 0 };
          })
        );
        set({ valueFunction: values, grid: newGrid });
      },

      setPolicy: (policy) => {
        const { gridSize, grid } = get();
        const newGrid = grid.map((row, rowIdx) =>
          row.map((cell, colIdx) => {
            const state = rowIdx * gridSize + colIdx;
            const statePolicy = policy[state] || [0.25, 0.25, 0.25, 0.25];
            const maxProb = Math.max(...statePolicy);
            const bestActions = statePolicy
              .map((p, i) => (p === maxProb && p > 0 ? i : -1))
              .filter((i) => i >= 0) as Action[];
            return { ...cell, policy: statePolicy, bestActions };
          })
        );
        set({ policy, grid: newGrid });
      },

      setPolicyArrows: (arrows) => set({ policyArrows: arrows }),

      setCurrentIteration: (iteration) => set({ currentIteration: iteration }),

      addIterationRecord: (record) => set((state) => ({
        history: [...state.history, record]
      })),

      addConvergencePoint: (point) => set((state) => ({
        convergenceHistory: [...state.convergenceHistory, point]
      })),

      setConvergenceHistory: (history) => set({ convergenceHistory: history }),

      setResult: (result) => set({ result }),

      clearHistory: () => set({ history: [], convergenceHistory: [], currentIteration: 0 }),

      // TD数据Actions
      setTDData: (data) => set((state) => ({
        episodeRewards: data.episodeRewards ?? state.episodeRewards,
        episodeLengths: data.episodeLengths ?? state.episodeLengths,
        successRate: data.successRate ?? state.successRate,
        avgReward: data.avgReward ?? state.avgReward
      })),

      // Agent Actions
      setAgentState: (state) => {
        if (state === null) {
          set({ agentState: null, agentPosition: null });
        } else {
          const { gridSize } = get();
          const row = Math.floor(state / gridSize);
          const col = state % gridSize;
          set({ agentState: state, agentPosition: { row, col } });
        }
      },

      moveAgent: (action) => {
        const { agentState, gridSize } = get();
        if (agentState === null) return;

        const row = Math.floor(agentState / gridSize);
        const col = agentState % gridSize;

        let newRow = row;
        let newCol = col;

        switch (action) {
          case Action.UP:
            newRow = Math.max(0, row - 1);
            break;
          case Action.DOWN:
            newRow = Math.min(gridSize - 1, row + 1);
            break;
          case Action.LEFT:
            newCol = Math.max(0, col - 1);
            break;
          case Action.RIGHT:
            newCol = Math.min(gridSize - 1, col + 1);
            break;
        }

        const newState = newRow * gridSize + newCol;
        set({
          agentState: newState,
          agentPosition: { row: newRow, col: newCol }
        });
      },

      // 可视化Actions
      setVisualization: (settings) => set((state) => ({
        visualization: { ...state.visualization, ...settings }
      })),

      // 播放控制Actions
      setIterationSnapshots: (snapshots) => set({ iterationSnapshots: snapshots, playbackIndex: 0 }),

      setPlaybackIndex: (index) => set({ playbackIndex: index }),

      setIsPlaying: (playing) => set({ isPlaying: playing }),

      setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),

      playAnimation: () => set({ isPlaying: true }),

      pauseAnimation: () => set({ isPlaying: false }),

      stepForward: () => {
        const { playbackIndex, iterationSnapshots } = get();
        if (playbackIndex < iterationSnapshots.length - 1) {
          const newIndex = playbackIndex + 1;
          get().applySnapshot(newIndex);
          set({ playbackIndex: newIndex });
        }
      },

      stepBackward: () => {
        const { playbackIndex } = get();
        if (playbackIndex > 0) {
          const newIndex = playbackIndex - 1;
          get().applySnapshot(newIndex);
          set({ playbackIndex: newIndex });
        }
      },

      seekTo: (index) => {
        const { iterationSnapshots } = get();
        if (index >= 0 && index < iterationSnapshots.length) {
          get().applySnapshot(index);
          set({ playbackIndex: index });
        }
      },

      applySnapshot: (index) => {
        const { iterationSnapshots, gridSize, grid } = get();
        if (index < 0 || index >= iterationSnapshots.length) return;

        const snapshot = iterationSnapshots[index];

        // 更新值函数
        const newGrid = grid.map((row, rowIdx) =>
          row.map((cell, colIdx) => {
            const state = rowIdx * gridSize + colIdx;
            const value = snapshot.values[state] || 0;
            const arrows = snapshot.policyArrows[String(state)] || [];
            const bestActions = arrows.map(arrow => {
              switch (arrow) {
                case 'UP': return Action.UP;
                case 'DOWN': return Action.DOWN;
                case 'LEFT': return Action.LEFT;
                case 'RIGHT': return Action.RIGHT;
                default: return Action.UP;
              }
            });
            return { ...cell, value, bestActions };
          })
        );

        // 转换策略箭头格式
        const policyArrows: Record<number, string[]> = {};
        Object.entries(snapshot.policyArrows).forEach(([key, value]) => {
          policyArrows[parseInt(key)] = value;
        });

        set({
          valueFunction: snapshot.values,
          policyArrows,
          grid: newGrid,
          currentIteration: snapshot.iteration
        });
      },

      // 重置Actions
      reset: () => {
        const grid = createInitialGrid(4);
        set({
          envId: null,
          envConfig: defaultEnvConfig,
          gridSize: 4,
          grid,
          terminalStates: [0, 15],
          expId: null,
          algorithm: 'policy_iteration',
          algorithmConfig: defaultAlgorithmConfig,
          isRunning: false,
          isPaused: false,
          progress: 0,
          valueFunction: new Array(16).fill(0),
          policy: new Array(16).fill(null).map(() => [0.25, 0.25, 0.25, 0.25]),
          policyArrows: {},
          currentIteration: 0,
          history: [],
          convergenceHistory: [],
          result: null,
          episodeRewards: [],
          episodeLengths: [],
          successRate: 0,
          avgReward: 0,
          agentState: null,
          agentPosition: null,
          stats: defaultStats,
          // 播放控制重置
          iterationSnapshots: [],
          playbackIndex: 0,
          isPlaying: false,
          playbackSpeed: 250
        });
      },

      resetAlgorithm: () => set({
        expId: null,
        isRunning: false,
        isPaused: false,
        progress: 0,
        currentIteration: 0,
        history: [],
        convergenceHistory: [],
        result: null,
        episodeRewards: [],
        episodeLengths: [],
        successRate: 0,
        avgReward: 0,
        // 播放控制重置
        iterationSnapshots: [],
        playbackIndex: 0,
        isPlaying: false
      })
    }),
    { name: 'experiment-store' }
  )
);

export default useExperimentStore;
