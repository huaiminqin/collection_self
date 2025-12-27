from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Class(Base):
    """班级模型"""
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="班级名称")
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, comment="所属年级ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    grade = relationship("Grade", back_populates="classes")
    members = relationship("Member", back_populates="class_", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="class_", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Class(id={self.id}, name={self.name}, grade_id={self.grade_id})>"
