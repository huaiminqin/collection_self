from typing import List, Optional
from datetime import datetime
import os
import uuid
import logging

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import Submission, Task, Member
from app.config import settings

logger = logging.getLogger(__name__)


class SubmissionError(Exception):
    """提交错误"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class SubmissionService:
    """文件提交服务"""
    
    # 图片类型
    IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    
    # 文件类型映射
    FILE_TYPE_MAP = {
        "image": IMAGE_TYPES,
        "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"],
        "document": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "text": [".txt", ".md", ".json", ".xml", ".csv"],
    }
    
    @staticmethod
    def get_submissions(
        db: Session, 
        task_id: Optional[int] = None,
        member_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Submission]:
        """获取提交列表"""
        query = db.query(Submission)
        if task_id:
            query = query.filter(Submission.task_id == task_id)
        if member_id:
            query = query.filter(Submission.member_id == member_id)
        return query.order_by(Submission.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_public_submissions(
        db: Session,
        task_id: int,
        exclude_member_id: Optional[int] = None
    ) -> List[dict]:
        """获取公开的提交列表（用于用户查看其他人的提交）"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return []
        
        # 如果任务设置为仅管理员可见，返回空
        if task.admin_only_visible:
            return []
        
        query = db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.is_private == False
        )
        
        if exclude_member_id:
            query = query.filter(Submission.member_id != exclude_member_id)
        
        submissions = query.all()
        
        result = []
        for s in submissions:
            member = db.query(Member).filter(Member.id == s.member_id).first()
            if member:
                result.append({
                    "id": s.id,
                    "member_id": s.member_id,
                    "member_name": member.name,
                    "submission_type": s.submission_type,
                    "original_filename": s.original_filename,
                    "text_content": s.text_content,
                    "questionnaire_answers": s.questionnaire_answers,
                    "file_size": s.file_size,
                    "is_private": s.is_private,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })
        
        return result
    
    @staticmethod
    def get_submission(db: Session, submission_id: int) -> Optional[Submission]:
        """获取单个提交"""
        return db.query(Submission).filter(Submission.id == submission_id).first()
    
    @staticmethod
    def get_submission_by_task_member(
        db: Session, task_id: int, member_id: int, item_index: int = 1, submission_type: str = None
    ) -> Optional[Submission]:
        """根据任务、成员、项目索引和提交类型获取提交"""
        query = db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.member_id == member_id,
            Submission.item_index == item_index
        )
        if submission_type:
            query = query.filter(Submission.submission_type == submission_type)
        return query.first()
    
    @staticmethod
    def get_member_submissions_count(db: Session, task_id: int, member_id: int) -> int:
        """获取成员在某任务的提交数量"""
        return db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.member_id == member_id
        ).count()
    
    @staticmethod
    def validate_file_type(task: Task, file_ext: str, submission_type: str) -> None:
        """验证文件类型"""
        collect_types = task.collect_types or {}
        
        # 如果是图片类型提交
        if submission_type == "image":
            if file_ext.lower() not in SubmissionService.IMAGE_TYPES:
                raise SubmissionError(
                    "invalid_image_type",
                    f"不支持的图片格式: {file_ext}，支持: {', '.join(SubmissionService.IMAGE_TYPES)}"
                )
            return
        
        # 如果是文件类型提交且有类型限制
        if task.allowed_types:
            allowed = False
            allowed_types = task.allowed_types
            if isinstance(allowed_types, str):
                allowed_types = [t.strip() for t in allowed_types.split(",") if t.strip()]
            
            for type_name in allowed_types:
                if type_name in SubmissionService.FILE_TYPE_MAP:
                    if file_ext.lower() in SubmissionService.FILE_TYPE_MAP[type_name]:
                        allowed = True
                        break
                elif file_ext.lower() == type_name.lower() or file_ext.lower() == f".{type_name.lower()}":
                    allowed = True
                    break
            
            if not allowed:
                raise SubmissionError(
                    "invalid_file_type",
                    f"不允许的文件类型: {file_ext}"
                )
    
    @staticmethod
    async def create_file_submission(
        db: Session,
        task_id: int,
        member_id: int,
        file: UploadFile,
        is_private: bool = False,
        item_index: int = 1,
        submission_type: str = "file"
    ) -> Submission:
        """创建文件/图片提交"""
        logger.info(f"[创建提交] task_id={task_id}, member_id={member_id}, type={submission_type}")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise SubmissionError("task_not_found", "任务不存在")
        
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise SubmissionError("member_not_found", "成员不存在")
        
        # 检查截止时间
        if task.deadline and datetime.now() > task.deadline:
            raise SubmissionError("deadline_passed", f"已过截止时间")
        
        # 获取文件扩展名并验证
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        SubmissionService.validate_file_type(task, file_ext, submission_type)
        
        # 检查是否已存在同类型提交
        existing = SubmissionService.get_submission_by_task_member(db, task_id, member_id, item_index, submission_type)
        
        if existing:
            if not task.allow_modify:
                raise SubmissionError("modify_not_allowed", "该任务不允许修改已上传内容")
        
        # 生成存储文件名
        stored_filename = f"{uuid.uuid4().hex}{file_ext}"
        upload_dir = os.path.join(settings.upload_dir, str(task_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, stored_filename)
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise SubmissionError("file_save_error", f"保存文件失败: {e}")
        
        file_size = len(content)
        
        # 处理可见性
        actual_private = is_private
        if task.admin_only_visible:
            actual_private = True
        elif not task.allow_user_set_visibility:
            actual_private = False
        
        try:
            if existing:
                # 删除旧文件
                if existing.file_path and os.path.exists(existing.file_path):
                    os.remove(existing.file_path)
                
                existing.original_filename = file.filename
                existing.stored_filename = stored_filename
                existing.file_path = file_path
                existing.file_type = file.content_type
                existing.file_size = file_size
                existing.submission_type = submission_type
                existing.is_private = actual_private
                existing.upload_count += 1
                
                db.commit()
                db.refresh(existing)
                return existing
            else:
                submission = Submission(
                    task_id=task_id,
                    member_id=member_id,
                    submission_type=submission_type,
                    original_filename=file.filename,
                    stored_filename=stored_filename,
                    file_path=file_path,
                    file_type=file.content_type,
                    file_size=file_size,
                    is_private=actual_private,
                    item_index=item_index,
                    upload_count=1
                )
                db.add(submission)
                db.commit()
                db.refresh(submission)
                return submission
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise SubmissionError("db_error", f"数据库操作失败: {e}")
    
    @staticmethod
    def create_text_submission(
        db: Session,
        task_id: int,
        member_id: int,
        text_content: str,
        is_private: bool = False,
        item_index: int = 1
    ) -> Submission:
        """创建文本提交"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise SubmissionError("task_not_found", "任务不存在")
        
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise SubmissionError("member_not_found", "成员不存在")
        
        if task.deadline and datetime.now() > task.deadline:
            raise SubmissionError("deadline_passed", "已过截止时间")
        
        existing = SubmissionService.get_submission_by_task_member(db, task_id, member_id, item_index, "text")
        
        if existing:
            if not task.allow_modify:
                raise SubmissionError("modify_not_allowed", "该任务不允许修改")
        
        # 处理可见性
        actual_private = is_private
        if task.admin_only_visible:
            actual_private = True
        elif not task.allow_user_set_visibility:
            actual_private = False
        
        if existing:
            existing.text_content = text_content
            existing.is_private = actual_private
            existing.upload_count += 1
            db.commit()
            db.refresh(existing)
            return existing
        else:
            submission = Submission(
                task_id=task_id,
                member_id=member_id,
                submission_type="text",
                text_content=text_content,
                is_private=actual_private,
                item_index=item_index,
                upload_count=1
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
            return submission
    
    @staticmethod
    def create_questionnaire_submission(
        db: Session,
        task_id: int,
        member_id: int,
        answers: dict,
        is_private: bool = False,
        item_index: int = 1
    ) -> Submission:
        """创建问卷提交"""
        logger.info(f"[问卷提交] task_id={task_id}, member_id={member_id}, answers={answers}")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise SubmissionError("task_not_found", "任务不存在")
        
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise SubmissionError("member_not_found", "成员不存在")
        
        if task.deadline and datetime.now() > task.deadline:
            raise SubmissionError("deadline_passed", "已过截止时间")
        
        # 验证必填项
        if task.questionnaire_config:
            logger.info(f"[问卷配置] {task.questionnaire_config}")
            for i, q in enumerate(task.questionnaire_config):
                if q.get("required", True):
                    # 支持整数和字符串键
                    answer_value = answers.get(str(i)) or answers.get(i)
                    if not answer_value or (isinstance(answer_value, list) and len(answer_value) == 0):
                        raise SubmissionError("required_field_missing", f"请填写必填项: {q.get('title', f'问题{i+1}')}")
        
        existing = SubmissionService.get_submission_by_task_member(db, task_id, member_id, item_index, "questionnaire")
        
        if existing:
            if not task.allow_modify:
                raise SubmissionError("modify_not_allowed", "该任务不允许修改")
        
        actual_private = is_private
        if task.admin_only_visible:
            actual_private = True
        elif not task.allow_user_set_visibility:
            actual_private = False
        
        if existing:
            existing.questionnaire_answers = answers
            existing.is_private = actual_private
            existing.upload_count += 1
            db.commit()
            db.refresh(existing)
            return existing
        else:
            submission = Submission(
                task_id=task_id,
                member_id=member_id,
                submission_type="questionnaire",
                questionnaire_answers=answers,
                is_private=actual_private,
                item_index=item_index,
                upload_count=1
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
            return submission
    
    @staticmethod
    def delete_submission(db: Session, submission_id: int) -> bool:
        """删除提交"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return False
        
        if submission.file_path and os.path.exists(submission.file_path):
            os.remove(submission.file_path)
        
        db.delete(submission)
        db.commit()
        return True
    
    @staticmethod
    def get_file_path(db: Session, submission_id: int) -> Optional[str]:
        """获取文件路径"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return None
        return submission.file_path
    
    # 兼容旧接口
    @staticmethod
    async def create_submission(
        db: Session,
        task_id: int,
        member_id: int,
        file: UploadFile
    ) -> Submission:
        """创建提交（兼容旧接口）"""
        return await SubmissionService.create_file_submission(
            db, task_id, member_id, file, is_private=False, item_index=1, submission_type="file"
        )
