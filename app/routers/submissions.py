from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Body
from fastapi.responses import FileResponse, StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import quote
import os

from app.database import get_db
from app.services.submission import SubmissionService, SubmissionError
from app.services.export import ExportService
from app.schemas.submission import (
    SubmissionResponse, ExportRequest, 
    TextSubmissionCreate, QuestionnaireSubmissionCreate
)

router = APIRouter()


@router.get("/", response_model=List[SubmissionResponse])
def get_submissions(
    task_id: Optional[int] = Query(None),
    member_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取提交列表"""
    return SubmissionService.get_submissions(db, task_id=task_id, member_id=member_id, skip=skip, limit=limit)


@router.get("/public")
def get_public_submissions(
    task_id: int = Query(...),
    exclude_member_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """获取公开的提交列表（用户查看其他人的提交）"""
    return SubmissionService.get_public_submissions(db, task_id, exclude_member_id)


# 导出端点 - 必须放在 /{submission_id} 之前
@router.post("/export")
def export_submissions(request: ExportRequest, db: Session = Depends(get_db)):
    """批量导出提交文件（每人一个文件夹）"""
    try:
        zip_buffer, filename, file_count, total_size = ExportService.export_task_submissions(
            db, task_id=request.task_id, member_ids=request.member_ids, naming_format=request.naming_format
        )
        encoded_filename = quote(filename, safe='')
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "X-File-Count": str(file_count),
                "X-Total-Size": str(total_size)
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export/text")
def export_text_submissions(
    task_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """导出所有文本提交为TXT"""
    try:
        buf, filename = ExportService.export_text_submissions(db, task_id)
        encoded_filename = quote(filename, safe='')
        return StreamingResponse(
            buf,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/preview")
def preview_export(
    task_id: int = Query(...),
    naming_format: str = Query("{student_id}_{name}"),
    db: Session = Depends(get_db)
):
    """预览导出文件结构"""
    from app.services.export import ExportService
    preview = ExportService.get_export_preview(db, task_id, naming_format)
    return {"preview": preview, "count": len(preview)}


@router.get("/export/texts")
def get_all_texts(
    task_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """获取所有文本内容（在线查看）"""
    from app.services.export import ExportService
    texts = ExportService.get_all_text_content(db, task_id)
    return {"texts": texts, "count": len(texts)}


@router.get("/export/questionnaires")
def get_all_questionnaires(
    task_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """获取所有问卷答案（在线查看）"""
    from app.services.export import ExportService
    questionnaires = ExportService.get_all_questionnaire_content(db, task_id)
    return {"questionnaires": questionnaires, "count": len(questionnaires)}


# 文本提交
@router.post("/text", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_text_submission(
    data: TextSubmissionCreate,
    db: Session = Depends(get_db)
):
    """提交文本内容"""
    try:
        return SubmissionService.create_text_submission(
            db, data.task_id, data.member_id, data.text_content, data.is_private, data.item_index
        )
    except SubmissionError as e:
        raise HTTPException(status_code=400, detail={"error": e.code, "message": e.message})


# 问卷提交
@router.post("/questionnaire", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_questionnaire_submission(
    data: QuestionnaireSubmissionCreate,
    db: Session = Depends(get_db)
):
    """提交问卷答案"""
    try:
        return SubmissionService.create_questionnaire_submission(
            db, data.task_id, data.member_id, data.answers, data.is_private, data.item_index
        )
    except SubmissionError as e:
        raise HTTPException(status_code=400, detail={"error": e.code, "message": e.message})


# 单个提交端点
@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """获取单个提交"""
    submission = SubmissionService.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")
    return submission


@router.get("/{submission_id}/download")
def download_file(submission_id: int, db: Session = Depends(get_db)):
    """下载提交的文件"""
    submission = SubmissionService.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")
    
    if submission.submission_type == "text":
        # 文本内容直接返回
        content = submission.text_content or ""
        return Response(
            content=content.encode('utf-8'),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=text.txt"}
        )
    
    if submission.submission_type == "questionnaire":
        # 问卷答案导出为JSON和TXT
        import json
        from app.models import Task
        task = db.query(Task).filter(Task.id == submission.task_id).first()
        answers = submission.questionnaire_answers or {}
        
        # 格式化为可读文本
        lines = ["问卷答案", "=" * 40, ""]
        config = task.questionnaire_config if task else []
        for i, q in enumerate(config):
            title = q.get("title", f"问题{i+1}")
            ans = answers.get(str(i), answers.get(i, ""))
            lines.append(f"【{i+1}】{title}")
            if isinstance(ans, list):
                lines.append(f"答案: {', '.join(ans)}")
            else:
                lines.append(f"答案: {ans}")
            lines.append("")
        
        content = "\n".join(lines)
        encoded_filename = quote("问卷答案.txt", safe='')
        return Response(
            content=content.encode('utf-8'),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    
    if not submission.file_path or not os.path.exists(submission.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        submission.file_path,
        filename=submission.original_filename,
        media_type=submission.file_type or "application/octet-stream"
    )


@router.get("/{submission_id}/preview")
def preview_file(submission_id: int, db: Session = Depends(get_db)):
    """预览文件内容（图片/文本）"""
    submission = SubmissionService.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")
    
    if submission.submission_type == "text":
        return {"type": "text", "content": submission.text_content}
    
    if submission.submission_type == "questionnaire":
        return {"type": "questionnaire", "answers": submission.questionnaire_answers}
    
    if submission.submission_type == "image" and submission.file_path:
        if os.path.exists(submission.file_path):
            return FileResponse(
                submission.file_path,
                media_type=submission.file_type or "image/jpeg"
            )
    
    return {"type": "file", "filename": submission.original_filename, "can_preview": False}


# 文件上传
@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    task_id: int = Query(...),
    member_id: int = Query(...),
    is_private: bool = Query(False),
    item_index: int = Query(1),
    submission_type: str = Query("file"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传文件/图片"""
    try:
        return await SubmissionService.create_file_submission(
            db, task_id, member_id, file, is_private, item_index, submission_type
        )
    except SubmissionError as e:
        raise HTTPException(status_code=400, detail={"error": e.code, "message": e.message})


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    """删除提交"""
    if not SubmissionService.delete_submission(db, submission_id):
        raise HTTPException(status_code=404, detail="提交不存在")
