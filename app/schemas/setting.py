from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SettingBase(BaseModel):
    """设置基础模式"""
    key: str
    value: Optional[str] = None


class SettingCreate(SettingBase):
    """创建设置请求"""
    pass


class SettingUpdate(BaseModel):
    """更新设置请求"""
    value: Optional[str] = None


class SettingResponse(BaseModel):
    """设置响应"""
    id: int
    key: str
    value: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NamingFormatRequest(BaseModel):
    """命名格式请求"""
    format: str  # 如 "{student_id}_{name}"


class NamingFormatResponse(BaseModel):
    """命名格式响应"""
    format: str
    available_variables: list[str] = ["student_id", "name", "gender", "dormitory"]
