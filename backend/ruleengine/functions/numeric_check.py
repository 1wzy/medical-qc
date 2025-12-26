"""
数值检查类函数
包括字符计数、数值范围检查、时间计算等
"""
from ruleengine.registry import register_function
from typing import Dict, Any, Optional
import re


@register_function(
    name="count_characters",
    description="统计文本中的字符数量（支持中文字符计数）",
    category="数值检查",
    inputs=[
        {
            "name": "text",
            "type": "str",
            "desc": "待统计的文本"
        },
        {
            "name": "count_chinese_only",
            "type": "bool",
            "desc": "是否只统计中文字符，默认False（统计所有字符）"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(字符数), evidence(统计详情), details(详细信息)"
    },
    tags=["numeric", "count", "text", "chinese"]
)
def count_characters(text: str, count_chinese_only: bool = False) -> Dict[str, Any]:
    """
    统计文本中的字符数量
    
    Args:
        text: 待统计的文本
        count_chinese_only: 是否只统计中文字符
        
    Returns:
        包含字符数的字典
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    if count_chinese_only:
        # 只统计中文字符（包括中文标点）
        chinese_pattern = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
        matches = re.findall(chinese_pattern, text)
        count = len(matches)
        evidence = {
            "chinese_count": count,
            "total_length": len(text),
            "chinese_chars": "".join(matches[:10]) + ("..." if len(matches) > 10 else "")
        }
    else:
        # 统计所有字符（包括空格）
        count = len(text)
        # 统计中文字符数
        chinese_pattern = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
        chinese_matches = re.findall(chinese_pattern, text)
        chinese_count = len(chinese_matches)
        evidence = {
            "total_count": count,
            "chinese_count": chinese_count,
            "non_chinese_count": count - chinese_count
        }
    
    return {
        "result": count,
        "evidence": evidence,
        "details": {
            "text_length": len(text),
            "count_mode": "chinese_only" if count_chinese_only else "all",
            "count": count
        }
    }


@register_function(
    name="count_chinese_characters",
    description="统计文本中的中文字符数量",
    category="数值检查",
    inputs=[
        {
            "name": "text",
            "type": "str",
            "desc": "待统计的文本"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(中文字符数), evidence(统计详情), details(详细信息)"
    },
    tags=["numeric", "count", "chinese"]
)
def count_chinese_characters(text: str) -> Dict[str, Any]:
    """
    统计文本中的中文字符数量
    
    Args:
        text: 待统计的文本
        
    Returns:
        包含中文字符数的字典
    """
    return count_characters(text, count_chinese_only=True)


@register_function(
    name="is_number_in_range",
    description="检查数值是否在指定范围内",
    category="数值检查",
    inputs=[
        {
            "name": "value",
            "type": "float",
            "desc": "待检查的数值"
        },
        {
            "name": "min_value",
            "type": "float",
            "desc": "最小值（包含）"
        },
        {
            "name": "max_value",
            "type": "float",
            "desc": "最大值（包含）"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(是否在范围内), evidence(范围信息), details(详细信息)"
    },
    tags=["numeric", "range", "validation"]
)
def is_number_in_range(value: float, min_value: float, max_value: float) -> Dict[str, Any]:
    """
    检查数值是否在指定范围内
    
    Args:
        value: 待检查的数值
        min_value: 最小值（包含）
        max_value: 最大值（包含）
        
    Returns:
        包含检查结果的字典
    """
    try:
        value_float = float(value)
        min_float = float(min_value)
        max_float = float(max_value)
        
        in_range = min_float <= value_float <= max_float
        
        return {
            "result": in_range,
            "evidence": {
                "value": value_float,
                "range": f"[{min_float}, {max_float}]",
                "in_range": in_range
            },
            "details": {
                "value": value_float,
                "min": min_float,
                "max": max_float,
                "in_range": in_range
            }
        }
    except (ValueError, TypeError) as e:
        return {
            "result": False,
            "evidence": {
                "error": f"无法转换为数值: {str(e)}"
            },
            "details": {
                "error": str(e),
                "value": value
            }
        }

