"""
用户相关的 Schema
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models.user import UserRole, UserStatus


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    real_name: Optional[str]
    email: Optional[str]
    role: str
    status: str
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: UserResponse


class TokenData(BaseModel):
    """Token数据"""
    user_id: int
    username: str
    role: str

