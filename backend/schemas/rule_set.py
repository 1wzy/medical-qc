from typing import List, Optional
from pydantic import BaseModel


class RuleSetBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_ids: Optional[List[int]] = None
    status: str = "active"


class RuleSetCreate(RuleSetBase):
    pass


class RuleSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_ids: Optional[List[int]] = None
    status: Optional[str] = None


class RuleSetOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rule_ids: List[int]
    status: str
    rule_count: int  # 规则数量（计算字段）
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RuleSetListResponse(BaseModel):
    total: int
    items: List[RuleSetOut]

