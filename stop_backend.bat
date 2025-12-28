@echo off
chcp 65001 >nul
echo 正在停止所有后端服务...
echo.

echo 查找占用 8000 端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 发现进程: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   无法停止进程 %%a（可能需要管理员权限）
    ) else (
        echo   已停止进程 %%a
    )
)

echo.
echo 等待端口释放...
timeout /t 2 /nobreak >nul

echo.
netstat -ano | findstr :8000
if errorlevel 1 (
    echo ✓ 所有后端服务已停止
) else (
    echo ⚠ 仍有进程占用 8000 端口
    echo   请手动结束这些进程或重启计算机
)

echo.
pause

