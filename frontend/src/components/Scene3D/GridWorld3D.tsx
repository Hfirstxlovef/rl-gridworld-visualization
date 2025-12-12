/**
 * GridWorld3D - 3D网格世界主组件
 *
 * 支持动态网格尺寸、值函数热力图、策略箭头可视化
 */

import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import { useExperimentStore } from '../../store';
import { GridCell, Action } from '../../types';

// 颜色插值：从蓝色（低值）到红色（高值）
function valueToColor(value: number, minValue: number, maxValue: number): THREE.Color {
  if (maxValue === minValue) {
    return new THREE.Color('#3a3a5a');
  }

  const normalized = (value - minValue) / (maxValue - minValue);
  const color = new THREE.Color();

  // 蓝 -> 青 -> 绿 -> 黄 -> 红
  if (normalized < 0.25) {
    color.setHSL(0.66, 0.8, 0.3 + normalized * 1.2);
  } else if (normalized < 0.5) {
    color.setHSL(0.5, 0.8, 0.3 + normalized * 0.8);
  } else if (normalized < 0.75) {
    color.setHSL(0.33, 0.8, 0.4 + (normalized - 0.5) * 0.6);
  } else {
    color.setHSL(0.0, 0.8, 0.4 + (normalized - 0.75) * 0.4);
  }

  return color;
}

// 单个网格单元组件
interface GridCellMeshProps {
  cell: GridCell;
  position: [number, number, number];
  cellSize: number;
  minValue: number;
  maxValue: number;
  showHeatmap: boolean;
  showArrows: boolean;
}

const GridCellMesh: React.FC<GridCellMeshProps> = ({
  cell,
  position,
  cellSize,
  minValue,
  maxValue,
  showHeatmap,
  showArrows
}) => {
  const meshRef = useRef<THREE.Mesh>(null);

  // 根据单元格类型确定颜色
  const getBaseColor = () => {
    if (cell.type === 'terminal') {
      return new THREE.Color('#ffd700'); // 金色终止状态
    }
    if (cell.type === 'cliff') {
      return new THREE.Color('#8b0000'); // 深红色悬崖
    }
    if (cell.type === 'start') {
      return new THREE.Color('#00ff00'); // 绿色起点
    }

    if (showHeatmap && cell.value !== 0) {
      return valueToColor(cell.value, minValue, maxValue);
    }

    return new THREE.Color('#2d2d4d');
  };

  // 根据值函数计算高度偏移
  const heightOffset = showHeatmap
    ? Math.max(0, (cell.value - minValue) / (maxValue - minValue || 1)) * 0.3
    : 0;

  // 箭头方向
  const arrowRotations: Record<Action, number> = {
    [Action.UP]: 0,
    [Action.DOWN]: Math.PI,
    [Action.LEFT]: Math.PI / 2,
    [Action.RIGHT]: -Math.PI / 2
  };

  return (
    <group position={position}>
      {/* 地板单元 */}
      <mesh
        ref={meshRef}
        position={[0, heightOffset / 2, 0]}
        receiveShadow
        castShadow
      >
        <boxGeometry args={[cellSize * 0.95, 0.1 + heightOffset, cellSize * 0.95]} />
        <meshStandardMaterial
          color={getBaseColor()}
          roughness={0.6}
          metalness={0.2}
          emissive={cell.type === 'terminal' ? '#ffd700' : undefined}
          emissiveIntensity={cell.type === 'terminal' ? 0.3 : 0}
        />
      </mesh>

      {/* 值函数文本 */}
      {showHeatmap && cell.type !== 'terminal' && (
        <Html position={[0, 0.2 + heightOffset, 0]} center>
          <div style={{ color: '#fff', fontSize: '12px', fontWeight: 'bold', whiteSpace: 'nowrap' }}>
            {cell.value.toFixed(1)}
          </div>
        </Html>
      )}

      {/* 状态编号 */}
      <Html position={[-cellSize * 0.35, 0.15 + heightOffset, -cellSize * 0.35]} center>
        <div style={{ color: '#888', fontSize: '10px', whiteSpace: 'nowrap' }}>
          {cell.state}
        </div>
      </Html>

      {/* 策略箭头 */}
      {showArrows && cell.type !== 'terminal' && cell.bestActions.length > 0 && (
        <group position={[0, 0.15 + heightOffset, 0]}>
          {cell.bestActions.map((action, idx) => (
            <mesh
              key={idx}
              rotation={[-Math.PI / 2, arrowRotations[action], 0]}
              position={[0, 0.01 * idx, 0]}
            >
              <coneGeometry args={[cellSize * 0.1, cellSize * 0.25, 8]} />
              <meshStandardMaterial
                color="#00ff88"
                emissive="#00ff88"
                emissiveIntensity={0.5}
              />
            </mesh>
          ))}
        </group>
      )}

      {/* 终止状态标记 */}
      {cell.type === 'terminal' && (
        <Html position={[0, 0.3, 0]} center>
          <div style={{ color: '#fff', fontSize: '20px', fontWeight: 'bold' }}>
            T
          </div>
        </Html>
      )}
    </group>
  );
};

