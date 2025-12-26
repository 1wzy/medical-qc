"""
执行上下文管理
负责管理规则执行过程中的数据流转和状态
"""
from typing import Any, Dict, List, Optional, Union
import json


class ExecutionContext:
    """
    执行上下文
    
    设计思路：
    1. 集中管理执行过程中的所有数据（病历、节点输出、中间变量）
    2. 支持参数引用解析（source/output模式）
    3. 提供证据提取接口
    """
    
    def __init__(self):
        self.medical_record: Optional[Dict[str, Any]] = None
        self.node_outputs: Dict[str, Dict[str, Any]] = {}  # {node_id: {output_name: value}}
        self.skip_reason: Optional[str] = None
        self.metadata: Dict[str, Any] = {}  # 可扩展的元数据
    
    def set_medical_record(self, record: Dict[str, Any]):
        """设置病历数据"""
        self.medical_record = record
    
    def get_medical_record(self) -> Optional[Dict[str, Any]]:
        """获取病历数据"""
        return self.medical_record
    
    def has_medical_record(self) -> bool:
        """检查是否有病历数据"""
        return self.medical_record is not None
    
    def set_node_output(self, node_id: str, outputs: Dict[str, Any]):
        """
        保存节点输出
        
        Args:
            node_id: 节点ID
            outputs: 节点输出字典
        """
        self.node_outputs[node_id] = outputs
    
    def get_node_output(self, node_id: str) -> Dict[str, Any]:
        """获取节点输出"""
        return self.node_outputs.get(node_id, {})
    
    def set_skip_reason(self, reason: str):
        """设置跳过原因"""
        self.skip_reason = reason
    
    def get_skip_reason(self) -> Optional[str]:
        """获取跳过原因"""
        return self.skip_reason
    
    def resolve_params(self, params: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
        """
        解析参数中的引用
        
        支持：
        - 单引用: {"source": "node1", "output": "x"}
        - 多引用拼接: [{"source": "n1", "output": "x"}, {"source": "n2", "output": "y"}]
        - 嵌套结构
        
        Args:
            params: 待解析的参数
            
        Returns:
            解析后的参数值
        """
        if isinstance(params, dict):
            # 检查是否是引用格式
            if "source" in params and "output" in params:
                return self._resolve_reference(params["source"], params["output"])
            
            # 递归处理字典
            return {k: self.resolve_params(v) for k, v in params.items()}
        
        elif isinstance(params, list):
            # 检查是否是多引用列表
            if all(isinstance(item, dict) and "source" in item and "output" in item 
                   for item in params):
                # 多引用拼接
                parts = []
                for item in params:
                    value = self._resolve_reference(item["source"], item["output"])
                    parts.append(str(value))
                return "\n".join(parts)
            
            # 递归处理列表
            return [self.resolve_params(item) for item in params]
        
        else:
            # 基本类型直接返回
            return params
    
    def _resolve_reference(self, source_id: str, output_key: str) -> Any:
        """
        解析单个引用
        
        Args:
            source_id: 源节点ID
            output_key: 输出字段名
            
        Returns:
            引用的值
        """
        if source_id not in self.node_outputs:
            raise RuntimeError(f"节点 {source_id} 尚未执行或不存在")
        
        node_output = self.node_outputs[source_id]
        if output_key not in node_output:
            raise KeyError(f"节点 {source_id} 无输出 '{output_key}'")
        
        return node_output[output_key]
    
    def extract_evidence(self) -> Dict[str, Any]:
        """
        提取执行证据
        
        用于生成质控报告，包含关键节点输出
        
        Returns:
            证据字典
        """
        evidence = {}
        
        for node_id, outputs in self.node_outputs.items():
            for key, value in outputs.items():
                # 处理长字符串（截断）
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                
                evidence[f"node_{node_id}.{key}"] = value
        
        return evidence

