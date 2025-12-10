"""
XML Exporter - XML日志导出模块

按照实验要求将迭代数据导出为XML格式。
文件命名规则: {ExperimentType}_{YYYYMMDD}_{HHMM}.xml
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os

from ..algorithm.dp_solver import IterationRecord, EpisodeRecord, DPResult


@dataclass
class ExperimentMetadata:
    """实验元数据"""
    experiment_id: str
    experiment_type: str  # basic, windy, cliff
    algorithm: str
    grid_size: int
    gamma: float
    theta: float
    step_reward: float
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class XMLExporter:
    """
    XML日志导出器

    将实验数据导出为结构化的XML文件，包含：
    - 实验配置信息
    - 迭代过程记录
    - 最终结果（值函数、策略）
    """

    def __init__(self, output_dir: str = "data/exports"):
        """
        初始化导出器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, experiment_type: str) -> str:
        """
        生成文件名

        Args:
            experiment_type: 实验类型

        Returns:
            格式化的文件名
        """
        now = datetime.now()
        type_name = experiment_type.capitalize() + "Gridworld"
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{type_name}_{timestamp}.xml"

    def _prettify(self, elem: ET.Element) -> str:
        """
        美化XML输出

        Args:
            elem: XML元素

        Returns:
            格式化的XML字符串
        """
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def export_basic_gridworld(
        self,
        metadata: ExperimentMetadata,
        result: DPResult,
        iterations: List[IterationRecord],
        episodes: Optional[List[EpisodeRecord]] = None
    ) -> str:
        """
        导出基础网格世界实验结果

        Args:
            metadata: 实验元数据
            result: DP算法结果
            iterations: 迭代记录列表
            episodes: 回合记录列表（可选）

        Returns:
            导出的文件路径
        """
        # 创建根元素
        root = ET.Element("Experiment")
        root.set("version", "1.0")
        root.set("xmlns", "http://rl-gridworld.edu/schema")

        # 元数据
        meta_elem = ET.SubElement(root, "Metadata")
        ET.SubElement(meta_elem, "ExperimentID").text = metadata.experiment_id
        ET.SubElement(meta_elem, "ExperimentType").text = metadata.experiment_type
        ET.SubElement(meta_elem, "Algorithm").text = metadata.algorithm
        ET.SubElement(meta_elem, "CreatedAt").text = metadata.created_at.isoformat()

        # 配置信息
        config_elem = ET.SubElement(root, "Configuration")
        ET.SubElement(config_elem, "GridSize").text = str(metadata.grid_size)
        ET.SubElement(config_elem, "DiscountFactor").text = str(metadata.gamma)
        ET.SubElement(config_elem, "ConvergenceThreshold").text = str(metadata.theta)
        ET.SubElement(config_elem, "StepReward").text = str(metadata.step_reward)

        # 执行摘要
        summary_elem = ET.SubElement(root, "ExecutionSummary")
        ET.SubElement(summary_elem, "Converged").text = str(result.converged).lower()
        ET.SubElement(summary_elem, "TotalIterations").text = str(result.total_iterations)
        ET.SubElement(summary_elem, "TotalEpisodes").text = str(result.total_episodes)
        ET.SubElement(summary_elem, "ExecutionTime").text = f"{result.execution_time:.4f}"

        # 迭代历史
        history_elem = ET.SubElement(root, "IterationHistory")
        for record in iterations:
            iter_elem = ET.SubElement(history_elem, "Iteration")
            iter_elem.set("number", str(record.iteration))

            ET.SubElement(iter_elem, "State").text = str(record.state)
            if record.action:
                ET.SubElement(iter_elem, "Action").text = record.action
            ET.SubElement(iter_elem, "OldValue").text = f"{record.old_value:.6f}"
            ET.SubElement(iter_elem, "NewValue").text = f"{record.new_value:.6f}"
            ET.SubElement(iter_elem, "Delta").text = f"{record.delta:.6f}"
            ET.SubElement(iter_elem, "Timestamp").text = f"{record.timestamp:.6f}"

        # 回合历史（如果有）
        if episodes:
            episodes_elem = ET.SubElement(root, "EpisodeHistory")
            for ep_record in episodes:
                ep_elem = ET.SubElement(episodes_elem, "Episode")
                ep_elem.set("number", str(ep_record.episode))

                ET.SubElement(ep_elem, "PolicyStable").text = str(ep_record.policy_stable).lower()
                ET.SubElement(ep_elem, "MaxDelta").text = f"{ep_record.max_delta:.6f}"

                # 该回合的值函数
                values_elem = ET.SubElement(ep_elem, "ValueFunction")
                for i, v in enumerate(ep_record.value_function):
                    state_elem = ET.SubElement(values_elem, "State")
                    state_elem.set("id", str(i))
                    state_elem.text = f"{v:.6f}"

        # 最终结果
        result_elem = ET.SubElement(root, "FinalResult")

        # 最终值函数
        final_values_elem = ET.SubElement(result_elem, "ValueFunction")
        for i, v in enumerate(result.final_values):
            state_elem = ET.SubElement(final_values_elem, "State")
            state_elem.set("id", str(i))
            row = i // metadata.grid_size
            col = i % metadata.grid_size
            state_elem.set("row", str(row))
            state_elem.set("col", str(col))
            state_elem.text = f"{v:.6f}"

        # 最终策略
        final_policy_elem = ET.SubElement(result_elem, "Policy")
        action_names = ["up", "down", "left", "right"]
        for i, probs in enumerate(result.final_policy):
            state_elem = ET.SubElement(final_policy_elem, "State")
            state_elem.set("id", str(i))
            row = i // metadata.grid_size
            col = i % metadata.grid_size
            state_elem.set("row", str(row))
            state_elem.set("col", str(col))

            for j, prob in enumerate(probs):
                if prob > 0:
                    action_elem = ET.SubElement(state_elem, "Action")
                    action_elem.set("name", action_names[j])
                    action_elem.set("probability", f"{prob:.4f}")

        # 写入文件
        filename = self._generate_filename(metadata.experiment_type)
        filepath = self.output_dir / filename

        xml_string = self._prettify(root)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        return str(filepath)

    def export_iteration_log(
        self,
        experiment_id: str,
        experiment_type: str,
        iterations: List[Dict[str, Any]]
    ) -> str:
        """
        导出简化的迭代日志

        Args:
            experiment_id: 实验ID
            experiment_type: 实验类型
            iterations: 迭代数据列表

        Returns:
            导出的文件路径
        """
        root = ET.Element("IterationLog")
        root.set("experimentId", experiment_id)
        root.set("type", experiment_type)
        root.set("timestamp", datetime.now().isoformat())

        for i, data in enumerate(iterations):
            iter_elem = ET.SubElement(root, "Iteration")
            iter_elem.set("number", str(i))

            for key, value in data.items():
                elem = ET.SubElement(iter_elem, key.replace("_", "").title())
                if isinstance(value, float):
                    elem.text = f"{value:.6f}"
                elif isinstance(value, list):
                    elem.text = ",".join(str(v) for v in value)
                else:
                    elem.text = str(value)

        filename = f"IterationLog_{experiment_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        filepath = self.output_dir / filename

        xml_string = self._prettify(root)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        return str(filepath)

    def read_xml_log(self, filepath: str) -> Dict[str, Any]:
        """
        读取XML日志文件

        Args:
            filepath: 文件路径

        Returns:
            解析后的数据字典
        """
        tree = ET.parse(filepath)
        root = tree.getroot()

        result = {
            "metadata": {},
            "configuration": {},
            "summary": {},
            "iterations": [],
            "final_result": {}
        }

        # 解析元数据
        meta = root.find("Metadata")
        if meta is not None:
            for child in meta:
                result["metadata"][child.tag] = child.text

        # 解析配置
        config = root.find("Configuration")
        if config is not None:
            for child in config:
                result["configuration"][child.tag] = child.text

        # 解析摘要
        summary = root.find("ExecutionSummary")
        if summary is not None:
            for child in summary:
                result["summary"][child.tag] = child.text

        # 解析迭代历史
        history = root.find("IterationHistory")
        if history is not None:
            for iter_elem in history.findall("Iteration"):
                iteration_data = {"number": iter_elem.get("number")}
                for child in iter_elem:
                    iteration_data[child.tag] = child.text
                result["iterations"].append(iteration_data)

        # 解析最终结果
        final = root.find("FinalResult")
        if final is not None:
            values_elem = final.find("ValueFunction")
            if values_elem is not None:
                result["final_result"]["values"] = []
                for state_elem in values_elem.findall("State"):
                    result["final_result"]["values"].append({
                        "id": state_elem.get("id"),
                        "row": state_elem.get("row"),
                        "col": state_elem.get("col"),
                        "value": state_elem.text
                    })

            policy_elem = final.find("Policy")
            if policy_elem is not None:
                result["final_result"]["policy"] = []
                for state_elem in policy_elem.findall("State"):
                    state_policy = {
                        "id": state_elem.get("id"),
                        "actions": []
                    }
                    for action_elem in state_elem.findall("Action"):
                        state_policy["actions"].append({
                            "name": action_elem.get("name"),
                            "probability": action_elem.get("probability")
                        })
                    result["final_result"]["policy"].append(state_policy)

        return result

    def list_exports(self) -> List[Dict[str, str]]:
        """
        列出所有导出文件

        Returns:
            文件信息列表
        """
        files = []
        for filepath in self.output_dir.glob("*.xml"):
            stat = filepath.stat()
            files.append({
                "filename": filepath.name,
                "path": str(filepath),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def delete_export(self, filename: str) -> bool:
        """
        删除导出文件

        Args:
            filename: 文件名

        Returns:
            是否删除成功
        """
        filepath = self.output_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False


# 创建默认导出器实例
default_exporter = XMLExporter()


def export_experiment(
    metadata: ExperimentMetadata,
    result: DPResult,
    iterations: List[IterationRecord],
    episodes: Optional[List[EpisodeRecord]] = None
) -> str:
    """
    导出实验的便捷函数

    Args:
        metadata: 实验元数据
        result: 算法结果
        iterations: 迭代记录
        episodes: 回合记录

    Returns:
        导出文件路径
    """
    return default_exporter.export_basic_gridworld(
        metadata, result, iterations, episodes
    )
