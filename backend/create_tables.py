"""
手动创建数据库表脚本
用于确保所有表（包括用户表）都被正确创建
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from db import Base, engine
# 导入所有模型，确保它们被注册到 Base.metadata
from models import (
    Rule,
    RuleExecutionRecord,
    BasicData,
    Dataset,
    Batch,
    RuleSet,
    User,  # 确保用户模型被导入
)

def create_all_tables():
    """创建所有数据库表"""
    try:
        print("正在创建数据库表...")
        print(f"数据库连接: {engine.url}")
        print()
        
        # 列出所有要创建的表
        tables = list(Base.metadata.tables.keys())
        print(f"将创建以下表 ({len(tables)} 个):")
        for table_name in sorted(tables):
            print(f"  - {table_name}")
        print()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建成功！")
        print()
        print("已创建的表:")
        for table_name in sorted(tables):
            print(f"  ✓ {table_name}")
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_all_tables()




