/**
 * ExperimentScene - 实验3D场景主组件
 *
 * 集成Canvas、光照、相机控制和GridWorld3D
 */

import React, { Suspense, useRef, useEffect } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import {
  OrbitControls,
  PerspectiveCamera,
  Grid,
  Stars
} from '@react-three/drei';
import * as THREE from 'three';
import { Spin } from 'antd';
import GridWorld3D from './GridWorld3D';
import { useExperimentStore } from '../../store';

// 相机控制组件
const CameraController: React.FC = () => {
  const { gridSize, visualization, agentPosition } = useExperimentStore();
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  // 根据网格大小调整相机位置
  useEffect(() => {
    const distance = gridSize * 1.5;
    if (visualization.cameraMode === 'topdown') {
      camera.position.set(0, distance, 0.1);
    } else {
      camera.position.set(distance * 0.7, distance * 0.8, distance * 0.7);
    }
    camera.lookAt(0, 0, 0);
  }, [gridSize, visualization.cameraMode, camera]);

  // 跟随模式
  useFrame(() => {
    if (visualization.cameraMode === 'follow' && agentPosition && controlsRef.current) {
      const cellSize = 1.0;
      const offset = (gridSize - 1) * cellSize / 2;
      const targetX = agentPosition.col * cellSize - offset;
      const targetZ = agentPosition.row * cellSize - offset;
      controlsRef.current.target.lerp(new THREE.Vector3(targetX, 0, targetZ), 0.1);
    }
  });

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={true}
      enableZoom={true}
      enableRotate={visualization.cameraMode !== 'topdown'}
      minDistance={3}
      maxDistance={30}
      maxPolarAngle={visualization.cameraMode === 'topdown' ? 0.1 : Math.PI / 2.1}
      minPolarAngle={visualization.cameraMode === 'topdown' ? 0 : 0.2}
    />
  );
};

// 光照设置
const Lighting: React.FC = () => {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight
        position={[10, 20, 10]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={50}
        shadow-camera-left={-15}
        shadow-camera-right={15}
        shadow-camera-top={15}
        shadow-camera-bottom={-15}
      />
      <pointLight position={[-10, 15, -10]} intensity={0.3} color="#6666ff" />
      <pointLight position={[10, 15, 10]} intensity={0.2} color="#ff6666" />
    </>
  );
};

// 背景和环境
const SceneEnvironment: React.FC = () => {
  const { gridSize } = useExperimentStore();

  return (
    <>
      {/* 深空背景 */}
      <color attach="background" args={['#0a0a1a']} />
      <fog attach="fog" args={['#0a0a1a', 15, 40]} />

      {/* 星空 */}
      <Stars
        radius={100}
        depth={50}
        count={3000}
        factor={4}
        saturation={0}
        fade
        speed={0.5}
      />

      {/* 参考网格 */}
      <Grid
        args={[30, 30]}
        position={[0, -0.05, 0]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#1a1a3a"
        sectionSize={gridSize}
        sectionThickness={1}
        sectionColor="#2a2a5a"
        fadeDistance={30}
        fadeStrength={1}
        followCamera={false}
      />
    </>
  );
};

// 加载指示器
const LoadingFallback: React.FC = () => (
  <div
    style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 100%)'
    }}
  >
    <Spin size="large" tip="加载3D场景中..." />
  </div>
);

// 场景内容
const SceneContent: React.FC = () => {
  const { gridSize } = useExperimentStore();

  return (
    <>
      <PerspectiveCamera
        makeDefault
        position={[gridSize * 1.2, gridSize * 1.5, gridSize * 1.2]}
        fov={50}
      />
      <CameraController />
      <Lighting />
      <SceneEnvironment />
      <GridWorld3D />
    </>
  );
};

// 主导出组件
interface ExperimentSceneProps {
  className?: string;
  style?: React.CSSProperties;
}

const ExperimentScene: React.FC<ExperimentSceneProps> = ({ className, style }) => {
  return (
    <div
      className={className}
      style={{
        width: '100%',
        height: '100%',
        background: '#0a0a1a',
        ...style
      }}
    >
      <Suspense fallback={<LoadingFallback />}>
        <Canvas
          shadows
          gl={{
            antialias: true,
            toneMapping: THREE.ACESFilmicToneMapping,
            toneMappingExposure: 1.2
          }}
          dpr={[1, 2]}
        >
          <SceneContent />
        </Canvas>
      </Suspense>
    </div>
  );
};

export default ExperimentScene;
