from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Grade(Base):
    """年级模型"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="年级名称")
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, comment="所属学院ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    college = relationship("College", back_populates="grades")
    classes = relationship("Class", back_populates="grade", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Grade(id={self.id}, name={self.name}, college_id={self.college_id})>"
