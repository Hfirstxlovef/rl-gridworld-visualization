/**
 * AlgorithmComparison - 算法对比可视化组件
 *
 * 用于对比SARSA和Q-Learning算法在相同环境下的性能差异
 * 主要应用于Cliff Walking实验 (练习6.9/6.10)
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import { Card, Row, Col, Statistic, Tag } from 'antd';
import { TrophyOutlined, RiseOutlined, SafetyOutlined } from '@ant-design/icons';

export interface AlgorithmRunResult {
  algorithm: 'sarsa' | 'q_learning';
  episodeRewards: number[];
  avgReward: number;
  successRate: number;
  totalEpisodes: number;
  executionTime: number;
}

interface AlgorithmComparisonProps {
  sarsaResult?: AlgorithmRunResult;
  qLearningResult?: AlgorithmRunResult;
  windowSize?: number;
  title?: string;
}

const COLORS = {
  sarsa: '#8884d8',      // 紫色
  q_learning: '#82ca9d', // 绿色
  sarsa_light: '#b4b0e8',
  q_learning_light: '#b8e6c8'
};

const AlgorithmComparison: React.FC<AlgorithmComparisonProps> = ({
  sarsaResult,
  qLearningResult,
  windowSize = 10,
  title = 'SARSA vs Q-Learning 算法对比'
}) => {
  // 生成对比学习曲线数据
  const comparisonData = useMemo(() => {
    if (!sarsaResult && !qLearningResult) return [];

    const maxLength = Math.max(
      sarsaResult?.episodeRewards.length || 0,
      qLearningResult?.episodeRewards.length || 0
    );

    // 计算滑动窗口平均
    const calcWindowAvg = (rewards: number[], index: number) => {
      const start = Math.max(0, index - windowSize + 1);
      const window = rewards.slice(start, index + 1);
      return window.reduce((a, b) => a + b, 0) / window.length;
    };

    const data = [];
    for (let i = 0; i < maxLength; i++) {
      const point: any = { episode: i + 1 };

      if (sarsaResult && i < sarsaResult.episodeRewards.length) {
        point.sarsa = calcWindowAvg(sarsaResult.episodeRewards, i);
        point.sarsaRaw = sarsaResult.episodeRewards[i];
      }

      if (qLearningResult && i < qLearningResult.episodeRewards.length) {
        point.qLearning = calcWindowAvg(qLearningResult.episodeRewards, i);
        point.qLearningRaw = qLearningResult.episodeRewards[i];
      }

      data.push(point);
    }

    return data;
  }, [sarsaResult, qLearningResult, windowSize]);

  // 性能对比柱状图数据
  const performanceData = useMemo(() => {
    const data = [];

    if (sarsaResult) {
      data.push({
        name: 'SARSA',
        avgReward: sarsaResult.avgReward,
        successRate: sarsaResult.successRate * 100,
        algorithm: 'sarsa'
      });
    }

    if (qLearningResult) {
      data.push({
        name: 'Q-Learning',
        avgReward: qLearningResult.avgReward,
        successRate: qLearningResult.successRate * 100,
        algorithm: 'q_learning'
      });
    }

    return data;
  }, [sarsaResult, qLearningResult]);

  // 判断获胜者
  const winner = useMemo(() => {
    if (!sarsaResult || !qLearningResult) return null;

    const sarsaScore = sarsaResult.avgReward;
    const qScore = qLearningResult.avgReward;

    if (sarsaScore > qScore) return 'sarsa';
    if (qScore > sarsaScore) return 'q_learning';
    return 'tie';
  }, [sarsaResult, qLearningResult]);

  if (!sarsaResult && !qLearningResult) {
    return (
      <Card title={title} size="small">
        <div style={{ textAlign: 'center', color: '#888', padding: 20 }}>
          运行SARSA和Q-Learning算法后显示对比结果
        </div>
      </Card>
    );
  }

  return (
    <div>
      <Card title={title} size="small" style={{ marginBottom: 16 }}>
        {/* 统计对比 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          {sarsaResult && (
            <Col span={12}>
              <Card
                size="small"
                style={{
                  borderColor: COLORS.sarsa,
                  backgroundColor: 'rgba(136, 132, 216, 0.1)'
                }}
              >
                <Statistic
                  title={
                    <span>
                      <Tag color="purple">SARSA</Tag>
                      {winner === 'sarsa' && <TrophyOutlined style={{ color: '#ffd700' }} />}
                    </span>
                  }
                  value={sarsaResult.avgReward.toFixed(2)}
                  prefix={<RiseOutlined />}
                  suffix="平均奖励"
                  valueStyle={{ fontSize: 18, color: COLORS.sarsa }}
                />
                <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                  成功率: {(sarsaResult.successRate * 100).toFixed(1)}%
                  <SafetyOutlined style={{ marginLeft: 4 }} />
                </div>
              </Card>
            </Col>
          )}

          {qLearningResult && (
            <Col span={12}>
              <Card
                size="small"
                style={{
                  borderColor: COLORS.q_learning,
                  backgroundColor: 'rgba(130, 202, 157, 0.1)'
                }}
              >
                <Statistic
                  title={
                    <span>
                      <Tag color="green">Q-Learning</Tag>
                      {winner === 'q_learning' && <TrophyOutlined style={{ color: '#ffd700' }} />}
                    </span>
                  }
                  value={qLearningResult.avgReward.toFixed(2)}
                  prefix={<RiseOutlined />}
                  suffix="平均奖励"
                  valueStyle={{ fontSize: 18, color: COLORS.q_learning }}
                />
                <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                  成功率: {(qLearningResult.successRate * 100).toFixed(1)}%
                  <SafetyOutlined style={{ marginLeft: 4 }} />
                </div>
              </Card>
            </Col>
          )}
        </Row>

        {/* 学习曲线对比 */}
        {comparisonData.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, marginBottom: 8, color: '#1890ff' }}>
              学习曲线对比 (滑动窗口平均, 窗口={windowSize})
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={comparisonData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis
                  dataKey="episode"
                  stroke="#888"
                  tick={{ fill: '#888', fontSize: 10 }}
                />
                <YAxis
                  stroke="#888"
                  tick={{ fill: '#888', fontSize: 10 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f1f1f',
                    border: '1px solid #333',
                    borderRadius: 4
                  }}
                  labelStyle={{ color: '#fff' }}
                  formatter={(value: number, name: string) => [
                    value.toFixed(2),
                    name === 'sarsa' ? 'SARSA' : 'Q-Learning'
                  ]}
                />
                <Legend
                  formatter={(value) => (
                    <span style={{ color: '#888', fontSize: 11 }}>
                      {value === 'sarsa' ? 'SARSA (On-policy)' : 'Q-Learning (Off-policy)'}
                    </span>
                  )}
                />
                {sarsaResult && (
                  <Line
                    type="monotone"
                    dataKey="sarsa"
                    stroke={COLORS.sarsa}
                    strokeWidth={2}
                    dot={false}
                  />
                )}
                {qLearningResult && (
                  <Line
                    type="monotone"
                    dataKey="qLearning"
                    stroke={COLORS.q_learning}
                    strokeWidth={2}
                    dot={false}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 性能柱状图 */}
        {performanceData.length === 2 && (
          <div>
            <div style={{ fontSize: 12, marginBottom: 8, color: '#1890ff' }}>
              性能指标对比
            </div>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={performanceData} layout="vertical" margin={{ left: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis type="number" stroke="#888" tick={{ fill: '#888', fontSize: 10 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#888"
                  tick={{ fill: '#888', fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f1f1f',
                    border: '1px solid #333'
                  }}
                  formatter={(value: number) => value.toFixed(2)}
                />
                <Bar dataKey="avgReward" name="平均奖励">
                  {performanceData.map((entry, index) => (
                    <Cell
                      key={index}
                      fill={entry.algorithm === 'sarsa' ? COLORS.sarsa : COLORS.q_learning}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 算法特性说明 */}
        <div style={{
          marginTop: 16,
          padding: 12,
          backgroundColor: '#1a1a2e',
          borderRadius: 4,
          fontSize: 11,
          color: '#888'
        }}>
          <strong style={{ color: '#1890ff' }}>算法特性对比:</strong>
          <ul style={{ margin: '8px 0 0 0', paddingLeft: 16 }}>
            <li>
              <span style={{ color: COLORS.sarsa }}>SARSA (On-policy)</span>:
              保守策略，考虑探索行为，在Cliff环境中选择安全路径
            </li>
            <li>
              <span style={{ color: COLORS.q_learning }}>Q-Learning (Off-policy)</span>:
              激进策略，追求最优行为，在Cliff环境中选择悬崖边缘最短路径
            </li>
          </ul>
        </div>
      </Card>
    </div>
  );
};

export default AlgorithmComparison;
