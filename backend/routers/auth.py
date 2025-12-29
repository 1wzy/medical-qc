"""
认证相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from models.user import User, UserStatus
from schemas.user import UserLogin, LoginResponse, UserResponse, TokenData
from utils.auth import verify_password, create_access_token, decode_access_token

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态（status 是字符串值）
    if user.status == UserStatus.INACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    返回token和用户信息
    """
    # 查找用户
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户状态（status 是字符串值）
    if user.status == UserStatus.INACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，无法登录"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 生成token
    # 注意：user.role 和 user.status 已经是字符串值
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role}
    )
    
    # 返回token和用户信息
    return LoginResponse(
        token=access_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            email=user.email,
            role=user.role,  # 已经是字符串值
            status=user.status,  # 已经是字符串值
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    # 注意：role 和 status 已经是字符串值
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        email=current_user.email,
        role=current_user.role,  # 已经是字符串值
        status=current_user.status,  # 已经是字符串值
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )


@router.post("/logout")
def logout():
    """用户登出（前端删除token即可）"""
    return {"message": "登出成功"}

