import json
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean

from db import Base


class RuleStatus(str, Enum):
    draft = "draft"
    published = "published"
    offline = "offline"


class Rule(Base):
    __tablename__ = "qc_rule"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    module = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), default="unknown")
    deduct = Column(Integer, default=0)
    fields_name = Column(Text, nullable=True)  # JSON list
    config = Column(Text, nullable=False)  # 完整 rule_config JSON
    status = Column(String(32), default=RuleStatus.draft.value, index=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def config_dict(self):
        try:
            return json.loads(self.config)
        except Exception:
            return {}

    def fields_name_list(self):
        try:
            return json.loads(self.fields_name) if self.fields_name else []
        except Exception:
            return []


class RuleExecutionRecord(Base):
    __tablename__ = "qc_rule_execution_record"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rule_id = Column(Integer, index=True, nullable=False)
    rule_version = Column(Integer, default=1)
    medical_id = Column(String(128), nullable=True)
    passed = Column(Boolean, nullable=True)
    flag = Column(Integer, default=0)  # 1 pass, 0 fail, 2 skipped, -1 error
    deduct = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    explanation = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)  # 证据 JSON
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

