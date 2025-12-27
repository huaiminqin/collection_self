from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Member(Base):
    """成员模型"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, unique=True, index=True, comment="学号")
    name = Column(String(100), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    dormitory = Column(String(50), nullable=True, comment="寝室号")
    qq_email = Column(String(100), nullable=True, comment="QQ邮箱")
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, comment="所属班级ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    class_ = relationship("Class", back_populates="members")
    submissions = relationship("Submission", back_populates="member", cascade="all, delete-orphan")
    reminder_logs = relationship("ReminderLog", back_populates="member", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Member(id={self.id}, student_id={self.student_id}, name={self.name})>"
