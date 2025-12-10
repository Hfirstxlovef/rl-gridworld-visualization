/**
 * ConvergenceChart - 收敛曲线图表组件
 *
 * 显示算法迭代过程中的值函数变化和收敛情况
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
import { Card, Empty } from 'antd';

export interface ConvergenceDataPoint {
  iteration: number;
  maxDelta: number;
  avgValue: number;
  minValue?: number;
  maxValue?: number;
}

interface ConvergenceChartProps {
  data: ConvergenceDataPoint[];
  theta?: number;  // 收敛阈值
  title?: string;
  height?: number;
}

const ConvergenceChart: React.FC<ConvergenceChartProps> = ({
  data,
  theta = 1e-6,
  title = '收敛曲线',
  height = 200
}) => {
  // 格式化数据
  const chartData = useMemo(() => {
    return data.map((d, idx) => ({
      ...d,
      iteration: d.iteration || idx + 1,
      maxDelta: Math.abs(d.maxDelta),
      logDelta: d.maxDelta > 0 ? Math.log10(Math.abs(d.maxDelta)) : -10
    }));
  }, [data]);

  if (data.length === 0) {
    return (
      <Card title={title} size="small">
        <Empty description="运行算法后显示收敛曲线" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </Card>
    );
  }

  return (
    <Card title={title} size="small" className="convergence-chart">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            dataKey="iteration"
            stroke="#888"
            fontSize={10}
            label={{ value: '迭代次数', position: 'bottom', fontSize: 10, fill: '#888' }}
          />
          <YAxis
            stroke="#888"
            fontSize={10}
            tickFormatter={(v) => v.toExponential(0)}
            label={{ value: 'Δ (log)', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#888' }}
          />
          <Tooltip
            contentStyle={{
              background: '#1a1a2e',
              border: '1px solid #333',
              borderRadius: 4,
              fontSize: 11
            }}
            formatter={(value: number, name: string) => {
              if (name === 'maxDelta') return [value.toExponential(4), '最大变化Δ'];
              if (name === 'avgValue') return [value.toFixed(4), '平均值V'];
              return [value, name];
            }}
            labelFormatter={(label) => `迭代 ${label}`}
          />
          <Legend
            wrapperStyle={{ fontSize: 10 }}
            formatter={(value) => {
              if (value === 'maxDelta') return '最大Δ';
              if (value === 'avgValue') return '平均V(s)';
              return value;
            }}
          />

          {/* 收敛阈值参考线 */}
          <ReferenceLine
            y={theta}
            stroke="#ff4444"
            strokeDasharray="5 5"
            label={{ value: `θ=${theta}`, position: 'right', fontSize: 9, fill: '#ff4444' }}
          />

          {/* 最大变化曲线 */}
          <Line
            type="monotone"
            dataKey="maxDelta"
            stroke="#00ff88"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#00ff88' }}
          />

          {/* 平均值曲线 */}
          <Line
            type="monotone"
            dataKey="avgValue"
            stroke="#4488ff"
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: '#4488ff' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default ConvergenceChart;
