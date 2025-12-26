"""
结果评估器
负责评估规则执行结果、生成解释文本
"""
from typing import Any, Dict, Optional
import re
from ruleengine.core.config import RuleConfig
from ruleengine.core.context import ExecutionContext


class ResultEvaluator:
    """
    结果评估器
    
    设计思路：
    1. 根据 result_rule 配置判断是否通过
    2. 支持模板化解释文本生成
    3. 支持跳过场景的特殊处理
    """
    
    def __init__(self, config: RuleConfig):
        self.config = config
    
    def evaluate(self, context: ExecutionContext) -> bool:
        """
        评估规则是否通过
        
        Args:
            context: 执行上下文
            
        Returns:
            是否通过
        """
        # 检查是否被跳过
        if context.get_skip_reason():
            return None  # None 表示跳过，不适用
        
        # 根据 result_rule 判断
        pass_cond = self.config.get_pass_condition()
        if not pass_cond:
            return False
        
        source_id = str(pass_cond.get("source"))
        output_key = pass_cond.get("output")
        expected_value = pass_cond.get("expect", True)
        
        node_output = context.get_node_output(source_id)
        actual_value = node_output.get(output_key)
        
        return actual_value == expected_value
    
    def render_explanation(self, context: ExecutionContext, passed: Optional[bool]) -> str:
        """
        渲染解释文本
        
        支持模板语法：{{node_X.key}} 用于引用节点输出
        
        Args:
            context: 执行上下文
            passed: 是否通过（None表示跳过）
            
        Returns:
            解释文本
        """
        if passed is None:
            # 跳过场景
            skip_reason = context.get_skip_reason()
            template = self.config.get_explanation_template(skip_reason)
            if template:
                return self._render_template(template, context)
            return "不满足质控条件，无需质控"
        
        # 正常场景
        status = "pass" if passed else "fail"
        template = self.config.get_explanation_template(status)
        if not template:
            return "符合" if passed else "不符合"
        
        return self._render_template(template, context)
    
    def _render_template(self, template: str, context: ExecutionContext) -> str:
        """
        渲染模板字符串
        
        支持 {{node_X.key}} 语法
        
        Args:
            template: 模板字符串
            context: 执行上下文
            
        Returns:
            渲染后的文本
        """
        result = template
        
        # 匹配 {{node_X.key}} 模式
        pattern = r'\{\{node_(\d+)\.(\w+)\}\}'
        matches = re.findall(pattern, result)
        
        for node_id_str, key in matches:
            node_id = int(node_id_str)
            node_output = context.get_node_output(str(node_id))
            
            if key in node_output:
                value = str(node_output[key])
                placeholder = f"{{{{node_{node_id}.{key}}}}}"
                result = result.replace(placeholder, value)
        
        return result

