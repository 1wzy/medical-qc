"""
创建批次表的脚本
如果表已存在，不会报错
"""
from db import Base, engine
import models  # 确保所有模型被导入

print("正在创建数据库表...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")
    
    # 检查批次表是否存在
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'batch' in tables:
        print("✓ 批次表 (batch) 已存在")
        # 显示表结构
        columns = inspector.get_columns('batch')
        print(f"  表包含 {len(columns)} 个字段:")
        for col in columns:
            print(f"    - {col['name']}: {col['type']}")
    else:
        print("⚠ 批次表 (batch) 不存在，但创建过程没有报错")
        print(f"  当前数据库中的表: {', '.join(tables)}")
        
except Exception as e:
    print(f"✗ 创建表时出错: {e}")
    import traceback
    traceback.print_exc()

