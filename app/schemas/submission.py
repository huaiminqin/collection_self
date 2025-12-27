from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class SubmissionBase(BaseModel):
    """提交基础模式"""
    task_id: int
    member_id: int


class SubmissionCreate(SubmissionBase):
    """创建提交请求"""
    submission_type: str = "file"  # file, text, image, questionnaire
    text_content: Optional[str] = None
    questionnaire_answers: Optional[Dict[str, Any]] = None
    is_private: bool = False
    item_index: int = 1


class TextSubmissionCreate(BaseModel):
    """文本提交请求"""
    task_id: int
    member_id: int
    text_content: str
    is_private: bool = False
    item_index: int = 1


class QuestionnaireSubmissionCreate(BaseModel):
    """问卷提交请求"""
    task_id: int
    member_id: int
    answers: Dict[str, Any]
    is_private: bool = False
    item_index: int = 1


class SubmissionResponse(BaseModel):
    """提交响应"""
    id: int
    task_id: int
    member_id: int
    submission_type: str
    original_filename: Optional[str] = None
    stored_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: int = 0
    text_content: Optional[str] = None
    questionnaire_answers: Optional[Dict[str, Any]] = None
    is_private: bool = False
    upload_count: int = 1
    item_index: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubmissionWithMember(SubmissionResponse):
    """带成员信息的提交响应"""
    member_name: str
    member_student_id: str


class SubmissionPreview(BaseModel):
    """提交预览（用于公开展示）"""
    id: int
    member_id: int
    member_name: str
    submission_type: str
    original_filename: Optional[str]
    text_content: Optional[str]
    questionnaire_answers: Optional[Dict[str, Any]]
    file_size: int
    is_private: bool
    created_at: datetime


class ExportRequest(BaseModel):
    """导出请求"""
    task_id: int
    member_ids: Optional[List[int]] = None
    naming_format: Optional[str] = None


class ExportResponse(BaseModel):
    """导出响应"""
    filename: str
    file_count: int
    total_size: int
