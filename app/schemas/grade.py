from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class GradeBase(BaseModel):
    """年级基础模式"""
    name: str
    college_id: int


class GradeCreate(GradeBase):
    """创建年级请求"""
    pass


class GradeUpdate(BaseModel):
    """更新年级请求"""
    name: Optional[str] = None
    college_id: Optional[int] = None


class GradeResponse(BaseModel):
    """年级响应"""
    id: int
    name: str
    college_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GradeWithClasses(GradeResponse):
    """带班级列表的年级响应"""
    classes: List["ClassResponse"] = []


# 避免循环导入
from app.schemas.class_ import ClassResponse
GradeWithClasses.model_rebuild()
