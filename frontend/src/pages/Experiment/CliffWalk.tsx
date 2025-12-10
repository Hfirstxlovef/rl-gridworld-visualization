/**
 * CliffWalk - 悬崖行走实验页面
 *
 * 练习6.9/6.10: SARSA vs Q-Learning对比实验
 * 展示On-policy与Off-policy TD算法在风险环境中的不同行为
 */

import React, { useState, useCallback } from 'react';
import {
  Typography,
  Card,
  Button,
  Space,
  Row,
  Col,
  Slider,
  InputNumber,
  Form,
  Divider,
  message,
  Spin
} from 'antd';
import {
  PlayCircleOutlined,
  ExperimentOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { AlgorithmComparison, AlgorithmRunResult } from '../../components/Charts';
import { createEnvironment, runAlgorithmSync } from '../../services/api';

const { Title, Paragraph, Text } = Typography;

const CliffWalk: React.FC = () => {
  // 算法参数
  const [alpha, setAlpha] = useState(0.5);
  const [epsilon, setEpsilon] = useState(0.1);
  const [gamma, setGamma] = useState(1.0);
  const [maxEpisodes, setMaxEpisodes] = useState(500);

  // 实验结果
  const [sarsaResult, setSarsaResult] = useState<AlgorithmRunResult | undefined>();
  const [qLearningResult, setQLearningResult] = useState<AlgorithmRunResult | undefined>();

  // 加载状态
  const [isRunning, setIsRunning] = useState(false);
  const [currentAlgo, setCurrentAlgo] = useState<string>('');

  // 运行单个算法
  const runSingleAlgorithm = useCallback(async (algorithm: 'sarsa' | 'q_learning') => {
    try {
      // 创建Cliff环境
      const envResponse = await createEnvironment({
        type: 'cliff',
        gridSize: 12,
        stepReward: -1,
        terminalReward: 0,
        gamma: gamma
      });

      // 运行算法
      const result = await runAlgorithmSync(envResponse.env_id, {
        algorithm,
        gamma,
        theta: 1e-6,
        maxIterations: 1000,
        learningRate: alpha,
        epsilon,
        maxEpisodes
      });

      return {
        algorithm,
        episodeRewards: result.episode_rewards || [],
        avgReward: result.avg_reward || 0,
        successRate: result.success_rate || 0,
        totalEpisodes: result.total_episodes,
        executionTime: result.execution_time
      } as AlgorithmRunResult;
    } catch (error: any) {
      throw new Error(`${algorithm} 执行失败: ${error.message}`);
    }
  }, [alpha, epsilon, gamma, maxEpisodes]);

  // 运行对比实验
  const runComparison = useCallback(async () => {
    setIsRunning(true);
    setSarsaResult(undefined);
    setQLearningResult(undefined);

    try {
      // 运行SARSA
      setCurrentAlgo('SARSA');
      const sarsa = await runSingleAlgorithm('sarsa');
      setSarsaResult(sarsa);
      message.success(`SARSA完成: 平均奖励 ${sarsa.avgReward.toFixed(2)}`);

      // 运行Q-Learning
      setCurrentAlgo('Q-Learning');
      const qLearning = await runSingleAlgorithm('q_learning');
      setQLearningResult(qLearning);
      message.success(`Q-Learning完成: 平均奖励 ${qLearning.avgReward.toFixed(2)}`);

      message.info('对比实验完成！');
    } catch (error: any) {
      message.error(error.message);
    } finally {
      setIsRunning(false);
      setCurrentAlgo('');
    }
  }, [runSingleAlgorithm]);

  // 重置结果
  const resetResults = () => {
    setSarsaResult(undefined);
    setQLearningResult(undefined);
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2}>
        <ExperimentOutlined /> 悬崖行走 (Cliff Walking)
      </Title>

      <Paragraph>
        <Text strong>练习6.9/6.10:</Text> 在悬崖行走环境中对比SARSA和Q-Learning算法。
        智能体从左下角出发，需要到达右下角目标，底部边缘是悬崖(掉落-100奖励并重置)。
      </Paragraph>

      <Row gutter={[16, 16]}>
        {/* 参数配置 */}
        <Col xs={24} md={8}>
          <Card title="实验参数" size="small">
            <Form layout="vertical" size="small">
              <Form.Item label={`学习率 (α): ${alpha}`}>
                <Slider
                  min={0.01}
                  max={1.0}
                  step={0.01}
                  value={alpha}
                  onChange={setAlpha}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label={`探索率 (ε): ${epsilon}`}>
                <Slider
                  min={0}
                  max={0.5}
                  step={0.01}
                  value={epsilon}
                  onChange={setEpsilon}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label={`折扣因子 (γ): ${gamma}`}>
                <Slider
                  min={0.9}
                  max={1.0}
                  step={0.01}
                  value={gamma}
                  onChange={setGamma}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label="训练回合数">
                <InputNumber
                  min={100}
                  max={2000}
                  step={100}
                  value={maxEpisodes}
                  onChange={(v) => setMaxEpisodes(v || 500)}
                  style={{ width: '100%' }}
                  disabled={isRunning}
                />
              </Form.Item>

              <Divider style={{ margin: '12px 0' }} />

              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={runComparison}
                  loading={isRunning}
                  block
                >
                  {isRunning ? `运行 ${currentAlgo}...` : '运行对比实验'}
                </Button>

                <Button
                  icon={<ReloadOutlined />}
                  onClick={resetResults}
                  disabled={isRunning || (!sarsaResult && !qLearningResult)}
                  block
                >
                  重置结果
                </Button>
              </Space>
            </Form>
          </Card>

          {/* 环境说明 */}
          <Card title="环境说明" size="small" style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, color: '#888' }}>
              <p><strong>网格:</strong> 4×12</p>
              <p><strong>起点:</strong> 左下角 (3,0)</p>
              <p><strong>终点:</strong> 右下角 (3,11)</p>
              <p><strong>悬崖:</strong> 底部边缘 (3,1)-(3,10)</p>
              <p><strong>奖励:</strong> 每步-1, 掉落悬崖-100</p>
              <Divider style={{ margin: '8px 0' }} />
              <p style={{ color: '#1890ff' }}>
                <strong>预期行为:</strong>
              </p>
              <ul style={{ paddingLeft: 16, margin: 0 }}>
                <li>SARSA: 选择安全路径(上方)</li>
                <li>Q-Learning: 选择最短路径(悬崖边)</li>
              </ul>
            </div>
          </Card>
        </Col>

        {/* 对比结果 */}
        <Col xs={24} md={16}>
          {isRunning && (
            <Card>
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <div style={{ marginTop: 16, color: '#1890ff' }}>
                  正在运行 {currentAlgo} 算法...
                </div>
              </div>
            </Card>
          )}

          {!isRunning && (
            <AlgorithmComparison
              sarsaResult={sarsaResult}
              qLearningResult={qLearningResult}
              windowSize={10}
              title="SARSA vs Q-Learning 对比 (Cliff Walking)"
            />
          )}
        </Col>
      </Row>
    </div>
  );
};

export default CliffWalk;
