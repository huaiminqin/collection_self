from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.organization import OrganizationService
from app.schemas.class_ import ClassCreate, ClassUpdate, ClassResponse, ClassWithMembers

router = APIRouter()


@router.get("/", response_model=List[ClassResponse])
def get_classes(
    grade_id: Optional[int] = Query(None, description="按年级筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取班级列表"""
    return OrganizationService.get_classes(db, grade_id=grade_id, skip=skip, limit=limit)


@router.get("/{class_id}", response_model=ClassWithMembers)
def get_class(class_id: int, db: Session = Depends(get_db)):
    """获取单个班级（包含成员列表）"""
    class_ = OrganizationService.get_class(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="班级不存在")
    return class_


@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(class_: ClassCreate, db: Session = Depends(get_db)):
    """创建班级"""
    # 验证年级存在
    grade = OrganizationService.get_grade(db, class_.grade_id)
    if not grade:
        raise HTTPException(status_code=400, detail="所属年级不存在")
    return OrganizationService.create_class(db, class_)


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, class_: ClassUpdate, db: Session = Depends(get_db)):
    """更新班级"""
    if class_.grade_id:
        grade = OrganizationService.get_grade(db, class_.grade_id)
        if not grade:
            raise HTTPException(status_code=400, detail="所属年级不存在")
    
    updated = OrganizationService.update_class(db, class_id, class_)
    if not updated:
        raise HTTPException(status_code=404, detail="班级不存在")
    return updated


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    """删除班级（级联删除成员）"""
    if not OrganizationService.delete_class(db, class_id):
        raise HTTPException(status_code=404, detail="班级不存在")
