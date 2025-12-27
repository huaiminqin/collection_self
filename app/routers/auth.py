from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.services.auth import AuthService
from app.schemas.auth import AdminSetup, LoginRequest, LoginResponse, AdminResponse
from app.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前管理员（认证依赖）"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = AuthService.decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = AuthService.get_admin(db, token_data.username)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin


async def get_optional_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前管理员（可选，用于判断是否为管理员）"""
    if not token:
        return None
    
    token_data = AuthService.decode_token(token)
    if not token_data:
        return None
    
    return AuthService.get_admin(db, token_data.username)


@router.get("/status")
def get_auth_status(db: Session = Depends(get_db)):
    """获取认证状态"""
    setup_required = AuthService.is_setup_required(db)
    return {
        "setup_required": setup_required,
        "message": "需要初始设置管理员" if setup_required else "系统已初始化"
    }


@router.post("/setup", response_model=AdminResponse)
def setup_admin(setup: AdminSetup, db: Session = Depends(get_db)):
    """初始设置管理员"""
    if not AuthService.is_setup_required(db):
        raise HTTPException(status_code=400, detail="管理员已存在，无法重复设置")
    
    if len(setup.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    
    admin = AuthService.setup_admin(db, setup)
    return admin


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """管理员登录"""
    admin = AuthService.authenticate_admin(db, form_data.username, form_data.password)
    
    if not admin:
        # 检查是否被锁定
        existing_admin = AuthService.get_admin(db, form_data.username)
        if existing_admin and AuthService.is_account_locked(existing_admin):
            remaining = AuthService.get_lockout_remaining(existing_admin)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "account_locked",
                    "message": f"账号已被锁定，请{remaining}秒后重试",
                    "unlock_in": remaining
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return LoginResponse(access_token=access_token)


@router.get("/me", response_model=AdminResponse)
def get_current_user(admin = Depends(get_current_admin)):
    """获取当前登录用户"""
    return admin
