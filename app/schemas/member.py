from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class MemberBase(BaseModel):
    """成员基础模式"""
    student_id: str
    name: str
    gender: Optional[str] = None
    dormitory: Optional[str] = None
    qq_email: Optional[str] = None


class MemberCreate(MemberBase):
    """创建成员请求"""
    class_id: int


class MemberUpdate(BaseModel):
    """更新成员请求"""
    student_id: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    dormitory: Optional[str] = None
    qq_email: Optional[str] = None
    class_id: Optional[int] = None


class MemberResponse(BaseModel):
    """成员响应"""
    id: int
    student_id: str
    name: str
    gender: Optional[str]
    dormitory: Optional[str]
    qq_email: Optional[str]
    class_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemberImportItem(BaseModel):
    """导入成员项"""
    student_id: str
    name: str
    gender: Optional[str] = None
    dormitory: Optional[str] = None
    qq_email: Optional[str] = None


class MemberImportResult(BaseModel):
    """导入结果"""
    success_count: int
    skip_count: int
    error_count: int
    errors: list[str] = []


class MemberWithSubmissionStatus(MemberResponse):
    """带提交状态的成员响应"""
    has_submitted: bool = False
    submission_count: int = 0
