from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.organization import OrganizationService
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse, GradeWithClasses

router = APIRouter()


@router.get("/", response_model=List[GradeResponse])
def get_grades(
    college_id: Optional[int] = Query(None, description="按学院筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取年级列表"""
    return OrganizationService.get_grades(db, college_id=college_id, skip=skip, limit=limit)


@router.get("/{grade_id}", response_model=GradeWithClasses)
def get_grade(grade_id: int, db: Session = Depends(get_db)):
    """获取单个年级（包含班级列表）"""
    grade = OrganizationService.get_grade(db, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")
    return grade


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(grade: GradeCreate, db: Session = Depends(get_db)):
    """创建年级"""
    # 验证学院存在
    college = OrganizationService.get_college(db, grade.college_id)
    if not college:
        raise HTTPException(status_code=400, detail="所属学院不存在")
    return OrganizationService.create_grade(db, grade)


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, grade: GradeUpdate, db: Session = Depends(get_db)):
    """更新年级"""
    if grade.college_id:
        college = OrganizationService.get_college(db, grade.college_id)
        if not college:
            raise HTTPException(status_code=400, detail="所属学院不存在")
    
    updated = OrganizationService.update_grade(db, grade_id, grade)
    if not updated:
        raise HTTPException(status_code=404, detail="年级不存在")
    return updated


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(grade_id: int, db: Session = Depends(get_db)):
    """删除年级（级联删除班级）"""
    if not OrganizationService.delete_grade(db, grade_id):
        raise HTTPException(status_code=404, detail="年级不存在")
