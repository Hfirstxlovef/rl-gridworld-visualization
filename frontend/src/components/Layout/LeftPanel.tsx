import React, { useState } from 'react';
import { Card, Select, InputNumber, Button, Space, Divider, Slider, Form } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, ReloadOutlined, StepForwardOutlined } from '@ant-design/icons';

const { Option } = Select;

interface TrainingConfig {
  algorithm: string;
  mazeSize: number;
  learningRate: number;
  discountFactor: number;
  epsilon: number;
  episodes: number;
}

const LeftPanel: React.FC = () => {
  const [config, setConfig] = useState<TrainingConfig>({
    algorithm: 'q-learning',
    mazeSize: 10,
    learningRate: 0.1,
    discountFactor: 0.95,
    epsilon: 0.1,
    episodes: 1000,
  });

  const [isTraining, setIsTraining] = useState(false);
  const [speed, setSpeed] = useState(50);

  const handleConfigChange = (key: keyof TrainingConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleStartTraining = () => {
    setIsTraining(true);
    // TODO: 通过 WebSocket 发送开始训练命令
    console.log('开始训练，配置:', config);
  };

  const handlePauseTraining = () => {
    setIsTraining(false);
    // TODO: 通过 WebSocket 发送暂停训练命令
    console.log('暂停训练');
  };

  const handleResetTraining = () => {
    setIsTraining(false);
    // TODO: 通过 WebSocket 发送重置训练命令
    console.log('重置训练');
  };

  const handleStepForward = () => {
    // TODO: 通过 WebSocket 发送单步执行命令
    console.log('单步执行');
  };

  return (
    <div className="left-panel">
      <Card title="算法配置" size="small" className="config-card">
        <Form layout="vertical" size="small">
          <Form.Item label="算法选择">
            <Select
              value={config.algorithm}
              onChange={(value) => handleConfigChange('algorithm', value)}
              style={{ width: '100%' }}
            >
              <Option value="q-learning">Q-Learning</Option>
              <Option value="sarsa">SARSA</Option>
              <Option value="dqn">DQN (深度Q网络)</Option>
            </Select>
          </Form.Item>

          <Form.Item label="迷宫大小">
            <InputNumber
              min={5}
              max={50}
              value={config.mazeSize}
              onChange={(value) => handleConfigChange('mazeSize', value)}
              style={{ width: '100%' }}
              addonAfter="× N"
            />
          </Form.Item>

          <Form.Item label={`学习率 (α): ${config.learningRate}`}>
            <Slider
              min={0.01}
              max={1}
              step={0.01}
              value={config.learningRate}
              onChange={(value) => handleConfigChange('learningRate', value)}
            />
          </Form.Item>

          <Form.Item label={`折扣因子 (γ): ${config.discountFactor}`}>
            <Slider
              min={0}
              max={1}
              step={0.01}
              value={config.discountFactor}
              onChange={(value) => handleConfigChange('discountFactor', value)}
            />
          </Form.Item>

          <Form.Item label={`探索率 (ε): ${config.epsilon}`}>
            <Slider
              min={0}
              max={1}
              step={0.01}
              value={config.epsilon}
              onChange={(value) => handleConfigChange('epsilon', value)}
            />
          </Form.Item>

          <Form.Item label="训练回合数">
            <InputNumber
              min={100}
              max={100000}
              step={100}
              value={config.episodes}
              onChange={(value) => handleConfigChange('episodes', value)}
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Card>

      <Card title="训练控制" size="small" className="control-card">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div className="speed-control">
            <span>演示速度: {speed}%</span>
            <Slider
              min={1}
              max={100}
              value={speed}
              onChange={setSpeed}
            />
          </div>

          <Divider style={{ margin: '8px 0' }} />

          <Space wrap>
            {isTraining ? (
              <Button
                type="primary"
                icon={<PauseCircleOutlined />}
                onClick={handlePauseTraining}
                danger
              >
                暂停
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStartTraining}
              >
                开始训练
              </Button>
            )}

            <Button
              icon={<StepForwardOutlined />}
              onClick={handleStepForward}
              disabled={isTraining}
            >
              单步
            </Button>

            <Button
              icon={<ReloadOutlined />}
              onClick={handleResetTraining}
            >
              重置
            </Button>
          </Space>
        </Space>
      </Card>
    </div>
  );
};

export default LeftPanel;
