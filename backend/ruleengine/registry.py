"""
函数注册表
提供原子函数的注册和管理机制
"""
from typing import Dict, Callable, Any, List
import inspect


# 全局函数注册表
function_registry: Dict[str, dict] = {}


def register_function(
    name: str,
    description: str = "",
    category: str = "通用",
    inputs: List[dict] = None,
    outputs: dict = None,
    tags: List[str] = None
):
    """
    函数注册装饰器
    
    设计思路：
    1. 通过装饰器自动注册函数到全局注册表
    2. 记录函数的元数据（描述、输入输出、分类等）
    3. 支持前端动态获取可用函数列表
    
    使用示例：
        @register_function(
            name="extract_field",
            description="提取病历字段",
            category="文本提取",
            inputs=[{"name": "field_name", "type": "str", "desc": "字段名"}],
            outputs={"type": "dict", "desc": "包含result字段"}
        )
        def extract_field(field_name: str, medical_record: dict):
            ...
    
    Args:
        name: 注册名（供规则配置中引用）
        description: 函数功能描述
        category: 分类（如"文本提取"、"逻辑判断"等）
        inputs: 输入参数说明
        outputs: 输出结构说明
        tags: 标签列表
    """
    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = {"type": "dict", "desc": "标准输出结构: {result, evidence, details}"}
    if tags is None:
        tags = []

    def decorator(func: Callable) -> Callable:
        # 验证输入参数定义
        sig = inspect.signature(func)
        param_names = set(sig.parameters.keys())
        input_names = {inp["name"] for inp in inputs}
        
        if not input_names.issubset(param_names):
            missing = input_names - param_names
            raise ValueError(f"函数 {func.__name__} 缺少参数定义: {missing}")

        # 注册函数
        function_registry[name] = {
            "function": func,
            "description": description,
            "category": category,
            "inputs": inputs,
            "outputs": outputs,
            "tags": tags,
            "original_name": func.__name__
        }

        # 也允许通过原始函数名访问
        function_registry[func.__name__] = function_registry[name]

        return func

    return decorator


def get_registered_functions() -> Dict[str, dict]:
    """获取所有已注册的函数"""
    return function_registry.copy()


def get_function_info(name: str) -> dict:
    """获取函数信息"""
    return function_registry.get(name)
