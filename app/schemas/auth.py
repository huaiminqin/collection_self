from pydantic import BaseModel
from typing import Optional


class AdminSetup(BaseModel):
    """管理员初始设置"""
    username: str
    password: str


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"


class AdminResponse(BaseModel):
    """管理员响应"""
    id: int
    username: str
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Token数据"""
    username: Optional[str] = None
