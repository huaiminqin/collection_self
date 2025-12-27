from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.organization import OrganizationService
from app.schemas.college import CollegeCreate, CollegeUpdate, CollegeResponse, CollegeWithGrades

router = APIRouter()


@router.get("/", response_model=List[CollegeResponse])
def get_colleges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取学院列表"""
    return OrganizationService.get_colleges(db, skip=skip, limit=limit)


@router.get("/{college_id}", response_model=CollegeWithGrades)
def get_college(college_id: int, db: Session = Depends(get_db)):
    """获取单个学院（包含年级列表）"""
    college = OrganizationService.get_college(db, college_id)
    if not college:
        raise HTTPException(status_code=404, detail="学院不存在")
    return college


@router.post("/", response_model=CollegeResponse, status_code=status.HTTP_201_CREATED)
def create_college(college: CollegeCreate, db: Session = Depends(get_db)):
    """创建学院"""
    existing = OrganizationService.get_college_by_name(db, college.name)
    if existing:
        raise HTTPException(status_code=400, detail="学院名称已存在")
    return OrganizationService.create_college(db, college)


@router.put("/{college_id}", response_model=CollegeResponse)
def update_college(college_id: int, college: CollegeUpdate, db: Session = Depends(get_db)):
    """更新学院"""
    updated = OrganizationService.update_college(db, college_id, college)
    if not updated:
        raise HTTPException(status_code=404, detail="学院不存在")
    return updated


@router.delete("/{college_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_college(college_id: int, db: Session = Depends(get_db)):
    """删除学院（级联删除年级和班级）"""
    if not OrganizationService.delete_college(db, college_id):
        raise HTTPException(status_code=404, detail="学院不存在")
