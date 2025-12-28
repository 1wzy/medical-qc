import json
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text

from db import Base


class RuleSetStatus(str, Enum):
    active = "active"  # 启用
    inactive = "inactive"  # 禁用


class RuleSet(Base):
    """规则集表 - 存储规则集信息"""
    __tablename__ = "rule_set"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)  # 规则集名称
    description = Column(Text, nullable=True)  # 描述
    rule_ids = Column(Text, nullable=True)  # JSON数组，存储规则ID列表
    status = Column(String(32), default=RuleSetStatus.active.value, index=True)  # 状态
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def rule_ids_list(self):
        """将JSON字符串转换为ID列表"""
        try:
            return json.loads(self.rule_ids) if self.rule_ids else []
        except Exception:
            return []

