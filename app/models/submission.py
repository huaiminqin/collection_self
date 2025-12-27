from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):
    """文件提交模型"""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, comment="所属任务ID")
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, comment="提交成员ID")
    
    # 提交类型: file, text, image, questionnaire
    submission_type = Column(String(20), default="file", comment="提交类型")
    
    # 文件信息（file/image类型使用）
    original_filename = Column(String(255), nullable=True, comment="原始文件名")
    stored_filename = Column(String(255), nullable=True, comment="存储文件名")
    file_path = Column(String(500), nullable=True, comment="文件存储路径")
    file_type = Column(String(100), nullable=True, comment="文件类型/MIME类型")
    file_size = Column(BigInteger, default=0, comment="文件大小(字节)")
    
    # 文本内容（text类型使用）
    text_content = Column(Text, nullable=True, comment="文本内容")
    
    # 问卷答案（questionnaire类型使用）
    questionnaire_answers = Column(JSON, nullable=True, comment="问卷答案")
    
    # 可见性设置
    is_private = Column(Boolean, default=False, comment="是否仅管理员可见（用户自选）")
    
    # 上传统计
    upload_count = Column(Integer, default=1, comment="上传次数")
    item_index = Column(Integer, default=1, comment="第几项提交（用于多项提交）")
    
    created_at = Column(DateTime, server_default=func.now(), comment="首次上传时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")
    
    # 关联关系
    task = relationship("Task", back_populates="submissions")
    member = relationship("Member", back_populates="submissions")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, task_id={self.task_id}, member_id={self.member_id}, type={self.submission_type})>"
