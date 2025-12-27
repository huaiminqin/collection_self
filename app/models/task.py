from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Task(Base):
    """收集任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="任务标题")
    description = Column(Text, nullable=True, comment="任务描述")
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, comment="所属班级ID")
    
    # 收集类型配置
    collect_types = Column(JSON, nullable=True, comment="收集类型配置: {file:bool, text:bool, image:bool, questionnaire:bool}")
    items_per_person = Column(Integer, default=1, comment="每人需要提交的项目数")
    
    # 文件类型配置 - JSON数组存储允许的类型
    allowed_types = Column(JSON, nullable=True, comment="允许的文件类型列表")
    
    # 问卷配置 - JSON存储问卷题目
    questionnaire_config = Column(JSON, nullable=True, comment="问卷配置: [{type, title, options, required}]")
    
    # 任务配置
    deadline = Column(DateTime, nullable=True, comment="截止时间")
    max_uploads = Column(Integer, default=1, comment="每人最大上传次数")
    allow_modify = Column(Boolean, default=True, comment="是否允许修改已上传文件")
    admin_only_visible = Column(Boolean, default=False, comment="是否仅管理员可见提交状态")
    allow_user_set_visibility = Column(Boolean, default=True, comment="是否允许用户自选可见性")
    naming_format = Column(String(200), default="{student_id}_{name}", comment="导出命名格式")
    
    # 提醒配置
    remind_before_hours = Column(Integer, default=24, comment="截止前多少小时提醒")
    auto_remind_enabled = Column(Boolean, default=False, comment="是否启用自动提醒")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    class_ = relationship("Class", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan")
    reminder_logs = relationship("ReminderLog", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, class_id={self.class_id})>"
