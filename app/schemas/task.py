from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class QuestionnaireItem(BaseModel):
    """问卷题目"""
    type: str  # text, radio, checkbox, image, file
    title: str
    options: Optional[List[str]] = None  # 单选/多选的选项
    required: bool = True


class CollectTypes(BaseModel):
    """收集类型配置"""
    file: bool = False
    text: bool = False
    image: bool = False
    questionnaire: bool = False


class TaskBase(BaseModel):
    """任务基础模式"""
    title: str
    description: Optional[str] = None
    collect_types: Optional[Dict[str, bool]] = None
    items_per_person: int = 1
    allowed_types: Optional[List[str]] = None
    questionnaire_config: Optional[List[Dict[str, Any]]] = None
    deadline: Optional[datetime] = None
    max_uploads: int = 1
    allow_modify: bool = True
    admin_only_visible: bool = False
    allow_user_set_visibility: bool = True
    naming_format: str = "{student_id}_{name}"
    remind_before_hours: int = 24
    auto_remind_enabled: bool = False


class TaskCreate(TaskBase):
    """创建任务请求"""
    class_id: int


class TaskUpdate(BaseModel):
    """更新任务请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    collect_types: Optional[Dict[str, bool]] = None
    items_per_person: Optional[int] = None
    allowed_types: Optional[List[str]] = None
    questionnaire_config: Optional[List[Dict[str, Any]]] = None
    deadline: Optional[datetime] = None
    max_uploads: Optional[int] = None
    allow_modify: Optional[bool] = None
    admin_only_visible: Optional[bool] = None
    allow_user_set_visibility: Optional[bool] = None
    naming_format: Optional[str] = None
    remind_before_hours: Optional[int] = None
    auto_remind_enabled: Optional[bool] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    title: str
    description: Optional[str]
    class_id: int
    collect_types: Optional[Dict[str, bool]]
    items_per_person: int
    allowed_types: Optional[List[str]]
    questionnaire_config: Optional[List[Dict[str, Any]]]
    deadline: Optional[datetime]
    max_uploads: int
    allow_modify: bool
    admin_only_visible: bool
    allow_user_set_visibility: bool
    naming_format: str
    remind_before_hours: int
    auto_remind_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskStats(BaseModel):
    """任务统计"""
    task_id: int
    total_members: int
    submitted_count: int
    not_submitted_count: int
    submission_rate: float


class TaskWithStats(TaskResponse):
    """带统计的任务响应"""
    stats: Optional[TaskStats] = None
