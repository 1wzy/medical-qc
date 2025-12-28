@echo off
chcp 65001 >nul
echo 正在停止前后端服务...
echo.

REM 更精确的方式：查找占用 8000 和 5173 端口的进程
echo 正在查找占用端口的进程...

REM 使用 netstat 查找占用 8000 端口的进程（后端）
echo 查找后端进程 (端口 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 停止后端进程 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   无法停止进程 %%a（可能需要管理员权限）
    )
)

REM 使用 netstat 查找占用 5173 端口的进程（前端）
echo 查找前端进程 (端口 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo 停止前端进程 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   无法停止进程 %%a（可能需要管理员权限）
    )
)

REM 额外清理：停止所有相关的 Python 和 Node 进程（可选，谨慎使用）
REM echo.
REM echo 清理残留进程...
REM taskkill /F /IM python.exe /T >nul 2>&1
REM taskkill /F /IM node.exe /T >nul 2>&1

echo.
echo ========================================
echo 服务已停止
echo ========================================
echo.
timeout /t 2 /nobreak >nul

