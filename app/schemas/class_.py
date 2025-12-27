from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ClassBase(BaseModel):
    """班级基础模式"""
    name: str
    grade_id: int


class ClassCreate(ClassBase):
    """创建班级请求"""
    pass


class ClassUpdate(BaseModel):
    """更新班级请求"""
    name: Optional[str] = None
    grade_id: Optional[int] = None


class ClassResponse(BaseModel):
    """班级响应"""
    id: int
    name: str
    grade_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClassWithMembers(ClassResponse):
    """带成员列表的班级响应"""
    members: List["MemberResponse"] = []


# 避免循环导入
from app.schemas.member import MemberResponse
ClassWithMembers.model_rebuild()
