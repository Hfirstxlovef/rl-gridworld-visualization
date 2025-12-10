"""
XML导出功能测试

测试XML日志导出器的字段完整性和格式正确性
"""

import pytest
import os
import sys
import tempfile
import numpy as np
from datetime import datetime
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.export.xml_exporter import (
    XMLExporter, ExperimentMetadata, export_experiment
)
from app.services.algorithm.dp_solver import IterationRecord, EpisodeRecord, DPResult

# XML命名空间
NS = {'ns': 'http://rl-gridworld.edu/schema'}


def find_elem(root, path):
    """在带命名空间的XML中查找元素"""
    # 尝试带命名空间的查找
    result = root.find(path.replace('/', '/ns:').replace('/ns:/', '/'), NS)
    if result is None:
        # 回退到不带命名空间的查找
        result = root.find(path)
    if result is None:
        # 尝试使用 {namespace} 前缀
        ns_path = path
        for part in ['Metadata', 'Configuration', 'ExecutionSummary', 'IterationHistory',
                     'EpisodeHistory', 'FinalResult', 'ValueFunction', 'Policy', 'Iteration',
                     'Episode', 'State', 'Action', 'ExperimentID', 'ExperimentType',
                     'Algorithm', 'CreatedAt', 'GridSize', 'DiscountFactor',
                     'ConvergenceThreshold', 'StepReward', 'Converged', 'TotalIterations',
                     'TotalEpisodes', 'ExecutionTime', 'OldValue', 'NewValue', 'Delta',
                     'Timestamp', 'PolicyStable', 'MaxDelta']:
            ns_path = ns_path.replace(part, f'{{http://rl-gridworld.edu/schema}}{part}')
        result = root.find(ns_path)
    return result


def findall_elem(root, path):
    """在带命名空间的XML中查找所有元素"""
    ns_path = path
    for part in ['Iteration', 'Episode', 'State', 'Action']:
        ns_path = ns_path.replace(part, f'{{http://rl-gridworld.edu/schema}}{part}')
    result = root.findall(ns_path)
    if not result:
        result = root.findall(path)
    return result


def create_dp_result(n_states=16, algorithm='policy_iteration', converged=True,
                     total_iterations=5, total_episodes=0, execution_time=0.02):
    """创建 DPResult 测试数据的辅助函数"""
    return DPResult(
        algorithm=algorithm,
        converged=converged,
        total_iterations=total_iterations,
        total_episodes=total_episodes,
        final_values=np.zeros(n_states),
        final_policy=np.full((n_states, 4), 0.25),
        history=[],
        episode_history=[],
        execution_time=execution_time
    )


