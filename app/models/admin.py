from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Admin(Base):
    """管理员模型"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 登录安全
    failed_attempts = Column(Integer, default=0, comment="连续登录失败次数")
    locked_until = Column(DateTime, nullable=True, comment="锁定截止时间")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username})>"
