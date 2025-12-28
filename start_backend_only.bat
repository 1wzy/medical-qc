@echo off
chcp 65001 >nul
echo 正在启动后端服务...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查目录是否存在
if not exist "backend\" (
    echo 错误: 找不到 backend 目录
    pause
    exit /b 1
)

REM 先停止可能存在的旧进程
echo 检查并停止旧的后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul

REM 启动后端（使用 conda 环境）
echo 启动后端服务...
start "Backend Service" cmd /k "cd /d "%~dp0backend" && call conda activate medical-qc && python main.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 后端服务已启动！
echo ========================================
echo.
echo 后端地址: http://127.0.0.1:8000
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo 注意：请保持此窗口打开以查看后端日志
echo 按任意键关闭此窗口（服务将继续运行）...
pause >nul

