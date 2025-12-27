import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "班级文件收集系统"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = False
    
    # MySQL数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "class_collection"
    
    # 文件存储配置
    upload_dir: str = "./uploads"
    max_file_size: int = 104857600  # 100MB
    
    # QQ邮箱SMTP配置
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_ssl: bool = True
    
    # 系统URL
    site_url: str = "http://localhost:8000"
    
    # JWT配置
    access_token_expire_minutes: int = 60 * 24  # 24小时
    
    # 账号锁定配置
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
