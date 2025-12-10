/**
 * TeachingMode - 教学演示模式组件
 *
 * 提供算法步骤式演示，帮助学生理解强化学习算法原理
 * 支持DP算法和TD算法的可视化教学
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  Steps,
  Button,
  Space,
  Typography,
  Tag,
  Collapse,
  Alert,
  Progress,
  Divider,
  Switch
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepForwardOutlined,
  ReloadOutlined,
  BulbOutlined,
  BookOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

// 算法步骤定义
interface AlgorithmStep {
  title: string;
  description: string;
  formula?: string;
  highlight?: string;
}

// DP算法教学步骤
const dpSteps: AlgorithmStep[] = [
  {
    title: '初始化',
    description: '将所有状态的值函数V(s)初始化为0，策略π初始化为均匀随机策略',
    formula: 'V(s) = 0, π(a|s) = 1/|A|',
    highlight: '初始化是迭代算法的起点'
  },
  {
    title: '策略评估',
    description: '在当前策略下，计算每个状态的期望回报。反复更新直到值函数收敛',
    formula: 'V(s) ← Σ π(a|s) Σ p(s\',r|s,a)[r + γV(s\')]',
    highlight: 'Bellman期望方程的迭代求解'
  },
  {
    title: '策略改进',
    description: '根据当前值函数，贪婪地选择每个状态的最优动作',
    formula: 'π(s) = argmax_a Σ p(s\',r|s,a)[r + γV(s\')]',
    highlight: '策略改进定理保证性能单调提升'
  },
  {
    title: '收敛检查',
    description: '检查策略是否稳定（不再改变），如果稳定则找到最优策略',
    formula: 'if π_old = π_new: 停止',
    highlight: '策略迭代通常在少数几轮后收敛'
  }
];

// TD算法教学步骤 (SARSA)
const sarsaSteps: AlgorithmStep[] = [
  {
    title: '初始化Q表',
    description: '将所有状态-动作对的Q值初始化为0',
    formula: 'Q(s,a) = 0, ∀s∈S, a∈A',
    highlight: 'Q表存储每个状态-动作对的价值估计'
  },
  {
    title: '选择动作',
    description: '使用ε-贪婪策略：以概率ε随机探索，否则选择当前最优动作',
    formula: 'A = ε-greedy(Q,S)',
    highlight: '探索与利用的平衡是TD学习的关键'
  },
  {
    title: '执行动作',
    description: '在环境中执行动作A，观察奖励R和下一状态S\'',
    formula: 'S\', R = env.step(A)',
    highlight: '与环境交互获取经验'
  },
  {
    title: '选择下一动作',
    description: 'SARSA特点：在更新前先选择下一个动作A\'',
    formula: 'A\' = ε-greedy(Q,S\')',
    highlight: 'On-policy: 使用实际执行的动作'
  },
  {
    title: 'TD更新',
    description: '使用TD误差更新Q值',
    formula: 'Q(S,A) ← Q(S,A) + α[R + γQ(S\',A\') - Q(S,A)]',
    highlight: 'TD误差 = R + γQ(S\',A\') - Q(S,A)'
  },
  {
    title: '状态转移',
    description: '移动到下一状态，继续学习直到回合结束',
    formula: 'S ← S\', A ← A\'',
    highlight: '重复直到到达终止状态'
  }
];

// Q-Learning教学步骤
const qLearningSteps: AlgorithmStep[] = [
  {
    title: '初始化Q表',
    description: '将所有状态-动作对的Q值初始化为0',
    formula: 'Q(s,a) = 0, ∀s∈S, a∈A',
    highlight: 'Q表存储每个状态-动作对的价值估计'
  },
  {
    title: '选择动作',
    description: '使用ε-贪婪策略选择动作',
    formula: 'A = ε-greedy(Q,S)',
    highlight: '行为策略用于探索'
  },
  {
    title: '执行动作',
    description: '在环境中执行动作，观察结果',
    formula: 'S\', R = env.step(A)',
    highlight: '收集经验样本'
  },
  {
    title: 'TD更新 (Off-policy)',
    description: 'Q-Learning使用最大Q值更新，而非实际动作',
    formula: 'Q(S,A) ← Q(S,A) + α[R + γ max_a Q(S\',a) - Q(S,A)]',
    highlight: 'Off-policy: 学习最优策略，与行为策略无关'
  },
  {
    title: '状态转移',
    description: '移动到下一状态继续学习',
    formula: 'S ← S\'',
    highlight: '重复直到收敛'
  }
];

interface TeachingModeProps {
  algorithm: 'policy_iteration' | 'value_iteration' | 'sarsa' | 'q_learning';
  onStepChange?: (step: number) => void;
}

const TeachingMode: React.FC<TeachingModeProps> = ({
  algorithm,
  onStepChange
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [autoPlaySpeed] = useState(2000);
  const [showFormulas, setShowFormulas] = useState(true);

  // 获取当前算法的步骤
  const getSteps = useCallback(() => {
    switch (algorithm) {
      case 'policy_iteration':
      case 'value_iteration':
        return dpSteps;
      case 'sarsa':
        return sarsaSteps;
      case 'q_learning':
        return qLearningSteps;
      default:
        return dpSteps;
    }
  }, [algorithm]);

  const steps = getSteps();

  // 自动播放
  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isPlaying) {
      timer = setInterval(() => {
        setCurrentStep(prev => {
          const next = (prev + 1) % steps.length;
          onStepChange?.(next);
          return next;
        });
      }, autoPlaySpeed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, autoPlaySpeed, steps.length, onStepChange]);

  // 下一步
  const nextStep = () => {
    const next = (currentStep + 1) % steps.length;
    setCurrentStep(next);
    onStepChange?.(next);
  };

  // 上一步
  const prevStep = () => {
    const prev = currentStep === 0 ? steps.length - 1 : currentStep - 1;
    setCurrentStep(prev);
    onStepChange?.(prev);
  };

  // 重置
  const reset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
    onStepChange?.(0);
  };

  // 算法类型标签
  const getAlgorithmTag = () => {
    switch (algorithm) {
      case 'policy_iteration':
        return <Tag color="blue">策略迭代 (DP)</Tag>;
      case 'value_iteration':
        return <Tag color="cyan">值迭代 (DP)</Tag>;
      case 'sarsa':
        return <Tag color="purple">SARSA (On-policy TD)</Tag>;
      case 'q_learning':
        return <Tag color="green">Q-Learning (Off-policy TD)</Tag>;
      default:
        return null;
    }
  };

  // 算法简介
  const getAlgorithmIntro = () => {
    switch (algorithm) {
      case 'policy_iteration':
        return '策略迭代交替进行策略评估和策略改进，直到策略收敛到最优。';
      case 'value_iteration':
        return '值迭代将策略评估和改进合并为一步，直接迭代计算最优值函数。';
      case 'sarsa':
        return 'SARSA是On-policy TD控制算法，使用实际执行的动作进行更新。';
      case 'q_learning':
        return 'Q-Learning是Off-policy TD控制算法，直接学习最优策略。';
      default:
        return '';
    }
  };

  const currentStepData = steps[currentStep];

  return (
    <Card
      title={
        <Space>
          <BookOutlined />
          <span>教学演示模式</span>
          {getAlgorithmTag()}
        </Space>
      }
      size="small"
      extra={
        <Space>
          <Text type="secondary" style={{ fontSize: 12 }}>显示公式</Text>
          <Switch
            size="small"
            checked={showFormulas}
            onChange={setShowFormulas}
          />
        </Space>
      }
    >
      {/* 算法简介 */}
      <Alert
        message={getAlgorithmIntro()}
        type="info"
        showIcon
        icon={<BulbOutlined />}
        style={{ marginBottom: 16 }}
      />

      {/* 步骤进度 */}
      <Steps
        current={currentStep}
        size="small"
        style={{ marginBottom: 16 }}
        items={steps.map((step, index) => ({
          title: step.title,
          status: index < currentStep ? 'finish' : index === currentStep ? 'process' : 'wait'
        }))}
      />

      {/* 当前步骤详情 */}
      <Card
        size="small"
        style={{
          backgroundColor: '#1a1a2e',
          border: '1px solid #1890ff',
          marginBottom: 16
        }}
      >
        <Title level={5} style={{ color: '#1890ff', marginBottom: 8 }}>
          第 {currentStep + 1} 步: {currentStepData.title}
        </Title>

        <Paragraph style={{ color: '#fff', marginBottom: 12 }}>
          {currentStepData.description}
        </Paragraph>

        {showFormulas && currentStepData.formula && (
          <div style={{
            backgroundColor: '#0d1117',
            padding: '8px 12px',
            borderRadius: 4,
            fontFamily: 'monospace',
            color: '#58a6ff',
            marginBottom: 8
          }}>
            {currentStepData.formula}
          </div>
        )}

        {currentStepData.highlight && (
          <Text type="warning" style={{ fontSize: 12 }}>
            <BulbOutlined /> {currentStepData.highlight}
          </Text>
        )}
      </Card>

      {/* 进度条 */}
      <Progress
        percent={Math.round(((currentStep + 1) / steps.length) * 100)}
        size="small"
        status="active"
        format={() => `${currentStep + 1}/${steps.length}`}
        style={{ marginBottom: 16 }}
      />

      {/* 控制按钮 */}
      <Space wrap style={{ width: '100%', justifyContent: 'center' }}>
        <Button
          icon={<StepForwardOutlined style={{ transform: 'rotate(180deg)' }} />}
          onClick={prevStep}
          disabled={isPlaying}
        >
          上一步
        </Button>

        <Button
          type="primary"
          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          onClick={() => setIsPlaying(!isPlaying)}
        >
          {isPlaying ? '暂停' : '自动播放'}
        </Button>

        <Button
          icon={<StepForwardOutlined />}
          onClick={nextStep}
          disabled={isPlaying}
        >
          下一步
        </Button>

        <Button
          icon={<ReloadOutlined />}
          onClick={reset}
        >
          重置
        </Button>
      </Space>

      <Divider style={{ margin: '16px 0' }} />

      {/* 算法对比说明 */}
      <Collapse ghost size="small">
        <Panel header="算法原理详解" key="1">
          {['policy_iteration', 'value_iteration'].includes(algorithm) ? (
            <div style={{ fontSize: 12, color: '#888' }}>
              <p><strong>动态规划 (DP) 特点:</strong></p>
              <ul>
                <li>需要完整的环境模型 (状态转移概率)</li>
                <li>计算所有状态的值函数</li>
                <li>保证收敛到最优解</li>
                <li>适用于小规模问题</li>
              </ul>
            </div>
          ) : (
            <div style={{ fontSize: 12, color: '#888' }}>
              <p><strong>时序差分 (TD) 特点:</strong></p>
              <ul>
                <li>无需环境模型，从经验中学习</li>
                <li>结合蒙特卡洛和DP的优点</li>
                <li>每步更新，无需等待回合结束</li>
                <li>适用于大规模和连续问题</li>
              </ul>
              <Divider style={{ margin: '8px 0' }} />
              <p><strong>SARSA vs Q-Learning:</strong></p>
              <ul>
                <li><Text style={{ color: '#8884d8' }}>SARSA</Text>: 保守，考虑探索风险</li>
                <li><Text style={{ color: '#82ca9d' }}>Q-Learning</Text>: 激进，追求最优路径</li>
              </ul>
            </div>
          )}
        </Panel>
      </Collapse>
    </Card>
  );
};

export default TeachingMode;
