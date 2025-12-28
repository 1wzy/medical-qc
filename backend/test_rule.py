"""
测试规则执行
"""
import json
from db import SessionLocal
from models.rule import Rule
from ruleengine.core.engine import RuleEngine

# 导入规则引擎函数库，确保装饰器执行（函数注册）
from ruleengine import functions  # 这会触发所有函数的注册

# 测试用的病历数据
test_medical_record = {
    "入院记录": {
        "主诉": "患者因头痛、发热3天入院"
    }
}

def test_rule_by_id(rule_id: int):
    """根据规则ID测试规则"""
    db = SessionLocal()
    try:
        # 获取规则
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            print(f"❌ 规则 ID {rule_id} 不存在")
            return
        
        print(f"📋 规则信息:")
        print(f"   ID: {rule.id}")
        print(f"   名称: {rule.name}")
        print(f"   状态: {rule.status}")
        print(f"   描述: {rule.description}")
        print()
        
        if rule.status != "published":
            print(f"⚠️  警告: 规则状态为 '{rule.status}'，建议使用已发布的规则")
            print()
        
        # 获取规则配置
        rule_config = rule.config_dict()
        
        # 创建规则引擎
        engine = RuleEngine(rule_config)
        
        # 执行规则
        print("🔍 执行规则...")
        print(f"📝 测试病历数据: {json.dumps(test_medical_record, ensure_ascii=False, indent=2)}")
        print()
        
        result = engine.execute(test_medical_record)
        
        # 显示结果
        print("=" * 80)
        print("📊 执行结果:")
        print("=" * 80)
        print(f"规则ID: {result.get('rule_id')}")
        print(f"规则名称: {result.get('rule_name')}")
        print(f"是否通过: {'✅ 通过' if result.get('passed') else '❌ 不通过'}")
        print(f"状态标志: {result.get('flag')} (1=通过, 0=不通过, 2=跳过, -1=错误)")
        print(f"扣分: {result.get('deduct')}")
        print(f"执行耗时: {result.get('duration_ms')}ms")
        print()
        print(f"解释说明:")
        print(f"  {result.get('explanation')}")
        print()
        
        if result.get('answer'):
            print(f"证据数据:")
            print(json.dumps(result.get('answer'), ensure_ascii=False, indent=2))
            print()
        
        if result.get('flag') == -1:
            print("❌ 执行出错！")
            error_info = result.get('answer', {}).get('error', '未知错误')
            print(f"错误信息: {error_info}")
        elif result.get('passed'):
            print("✅ 规则执行成功，测试通过！")
        else:
            print("⚠️  规则执行成功，但测试不通过（这是正常的，取决于测试数据）")
        
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_rule_by_config(rule_config_path: str):
    """根据规则配置文件测试规则"""
    try:
        with open(rule_config_path, 'r', encoding='utf-8') as f:
            rule_config = json.load(f)
        
        print(f"📋 从配置文件加载规则: {rule_config_path}")
        print(f"   规则ID: {rule_config.get('rule_id')}")
        print(f"   规则名称: {rule_config.get('rule_name')}")
        print()
        
        # 创建规则引擎
        engine = RuleEngine(rule_config)
        
        # 执行规则
        print("🔍 执行规则...")
        print(f"📝 测试病历数据: {json.dumps(test_medical_record, ensure_ascii=False, indent=2)}")
        print()
        
        result = engine.execute(test_medical_record)
        
        # 显示结果
        print("=" * 80)
        print("📊 执行结果:")
        print("=" * 80)
        print(f"规则ID: {result.get('rule_id')}")
        print(f"规则名称: {result.get('rule_name')}")
        print(f"是否通过: {'✅ 通过' if result.get('passed') else '❌ 不通过'}")
        print(f"状态标志: {result.get('flag')} (1=通过, 0=不通过, 2=跳过, -1=错误)")
        print(f"扣分: {result.get('deduct')}")
        print(f"执行耗时: {result.get('duration_ms')}ms")
        print()
        print(f"解释说明:")
        print(f"  {result.get('explanation')}")
        print()
        
        if result.get('answer'):
            print(f"证据数据:")
            print(json.dumps(result.get('answer'), ensure_ascii=False, indent=2))
            print()
        
        if result.get('flag') == -1:
            print("❌ 执行出错！")
            error_info = result.get('answer', {}).get('error', '未知错误')
            print(f"错误信息: {error_info}")
        elif result.get('passed'):
            print("✅ 规则执行成功，测试通过！")
        else:
            print("⚠️  规则执行成功，但测试不通过（这是正常的，取决于测试数据）")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {rule_config_path}")
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()

def list_rules():
    """列出所有规则"""
    db = SessionLocal()
    try:
        rules = db.query(Rule).order_by(Rule.id.desc()).all()
        print(f"📋 数据库中的规则列表 (共 {len(rules)} 条):")
        print()
        for rule in rules:
            print(f"  ID: {rule.id} | 名称: {rule.name} | 状态: {rule.status}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  测试数据库中的规则: python test_rule.py <rule_id>")
        print("  测试配置文件中的规则: python test_rule.py --file <config_file_path>")
        print("  列出所有规则: python test_rule.py --list")
        print()
        print("示例:")
        print("  python test_rule.py 12")
        print("  python test_rule.py --file rule_config_主诉长度检查.json")
        print("  python test_rule.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_rules()
    elif sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("❌ 请指定配置文件路径")
            sys.exit(1)
        test_rule_by_config(sys.argv[2])
    else:
        try:
            rule_id = int(sys.argv[1])
            test_rule_by_id(rule_id)
        except ValueError:
            print(f"❌ 无效的规则ID: {sys.argv[1]}")
            sys.exit(1)

