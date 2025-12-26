"""
正则工具函数
用于从LLM返回的文本中提取结构化信息
"""
import re


def regex_conclusion(text: str) -> Optional[str]:
    """
    提取 <conclusion> 标签中的内容
    
    Args:
        text: 待解析的文本
        
    Returns:
        结论文本，如果未找到则返回None
    """
    matches = re.findall(r"<conclusion>(.*?)</conclusion>", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None


def regex_reason(text: str) -> Optional[str]:
    """
    提取 <reason> 标签中的内容
    
    Args:
        text: 待解析的文本
        
    Returns:
        原因文本，如果未找到则返回None
    """
    matches = re.findall(r"<reason>(.*?)</reason>", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None


def regex_thinking(text: str) -> Optional[str]:
    """
    提取 <thinking> 标签中的内容
    
    Args:
        text: 待解析的文本
        
    Returns:
        思考过程文本，如果未找到则返回None
    """
    matches = re.findall(r"<thinking>(.*?)</thinking>", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None


def regex_content(text: str) -> Optional[str]:
    """
    提取 <content> 标签中的内容
    
    Args:
        text: 待解析的文本
        
    Returns:
        内容文本，如果未找到则返回None
    """
    matches = re.findall(r"<content>(.*?)</content>", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None


def regex_times(text: str) -> Optional[str]:
    """
    提取 <times> 标签中的内容
    
    Args:
        text: 待解析的文本
        
    Returns:
        时间信息文本，如果未找到则返回None
    """
    matches = re.findall(r"<times>(.*?)</times>", text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None

