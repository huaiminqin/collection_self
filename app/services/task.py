from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Task, Member, Submission
from app.schemas.task import TaskCreate, TaskUpdate, TaskStats


class TaskService:
    """收集任务管理服务"""
    
    @staticmethod
    def get_tasks(
        db: Session, 
        class_id: Optional[int] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """获取任务列表"""
        query = db.query(Task)
        if class_id:
            query = query.filter(Task.class_id == class_id)
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """获取单个任务"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """创建任务"""
        db_task = Task(
            title=task.title,
            description=task.description,
            class_id=task.class_id,
            collect_types=task.collect_types,
            items_per_person=task.items_per_person,
            allowed_types=task.allowed_types,
            questionnaire_config=task.questionnaire_config,
            deadline=task.deadline,
            max_uploads=task.max_uploads,
            allow_modify=task.allow_modify,
            admin_only_visible=task.admin_only_visible,
            allow_user_set_visibility=task.allow_user_set_visibility,
            naming_format=task.naming_format,
            remind_before_hours=task.remind_before_hours,
            auto_remind_enabled=task.auto_remind_enabled,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
        """更新任务"""
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return None
        
        update_data = task.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """删除任务（级联删除提交记录）"""
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def get_task_stats(db: Session, task_id: int) -> Optional[TaskStats]:
        """获取任务统计"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # 获取班级总人数
        total_members = db.query(func.count(Member.id)).filter(
            Member.class_id == task.class_id
        ).scalar() or 0
        
        # 获取已提交人数（去重）
        submitted_count = db.query(func.count(func.distinct(Submission.member_id))).filter(
            Submission.task_id == task_id
        ).scalar() or 0
        
        # 计算未提交人数
        not_submitted_count = total_members - submitted_count
        
        # 计算提交率
        submission_rate = (submitted_count / total_members * 100) if total_members > 0 else 0
        
        return TaskStats(
            task_id=task_id,
            total_members=total_members,
            submitted_count=submitted_count,
            not_submitted_count=not_submitted_count,
            submission_rate=round(submission_rate, 2)
        )
    
    @staticmethod
    def is_deadline_passed(task: Task) -> bool:
        """检查是否已过截止时间"""
        if not task.deadline:
            return False
        return datetime.now() > task.deadline
    
    @staticmethod
    def get_tasks_needing_reminder(db: Session) -> List[Task]:
        """获取需要发送提醒的任务"""
        now = datetime.now()
        tasks = db.query(Task).filter(
            Task.auto_remind_enabled == True,
            Task.deadline != None,
            Task.deadline > now
        ).all()
        
        result = []
        for task in tasks:
            from datetime import timedelta
            remind_time = task.deadline - timedelta(hours=task.remind_before_hours)
            if now >= remind_time:
                result.append(task)
        
        return result
