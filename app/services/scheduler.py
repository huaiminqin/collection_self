"""定时任务服务"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Task, Member, Submission
from app.services.email import EmailService
from app.services.member import MemberService

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务服务"""
    
    _scheduler: Optional[BackgroundScheduler] = None
    _is_running: bool = False
    
    @classmethod
    def get_scheduler(cls) -> BackgroundScheduler:
        """获取调度器实例"""
        if cls._scheduler is None:
            cls._scheduler = BackgroundScheduler()
        return cls._scheduler
    
    @classmethod
    def start(cls):
        """启动调度器"""
        if cls._is_running:
            return
        
        scheduler = cls.get_scheduler()
        
        # 添加自动提醒检查任务（每10分钟检查一次）
        scheduler.add_job(
            cls.check_and_send_reminders,
            IntervalTrigger(minutes=10),
            id="auto_reminder_check",
            replace_existing=True
        )
        
        scheduler.start()
        cls._is_running = True
        logger.info("定时任务调度器已启动")
    
    @classmethod
    def stop(cls):
        """停止调度器"""
        if cls._scheduler and cls._is_running:
            cls._scheduler.shutdown()
            cls._is_running = False
            logger.info("定时任务调度器已停止")
    
    @classmethod
    def check_and_send_reminders(cls):
        """检查并发送自动提醒"""
        logger.info("开始检查自动提醒任务...")
        
        db = SessionLocal()
        try:
            now = datetime.now()
            
            # 获取启用了自动提醒且未过期的任务
            tasks = db.query(Task).filter(
                Task.auto_remind_enabled == True,
                Task.deadline != None,
                Task.deadline > now
            ).all()
            
            for task in tasks:
                # 计算提醒时间
                remind_time = task.deadline - timedelta(hours=task.remind_before_hours)
                
                # 检查是否到达提醒时间
                if now >= remind_time:
                    # 检查是否已经发送过提醒（避免重复发送）
                    # 这里简单检查最近1小时内是否发送过
                    from app.models import ReminderLog
                    recent_reminder = db.query(ReminderLog).filter(
                        ReminderLog.task_id == task.id,
                        ReminderLog.sent_at > now - timedelta(hours=1)
                    ).first()
                    
                    if recent_reminder:
                        continue
                    
                    # 获取未提交成员
                    unsubmitted = MemberService.get_unsubmitted_members(
                        db, task.class_id, task.id
                    )
                    
                    if unsubmitted:
                        logger.info(f"任务 {task.title} 发送自动提醒给 {len(unsubmitted)} 人")
                        EmailService.send_reminder_to_members(db, task, unsubmitted)
        
        except Exception as e:
            logger.error(f"自动提醒检查失败: {e}")
        finally:
            db.close()
        
        logger.info("自动提醒检查完成")
