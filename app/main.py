from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db
from app.services.scheduler import SchedulerService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    
    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # 启动定时任务调度器
    SchedulerService.start()
    
    yield
    
    # 关闭时停止调度器
    SchedulerService.stop()


app = FastAPI(
    title=settings.app_name,
    description="班级文件收集系统 - 支持学院/年级/班级管理、文件收集、批量导出、邮件提醒",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
from app.routers import auth, colleges, grades, classes, members, tasks, submissions, settings as settings_router

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(colleges.router, prefix="/api/v1/colleges", tags=["学院"])
app.include_router(grades.router, prefix="/api/v1/grades", tags=["年级"])
app.include_router(classes.router, prefix="/api/v1/classes", tags=["班级"])
app.include_router(members.router, prefix="/api/v1/members", tags=["成员"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务"])
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["提交"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["设置"])


@app.get("/")
async def root():
    """根路径 - 重定向到管理后台"""
    return RedirectResponse(url="/static/index.html")


@app.get("/admin")
async def admin_page():
    """管理后台"""
    return FileResponse("static/index.html")


@app.get("/submit")
async def submit_page():
    """用户提交页面"""
    return FileResponse("static/submit.html")


@app.get("/task/{task_id}")
async def task_submit_page(task_id: int):
    """任务提交页面（邮件链接）"""
    return RedirectResponse(url=f"/submit?task_id={task_id}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
