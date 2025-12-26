@echo off
chcp 65001 >nul
echo 正在启动前后端服务（静默模式，无窗口）...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"

REM 检查目录是否存在
if not exist "backend\" (
    echo 错误: 找不到 backend 目录
    pause
    exit /b 1
)
if not exist "frontend\" (
    echo 错误: 找不到 frontend 目录
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "logs\" mkdir logs

REM 创建后端启动脚本（包含输出重定向）
(
echo @echo off
echo cd /d "%SCRIPT_DIR%backend"
echo call conda activate medical-qc
echo python main.py ^> "%SCRIPT_DIR%logs\backend.log" 2^>^&1
) > "%TEMP%\start_backend_silent.bat"

REM 使用 VBScript 隐藏窗口运行后端脚本
echo Set WshShell = CreateObject("WScript.Shell"^) > "%TEMP%\run_backend.vbs"
echo WshShell.Run """%TEMP%\start_backend_silent.bat""", 0, False >> "%TEMP%\run_backend.vbs"
cscript //nologo "%TEMP%\run_backend.vbs"
del "%TEMP%\run_backend.vbs"

timeout /t 2 /nobreak >nul

REM 创建前端启动脚本（包含输出重定向）
(
echo @echo off
echo cd /d "%SCRIPT_DIR%frontend"
echo npm run dev ^> "%SCRIPT_DIR%logs\frontend.log" 2^>^&1
) > "%TEMP%\start_frontend_silent.bat"

REM 使用 VBScript 隐藏窗口运行前端脚本
echo Set WshShell = CreateObject("WScript.Shell"^) > "%TEMP%\run_frontend.vbs"
echo WshShell.Run """%TEMP%\start_frontend_silent.bat""", 0, False >> "%TEMP%\run_frontend.vbs"
cscript //nologo "%TEMP%\run_frontend.vbs"
del "%TEMP%\run_frontend.vbs"

echo.
echo ========================================
echo 前后端服务已启动（后台运行，无窗口）！
echo ========================================
echo.
echo 后端地址: http://127.0.0.1:8000
echo 前端地址: http://localhost:5173
echo.
echo 日志文件位置:
echo   - 后端日志: logs\backend.log
echo   - 前端日志: logs\frontend.log
echo.
echo 提示: 要查看实时日志，请使用文本编辑器打开日志文件
echo       要停止服务，请使用 stop.bat
echo.
echo 按任意键关闭此窗口（服务将继续在后台运行）...
pause >nul