class TestXMLExporter:
    """XML导出器测试"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = XMLExporter(output_dir=self.temp_dir)

    def test_exporter_initialization(self):
        """测试导出器初始化"""
        assert self.exporter is not None
        assert os.path.exists(self.temp_dir)

    def test_filename_generation(self):
        """测试文件名生成"""
        filename = self.exporter._generate_filename("basic")
        assert "BasicGridworld" in filename
        assert ".xml" in filename

    def test_export_basic_gridworld(self):
        """测试基础网格世界导出"""
        metadata = ExperimentMetadata(
            experiment_id='test-123',
            experiment_type='basic',
            algorithm='policy_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(
            n_states=16,
            algorithm='policy_iteration',
            total_iterations=10,
            total_episodes=3,
            execution_time=0.05
        )

        iterations = [
            IterationRecord(
                iteration=1,
                state=0,
                action='up',
                old_value=0.0,
                new_value=-1.0,
                delta=1.0,
                timestamp=0.001
            )
        ]

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=iterations
        )

        # 验证文件存在
        assert os.path.exists(filepath)

        # 解析XML
        tree = ET.parse(filepath)
        root = tree.getroot()
        assert 'Experiment' in root.tag

        # 检查元数据
        meta = find_elem(root, 'Metadata')
        assert meta is not None
        exp_id = find_elem(meta, 'ExperimentID')
        assert exp_id is not None
        assert exp_id.text == "test-123"

    def test_iteration_record_export(self):
        """测试迭代记录导出"""
        metadata = ExperimentMetadata(
            experiment_id='iter-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(
            n_states=16,
            algorithm='value_iteration',
            total_iterations=3,
            execution_time=0.02
        )

        iterations = [
            IterationRecord(iteration=1, state=0, action='up',
                          old_value=0.0, new_value=-0.5, delta=0.5, timestamp=0.001),
            IterationRecord(iteration=2, state=1, action='down',
                          old_value=-0.5, new_value=-0.8, delta=0.3, timestamp=0.002),
            IterationRecord(iteration=3, state=2, action='left',
                          old_value=-0.8, new_value=-0.85, delta=0.05, timestamp=0.003)
        ]

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=iterations
        )

        # 验证文件内容包含迭代记录
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'IterationHistory' in content
            assert 'Iteration' in content
            assert 'number="1"' in content

    def test_episode_record_export(self):
        """测试回合记录导出"""
        metadata = ExperimentMetadata(
            experiment_id='ep-test',
            experiment_type='basic',
            algorithm='policy_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = DPResult(
            algorithm='policy_iteration',
            converged=True,
            total_iterations=10,
            total_episodes=2,
            final_values=np.arange(16, dtype=float),
            final_policy=np.array([[1.0, 0.0, 0.0, 0.0]] * 16),
            history=[],
            episode_history=[],
            execution_time=0.1
        )

        iterations = []
        episodes = [
            EpisodeRecord(
                episode=1,
                policy_stable=False,
                max_delta=0.5,
                value_function=list(range(16)),
                policy=[[0.25, 0.25, 0.25, 0.25]] * 16,
                iterations=[]
            ),
            EpisodeRecord(
                episode=2,
                policy_stable=True,
                max_delta=0.001,
                value_function=list(range(16)),
                policy=[[1.0, 0.0, 0.0, 0.0]] * 16,
                iterations=[]
            )
        ]

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=iterations,
            episodes=episodes
        )

        # 验证文件内容包含回合记录
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'EpisodeHistory' in content
            assert 'Episode' in content

    def test_configuration_export(self):
        """测试配置信息导出"""
        metadata = ExperimentMetadata(
            experiment_id='config-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=6,
            gamma=0.95,
            theta=1e-8,
            step_reward=-0.5
        )

        result = create_dp_result(n_states=36, algorithm='value_iteration')

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        tree = ET.parse(filepath)
        root = tree.getroot()

        config = find_elem(root, 'Configuration')
        assert config is not None

        grid_size = find_elem(config, 'GridSize')
        assert grid_size is not None
        assert grid_size.text == "6"

    def test_final_result_export(self):
        """测试最终结果导出"""
        metadata = ExperimentMetadata(
            experiment_id='final-test',
            experiment_type='basic',
            algorithm='policy_iteration',
            grid_size=2,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = DPResult(
            algorithm='policy_iteration',
            converged=True,
            total_iterations=5,
            total_episodes=1,
            final_values=np.array([0.0, -1.5, -1.5, -3.0]),
            final_policy=np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]),
            history=[],
            episode_history=[],
            execution_time=0.01
        )

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        tree = ET.parse(filepath)
        root = tree.getroot()

        final_result = find_elem(root, 'FinalResult')
        assert final_result is not None

        # 检查值函数
        values = find_elem(final_result, 'ValueFunction')
        assert values is not None
        states = findall_elem(values, 'State')
        assert len(states) == 4

    def test_read_xml_log(self):
        """测试读取XML日志 - 验证文件可读"""
        metadata = ExperimentMetadata(
            experiment_id='read-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(n_states=16, algorithm='value_iteration')

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        # 验证文件存在且可读
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
            # 验证关键内容存在
            assert 'read-test' in content
            assert 'value_iteration' in content
            assert 'GridSize' in content

    def test_list_and_delete_exports(self):
        """测试列出和删除导出文件"""
        metadata = ExperimentMetadata(
            experiment_id='list-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(n_states=16, algorithm='value_iteration')

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        # 列出文件
        files = self.exporter.list_exports()
        assert len(files) >= 1

        # 找到并删除
        filename = os.path.basename(filepath)
        deleted = self.exporter.delete_export(filename)
        assert deleted == True

        # 验证已删除
        assert not os.path.exists(filepath)


class TestXMLFieldCompleteness:
    """XML字段完整性测试"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = XMLExporter(output_dir=self.temp_dir)

    def test_required_metadata_fields(self):
        """测试必需的元数据字段"""
        metadata = ExperimentMetadata(
            experiment_id='field-test',
            experiment_type='basic',
            algorithm='policy_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(n_states=16, algorithm='policy_iteration')

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        tree = ET.parse(filepath)
        root = tree.getroot()

        # 必需的元数据字段
        meta = find_elem(root, 'Metadata')
        assert meta is not None

        required_meta = ['ExperimentID', 'ExperimentType', 'Algorithm', 'CreatedAt']
        for field in required_meta:
            elem = find_elem(meta, field)
            assert elem is not None, f"Missing metadata: {field}"

    def test_iteration_record_fields(self):
        """测试迭代记录必需字段"""
        metadata = ExperimentMetadata(
            experiment_id='iter-field-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(
            n_states=16,
            algorithm='value_iteration',
            total_iterations=1,
            execution_time=0.01
        )

        iterations = [
            IterationRecord(
                iteration=1,
                state=5,
                action='right',
                old_value=0.0,
                new_value=-1.0,
                delta=1.0,
                timestamp=0.001
            )
        ]

        filepath = self.exporter.export_basic_gridworld(
            metadata=metadata,
            result=result,
            iterations=iterations
        )

        # 验证迭代字段存在
        with open(filepath, 'r') as f:
            content = f.read()
            required_fields = ['State', 'Action', 'OldValue', 'NewValue', 'Delta']
            for field in required_fields:
                assert field in content, f"Missing iteration field: {field}"


class TestExportConvenienceFunction:
    """测试便捷导出函数"""

    def test_export_experiment_function(self):
        """测试 export_experiment 便捷函数"""
        metadata = ExperimentMetadata(
            experiment_id='conv-test',
            experiment_type='basic',
            algorithm='value_iteration',
            grid_size=4,
            gamma=0.9,
            theta=1e-6,
            step_reward=-1.0
        )

        result = create_dp_result(n_states=16, algorithm='value_iteration')

        filepath = export_experiment(
            metadata=metadata,
            result=result,
            iterations=[]
        )

        assert os.path.exists(filepath)
        assert filepath.endswith('.xml')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
