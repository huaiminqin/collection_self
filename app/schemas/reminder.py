from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ReminderRequest(BaseModel):
    """提醒请求"""
    member_ids: Optional[List[int]] = None  # 为空则提醒所有未提交成员


class ReminderLogResponse(BaseModel):
    """提醒记录响应"""
    id: int
    task_id: int
    member_id: int
    email: str
    status: str
    error_message: Optional[str]
    sent_at: datetime
    
    class Config:
        from_attributes = True


class ReminderResult(BaseModel):
    """提醒结果"""
    total: int
    success: int
    failed: int
    errors: List[str] = []


class EmailConfig(BaseModel):
    """邮箱配置"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_ssl: bool = True


class EmailConfigResponse(BaseModel):
    """邮箱配置响应（隐藏密码）"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_use_ssl: bool
    is_configured: bool
