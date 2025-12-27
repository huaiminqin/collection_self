from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class College(Base):
    """学院模型"""
    __tablename__ = "colleges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="学院名称")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系 - 级联删除年级
    grades = relationship("Grade", back_populates="college", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<College(id={self.id}, name={self.name})>"
