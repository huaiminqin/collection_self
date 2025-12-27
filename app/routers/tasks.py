from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.task import TaskService
from app.services.organization import OrganizationService
from app.services.member import MemberService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStats, TaskWithStats
from app.schemas.member import MemberWithSubmissionStatus

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    class_id: Optional[int] = Query(None, description="按班级筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    return TaskService.get_tasks(db, class_id=class_id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskWithStats)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务（包含统计信息）"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    stats = TaskService.get_task_stats(db, task_id)
    
    # 构建响应
    response = TaskWithStats.model_validate(task)
    response.stats = stats
    return response


@router.get("/{task_id}/stats", response_model=TaskStats)
def get_task_stats(task_id: int, db: Session = Depends(get_db)):
    """获取任务统计"""
    stats = TaskService.get_task_stats(db, task_id)
    if not stats:
        raise HTTPException(status_code=404, detail="任务不存在")
    return stats


@router.get("/{task_id}/members", response_model=List[MemberWithSubmissionStatus])
def get_task_members(
    task_id: int, 
    submitted: Optional[bool] = Query(None, description="筛选已提交/未提交"),
    db: Session = Depends(get_db)
):
    """获取任务的成员列表及提交状态"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    members_with_status = MemberService.get_members_with_submission_status(
        db, task.class_id, task_id
    )
    
    result = []
    for member, has_submitted, submission_count in members_with_status:
        if submitted is not None and has_submitted != submitted:
            continue
        
        member_response = MemberWithSubmissionStatus.model_validate(member)
        member_response.has_submitted = has_submitted
        member_response.submission_count = submission_count
        result.append(member_response)
    
    return result


@router.get("/{task_id}/unsubmitted")
def get_unsubmitted_members(task_id: int, db: Session = Depends(get_db)):
    """获取未提交成员名单（用于复制催交）"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    members = MemberService.get_unsubmitted_members(db, task.class_id, task_id)
    
    return {
        "count": len(members),
        "members": [{"id": m.id, "name": m.name, "student_id": m.student_id} for m in members],
        "names_text": "、".join([m.name for m in members])
    }


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建任务"""
    # 验证班级存在
    class_ = OrganizationService.get_class(db, task.class_id)
    if not class_:
        raise HTTPException(status_code=400, detail="班级不存在")
    
    return TaskService.create_task(db, task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """更新任务"""
    updated = TaskService.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="任务不存在")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务（级联删除提交记录）"""
    if not TaskService.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="任务不存在")



# 提醒相关端点
from app.services.email import EmailService
from app.schemas.reminder import ReminderRequest, ReminderResult, ReminderLogResponse


@router.post("/{task_id}/remind", response_model=ReminderResult)
def send_reminder(
    task_id: int,
    request: ReminderRequest = None,
    db: Session = Depends(get_db)
):
    """发送提醒邮件"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取要提醒的成员
    if request and request.member_ids:
        # 提醒指定成员
        from app.models import Member
        members = db.query(Member).filter(Member.id.in_(request.member_ids)).all()
    else:
        # 提醒所有未提交成员
        members = MemberService.get_unsubmitted_members(db, task.class_id, task_id)
    
    if not members:
        raise HTTPException(status_code=400, detail="没有需要提醒的成员")
    
    result = EmailService.send_reminder_to_members(db, task, members)
    return result


@router.get("/{task_id}/reminder-logs", response_model=List[ReminderLogResponse])
def get_reminder_logs(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取任务的提醒记录"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    logs = EmailService.get_reminder_logs(db, task_id=task_id, skip=skip, limit=limit)
    return logs
