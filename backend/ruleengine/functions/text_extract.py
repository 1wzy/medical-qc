"""
文本提取类函数
包括字段提取、内容抽取等
"""
from ruleengine.registry import register_function
from typing import List, Dict, Any, Optional


@register_function(
    name="extract_field_content",
    description="从病历中提取指定字段的文本内容（支持二级嵌套结构；若 field 为空，则返回整个 section 内容）",
    category="文本提取",
    inputs=[
        {
            "name": "field_name",
            "type": "list[str]",
            "desc": "要提取的字段路径，格式为 [section, field]。若 field 为空字符串 ''，则返回该 section 下全部内容"
        },
        {
            "name": "medical_record",
            "type": "dict",
            "desc": "完整的病历数据字典，可能包含嵌套结构"
        }
    ],
    outputs={
        "type": "dict",
        "desc": "包含 result(文本), is_empty(是否为空), evidence(证据), details(详情)"
    },
    tags=["text", "extract", "field", "nested"]
)
def extract_field_content(field_name: List[str], medical_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    从病历中提取字段内容
    
    支持从二级嵌套的病历字典中提取字段内容。
    field_name 应为长度为2的字符串列表: [section, field]
    如果 field 为空字符串 ''，则返回该 section 的全部内容（合并为文本或原字典）
    """
    # 参数校验
    if not isinstance(field_name, list) or len(field_name) != 2:
        raise ValueError("field_name must be a list of two strings: [section, field]")
    
    section, field = field_name
    text = ""
    is_empty = True
    found = False
    details_data = {"section": section, "field": field}

    try:
        if section in medical_record and isinstance(medical_record[section], dict):
            if field == "":
                # 特殊情况：field 为空，返回整个 section 的内容
                section_dict = medical_record[section]
                if section_dict:
                    # 将字典的所有 value 转为字符串并拼接（保留原始结构信息）
                    lines = []
                    for k, v in section_dict.items():
                        v_str = str(v).strip() if isinstance(v, str) else repr(v)
                        lines.append(f"{k}: {v_str}")
                    text = "\n".join(lines)
                    is_empty = False
                else:
                    text = ""
                    is_empty = True
                found = True
                details_data["extract_mode"] = "full_section"
            else:
                # 正常提取二级字段
                if field in medical_record[section]:
                    raw_value = medical_record[section][field]
                    if isinstance(raw_value, str):
                        text = raw_value.strip()
                    else:
                        text = str(raw_value).strip()
                    is_empty = text == ""
                    found = True
                    details_data["extract_mode"] = "specific_field"
    except Exception as e:
        text = ""
        is_empty = True
        found = False
        details_data["error"] = str(e)

    if text == "":
        is_empty = True
        found = False
    else:
        text = ".".join(field_name) + ">>>" + text + "\n"
    
    return {
        "result": text,
        "is_empty": is_empty,
        "evidence": {"raw_text": text},
        "details": {
            **details_data,
            "found": found
        }
    }

