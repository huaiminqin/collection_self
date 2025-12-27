@echo off
chcp 65001 >nul
title 班级文件收集系统

echo ========================================
echo    班级文件收集系统 - 一键启动脚本
echo ========================================
echo.

:: 检查并启动 MySQL 服务
echo [1/3] 检查 MySQL 服务...
sc query mysql >nul 2>&1
if %errorlevel% equ 0 (
    sc query mysql | find "RUNNING" >nul
    if %errorlevel% neq 0 (
        echo      MySQL 服务未运行，正在启动...
        net start mysql >nul 2>&1
        if %errorlevel% equ 0 (
            echo      MySQL 服务启动成功！
        ) else (
            echo      MySQL 服务启动失败，请手动启动或检查服务名称
            echo      尝试其他服务名: MySQL80, MySQL57, MariaDB
            pause
            exit /b 1
        )
    ) else (
        echo      MySQL 服务已在运行
    )
) else (
    :: 尝试其他常见的 MySQL 服务名
    for %%s in (MySQL80 MySQL57 MariaDB) do (
        sc query %%s >nul 2>&1
        if !errorlevel! equ 0 (
            echo      找到服务: %%s
            net start %%s >nul 2>&1
            goto :mysql_ok
        )
    )
    echo      警告: 未找到 MySQL 服务，请确保 MySQL 已安装并运行
)
:mysql_ok

echo.
echo [2/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo      错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)
echo      Python 环境正常

echo.
echo [3/3] 启动应用服务器...
echo.
echo ========================================
echo    服务器启动中...
echo    管理后台: http://127.0.0.1:8000/admin
echo    用户提交: http://127.0.0.1:8000/submit?task_id=1
echo    按 Ctrl+C 停止服务器
echo ========================================
echo.

:: 启动应用
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
