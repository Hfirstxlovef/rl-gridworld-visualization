/**
 * usePlayback - 动画回放控制 Hook
 *
 * 管理迭代快照的自动播放、暂停、单步等操作
 */

import { useEffect, useCallback, useRef } from 'react';
import { useExperimentStore } from '../store';

export interface UsePlaybackReturn {
  // 状态
  isPlaying: boolean;
  playbackIndex: number;
  totalSnapshots: number;
  playbackSpeed: number;
  hasSnapshots: boolean;

  // 控制方法
  play: () => void;
  pause: () => void;
  togglePlay: () => void;
  stepForward: () => void;
  stepBackward: () => void;
  seekTo: (index: number) => void;
  setSpeed: (speed: number) => void;
  reset: () => void;
}

export function usePlayback(): UsePlaybackReturn {
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const {
    iterationSnapshots,
    playbackIndex,
    isPlaying,
    playbackSpeed,
    playAnimation,
    pauseAnimation,
    stepForward,
    stepBackward,
    seekTo,
    setPlaybackSpeed
  } = useExperimentStore();

  const totalSnapshots = iterationSnapshots.length;
  const hasSnapshots = totalSnapshots > 0;

  // 播放定时器
  useEffect(() => {
    if (isPlaying && hasSnapshots) {
      timerRef.current = setInterval(() => {
        const { playbackIndex, iterationSnapshots, applySnapshot, setPlaybackIndex, pauseAnimation } = useExperimentStore.getState();

        if (playbackIndex < iterationSnapshots.length - 1) {
          const newIndex = playbackIndex + 1;
          applySnapshot(newIndex);
          setPlaybackIndex(newIndex);
        } else {
          // 播放完成，停止
          pauseAnimation();
        }
      }, playbackSpeed);

      return () => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };
    }
  }, [isPlaying, playbackSpeed, hasSnapshots]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const play = useCallback(() => {
    if (hasSnapshots) {
      // 如果已经播放到最后，从头开始
      if (playbackIndex >= totalSnapshots - 1) {
        seekTo(0);
      }
      playAnimation();
    }
  }, [hasSnapshots, playbackIndex, totalSnapshots, playAnimation, seekTo]);

  const pause = useCallback(() => {
    pauseAnimation();
  }, [pauseAnimation]);

  const togglePlay = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);

  const setSpeed = useCallback((speed: number) => {
    setPlaybackSpeed(speed);
  }, [setPlaybackSpeed]);

  const reset = useCallback(() => {
    pauseAnimation();
    if (hasSnapshots) {
      seekTo(0);
    }
  }, [pauseAnimation, hasSnapshots, seekTo]);

  return {
    // 状态
    isPlaying,
    playbackIndex,
    totalSnapshots,
    playbackSpeed,
    hasSnapshots,

    // 控制方法
    play,
    pause,
    togglePlay,
    stepForward,
    stepBackward,
    seekTo,
    setSpeed,
    reset
  };
}

export default usePlayback;
