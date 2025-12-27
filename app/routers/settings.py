from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Setting
from app.schemas.setting import NamingFormatRequest, NamingFormatResponse
from app.schemas.reminder import EmailConfig, EmailConfigResponse
from app.utils.naming import validate_naming_format, AVAILABLE_VARIABLES

router = APIRouter()


def get_setting(db: Session, key: str) -> Optional[str]:
    """获取设置值"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting else None


def set_setting(db: Session, key: str, value: str) -> None:
    """设置值"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()


@router.get("/naming-format", response_model=NamingFormatResponse)
def get_naming_format(db: Session = Depends(get_db)):
    """获取默认命名格式"""
    format_value = get_setting(db, "default_naming_format") or "{student_id}_{name}"
    return NamingFormatResponse(
        format=format_value,
        available_variables=AVAILABLE_VARIABLES
    )


@router.put("/naming-format", response_model=NamingFormatResponse)
def set_naming_format(request: NamingFormatRequest, db: Session = Depends(get_db)):
    """设置默认命名格式"""
    is_valid, error = validate_naming_format(request.format)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    set_setting(db, "default_naming_format", request.format)
    
    return NamingFormatResponse(
        format=request.format,
        available_variables=AVAILABLE_VARIABLES
    )


@router.get("/email", response_model=EmailConfigResponse)
def get_email_config(db: Session = Depends(get_db)):
    """获取邮箱配置"""
    smtp_host = get_setting(db, "smtp_host") or ""
    smtp_port = get_setting(db, "smtp_port") or "465"
    smtp_user = get_setting(db, "smtp_user") or ""
    smtp_use_ssl = get_setting(db, "smtp_use_ssl") or "true"
    
    is_configured = bool(smtp_host and smtp_user)
    
    return EmailConfigResponse(
        smtp_host=smtp_host,
        smtp_port=int(smtp_port),
        smtp_user=smtp_user,
        smtp_use_ssl=smtp_use_ssl.lower() == "true",
        is_configured=is_configured
    )


@router.put("/email", response_model=EmailConfigResponse)
def set_email_config(config: EmailConfig, db: Session = Depends(get_db)):
    """设置邮箱配置"""
    set_setting(db, "smtp_host", config.smtp_host)
    set_setting(db, "smtp_port", str(config.smtp_port))
    set_setting(db, "smtp_user", config.smtp_user)
    set_setting(db, "smtp_password", config.smtp_password)
    set_setting(db, "smtp_use_ssl", str(config.smtp_use_ssl).lower())
    
    return EmailConfigResponse(
        smtp_host=config.smtp_host,
        smtp_port=config.smtp_port,
        smtp_user=config.smtp_user,
        smtp_use_ssl=config.smtp_use_ssl,
        is_configured=True
    )
