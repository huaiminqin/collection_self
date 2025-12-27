from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import io

from app.models import Member, Submission
from app.schemas.member import MemberCreate, MemberUpdate, MemberImportItem, MemberImportResult


class MemberService:
    """成员管理服务"""
    
    @staticmethod
    def get_members(
        db: Session, 
        class_id: Optional[int] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Member]:
        """获取成员列表"""
        query = db.query(Member)
        if class_id:
            query = query.filter(Member.class_id == class_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_member(db: Session, member_id: int) -> Optional[Member]:
        """获取单个成员"""
        return db.query(Member).filter(Member.id == member_id).first()
    
    @staticmethod
    def get_member_by_student_id(db: Session, student_id: str) -> Optional[Member]:
        """根据学号获取成员"""
        return db.query(Member).filter(Member.student_id == student_id).first()
    
    @staticmethod
    def create_member(db: Session, member: MemberCreate) -> Member:
        """创建成员"""
        db_member = Member(
            student_id=member.student_id,
            name=member.name,
            gender=member.gender,
            dormitory=member.dormitory,
            qq_email=member.qq_email,
            class_id=member.class_id
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    
    @staticmethod
    def update_member(db: Session, member_id: int, member: MemberUpdate) -> Optional[Member]:
        """更新成员"""
        db_member = db.query(Member).filter(Member.id == member_id).first()
        if not db_member:
            return None
        
        update_data = member.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_member, key, value)
        
        db.commit()
        db.refresh(db_member)
        return db_member
    
    @staticmethod
    def delete_member(db: Session, member_id: int) -> bool:
        """删除成员（级联删除提交记录）"""
        db_member = db.query(Member).filter(Member.id == member_id).first()
        if not db_member:
            return False
        
        db.delete(db_member)
        db.commit()
        return True
    
    @staticmethod
    def import_members(
        db: Session, 
        class_id: int, 
        members: List[MemberImportItem],
        skip_duplicates: bool = True
    ) -> MemberImportResult:
        """批量导入成员"""
        success_count = 0
        skip_count = 0
        error_count = 0
        errors = []
        
        for item in members:
            try:
                existing = MemberService.get_member_by_student_id(db, item.student_id)
                if existing:
                    if skip_duplicates:
                        skip_count += 1
                        continue
                    else:
                        # 覆盖模式：更新现有记录
                        existing.name = item.name
                        existing.gender = item.gender
                        existing.dormitory = item.dormitory
                        existing.qq_email = item.qq_email
                        existing.class_id = class_id
                        db.commit()
                        success_count += 1
                        continue
                
                db_member = Member(
                    student_id=item.student_id,
                    name=item.name,
                    gender=item.gender,
                    dormitory=item.dormitory,
                    qq_email=item.qq_email,
                    class_id=class_id
                )
                db.add(db_member)
                db.commit()
                success_count += 1
            except Exception as e:
                db.rollback()
                error_count += 1
                errors.append(f"学号 {item.student_id}: {str(e)}")
        
        return MemberImportResult(
            success_count=success_count,
            skip_count=skip_count,
            error_count=error_count,
            errors=errors
        )
    
    @staticmethod
    def get_members_with_submission_status(
        db: Session, 
        class_id: int, 
        task_id: int
    ) -> List[Tuple[Member, bool, int]]:
        """获取成员列表及其提交状态"""
        members = db.query(Member).filter(Member.class_id == class_id).all()
        result = []
        
        for member in members:
            submission = db.query(Submission).filter(
                Submission.member_id == member.id,
                Submission.task_id == task_id
            ).first()
            
            has_submitted = submission is not None
            submission_count = submission.upload_count if submission else 0
            result.append((member, has_submitted, submission_count))
        
        return result
    
    @staticmethod
    def get_unsubmitted_members(db: Session, class_id: int, task_id: int) -> List[Member]:
        """获取未提交成员列表"""
        # 获取已提交的成员ID
        submitted_ids = db.query(Submission.member_id).filter(
            Submission.task_id == task_id
        ).subquery()
        
        # 获取未提交的成员
        return db.query(Member).filter(
            Member.class_id == class_id,
            ~Member.id.in_(submitted_ids)
        ).all()
