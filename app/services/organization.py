from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import College, Grade, Class
from app.schemas.college import CollegeCreate, CollegeUpdate
from app.schemas.grade import GradeCreate, GradeUpdate
from app.schemas.class_ import ClassCreate, ClassUpdate


class OrganizationService:
    """组织结构管理服务"""
    
    # ============ 学院操作 ============
    
    @staticmethod
    def get_colleges(db: Session, skip: int = 0, limit: int = 100) -> List[College]:
        """获取学院列表"""
        return db.query(College).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_college(db: Session, college_id: int) -> Optional[College]:
        """获取单个学院"""
        return db.query(College).filter(College.id == college_id).first()
    
    @staticmethod
    def get_college_by_name(db: Session, name: str) -> Optional[College]:
        """根据名称获取学院"""
        return db.query(College).filter(College.name == name).first()
    
    @staticmethod
    def create_college(db: Session, college: CollegeCreate) -> College:
        """创建学院"""
        db_college = College(name=college.name)
        db.add(db_college)
        db.commit()
        db.refresh(db_college)
        return db_college
    
    @staticmethod
    def update_college(db: Session, college_id: int, college: CollegeUpdate) -> Optional[College]:
        """更新学院"""
        db_college = db.query(College).filter(College.id == college_id).first()
        if not db_college:
            return None
        
        if college.name is not None:
            db_college.name = college.name
        
        db.commit()
        db.refresh(db_college)
        return db_college
    
    @staticmethod
    def delete_college(db: Session, college_id: int) -> bool:
        """删除学院（级联删除年级和班级）"""
        db_college = db.query(College).filter(College.id == college_id).first()
        if not db_college:
            return False
        
        db.delete(db_college)
        db.commit()
        return True
    
    # ============ 年级操作 ============
    
    @staticmethod
    def get_grades(db: Session, college_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Grade]:
        """获取年级列表"""
        query = db.query(Grade)
        if college_id:
            query = query.filter(Grade.college_id == college_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_grade(db: Session, grade_id: int) -> Optional[Grade]:
        """获取单个年级"""
        return db.query(Grade).filter(Grade.id == grade_id).first()
    
    @staticmethod
    def create_grade(db: Session, grade: GradeCreate) -> Grade:
        """创建年级"""
        db_grade = Grade(name=grade.name, college_id=grade.college_id)
        db.add(db_grade)
        db.commit()
        db.refresh(db_grade)
        return db_grade
    
    @staticmethod
    def update_grade(db: Session, grade_id: int, grade: GradeUpdate) -> Optional[Grade]:
        """更新年级"""
        db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
        if not db_grade:
            return None
        
        if grade.name is not None:
            db_grade.name = grade.name
        if grade.college_id is not None:
            db_grade.college_id = grade.college_id
        
        db.commit()
        db.refresh(db_grade)
        return db_grade
    
    @staticmethod
    def delete_grade(db: Session, grade_id: int) -> bool:
        """删除年级（级联删除班级）"""
        db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
        if not db_grade:
            return False
        
        db.delete(db_grade)
        db.commit()
        return True
    
    # ============ 班级操作 ============
    
    @staticmethod
    def get_classes(db: Session, grade_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Class]:
        """获取班级列表"""
        query = db.query(Class)
        if grade_id:
            query = query.filter(Class.grade_id == grade_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_class(db: Session, class_id: int) -> Optional[Class]:
        """获取单个班级"""
        return db.query(Class).filter(Class.id == class_id).first()
    
    @staticmethod
    def create_class(db: Session, class_: ClassCreate) -> Class:
        """创建班级"""
        db_class = Class(name=class_.name, grade_id=class_.grade_id)
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return db_class
    
    @staticmethod
    def update_class(db: Session, class_id: int, class_: ClassUpdate) -> Optional[Class]:
        """更新班级"""
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if not db_class:
            return None
        
        if class_.name is not None:
            db_class.name = class_.name
        if class_.grade_id is not None:
            db_class.grade_id = class_.grade_id
        
        db.commit()
        db.refresh(db_class)
        return db_class
    
    @staticmethod
    def delete_class(db: Session, class_id: int) -> bool:
        """删除班级（级联删除成员）"""
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if not db_class:
            return False
        
        db.delete(db_class)
        db.commit()
        return True
