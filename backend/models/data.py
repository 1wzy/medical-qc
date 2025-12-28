import json
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT

from db import Base


class BasicData(Base):
    """基础数据表 - 存储上传的JSON文件数据"""
    __tablename__ = "basic_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), nullable=False, index=True)
    file_size = Column(Integer, default=0)  # 文件大小（字节）
    data_content = Column(LONGTEXT, nullable=False)  # JSON数据内容（使用LONGTEXT支持大文件）
    data_type = Column(String(50), default="json")  # 数据类型
    description = Column(Text, nullable=True)  # 描述信息
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def data_dict(self):
        """将JSON字符串转换为字典"""
        try:
            return json.loads(self.data_content)
        except Exception:
            return {}


class Dataset(Base):
    """数据集表 - 存储数据集信息"""
    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    data_source = Column(String(50), default="upload")  # upload: 上传文件, select: 从基础数据选择
    data_ids = Column(Text, nullable=True)  # JSON数组，存储关联的基础数据ID列表
    data_count = Column(Integer, default=0)  # 数据条数
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def data_ids_list(self):
        """将JSON字符串转换为ID列表"""
        try:
            return json.loads(self.data_ids) if self.data_ids else []
        except Exception:
            return []

