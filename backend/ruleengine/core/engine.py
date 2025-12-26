"""
规则执行引擎
负责解析规则配置、按流程执行节点、管理执行上下文
"""
from typing import Any, Dict, List, Optional
from ruleengine.core.context import ExecutionContext
from ruleengine.core.evaluator import ResultEvaluator
from ruleengine.core.config import RuleConfig
from ruleengine.registry import function_registry
import time


class RuleEngine:
    """
    规则执行引擎
    
    设计思路：
    1. 采用工作流模式，支持节点式规则编排
    2. 节点间通过上下文共享数据，支持参数引用
    3. 支持条件分支和提前终止（skip逻辑）
    4. 统一的错误处理和结果格式化
    """
    
    def __init__(self, rule_config: Dict[str, Any]):
        """
        初始化规则引擎
        
        Args:
            rule_config: 规则配置字典，包含规则元数据和执行流程
        """
        self.config = RuleConfig(rule_config)
        self.context = ExecutionContext()
        self.evaluator = ResultEvaluator(self.config)
        
    def execute(self, medical_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行规则，对病历进行质控检查
        
        Args:
            medical_record: 病历数据字典
            
        Returns:
            质控结果字典，包含：
            - rule_id, rule_name, description, module
            - passed: 是否通过
            - flag: 状态标志（1=通过, 0=不通过, 2=跳过, -1=错误）
            - deduct: 扣分
            - explanation: 解释说明
            - answer: 证据数据
        """
        start_time = time.time()
        
        try:
            # 1. 初始化执行上下文
            self.context.set_medical_record(medical_record)
            
            # 2. 执行规则节点流程
            self._execute_nodes()
            
            # 3. 评估最终结果
            passed = self.evaluator.evaluate(self.context)
            
            # 4. 生成解释文本
            explanation = self.evaluator.render_explanation(self.context, passed)
            
            # 5. 提取证据
            evidence = self.context.extract_evidence()
            
            # 6. 计算执行耗时
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 7. 构建返回结果
            return {
                "rule_id": self.config.rule_id,
                "rule_name": self.config.rule_name,
                "description": self.config.description,
                "module": self.config.module,
                "type": self.config.type,
                "fields_name": self.config.fields_name,
                "passed": passed,
                "flag": 1 if passed else 0,
                "conclusion": "符合" if passed else "不符合",
                "answer": evidence,
                "explanation": explanation,
                "deduct": 0 if passed else self.config.deduct,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            # 错误处理
            return {
                "rule_id": self.config.rule_id,
                "rule_name": self.config.rule_name,
                "description": self.config.description,
                "module": self.config.module,
                "type": self.config.type,
                "fields_name": self.config.fields_name,
                "passed": False,
                "flag": -1,
                "conclusion": "系统错误",
                "answer": {"error": str(e)},
                "explanation": f"【系统错误】规则执行失败：{str(e)}",
                "deduct": 0,
                "duration_ms": int((time.time() - start_time) * 1000)
            }
    
    def _execute_nodes(self):
        """按顺序执行所有节点"""
        nodes = self.config.get_nodes()
        
        for node in nodes:
            # 执行节点
            self._execute_single_node(node)
            
            # 检查是否需要跳过剩余流程
            if self._should_skip_remaining(node):
                break
    
    def _execute_single_node(self, node: Dict[str, Any]):
        """
        执行单个节点
        
        Args:
            node: 节点配置，包含 id, function, params, outputs
        """
        node_id = node["id"]
        func_name = node["function"]
        
        # 1. 查找注册的函数
        if func_name not in function_registry:
            raise KeyError(f"未找到注册函数: {func_name}")
        
        func_info = function_registry[func_name]
        func = func_info["function"]
        
        # 2. 解析参数（支持引用其他节点的输出）
        resolved_params = self.context.resolve_params(node.get("params", {}))
        
        # 3. 注入 medical_record（仅当函数签名包含该参数时）
        import inspect
        sig = inspect.signature(func)
        if "medical_record" in sig.parameters and self.context.has_medical_record():
            resolved_params["medical_record"] = self.context.get_medical_record()
        
        # 4. 调用函数
        raw_result = func(**resolved_params)
        
        # 5. 映射输出别名
        outputs = {}
        for alias, field in node.get("outputs", {}).items():
            if field in raw_result:
                outputs[alias] = raw_result[field]
            else:
                raise KeyError(f"函数返回中不存在字段 '{field}'，无法映射为 '{alias}'")
        
        # 6. 保存节点输出到上下文（统一转为字符串）
        self.context.set_node_output(str(node_id), outputs)
    
    def _should_skip_remaining(self, node: Dict[str, Any]) -> bool:
        """
        判断是否应该跳过剩余流程
        
        设计：支持在规则配置中定义 skip 条件，当节点输出满足条件时提前终止
        
        Args:
            node: 当前执行的节点
            
        Returns:
            是否跳过
        """
        skip_conditions = self.config.get_skip_conditions()
        if not skip_conditions:
            return False
        
        node_id = str(node["id"])
        
        # 检查所有 skip 条件
        for skip_key, skip_cond in skip_conditions.items():
            skip_source = str(skip_cond.get("source"))
            if skip_source == node_id_str:
                output_key = skip_cond.get("output")
                expected_value = skip_cond.get("expect", False)
                
                node_outputs = self.context.get_node_output(node_id_str)
                if output_key in node_outputs:
                    actual_value = node_outputs[output_key]
                    if actual_value == expected_value:
                        # 匹配到跳过条件
                        self.context.set_skip_reason(skip_key)
                        return True
        
        return False

