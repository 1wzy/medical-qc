import json
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text

from db import Base


class BatchStatus(str, Enum):
    pending = "pending"  # 待处理
    processing = "processing"  # 处理中
    completed = "completed"  # 已完成
    failed = "failed"  # 失败


class Batch(Base):
    """批次表 - 存储批次质控任务"""
    __tablename__ = "batch"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)  # 批次名称
    description = Column(Text, nullable=True)  # 描述
    rule_ids = Column(Text, nullable=False)  # JSON数组，存储规则ID列表（代替规则集）
    dataset_id = Column(Integer, nullable=False, index=True)  # 数据集ID
    status = Column(String(32), default=BatchStatus.pending.value, index=True)  # 状态
    total_count = Column(Integer, default=0)  # 总数据条数
    processed_count = Column(Integer, default=0)  # 已处理条数
    passed_count = Column(Integer, default=0)  # 通过条数
    failed_count = Column(Integer, default=0)  # 失败条数
    error_message = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def rule_ids_list(self):
        """将JSON字符串转换为ID列表"""
        try:
            return json.loads(self.rule_ids) if self.rule_ids else []
        except Exception:
            return []

