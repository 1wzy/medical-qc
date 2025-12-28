from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class BatchBase(BaseModel):
    name: str = Field(..., description="批次名称")
    description: Optional[str] = Field(None, description="描述")
    rule_ids: List[int] = Field(default_factory=list, description="规则ID列表")
    rule_set_id: Optional[int] = Field(None, description="规则集ID（如果提供，将使用规则集中的规则）")
    dataset_id: int = Field(..., description="数据集ID")


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_ids: Optional[List[int]] = None
    status: Optional[str] = None
    total_count: Optional[int] = None
    processed_count: Optional[int] = None
    passed_count: Optional[int] = None
    failed_count: Optional[int] = None
    error_message: Optional[str] = None


class BatchOut(BatchBase):
    id: int
    status: str
    total_count: int
    processed_count: int
    passed_count: int
    failed_count: int
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v


class BatchListResponse(BaseModel):
    items: List[BatchOut]
    total: int
    skip: int
    limit: int


class BatchExecuteRequest(BaseModel):
    """批次执行请求"""
    batch_id: int


class RuleExecutionResult(BaseModel):
    """规则执行结果"""
    rule_id: int
    rule_name: str
    passed: bool
    flag: int
    deduct: int
    explanation: Optional[str] = None
    answer: Optional[dict] = None
    error: Optional[str] = None
    duration_ms: int
    created_at: str


class DataItemExecutionResult(BaseModel):
    """数据项执行结果"""
    data_id: int
    file_name: str
    file_size: int
    overall_passed: bool  # 所有规则是否都通过
    rule_results: List[RuleExecutionResult]  # 每个规则的执行结果
    total_deduct: int  # 总扣分


class BatchExecutionDetail(BaseModel):
    """批次执行详情"""
    batch_id: int
    batch_name: str
    dataset_id: int
    dataset_name: str
    rule_ids: List[int]
    rule_names: List[str]
    status: str
    total_count: int
    processed_count: int
    passed_count: int
    failed_count: int
    data_results: List[DataItemExecutionResult]  # 每个数据项的执行结果
