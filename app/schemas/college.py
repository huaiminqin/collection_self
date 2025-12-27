from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CollegeBase(BaseModel):
    """学院基础模式"""
    name: str


class CollegeCreate(CollegeBase):
    """创建学院请求"""
    pass


class CollegeUpdate(BaseModel):
    """更新学院请求"""
    name: Optional[str] = None


class CollegeResponse(CollegeBase):
    """学院响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CollegeWithGrades(CollegeResponse):
    """带年级列表的学院响应"""
    grades: List["GradeResponse"] = []


# 避免循环导入
from app.schemas.grade import GradeResponse
CollegeWithGrades.model_rebuild()
