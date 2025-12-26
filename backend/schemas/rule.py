import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class RuleBase(BaseModel):
    name: str
    module: Optional[str] = None
    description: Optional[str] = None
    type: str = "unknown"
    deduct: int = 0
    fields_name: List[List[str]] = Field(default_factory=list)
    config: Dict[str, Any]  # 完整的 rule_config


class RuleCreate(RuleBase):
    auto_publish: bool = False  # 是否创建后自动发布


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    deduct: Optional[int] = None
    fields_name: Optional[List[List[str]]] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class RuleOut(BaseModel):
    id: int
    name: str
    module: Optional[str]
    description: Optional[str]
    type: str
    deduct: int
    fields_name: List[List[str]]
    config: Dict[str, Any]
    status: str
    version: int

    class Config:
        from_attributes = True

    @field_validator("fields_name", mode="before")
    @classmethod
    def parse_fields_name(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator("config", mode="before")
    @classmethod
    def parse_config(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v or {}


class ExecuteRequest(BaseModel):
    rule_id: int
    medical_record: Dict[str, Any]
    medical_id: Optional[str] = None


class ExecuteResponse(BaseModel):
    rule_id: int
    rule_name: str
    description: str
    module: str
    passed: Optional[bool]
    flag: int
    deduct: int
    answer: Dict[str, Any]
    explanation: str
    type: Optional[str] = None
    fields_name: List[List[str]] = Field(default_factory=list)

