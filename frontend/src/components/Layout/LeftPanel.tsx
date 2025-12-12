/**
 * LeftPanel - 左侧控制面板
 *
 * 包含算法配置、训练控制等功能
 */

import React, { useState } from 'react';
import {
  Card,
  Select,
  InputNumber,
  Button,
  Space,
  Divider,
  Slider,
  Form,
  Switch,
  Tooltip,
  Badge
} from 'antd';
import {
  PlayCircleOutlined,
  ReloadOutlined,
  SettingOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import { useExperimentStore } from '../../store';
import { useExperiment } from '../../hooks';
import { EnvironmentConfig, AlgorithmConfig } from '../../types';

const { Option } = Select;

const LeftPanel: React.FC = () => {
  const {
    envId,
    isRunning,
    visualization,
    setVisualization,
    setGridSize: updateGridSize
  } = useExperimentStore();

  const {
    isLoading,
    initEnvironment,
    resetEnv,
    runAlgorithm
  } = useExperiment();

  // 环境配置状态
  const [envConfig, setEnvConfig] = useState<EnvironmentConfig>({
    type: 'basic',
    gridSize: 4,
    stepReward: -1.0,
    terminalReward: 0.0,
    gamma: 1.0
  });

  // 算法配置状态
  const [algoConfig, setAlgoConfig] = useState<AlgorithmConfig>({
    algorithm: 'policy_iteration',
    gamma: 1.0,
    theta: 1e-6,
    maxIterations: 1000,
    learningRate: 0.1,
    epsilon: 0.1,
    maxEpisodes: 500
  });

  // 演示速度
  const [speed, setSpeed] = useState(50);

  // 更新环境配置
  const handleEnvConfigChange = (key: keyof EnvironmentConfig, value: any) => {
    setEnvConfig(prev => ({ ...prev, [key]: value }));
    if (key === 'gridSize') {
      updateGridSize(value);
    }
  };

  // 更新算法配置
  const handleAlgoConfigChange = (key: keyof AlgorithmConfig, value: any) => {
    setAlgoConfig(prev => ({ ...prev, [key]: value }));
  };

  // 初始化环境并运行
  const handleStartTraining = async () => {
    // 总是重新创建环境（确保使用最新配置）
    const currentEnvId = await initEnvironment(envConfig);
    if (!currentEnvId) return;

    // 运行算法
    await runAlgorithm(algoConfig);
  };

  // 重置
  const handleReset = async () => {
    await resetEnv();
  };

  return (
    <div className="left-panel">
      {/* 环境配置 */}
      <Card
        title={
          <span>
            <SettingOutlined /> 环境配置
          </span>
        }
        size="small"
        className="config-card"
        extra={
          envId ? (
            <Badge status="success" text="已创建" />
          ) : (
            <Badge status="default" text="未创建" />
          )
        }
      >
        <Form layout="vertical" size="small">
          <Form.Item label="实验类型">
            <Select
              value={envConfig.type}
              onChange={(value) => handleEnvConfigChange('type', value)}
              style={{ width: '100%' }}
            >
              <Option value="basic">基础网格世界 (4×4)</Option>
              <Option value="windy">有风网格世界 (7×10)</Option>
              <Option value="cliff">悬崖行走 (4×12)</Option>
            </Select>
          </Form.Item>

          {envConfig.type === 'basic' && (
            <Form.Item label="网格大小">
              <Space.Compact style={{ width: '100%' }}>
                <InputNumber
                  min={3}
                  max={10}
                  value={envConfig.gridSize}
                  onChange={(value) => handleEnvConfigChange('gridSize', value)}
                  style={{ width: '70%' }}
                />
                <Button disabled style={{ width: '30%', cursor: 'default' }}>× N</Button>
              </Space.Compact>
            </Form.Item>
          )}

          {envConfig.type === 'windy' && (
            <Form.Item label="网格大小">
              <Space.Compact style={{ width: '100%' }}>
                <InputNumber
                  value={10}
                  disabled
                  style={{ width: '50%' }}
                />
                <Button disabled style={{ width: '50%', cursor: 'default' }}>× 7 (固定)</Button>
              </Space.Compact>
            </Form.Item>
          )}

          {envConfig.type === 'cliff' && (
            <Form.Item label="网格大小">
              <Space.Compact style={{ width: '100%' }}>
                <InputNumber
                  value={12}
                  disabled
                  style={{ width: '50%' }}
                />
                <Button disabled style={{ width: '50%', cursor: 'default' }}>× 4 (固定)</Button>
              </Space.Compact>
            </Form.Item>
          )}

          <Form.Item label={`步长奖励: ${envConfig.stepReward}`}>
            <Slider
              min={-5}
              max={0}
              step={0.1}
              value={envConfig.stepReward}
              onChange={(value) => handleEnvConfigChange('stepReward', value)}
            />
          </Form.Item>

          <Form.Item label={`折扣因子 (γ): ${envConfig.gamma}`}>
            <Slider
              min={0}
              max={1}
              step={0.01}
              value={envConfig.gamma}
              onChange={(value) => handleEnvConfigChange('gamma', value)}
            />
          </Form.Item>
        </Form>
      </Card>

      {/* 算法配置 */}
      <Card
        title={
          <span>
            <ExperimentOutlined /> 算法配置
          </span>
        }
        size="small"
        className="config-card"
      >
        <Form layout="vertical" size="small">
          <Form.Item label="算法选择">
            <Select
              value={algoConfig.algorithm}
              onChange={(value) => handleAlgoConfigChange('algorithm', value)}
              style={{ width: '100%' }}
            >
              <Option value="policy_evaluation">策略评估 (DP)</Option>
              <Option value="policy_iteration">策略迭代 (DP)</Option>
              <Option value="value_iteration">值迭代 (DP)</Option>
              <Option value="sarsa">SARSA (TD)</Option>
              <Option value="q_learning">Q-Learning (TD)</Option>
            </Select>
          </Form.Item>

          {/* DP算法配置 */}
          {['policy_evaluation', 'policy_iteration', 'value_iteration'].includes(algoConfig.algorithm) && (
            <>
              <Form.Item label={`收敛阈值 (θ): ${algoConfig.theta}`}>
                <Select
                  value={algoConfig.theta}
                  onChange={(value) => handleAlgoConfigChange('theta', value)}
                  style={{ width: '100%' }}
                >
                  <Option value={1e-4}>1e-4 (快速)</Option>
                  <Option value={1e-6}>1e-6 (标准)</Option>
                  <Option value={1e-8}>1e-8 (精确)</Option>
                </Select>
              </Form.Item>

              <Form.Item label="最大迭代次数">
                <InputNumber
                  min={100}
                  max={10000}
                  step={100}
                  value={algoConfig.maxIterations}
                  onChange={(value) => handleAlgoConfigChange('maxIterations', value)}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </>
          )}

          {/* TD算法配置 (SARSA/Q-Learning) */}
          {['sarsa', 'q_learning'].includes(algoConfig.algorithm) && (
            <>
              <Form.Item label={`学习率 (α): ${algoConfig.learningRate}`}>
                <Slider
                  min={0.01}
                  max={1.0}
                  step={0.01}
                  value={algoConfig.learningRate}
                  onChange={(value) => handleAlgoConfigChange('learningRate', value)}
                />
              </Form.Item>

              <Form.Item label={`探索率 (ε): ${algoConfig.epsilon}`}>
                <Slider
                  min={0}
                  max={1.0}
                  step={0.01}
                  value={algoConfig.epsilon}
                  onChange={(value) => handleAlgoConfigChange('epsilon', value)}
                />
              </Form.Item>

              <Form.Item label="最大回合数">
                <InputNumber
                  min={50}
                  max={5000}
                  step={50}
                  value={algoConfig.maxEpisodes}
                  onChange={(value) => handleAlgoConfigChange('maxEpisodes', value)}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </>
          )}
        </Form>
      </Card>

      {/* 训练控制 */}
      <Card title="训练控制" size="small" className="control-card">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div className="speed-control">
            <span>演示速度: {speed}%</span>
            <Slider min={1} max={100} value={speed} onChange={setSpeed} />
          </div>

          <Divider style={{ margin: '8px 0' }} />

          <Space wrap style={{ width: '100%', justifyContent: 'center' }}>
            <Tooltip title="开始训练">
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStartTraining}
                loading={isLoading}
                disabled={isRunning}
              >
                {envId ? '开始训练' : '创建并训练'}
              </Button>
            </Tooltip>

            <Tooltip title="重置环境">
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
                disabled={!envId || isRunning}
              >
                重置
              </Button>
            </Tooltip>
          </Space>
        </Space>
      </Card>

      {/* 可视化设置 */}
      <Card title="可视化设置" size="small" className="config-card">
        <Form layout="horizontal" size="small">
          <Form.Item label="值函数热力图" style={{ marginBottom: 8 }}>
            <Switch
              checked={visualization.showValueHeatmap}
              onChange={(checked) => setVisualization({ showValueHeatmap: checked })}
            />
          </Form.Item>

          <Form.Item label="策略箭头" style={{ marginBottom: 8 }}>
            <Switch
              checked={visualization.showPolicyArrows}
              onChange={(checked) => setVisualization({ showPolicyArrows: checked })}
            />
          </Form.Item>

          <Form.Item label="显示Agent" style={{ marginBottom: 8 }}>
            <Switch
              checked={visualization.showAgent}
              onChange={(checked) => setVisualization({ showAgent: checked })}
            />
          </Form.Item>

          <Form.Item label="相机模式" style={{ marginBottom: 0 }}>
            <Select
              value={visualization.cameraMode}
              onChange={(value) => setVisualization({ cameraMode: value })}
              size="small"
              style={{ width: 100 }}
            >
              <Option value="orbit">环绕</Option>
              <Option value="topdown">俯视</Option>
              <Option value="follow">跟随</Option>
            </Select>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LeftPanel;
