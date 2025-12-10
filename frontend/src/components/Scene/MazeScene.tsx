import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Grid, Text } from '@react-three/drei';
import * as THREE from 'three';

// 迷宫单元格类型
type CellType = 'empty' | 'wall' | 'start' | 'end' | 'agent' | 'path';

interface MazeCell {
  x: number;
  y: number;
  type: CellType;
  qValue?: number;
}

// 单个墙壁方块组件
const WallBlock: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  return (
    <mesh position={position} castShadow receiveShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#4a4a4a" roughness={0.8} metalness={0.2} />
    </mesh>
  );
};

// 地板单元格组件
const FloorCell: React.FC<{
  position: [number, number, number];
  type: CellType;
  qValue?: number;
}> = ({ position, type, qValue = 0 }) => {
  const getColor = () => {
    switch (type) {
      case 'start':
        return '#52c41a'; // 绿色 - 起点
      case 'end':
        return '#faad14'; // 金色 - 终点
      case 'path':
        return '#1890ff'; // 蓝色 - 路径
      default:
        // 根据Q值显示热力图效果
        const intensity = Math.min(Math.abs(qValue) / 10, 1);
        return new THREE.Color().lerpColors(
          new THREE.Color('#2d2d2d'),
          new THREE.Color('#1890ff'),
          intensity
        );
    }
  };

  return (
    <mesh position={position} receiveShadow>
      <boxGeometry args={[0.95, 0.1, 0.95]} />
      <meshStandardMaterial color={getColor()} roughness={0.6} />
    </mesh>
  );
};

// 智能体组件
const Agent: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  // 添加简单的上下浮动动画
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 3) * 0.1;
    }
  });

  return (
    <mesh ref={meshRef} position={position} castShadow>
      <sphereGeometry args={[0.35, 32, 32]} />
      <meshStandardMaterial
        color="#ff4d4f"
        emissive="#ff4d4f"
        emissiveIntensity={0.3}
        roughness={0.3}
        metalness={0.7}
      />
    </mesh>
  );
};

// 终点标记组件
const GoalMarker: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 2;
    }
  });

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <torusGeometry args={[0.3, 0.08, 16, 32]} />
        <meshStandardMaterial
          color="#faad14"
          emissive="#faad14"
          emissiveIntensity={0.5}
        />
      </mesh>
      <pointLight color="#faad14" intensity={1} distance={3} />
    </group>
  );
};

// 迷宫场景主组件
const MazeScene: React.FC = () => {
  // 示例迷宫数据 - 10x10
  const mazeSize = 10;

  const mazeData = useMemo(() => {
    const data: MazeCell[][] = [];

    for (let y = 0; y < mazeSize; y++) {
      const row: MazeCell[] = [];
      for (let x = 0; x < mazeSize; x++) {
        let type: CellType = 'empty';

        // 设置边界墙
        if (x === 0 || x === mazeSize - 1 || y === 0 || y === mazeSize - 1) {
          // 除了起点和终点位置
          if (!(x === 1 && y === 0) && !(x === mazeSize - 2 && y === mazeSize - 1)) {
            type = 'wall';
          }
        }

        // 添加一些内部墙壁
        if ((x === 2 && y >= 2 && y <= 5) ||
            (x === 4 && y >= 4 && y <= 7) ||
            (x === 6 && y >= 1 && y <= 4) ||
            (x === 7 && y >= 5 && y <= 8) ||
            (y === 3 && x >= 4 && x <= 6)) {
          type = 'wall';
        }

        // 起点
        if (x === 1 && y === 1) {
          type = 'start';
        }

        // 终点
        if (x === mazeSize - 2 && y === mazeSize - 2) {
          type = 'end';
        }

        row.push({ x, y, type, qValue: 0 });
      }
      data.push(row);
    }

    return data;
  }, []);

  // 智能体位置 - 初始在起点
  const agentPosition: [number, number, number] = [1 - mazeSize / 2 + 0.5, 0.5, 1 - mazeSize / 2 + 0.5];

  return (
    <Canvas shadows>
      {/* 相机 */}
      <PerspectiveCamera makeDefault position={[0, 15, 15]} fov={50} />
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={30}
        maxPolarAngle={Math.PI / 2.2}
      />

      {/* 光照 */}
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
      <pointLight position={[-10, 10, -10]} intensity={0.3} />

      {/* 背景 */}
      <color attach="background" args={['#1a1a2e']} />
      <fog attach="fog" args={['#1a1a2e', 20, 40]} />

      {/* 网格辅助线 */}
      <Grid
        args={[30, 30]}
        position={[0, -0.5, 0]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#3a3a5a"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#4a4a7a"
        fadeDistance={30}
        fadeStrength={1}
        followCamera={false}
      />

      {/* 渲染迷宫 */}
      <group>
        {mazeData.map((row, y) =>
          row.map((cell, x) => {
            const posX = x - mazeSize / 2 + 0.5;
            const posZ = y - mazeSize / 2 + 0.5;

            if (cell.type === 'wall') {
              return (
                <WallBlock
                  key={`wall-${x}-${y}`}
                  position={[posX, 0.5, posZ]}
                />
              );
            }

            return (
              <FloorCell
                key={`floor-${x}-${y}`}
                position={[posX, 0, posZ]}
                type={cell.type}
                qValue={cell.qValue}
              />
            );
          })
        )}

        {/* 智能体 */}
        <Agent position={agentPosition} />

        {/* 终点标记 */}
        <GoalMarker
          position={[
            mazeSize - 2 - mazeSize / 2 + 0.5,
            0.8,
            mazeSize - 2 - mazeSize / 2 + 0.5,
          ]}
        />

        {/* 坐标标签 */}
        <Text
          position={[-mazeSize / 2 - 1, 0, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          fontSize={0.5}
          color="#888"
        >
          起点 →
        </Text>
      </group>
    </Canvas>
  );
};

export default MazeScene;
