"""
规则引擎测试脚本
用于快速测试引擎是否正常工作
"""
# 先导入函数模块，确保装饰器执行（函数注册）
from ruleengine import functions

from ruleengine.core.engine import RuleEngine
from ruleengine.registry import get_registered_functions


def test_engine():
    """测试规则引擎基本功能"""
    
    print("=" * 50)
    print("规则引擎测试")
    print("=" * 50)
    
    # 1. 检查函数注册
    print("\n1. 检查已注册的函数...")
    functions = get_registered_functions()
    print(f"   已注册函数数量: {len(functions)}")
    for name, info in functions.items():
        if not name.startswith("_"):  # 跳过内部函数
            print(f"   - {name}: {info.get('description', '无描述')}")
    
    if len(functions) == 0:
        print("   ⚠️ 警告：没有注册任何函数！")
        return False
    
    # 2. 创建测试规则配置
    print("\n2. 创建测试规则配置...")
    test_rule_config = {
        "rule_id": "test_001",
        "rule_name": "测试规则-字段提取",
        "module": "test",
        "description": "测试从病历中提取字段",
        "type": "test",
        "fields_name": [["测试", "字段"]],
        "function_list": {
            "nodes": [
                {
                    "id": 1,
                    "function": "extract_field_content",
                    "params": {
                        "field_name": ["入院记录", "主诉"]
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
                    "expect": False  # 期望字段不为空
                }
            },
            "explanation_template": {
                "pass": "字段存在且不为空",
                "fail": "字段为空或不存在"
            }
        },
        "deduct": 0
    }
    print("   ✓ 规则配置创建成功")
    
    # 3. 创建测试病历数据
    print("\n3. 创建测试病历数据...")
    test_medical_record = {
        "入院记录": {
            "主诉": "患者因头痛3天入院",
            "现病史": "患者3天前无明显诱因出现头痛..."
        }
    }
    print("   ✓ 测试病历创建成功")
    
    # 4. 执行规则
    print("\n4. 执行规则...")
    try:
        engine = RuleEngine(test_rule_config)
        result = engine.execute(test_medical_record)
        
        print("   ✓ 规则执行成功")
        print(f"\n   执行结果:")
        print(f"   - 规则ID: {result.get('rule_id')}")
        print(f"   - 规则名称: {result.get('rule_name')}")
        print(f"   - 是否通过: {result.get('passed')}")
        print(f"   - 状态标志: {result.get('flag')}")
        print(f"   - 解释: {result.get('explanation')}")
        print(f"   - 执行耗时: {result.get('duration_ms', 0)}ms")
        print(f"   - 证据: {result.get('answer', {})}")
        
        if result.get('flag') == -1:
            print("\n   ❌ 执行出错！")
            return False
        else:
            print("\n   ✅ 引擎工作正常！")
            return True
            
    except Exception as e:
        print(f"   ❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_field():
    """测试空字段场景"""
    print("\n" + "=" * 50)
    print("测试空字段场景")
    print("=" * 50)
    
    test_rule_config = {
        "rule_id": "test_002",
        "rule_name": "测试规则-空字段",
        "module": "test",
        "description": "测试空字段处理",
        "type": "test",
        "fields_name": [],
        "function_list": {
            "nodes": [
                {
                    "id": 1,
                    "function": "extract_field_content",
                    "params": {
                        "field_name": ["入院记录", "主诉"]
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
                    "expect": False
                }
            },
            "explanation_template": {
                "pass": "字段存在",
                "fail": "字段为空"
            }
        },
        "deduct": 0
    }
    
    # 空字段的病历
    test_medical_record = {
        "入院记录": {
            "主诉": "",  # 空字段
            "现病史": "患者..."
        }
    }
    
    try:
        engine = RuleEngine(test_rule_config)
        result = engine.execute(test_medical_record)
        
        print(f"\n   执行结果:")
        print(f"   - 是否通过: {result.get('passed')}")
        print(f"   - 解释: {result.get('explanation')}")
        print(f"   ✅ 空字段测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n开始测试规则引擎...\n")
    
    # 基本功能测试
    success1 = test_engine()
    
    # 空字段测试
    success2 = test_empty_field()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ 所有测试通过！引擎工作正常。")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    print("=" * 50)

