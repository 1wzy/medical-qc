"""
创建规则集表
"""
from db import Base, engine
from models.rule_set import RuleSet

if __name__ == "__main__":
    print("正在创建规则集表...")
    Base.metadata.create_all(bind=engine, tables=[RuleSet.__table__])
    print("规则集表创建完成！")

