"""认证服务"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
import bcrypt
from jose import JWTError, jwt

from app.models import Admin
from app.config import settings
from app.schemas.auth import AdminSetup, TokenData


# JWT配置
ALGORITHM = "HS256"


class AuthService:
    """认证服务"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
    
    @staticmethod
    def get_admin(db: Session, username: str) -> Optional[Admin]:
        """获取管理员"""
        return db.query(Admin).filter(Admin.username == username).first()
    
    @staticmethod
    def get_admin_count(db: Session) -> int:
        """获取管理员数量"""
        return db.query(Admin).count()
    
    @staticmethod
    def is_setup_required(db: Session) -> bool:
        """检查是否需要初始设置"""
        return AuthService.get_admin_count(db) == 0
    
    @staticmethod
    def setup_admin(db: Session, setup: AdminSetup) -> Admin:
        """初始设置管理员"""
        if not AuthService.is_setup_required(db):
            raise ValueError("管理员已存在，无法重复设置")
        
        hashed_password = AuthService.get_password_hash(setup.password)
        admin = Admin(
            username=setup.username,
            password_hash=hashed_password
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    @staticmethod
    def authenticate_admin(db: Session, username: str, password: str) -> Optional[Admin]:
        """验证管理员"""
        admin = AuthService.get_admin(db, username)
        if not admin:
            return None
        
        # 检查是否被锁定
        if admin.locked_until and datetime.now() < admin.locked_until:
            return None
        
        if not AuthService.verify_password(password, admin.password_hash):
            # 增加失败次数
            admin.failed_attempts += 1
            
            # 检查是否需要锁定
            if admin.failed_attempts >= settings.max_login_attempts:
                admin.locked_until = datetime.now() + timedelta(minutes=settings.lockout_duration_minutes)
            
            db.commit()
            return None
        
        # 登录成功，重置失败次数
        admin.failed_attempts = 0
        admin.locked_until = None
        db.commit()
        
        return admin
    
    @staticmethod
    def is_account_locked(admin: Admin) -> bool:
        """检查账号是否被锁定"""
        if not admin.locked_until:
            return False
        return datetime.now() < admin.locked_until
    
    @staticmethod
    def get_lockout_remaining(admin: Admin) -> Optional[int]:
        """获取锁定剩余时间（秒）"""
        if not admin.locked_until:
            return None
        remaining = (admin.locked_until - datetime.now()).total_seconds()
        return max(0, int(remaining))
