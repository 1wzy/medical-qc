@echo off
chcp 65001 >nul
echo 正在停止前后端服务...
echo.

REM 停止 Python 进程（后端）
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Service*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Backend Service*" >nul 2>&1

REM 停止 Node.js 进程（前端）
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST ^| findstr "PID"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM 更精确的方式：查找占用 8000 和 5173 端口的进程
echo 正在查找占用端口的进程...

REM 使用 netstat 查找占用 8000 端口的进程（后端）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 停止后端进程（PID: %%a）
    taskkill /F /PID %%a >nul 2>&1
)

REM 使用 netstat 查找占用 5173 端口的进程（前端）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo 停止前端进程（PID: %%a）
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo 服务已停止
echo ========================================
echo.
timeout /t 2 /nobreak >nul

