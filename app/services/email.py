"""邮件发送服务"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Task, Member, ReminderLog, Setting
from app.config import settings
from app.utils.email_template import generate_reminder_email
from app.schemas.reminder import ReminderResult

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class EmailService:
    """邮件发送服务"""
    
    @staticmethod
    def get_smtp_config(db: Session) -> dict:
        """从数据库获取SMTP配置"""
        def get_setting(key: str, default: str = "") -> str:
            setting = db.query(Setting).filter(Setting.key == key).first()
            return setting.value if setting else default
        
        config = {
            "host": get_setting("smtp_host", settings.smtp_host),
            "port": int(get_setting("smtp_port", str(settings.smtp_port))),
            "user": get_setting("smtp_user", settings.smtp_user),
            "password": get_setting("smtp_password", settings.smtp_password),
            "use_ssl": get_setting("smtp_use_ssl", str(settings.smtp_use_ssl)).lower() == "true",
        }
        
        logger.info(f"[SMTP配置] host={config['host']}, port={config['port']}, user={config['user']}, use_ssl={config['use_ssl']}, password={'*' * len(config['password']) if config['password'] else '未设置'}")
        return config
    
    @staticmethod
    def send_email(
        smtp_config: dict,
        to_email: str,
        subject: str,
        html_content: str
    ) -> tuple[bool, str]:
        """
        发送单封邮件
        
        Returns:
            (是否成功, 错误信息)
        """
        logger.info(f"[发送邮件] 收件人: {to_email}, 主题: {subject}")
        logger.debug(f"[SMTP连接] 正在连接 {smtp_config['host']}:{smtp_config['port']} (SSL={smtp_config['use_ssl']})")
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_config["user"]
            msg["To"] = to_email
            
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            server = None
            try:
                if smtp_config["use_ssl"]:
                    logger.debug("[SMTP] 使用SSL连接...")
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"], context=context, timeout=30)
                else:
                    logger.debug("[SMTP] 使用STARTTLS连接...")
                    server = smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=30)
                    server.starttls()
                
                logger.debug("[SMTP] 连接成功，正在登录...")
                server.login(smtp_config["user"], smtp_config["password"])
                logger.debug("[SMTP] 登录成功，正在发送...")
                server.sendmail(smtp_config["user"], to_email, msg.as_string())
                logger.info(f"[发送成功] {to_email}")
                
                # 邮件发送成功，直接返回
                return True, ""
            finally:
                # 安全关闭连接，忽略关闭时的错误
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP认证失败: {e.smtp_code} - {e.smtp_error}"
            logger.error(f"[发送失败] {to_email}: {error_msg}")
            return False, error_msg
        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP连接失败: {e}"
            logger.error(f"[发送失败] {to_email}: {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP错误: {e}"
            logger.error(f"[发送失败] {to_email}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"发送异常: {type(e).__name__}: {e}"
            logger.error(f"[发送失败] {to_email}: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def send_reminder_to_members(
        db: Session,
        task: Task,
        members: List[Member],
        submit_url_template: str = "{site_url}/task/{task_id}"
    ) -> ReminderResult:
        """
        向成员发送提醒邮件
        
        Args:
            db: 数据库会话
            task: 任务
            members: 成员列表
            submit_url_template: 提交链接模板
        
        Returns:
            发送结果
        """
        logger.info(f"[批量发送] 任务: {task.title}, 成员数: {len(members)}")
        
        smtp_config = EmailService.get_smtp_config(db)
        
        if not smtp_config["user"] or not smtp_config["password"]:
            logger.error("[批量发送] SMTP未配置，无法发送")
            return ReminderResult(
                total=len(members),
                success=0,
                failed=len(members),
                errors=["SMTP未配置，请在设置中配置邮箱账号和授权码"]
            )
        
        success = 0
        failed = 0
        errors = []
        
        for member in members:
            logger.info(f"[处理成员] {member.name} (学号: {member.student_id}, 邮箱: {member.qq_email})")
            
            if not member.qq_email:
                # 记录失败
                log = ReminderLog(
                    task_id=task.id,
                    member_id=member.id,
                    email="",
                    status="failed",
                    error_message="成员未设置QQ邮箱"
                )
                db.add(log)
                failed += 1
                errors.append(f"{member.name}: 未设置QQ邮箱")
                logger.warning(f"[跳过] {member.name}: 未设置QQ邮箱")
                continue
            
            # 生成提交链接
            submit_url = submit_url_template.format(
                site_url=settings.site_url,
                task_id=task.id
            )
            
            # 生成邮件内容
            subject, html_content = generate_reminder_email(
                task_title=task.title,
                deadline=task.deadline,
                submit_url=submit_url,
                member_name=member.name
            )
            
            logger.debug(f"[邮件内容] 主题: {subject}")
            
            # 发送邮件
            is_success, error_msg = EmailService.send_email(
                smtp_config,
                member.qq_email,
                subject,
                html_content
            )
            
            # 记录发送结果
            log = ReminderLog(
                task_id=task.id,
                member_id=member.id,
                email=member.qq_email,
                status="sent" if is_success else "failed",
                error_message=error_msg if not is_success else None
            )
            db.add(log)
            
            if is_success:
                success += 1
                logger.info(f"[成功] {member.name} ({member.qq_email})")
            else:
                failed += 1
                errors.append(f"{member.name}: {error_msg}")
                logger.error(f"[失败] {member.name}: {error_msg}")
        
        db.commit()
        
        logger.info(f"[批量发送完成] 成功: {success}, 失败: {failed}")
        
        return ReminderResult(
            total=len(members),
            success=success,
            failed=failed,
            errors=errors
        )
    
    @staticmethod
    def get_reminder_logs(
        db: Session,
        task_id: Optional[int] = None,
        member_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReminderLog]:
        """获取提醒记录"""
        query = db.query(ReminderLog)
        if task_id:
            query = query.filter(ReminderLog.task_id == task_id)
        if member_id:
            query = query.filter(ReminderLog.member_id == member_id)
        return query.order_by(ReminderLog.sent_at.desc()).offset(skip).limit(limit).all()
