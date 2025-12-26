"""
规则开发工具（命令行版本）
用于编写、测试规则，测试通过后生成导入用的JSON
"""
import json
from ruleengine.core.engine import RuleEngine
from ruleengine.registry import get_registered_functions


def print_available_functions():
    """打印所有可用的函数"""
    print("\n" + "=" * 60)
    print("可用的原子函数：")
    print("=" * 60)
    
    functions = get_registered_functions()
    by_category = {}
    
    for name, info in functions.items():
        if name.startswith("_"):
            continue
        category = info.get("category", "未分类")
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((name, info))
    
    for category, funcs in sorted(by_category.items()):
        print(f"\n【{category}】")
        for name, info in funcs:
            print(f"  - {name}")
            print(f"    描述: {info.get('description', '无')}")
            inputs = info.get("inputs", [])
            if inputs:
                print(f"    输入: {', '.join([inp.get('name', '') for inp in inputs])}")


def test_rule(rule_config_path: str, medical_record_path: str = None):
    """
    测试规则配置
    
    Args:
        rule_config_path: 规则配置JSON文件路径
        medical_record_path: 测试病历JSON文件路径（可选）
    """
    # 读取规则配置
    try:
        with open(rule_config_path, 'r', encoding='utf-8') as f:
            rule_config = json.load(f)
    except Exception as e:
        print(f"❌ 读取规则配置失败: {e}")
        return False
    
    # 读取测试病历
    if medical_record_path:
        try:
            with open(medical_record_path, 'r', encoding='utf-8') as f:
                medical_record = json.load(f)
        except Exception as e:
            print(f"❌ 读取测试病历失败: {e}")
            return False
    else:
        # 使用默认测试病历
        medical_record = {
            "入院记录": {
                "主诉": "患者因头痛3天入院",
                "现病史": "患者3天前无明显诱因出现头痛，呈持续性胀痛"
            }
        }
        print("⚠️  使用默认测试病历")
    
    # 执行测试
    print("\n" + "=" * 60)
    print("开始测试规则...")
    print("=" * 60)
    
    try:
        engine = RuleEngine(rule_config)
        result = engine.execute(medical_record)
        
        print(f"\n✅ 规则执行成功")
        print(f"规则ID: {result.get('rule_id')}")
        print(f"规则名称: {result.get('rule_name')}")
        print(f"是否通过: {result.get('passed')}")
        print(f"状态标志: {result.get('flag')} (1=通过, 0=不通过, -1=错误)")
        print(f"解释: {result.get('explanation')}")
        print(f"执行耗时: {result.get('duration_ms', 0)}ms")
        print(f"\n证据数据:")
        print(json.dumps(result.get('answer', {}), ensure_ascii=False, indent=2))
        
        if result.get('flag') == -1:
            print("\n❌ 规则执行出错！")
            return False
        else:
            print("\n✅ 规则测试通过！")
            return True
            
    except Exception as e:
        print(f"\n❌ 规则执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_import_json(rule_config_path: str, output_path: str = None):
    """
    生成导入用的JSON（用于API调用）
    
    Args:
        rule_config_path: 规则配置JSON文件路径
        output_path: 输出文件路径（可选，默认输出到控制台）
    """
    # 读取规则配置
    try:
        with open(rule_config_path, 'r', encoding='utf-8') as f:
            rule_config = json.load(f)
    except Exception as e:
        print(f"❌ 读取规则配置失败: {e}")
        return
    
    # 生成导入JSON
    import_data = {
        "name": rule_config.get("rule_name", "未命名规则"),
        "module": rule_config.get("module", ""),
        "description": rule_config.get("description", ""),
        "type": rule_config.get("type", "unknown"),
        "deduct": rule_config.get("deduct", 0),
        "fields_name": rule_config.get("fields_name", []),
        "config": rule_config
    }
    
    output_json = json.dumps(import_data, ensure_ascii=False, indent=2)
    
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"✅ 导入JSON已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    else:
        print("\n" + "=" * 60)
        print("导入用的JSON（复制到 Swagger UI 的 POST /api/rules/ 接口）:")
        print("=" * 60)
        print(output_json)


def create_rule_template(output_path: str = "rule_template.json"):
    """创建规则模板"""
    template = {
        "rule_id": "规则唯一标识_001",
        "rule_name": "规则名称",
        "module": "所属模块",
        "description": "规则描述",
        "type": "规则类型",
        "fields_name": [
            ["section", "field"]
        ],
        "function_list": {
            "nodes": [
                {
                    "id": 1,
                    "function": "extract_field_content",
                    "params": {
                        "field_name": ["section", "field"]
                    },
                    "outputs": {
                        "text": "result",
                        "is_empty": "is_empty"
                    }
                }
            ],
            "result_rule": {
                "pass": {
                    "source": 1,
                    "output": "is_empty",
                    "expect": false
                }
            },
            "explanation_template": {
                "pass": "通过说明",
                "fail": "不通过说明"
            }
        },
        "deduct": 10
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"✅ 规则模板已创建: {output_path}")
    except Exception as e:
        print(f"❌ 创建模板失败: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("规则开发工具")
        print("\n用法:")
        print("  python rule_dev_tool.py list                    # 列出所有可用函数")
        print("  python rule_dev_tool.py template [output.json]  # 创建规则模板")
        print("  python rule_dev_tool.py test <rule.json> [medical.json]  # 测试规则")
        print("  python rule_dev_tool.py import <rule.json> [output.json]  # 生成导入JSON")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        print_available_functions()
    elif command == "template":
        output = sys.argv[2] if len(sys.argv) > 2 else "rule_template.json"
        create_rule_template(output)
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请提供规则配置文件路径")
            sys.exit(1)
        rule_file = sys.argv[2]
        medical_file = sys.argv[3] if len(sys.argv) > 3 else None
        test_rule(rule_file, medical_file)
    elif command == "import":
        if len(sys.argv) < 3:
            print("❌ 请提供规则配置文件路径")
            sys.exit(1)
        rule_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        generate_import_json(rule_file, output_file)
    else:
        print(f"❌ 未知命令: {command}")

