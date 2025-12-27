@echo off
chcp 65001 >nul
title 班级文件收集系统 - 开发模式

echo ========================================
echo    班级文件收集系统 - 开发模式启动
echo ========================================
echo.

:: 检查并启动 MySQL 服务
echo [1/3] 检查 MySQL 服务...
net start mysql >nul 2>&1
echo      MySQL 服务检查完成

echo.
echo [2/3] 检查依赖...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo      安装依赖中...
    pip install -r requirements.txt
)
echo      依赖检查完成

echo.
echo [3/3] 启动开发服务器 (热重载模式)...
echo.
echo ========================================
echo    开发服务器启动中...
echo    管理后台: http://127.0.0.1:8000/admin
echo    用户提交: http://127.0.0.1:8000/submit?task_id=1
echo    API文档:  http://127.0.0.1:8000/docs
echo    按 Ctrl+C 停止服务器
echo ========================================
echo.

:: 启动应用 (开发模式，支持热重载)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
