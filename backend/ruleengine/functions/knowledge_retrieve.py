"""
知识检索类函数
从知识库中检索相关质控规范、标准等信息
"""
import sys
from pathlib import Path
from ruleengine.registry import register_function
from typing import Dict, Any, Optional, List

# 添加项目根目录到路径，以便导入 knowledge 模块
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from knowledge.knowledge_retriever import get_retriever
    KNOWLEDGE_AVAILABLE = True
except ImportError as e:
    KNOWLEDGE_AVAILABLE = False
    print(f"⚠️  知识库模块导入失败: {e}")


def _extract_department(medical_record: Dict[str, Any]) -> Optional[str]:
    """
    从病历中提取科室信息
    
    Args:
        medical_record: 病历数据字典
        
    Returns:
        科室名称，如果未找到则返回 None
    """
    # 尝试多种可能的字段名
    department_fields = [
        "入院科别",
        "admission_dept",
        "出院科别",
        "discharge_dept",
        "科室",
        "department",
        "科别",
        "dept"
    ]
    
    # 先尝试从基本信息中获取
    if "基本信息" in medical_record:
        basic_info = medical_record["基本信息"]
        if isinstance(basic_info, dict):
            for field in department_fields:
                if field in basic_info:
                    dept = basic_info[field]
                    if dept and isinstance(dept, str) and dept.strip():
                        return dept.strip()
    
    # 尝试从根级别获取
    for field in department_fields:
        if field in medical_record:
            dept = medical_record[field]
            if dept and isinstance(dept, str) and dept.strip():
                return dept.strip()
    
    return None


@register_function(
    name="retrieve_knowledge",
    description="从知识库中检索与查询相关的质控规范、标准等信息（自动从病历中提取科室信息）",
    category="知识检索",
    inputs=[
        {
            "name": "query",
            "type": "str",
            "desc": "查询文本，例如：'病历书写规范'、'用药规范'等"
        },
        {
            "name": "medical_record",
            "type": "dict",
            "desc": "完整的病历数据字典，用于自动提取科室信息"
        },
        {
            "name": "department",
            "type": "str",
            "desc": "可选，手动指定科室名称（如：'产科'、'内科'）。如果不提供，将从病历中自动提取"
        },
        {
            "name": "top_k",
            "type": "int",
            "desc": "可选，返回结果数量，默认3条"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(检索到的知识文本列表), evidence(检索详情), details(详细信息)"
    },
    tags=["knowledge", "retrieve", "search", "department"]
)
def retrieve_knowledge(
    query: str,
    medical_record: Dict[str, Any],
    department: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    从知识库中检索相关信息
    
    Args:
        query: 查询文本
        medical_record: 病历数据字典
        department: 科室名称（可选，如果不提供则从病历中提取）
        top_k: 返回结果数量
        
    Returns:
        包含检索结果的字典
    """
    if not KNOWLEDGE_AVAILABLE:
        return {
            "result": [],
            "evidence": {
                "error": "知识库模块未可用，请检查 knowledge 模块是否正确安装"
            },
            "details": {
                "query": query,
                "department": department,
                "error": "知识库模块未可用"
            }
        }
    
    try:
        # 1. 确定科室
        if not department:
            department = _extract_department(medical_record)
        
        if not department:
            return {
                "result": [],
                "evidence": {
                    "error": "无法从病历中提取科室信息，请手动指定 department 参数"
                },
                "details": {
                    "query": query,
                    "department": None,
                    "error": "科室信息未找到"
                }
            }
        
        # 2. 执行检索
        retriever = get_retriever()
        results = retriever.retrieve_by_department(
            query=query,
            department_name=department,
            top_k=top_k
        )
        
        # 3. 格式化结果
        knowledge_texts = []
        evidence_items = []
        
        for idx, item in enumerate(results, 1):
            content = item.get("content", "")
            similarity = item.get("similarity", 0)
            metadata = item.get("metadata", {})
            
            knowledge_texts.append(content)
            evidence_items.append({
                "rank": idx,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "similarity": round(similarity, 3),
                "metadata": metadata
            })
        
        # 合并所有知识文本
        combined_text = "\n\n".join(knowledge_texts)
        
        return {
            "result": knowledge_texts if knowledge_texts else [],
            "evidence": {
                "query": query,
                "department": department,
                "result_count": len(results),
                "results": evidence_items,
                "combined_text": combined_text[:500] + "..." if len(combined_text) > 500 else combined_text
            },
            "details": {
                "query": query,
                "department": department,
                "top_k": top_k,
                "result_count": len(results),
                "has_results": len(results) > 0
            }
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        
        return {
            "result": [],
            "evidence": {
                "error": f"知识检索失败: {error_msg}",
                "query": query,
                "department": department
            },
            "details": {
                "query": query,
                "department": department,
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
        }


@register_function(
    name="retrieve_knowledge_by_department",
    description="从指定科室的知识库中检索相关信息（需要明确指定科室）",
    category="知识检索",
    inputs=[
        {
            "name": "query",
            "type": "str",
            "desc": "查询文本"
        },
        {
            "name": "department",
            "type": "str",
            "desc": "科室名称，例如：'产科'、'内科'、'外科'等"
        },
        {
            "name": "top_k",
            "type": "int",
            "desc": "可选，返回结果数量，默认3条"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(检索到的知识文本列表), evidence(检索详情), details(详细信息)"
    },
    tags=["knowledge", "retrieve", "search", "department"]
)
def retrieve_knowledge_by_department(
    query: str,
    department: str,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    从指定科室的知识库中检索相关信息
    
    Args:
        query: 查询文本
        department: 科室名称
        top_k: 返回结果数量
        
    Returns:
        包含检索结果的字典
    """
    if not KNOWLEDGE_AVAILABLE:
        return {
            "result": [],
            "evidence": {
                "error": "知识库模块未可用，请检查 knowledge 模块是否正确安装"
            },
            "details": {
                "query": query,
                "department": department,
                "error": "知识库模块未可用"
            }
        }
    
    try:
        # 执行检索
        retriever = get_retriever()
        results = retriever.retrieve_by_department(
            query=query,
            department_name=department,
            top_k=top_k
        )
        
        # 格式化结果
        knowledge_texts = []
        evidence_items = []
        
        for idx, item in enumerate(results, 1):
            content = item.get("content", "")
            similarity = item.get("similarity", 0)
            metadata = item.get("metadata", {})
            
            knowledge_texts.append(content)
            evidence_items.append({
                "rank": idx,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "similarity": round(similarity, 3),
                "metadata": metadata
            })
        
        # 合并所有知识文本
        combined_text = "\n\n".join(knowledge_texts)
        
        return {
            "result": knowledge_texts if knowledge_texts else [],
            "evidence": {
                "query": query,
                "department": department,
                "result_count": len(results),
                "results": evidence_items,
                "combined_text": combined_text[:500] + "..." if len(combined_text) > 500 else combined_text
            },
            "details": {
                "query": query,
                "department": department,
                "top_k": top_k,
                "result_count": len(results),
                "has_results": len(results) > 0
            }
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        
        return {
            "result": [],
            "evidence": {
                "error": f"知识检索失败: {error_msg}",
                "query": query,
                "department": department
            },
            "details": {
                "query": query,
                "department": department,
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
        }

