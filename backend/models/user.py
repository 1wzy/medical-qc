"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

from db import Base


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"      # 激活
    INACTIVE = "inactive"  # 禁用


class User(Base):
    """用户表"""
    __tablename__ = "qc_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    email = Column(String(100), nullable=True, comment="邮箱")
    role = Column(String(32), default=UserRole.USER.value, nullable=False, index=True, comment="角色")
    status = Column(String(32), default=UserStatus.ACTIVE.value, nullable=False, index=True, comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"

