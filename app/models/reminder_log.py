from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReminderLog(Base):
    """提醒发送记录模型"""
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, comment="任务ID")
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, comment="成员ID")
    email = Column(String(100), nullable=False, comment="发送邮箱")
    status = Column(String(20), nullable=False, default="pending", comment="发送状态: pending/sent/failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    sent_at = Column(DateTime, server_default=func.now(), comment="发送时间")
    
    # 关联关系
    task = relationship("Task", back_populates="reminder_logs")
    member = relationship("Member", back_populates="reminder_logs")
    
    def __repr__(self):
        return f"<ReminderLog(id={self.id}, task_id={self.task_id}, member_id={self.member_id}, status={self.status})>"
