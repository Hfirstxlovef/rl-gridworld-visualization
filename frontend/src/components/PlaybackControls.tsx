/**
 * PlaybackControls - 动画回放控制组件
 *
 * 提供播放、暂停、单步、进度条等控制功能
 */

import React from 'react';
import { Button, Slider, Select, Typography, Tooltip } from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepBackwardOutlined,
  StepForwardOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { usePlayback } from '../hooks/usePlayback';

const { Text } = Typography;

// 速度选项（数值越大越慢，默认250ms=2x）
const speedOptions = [
  { value: 1000, label: '0.5x' },
  { value: 500, label: '1x' },
  { value: 250, label: '2x' },
  { value: 100, label: '4x' }
];

interface PlaybackControlsProps {
  disabled?: boolean;
}

const PlaybackControls: React.FC<PlaybackControlsProps> = ({ disabled = false }) => {
  const {
    isPlaying,
    playbackIndex,
    totalSnapshots,
    playbackSpeed,
    hasSnapshots,
    togglePlay,
    stepForward,
    stepBackward,
    seekTo,
    setSpeed,
    reset
  } = usePlayback();

  const isDisabled = disabled || !hasSnapshots;

  return (
    <div style={{ padding: '12px 0' }}>
      {/* 标题和迭代信息 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <Text strong style={{ color: '#000' }}>迭代回放</Text>
        <Text type="secondary" style={{ color: '#666' }}>
          {hasSnapshots ? `${playbackIndex + 1} / ${totalSnapshots}` : '无数据'}
        </Text>
      </div>

      {/* 进度条 */}
      <Slider
        min={0}
        max={Math.max(0, totalSnapshots - 1)}
        value={playbackIndex}
        onChange={(value) => seekTo(value)}
        disabled={isDisabled}
        tooltip={{
          formatter: (value) => `迭代 ${(value ?? 0) + 1}`
        }}
        style={{ marginBottom: 12 }}
      />

      {/* 控制按钮 */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <Tooltip title="重置">
          <Button
            icon={<ReloadOutlined />}
            onClick={reset}
            disabled={isDisabled}
            size="small"
          />
        </Tooltip>

        <Tooltip title="上一步">
          <Button
            icon={<StepBackwardOutlined />}
            onClick={stepBackward}
            disabled={isDisabled || playbackIndex === 0}
            size="small"
          />
        </Tooltip>

        <Button
          type="primary"
          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          onClick={togglePlay}
          disabled={isDisabled}
          size="middle"
          style={{ minWidth: 80 }}
        >
          {isPlaying ? '暂停' : '播放'}
        </Button>

        <Tooltip title="下一步">
          <Button
            icon={<StepForwardOutlined />}
            onClick={stepForward}
            disabled={isDisabled || playbackIndex >= totalSnapshots - 1}
            size="small"
          />
        </Tooltip>

        {/* 速度选择 */}
        <Select
          value={playbackSpeed}
          onChange={(value) => setSpeed(value)}
          options={speedOptions}
          disabled={isDisabled}
          size="small"
          style={{ width: 80 }}
        />
      </div>

      {/* 提示信息 */}
      {!hasSnapshots && (
        <Text type="secondary" style={{ display: 'block', textAlign: 'center', fontSize: 12, color: '#999' }}>
          运行算法后可回放迭代过程
        </Text>
      )}
    </div>
  );
};

export default PlaybackControls;
