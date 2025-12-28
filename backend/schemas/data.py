from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import json


class BasicDataBase(BaseModel):
    file_name: str
    description: Optional[str] = None


class BasicDataCreate(BasicDataBase):
    data_content: Dict[str, Any]  # JSON数据内容
    file_size: Optional[int] = 0


class BasicDataUpdate(BaseModel):
    file_name: Optional[str] = None
    description: Optional[str] = None
    data_content: Optional[Dict[str, Any]] = None


class BasicDataOut(BaseModel):
    id: int
    file_name: str
    file_size: int
    data_content: Dict[str, Any]
    data_type: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @field_validator("data_content", mode="before")
    @classmethod
    def parse_data_content(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v or {}

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if v:
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return ""


# 列表项响应模型（不包含完整JSON内容）
class BasicDataListItem(BaseModel):
    id: int
    file_name: str
    file_size: int
    data_content: Dict[str, Any] = Field(default_factory=dict)  # 列表视图为空对象
    data_type: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if v:
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return ""


class BasicDataListResponse(BaseModel):
    items: List[BasicDataListItem]
    total: int
    skip: int
    limit: int


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_source: str = "upload"  # upload 或 select


class DatasetCreate(DatasetBase):
    data_ids: Optional[List[int]] = None  # 从基础数据选择时的ID列表
    data_content: Optional[Dict[str, Any]] = None  # 直接上传时的JSON数据


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_ids: Optional[List[int]] = None
    data_content: Optional[Dict[str, Any]] = None


class DatasetOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    data_source: str
    data_ids: List[int]
    data_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @field_validator("data_ids", mode="before")
    @classmethod
    def parse_data_ids(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if v:
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return ""


class DatasetListResponse(BaseModel):
    items: List[DatasetOut]
    total: int
    skip: int
    limit: int


class DatasetDetailOut(DatasetOut):
    """数据集详情，包含关联的基础数据信息"""
    basic_data_list: Optional[List[BasicDataOut]] = None