// 网格边界墙
interface GridWallsProps {
  gridSize: number;
  cellSize: number;
}

const GridWalls: React.FC<GridWallsProps> = ({ gridSize, cellSize }) => {
  const wallHeight = 0.5;
  const wallThickness = 0.1;
  const totalSize = gridSize * cellSize;
  const offset = (gridSize - 1) * cellSize / 2;

  return (
    <group>
      {/* 北墙 */}
      <mesh position={[0, wallHeight / 2, -offset - cellSize / 2 - wallThickness / 2]}>
        <boxGeometry args={[totalSize + wallThickness * 2, wallHeight, wallThickness]} />
        <meshStandardMaterial color="#4a4a6a" roughness={0.8} />
      </mesh>

      {/* 南墙 */}
      <mesh position={[0, wallHeight / 2, offset + cellSize / 2 + wallThickness / 2]}>
        <boxGeometry args={[totalSize + wallThickness * 2, wallHeight, wallThickness]} />
        <meshStandardMaterial color="#4a4a6a" roughness={0.8} />
      </mesh>

      {/* 西墙 */}
      <mesh position={[-offset - cellSize / 2 - wallThickness / 2, wallHeight / 2, 0]}>
        <boxGeometry args={[wallThickness, wallHeight, totalSize]} />
        <meshStandardMaterial color="#4a4a6a" roughness={0.8} />
      </mesh>

      {/* 东墙 */}
      <mesh position={[offset + cellSize / 2 + wallThickness / 2, wallHeight / 2, 0]}>
        <boxGeometry args={[wallThickness, wallHeight, totalSize]} />
        <meshStandardMaterial color="#4a4a6a" roughness={0.8} />
      </mesh>
    </group>
  );
};

// Agent 组件
interface AgentProps {
  position: [number, number, number];
  cellSize: number;
}

const Agent: React.FC<AgentProps> = ({ position, cellSize }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 3) * 0.05;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.5;
    }
  });

  return (
    <mesh ref={meshRef} position={position} castShadow>
      <sphereGeometry args={[cellSize * 0.3, 32, 32]} />
      <meshStandardMaterial
        color="#ff4444"
        emissive="#ff4444"
        emissiveIntensity={0.4}
        roughness={0.3}
        metalness={0.7}
      />
    </mesh>
  );
};

// 主组件
const GridWorld3D: React.FC = () => {
  const {
    grid,
    gridSize,
    agentPosition,
    visualization
  } = useExperimentStore();

  const cellSize = 1.0;

  // 计算值函数范围
  const { minValue, maxValue } = useMemo(() => {
    let min = 0;
    let max = 0;
    grid.forEach(row => {
      row.forEach(cell => {
        if (cell.type !== 'terminal') {
          min = Math.min(min, cell.value);
          max = Math.max(max, cell.value);
        }
      });
    });
    return { minValue: min, maxValue: max };
  }, [grid]);

  // 计算网格中心偏移
  const offset = (gridSize - 1) * cellSize / 2;

  return (
    <group>
      {/* 渲染所有网格单元 */}
      {grid.map((row, rowIdx) =>
        row.map((cell, colIdx) => {
          const x = colIdx * cellSize - offset;
          const z = rowIdx * cellSize - offset;

          return (
            <GridCellMesh
              key={cell.state}
              cell={cell}
              position={[x, 0, z]}
              cellSize={cellSize}
              minValue={minValue}
              maxValue={maxValue}
              showHeatmap={visualization.showValueHeatmap}
              showArrows={visualization.showPolicyArrows}
            />
          );
        })
      )}

      {/* 网格边界 */}
      {visualization.showGrid && (
        <GridWalls gridSize={gridSize} cellSize={cellSize} />
      )}

      {/* Agent */}
      {visualization.showAgent && agentPosition && (
        <Agent
          position={[
            agentPosition.col * cellSize - offset,
            0.4,
            agentPosition.row * cellSize - offset
          ]}
          cellSize={cellSize}
        />
      )}
    </group>
  );
};

export default GridWorld3D;
