"""
规则配置模型
负责解析和验证规则配置
"""
from typing import Any, Dict, List, Optional


class RuleConfig:
    """
    规则配置模型
    
    设计思路：
    1. 封装规则配置的解析和访问
    2. 提供类型安全的配置访问接口
    3. 支持配置验证
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化规则配置
        
        Args:
            config: 规则配置字典
        """
        self._config = config
        self._validate()
    
    def _validate(self):
        """验证配置完整性"""
        required_fields = ["rule_id", "rule_name", "function_list"]
        for field in required_fields:
            if field not in self._config:
                raise ValueError(f"规则配置缺少必需字段: {field}")
        
        function_list = self._config["function_list"]
        if "nodes" not in function_list:
            raise ValueError("function_list 必须包含 nodes")
    
    @property
    def rule_id(self) -> str:
        return self._config.get("rule_id", "")
    
    @property
    def rule_name(self) -> str:
        return self._config.get("rule_name", "")
    
    @property
    def module(self) -> str:
        return self._config.get("module", "")
    
    @property
    def description(self) -> str:
        return self._config.get("description", "")
    
    @property
    def type(self) -> str:
        return self._config.get("type", "unknown")
    
    @property
    def fields_name(self) -> List[List[str]]:
        return self._config.get("fields_name", [])
    
    @property
    def deduct(self) -> int:
        return self._config.get("deduct", 0)
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """获取节点列表，按 id 排序"""
        nodes = self._config["function_list"]["nodes"]
        return sorted(nodes, key=lambda x: x["id"])
    
    def get_pass_condition(self) -> Optional[Dict[str, Any]]:
        """获取通过条件"""
        result_rule = self._config["function_list"].get("result_rule", {})
        return result_rule.get("pass")
    
    def get_skip_conditions(self) -> Dict[str, Dict[str, Any]]:
        """获取跳过条件"""
        result_rule = self._config["function_list"].get("result_rule", {})
        skip_conds = {}
        for key, value in result_rule.items():
            if key.startswith("skipped"):
                skip_conds[key] = value
        return skip_conds
    
    def get_explanation_template(self, status: str) -> Optional[str]:
        """
        获取解释模板
        
        Args:
            status: 状态（pass/fail/skipped_xxx）
            
        Returns:
            模板字符串
        """
        templates = self._config["function_list"].get("explanation_template", {})
        return templates.get(status, "")

