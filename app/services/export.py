"""批量导出服务"""
from typing import List, Optional, Tuple
from io import BytesIO
import zipfile
import os
import logging
import json

from sqlalchemy.orm import Session

from app.models import Task, Submission, Member
from app.utils.naming import apply_naming_format

logger = logging.getLogger(__name__)


class ExportService:
    """批量导出服务"""
    
    @staticmethod
    def export_task_submissions(
        db: Session,
        task_id: int,
        member_ids: Optional[List[int]] = None,
        naming_format: Optional[str] = None
    ) -> Tuple[BytesIO, str, int, int]:
        """导出任务的提交文件（每人一个文件夹）"""
        logger.info(f"[导出] 开始导出 task_id={task_id}")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("任务不存在")
        
        format_template = naming_format or task.naming_format or "{student_id}_{name}"
        
        query = db.query(Submission).filter(Submission.task_id == task_id)
        if member_ids:
            query = query.filter(Submission.member_id.in_(member_ids))
        
        submissions = query.all()
        if not submissions:
            raise ValueError("没有可导出的内容")
        
        # 按成员分组
        member_submissions = {}
        for s in submissions:
            if s.member_id not in member_submissions:
                member_submissions[s.member_id] = []
            member_submissions[s.member_id].append(s)
        
        zip_buffer = BytesIO()
        file_count = 0
        total_size = 0
        existing_folders = set()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for member_id, subs in member_submissions.items():
                member = db.query(Member).filter(Member.id == member_id).first()
                if not member:
                    continue
                
                member_data = {
                    "student_id": member.student_id,
                    "name": member.name,
                    "gender": member.gender or "",
                    "dormitory": member.dormitory or "",
                }
                folder_name = apply_naming_format(format_template, member_data, "")
                
                base_folder = folder_name
                counter = 1
                while folder_name in existing_folders:
                    folder_name = f"{base_folder}_{counter}"
                    counter += 1
                existing_folders.add(folder_name)
                
                for idx, sub in enumerate(subs, 1):
                    if sub.submission_type == "text" and sub.text_content:
                        fname = f"文本_{idx}.txt" if len(subs) > 1 else "文本.txt"
                        zf.writestr(f"{folder_name}/{fname}", sub.text_content.encode('utf-8'))
                        file_count += 1
                        total_size += len(sub.text_content.encode('utf-8'))
                    
                    elif sub.submission_type == "questionnaire" and sub.questionnaire_answers:
                        answers = sub.questionnaire_answers
                        jname = f"问卷_{idx}.json" if len(subs) > 1 else "问卷.json"
                        jcontent = json.dumps(answers, ensure_ascii=False, indent=2)
                        zf.writestr(f"{folder_name}/{jname}", jcontent.encode('utf-8'))
                        
                        tname = f"问卷_{idx}.txt" if len(subs) > 1 else "问卷.txt"
                        tcontent = ExportService._format_answers(task, answers)
                        zf.writestr(f"{folder_name}/{tname}", tcontent.encode('utf-8'))
                        
                        file_count += 2
                        total_size += len(jcontent) + len(tcontent)
                    
                    elif sub.file_path and os.path.exists(sub.file_path):
                        orig = sub.original_filename or f"file_{idx}"
                        zf.write(sub.file_path, f"{folder_name}/{orig}")
                        file_count += 1
                        total_size += sub.file_size or 0
        
        zip_buffer.seek(0)
        
        if file_count == 0:
            raise ValueError("没有可导出的文件")
        
        return zip_buffer, f"{task.title}_提交文件.zip", file_count, total_size
    
    @staticmethod
    def _format_answers(task: Task, answers: dict) -> str:
        lines = [f"问卷答案 - {task.title}", "=" * 40, ""]
        config = task.questionnaire_config or []
        for i, q in enumerate(config):
            title = q.get("title", f"问题{i+1}")
            ans = answers.get(str(i), "")
            lines.append(f"【{i+1}】{title}")
            if isinstance(ans, list):
                lines.append(f"答案: {', '.join(ans)}")
            else:
                lines.append(f"答案: {ans}")
            lines.append("")
        return "\n".join(lines)
    
    @staticmethod
    def export_text_submissions(db: Session, task_id: int) -> Tuple[BytesIO, str]:
        """导出所有文本为单个TXT"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("任务不存在")
        
        subs = db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.submission_type == "text"
        ).all()
        
        lines = [f"文本汇总 - {task.title}", "=" * 50, ""]
        for s in subs:
            m = db.query(Member).filter(Member.id == s.member_id).first()
            if m:
                lines.append(f"【{m.student_id} - {m.name}】")
                lines.append(s.text_content or "(空)")
                lines.append("-" * 30)
                lines.append("")
        
        content = "\n".join(lines)
        buf = BytesIO(content.encode('utf-8'))
        buf.seek(0)
        return buf, f"{task.title}_文本汇总.txt"
    
    @staticmethod
    def get_export_preview(db: Session, task_id: int, naming_format: str) -> List[dict]:
        """获取导出预览（文件夹结构）"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return []
        
        submissions = db.query(Submission).filter(Submission.task_id == task_id).all()
        
        # 按成员分组
        member_submissions = {}
        for s in submissions:
            if s.member_id not in member_submissions:
                member_submissions[s.member_id] = []
            member_submissions[s.member_id].append(s)
        
        preview = []
        for member_id, subs in member_submissions.items():
            member = db.query(Member).filter(Member.id == member_id).first()
            if not member:
                continue
            
            member_data = {
                "student_id": member.student_id,
                "name": member.name,
                "gender": member.gender or "",
                "dormitory": member.dormitory or "",
            }
            folder_name = apply_naming_format(naming_format, member_data, "")
            
            files = []
            for idx, sub in enumerate(subs, 1):
                if sub.submission_type == "text":
                    files.append(f"文本_{idx}.txt" if len(subs) > 1 else "文本.txt")
                elif sub.submission_type == "questionnaire":
                    files.append(f"问卷_{idx}.txt" if len(subs) > 1 else "问卷.txt")
                elif sub.original_filename:
                    files.append(sub.original_filename)
            
            preview.append({
                "folder": folder_name,
                "files": files,
                "member_name": member.name
            })
        
        return preview
    
    @staticmethod
    def get_all_text_content(db: Session, task_id: int) -> List[dict]:
        """获取所有文本内容（用于在线查看）"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return []
        
        subs = db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.submission_type == "text"
        ).all()
        
        result = []
        for s in subs:
            m = db.query(Member).filter(Member.id == s.member_id).first()
            if m:
                result.append({
                    "member_name": m.name,
                    "student_id": m.student_id,
                    "content": s.text_content or "",
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })
        
        return result
    
    @staticmethod
    def get_all_questionnaire_content(db: Session, task_id: int) -> List[dict]:
        """获取所有问卷答案（用于在线查看）"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return []
        
        subs = db.query(Submission).filter(
            Submission.task_id == task_id,
            Submission.submission_type == "questionnaire"
        ).all()
        
        config = task.questionnaire_config or []
        
        result = []
        for s in subs:
            m = db.query(Member).filter(Member.id == s.member_id).first()
            if m:
                answers = s.questionnaire_answers or {}
                # 格式化答案，添加问题标题
                formatted_answers = []
                for i, q in enumerate(config):
                    ans = answers.get(str(i), answers.get(i, ""))
                    formatted_answers.append({
                        "question": q.get("title", f"问题{i+1}"),
                        "answer": ans if not isinstance(ans, list) else ", ".join(ans),
                        "type": q.get("type", "text")
                    })
                
                result.append({
                    "member_name": m.name,
                    "student_id": m.student_id,
                    "answers": formatted_answers,
                    "raw_answers": answers,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })
        
        return result
