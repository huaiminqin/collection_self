from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.member import MemberService
from app.services.organization import OrganizationService
from app.schemas.member import (
    MemberCreate, MemberUpdate, MemberResponse, 
    MemberImportResult, MemberWithSubmissionStatus
)
from app.utils.excel_handler import (
    create_member_template, parse_member_excel, export_members_to_excel
)

router = APIRouter()


@router.get("/", response_model=List[MemberResponse])
def get_members(
    class_id: Optional[int] = Query(None, description="按班级筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取成员列表"""
    return MemberService.get_members(db, class_id=class_id, skip=skip, limit=limit)


@router.get("/template")
def download_template():
    """下载成员导入模板"""
    template = create_member_template()
    return StreamingResponse(
        template,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=member_template.xlsx"}
    )


@router.post("/import", response_model=MemberImportResult)
async def import_members(
    class_id: int = Query(..., description="目标班级ID"),
    skip_duplicates: bool = Query(True, description="跳过重复学号"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """批量导入成员"""
    # 验证班级存在
    class_ = OrganizationService.get_class(db, class_id)
    if not class_:
        raise HTTPException(status_code=400, detail="班级不存在")
    
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传Excel文件(.xlsx或.xls)")
    
    # 解析文件
    content = await file.read()
    try:
        members = parse_member_excel(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")
    
    if not members:
        raise HTTPException(status_code=400, detail="文件中没有有效数据")
    
    # 导入成员
    result = MemberService.import_members(db, class_id, members, skip_duplicates)
    return result


@router.get("/export")
def export_members(
    class_id: int = Query(..., description="班级ID"),
    db: Session = Depends(get_db)
):
    """导出班级成员列表"""
    members = MemberService.get_members(db, class_id=class_id)
    if not members:
        raise HTTPException(status_code=404, detail="没有成员数据")
    
    # 转换为字典列表
    members_data = [
        {
            "student_id": m.student_id,
            "name": m.name,
            "gender": m.gender,
            "dormitory": m.dormitory,
            "qq_email": m.qq_email,
        }
        for m in members
    ]
    
    excel_file = export_members_to_excel(members_data)
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=members.xlsx"}
    )


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """获取单个成员"""
    member = MemberService.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    return member


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """创建成员"""
    # 验证班级存在
    class_ = OrganizationService.get_class(db, member.class_id)
    if not class_:
        raise HTTPException(status_code=400, detail="班级不存在")
    
    # 检查学号是否重复
    existing = MemberService.get_member_by_student_id(db, member.student_id)
    if existing:
        raise HTTPException(status_code=400, detail="学号已存在")
    
    return MemberService.create_member(db, member)


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberUpdate, db: Session = Depends(get_db)):
    """更新成员"""
    if member.class_id:
        class_ = OrganizationService.get_class(db, member.class_id)
        if not class_:
            raise HTTPException(status_code=400, detail="班级不存在")
    
    if member.student_id:
        existing = MemberService.get_member_by_student_id(db, member.student_id)
        if existing and existing.id != member_id:
            raise HTTPException(status_code=400, detail="学号已存在")
    
    updated = MemberService.update_member(db, member_id, member)
    if not updated:
        raise HTTPException(status_code=404, detail="成员不存在")
    return updated


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """删除成员（级联删除提交记录）"""
    if not MemberService.delete_member(db, member_id):
        raise HTTPException(status_code=404, detail="成员不存在")
