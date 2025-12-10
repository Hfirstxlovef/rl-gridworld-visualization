/**
 * LearningCurve - TD算法学习曲线组件
 *
 * 显示训练过程中的回合奖励和滑动窗口平均
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
  ReferenceLine
} from 'recharts';

export interface LearningCurveDataPoint {
  episode: number;
  reward: number;
  avgReward?: number;
}

interface LearningCurveProps {
  episodeRewards: number[];
  windowSize?: number;
  title?: string;
  height?: number;
}

const LearningCurve: React.FC<LearningCurveProps> = ({
  episodeRewards,
  windowSize = 10,
  title = 'TD算法学习曲线',
  height = 250
}) => {
  // 计算滑动窗口平均并生成数据点
  const data = useMemo<LearningCurveDataPoint[]>(() => {
    if (!episodeRewards || episodeRewards.length === 0) {
      return [];
    }

    return episodeRewards.map((reward, index) => {
      const start = Math.max(0, index - windowSize + 1);
      const window = episodeRewards.slice(start, index + 1);
      const avgReward = window.reduce((a, b) => a + b, 0) / window.length;

      return {
        episode: index + 1,
        reward,
        avgReward
      };
    });
  }, [episodeRewards, windowSize]);

  // 计算统计数据
  const stats = useMemo(() => {
    if (!episodeRewards || episodeRewards.length === 0) {
      return { min: 0, max: 0, avg: 0, final: 0 };
    }

    const min = Math.min(...episodeRewards);
    const max = Math.max(...episodeRewards);
    const avg = episodeRewards.reduce((a, b) => a + b, 0) / episodeRewards.length;
    const finalWindow = episodeRewards.slice(-windowSize);
    const final = finalWindow.reduce((a, b) => a + b, 0) / finalWindow.length;

    return { min, max, avg, final };
  }, [episodeRewards, windowSize]);

  if (data.length === 0) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#888'
      }}>
        暂无学习数据
      </div>
    );
  }

  return (
    <div>
      <div style={{ fontSize: 12, marginBottom: 8, color: '#1890ff', fontWeight: 500 }}>
        {title}
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            dataKey="episode"
            stroke="#888"
            tick={{ fill: '#888', fontSize: 10 }}
            label={{ value: '回合', position: 'insideBottomRight', offset: -5, fill: '#888', fontSize: 10 }}
          />
          <YAxis
            stroke="#888"
            tick={{ fill: '#888', fontSize: 10 }}
            label={{ value: '奖励', angle: -90, position: 'insideLeft', fill: '#888', fontSize: 10 }}
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
              name === 'reward' ? '单次奖励' : '平均奖励'
            ]}
          />
          <Legend
            wrapperStyle={{ paddingTop: 10 }}
            formatter={(value) => (
              <span style={{ color: '#888', fontSize: 11 }}>
                {value === 'reward' ? '单次奖励' : `平均奖励 (窗口=${windowSize})`}
              </span>
            )}
          />
          <ReferenceLine
            y={0}
            stroke="#666"
            strokeDasharray="2 2"
          />
          <Line
            type="monotone"
            dataKey="reward"
            stroke="#8884d8"
            strokeWidth={1}
            dot={false}
            opacity={0.3}
          />
          <Line
            type="monotone"
            dataKey="avgReward"
            stroke="#82ca9d"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: 10,
        color: '#888',
        marginTop: 8,
        padding: '4px 8px',
        backgroundColor: '#1a1a2e',
        borderRadius: 4
      }}>
        <span>最小: {stats.min.toFixed(1)}</span>
        <span>最大: {stats.max.toFixed(1)}</span>
        <span>总平均: {stats.avg.toFixed(1)}</span>
        <span>最终平均: {stats.final.toFixed(1)}</span>
      </div>
    </div>
  );
};

export default LearningCurve;
