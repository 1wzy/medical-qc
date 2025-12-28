#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本：同时启动前后端服务
"""
import subprocess
import sys
import os
import time
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.absolute()
backend_dir = project_root / "backend"
frontend_dir = project_root / "frontend"


def stop_services():
    """停止所有服务（通过端口查找并终止进程）"""
    print("检查并停止旧的服务...")
    
    if sys.platform == "win32":
        # Windows: 通过端口查找并终止进程
        try:
            # 获取 netstat 输出
            result = subprocess.run(
                'netstat -ano', 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            pids_to_kill = set()
            
            # 查找占用端口的进程
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids_to_kill.add(('后端', pid))
                
                if ':5173' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids_to_kill.add(('前端', pid))
            
            # 终止找到的进程
            for service_name, pid in pids_to_kill:
                try:
                    subprocess.run(
                        f'taskkill /F /PID {pid}', 
                        capture_output=True, 
                        shell=True,
                        timeout=5
                    )
                    print(f"已停止{service_name}进程 (PID: {pid})")
                except Exception as e:
                    print(f"停止{service_name}进程 (PID: {pid}) 时出错: {e}")
                    
        except Exception as e:
            print(f"停止服务时出错: {e}")
    else:
        # Linux/Mac: 使用 lsof 或 fuser
        try:
            # 停止后端（端口 8000）
            subprocess.run(['lsof', '-ti:8000'], stdout=subprocess.PIPE)
            subprocess.run(['kill', '-9', '$(lsof -ti:8000)'], shell=True, capture_output=True)
            print("已停止后端服务")
        except:
            pass
        
        try:
            # 停止前端（端口 5173）
            subprocess.run(['kill', '-9', '$(lsof -ti:5173)'], shell=True, capture_output=True)
            print("已停止前端服务")
        except:
            pass


def start_backend():
    """启动后端服务（使用 conda 环境）"""
    print("正在启动后端服务（conda 环境: medical-qc）...")
    if sys.platform == "win32":
        # Windows: 使用 cmd 启动，先激活 conda 环境
        subprocess.Popen(
            f'cmd /k "cd /d {backend_dir} && call conda activate medical-qc && python main.py"',
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Linux/Mac: 直接使用当前 Python（假设已经在 conda 环境中）
        subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            shell=False
        )


def start_frontend():
    """启动前端服务"""
    print("正在启动前端服务...")
    if sys.platform == "win32":
        subprocess.Popen(
            'cmd /k "cd /d {} && npm run dev"'.format(frontend_dir),
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            shell=False
        )


def main():
    print("=" * 50)
    print("医疗质控系统 - 开发环境启动")
    print("=" * 50)
    print()
    
    # 检查后端目录
    if not backend_dir.exists():
        print(f"错误：找不到后端目录 {backend_dir}")
        sys.exit(1)
    
    # 检查前端目录
    if not frontend_dir.exists():
        print(f"错误：找不到前端目录 {frontend_dir}")
        sys.exit(1)
    
    try:
        # 先停止可能存在的旧服务
        stop_services()
        time.sleep(2)
        
        # 启动后端
        start_backend()
        print("后端服务已启动 (http://127.0.0.1:8000)")
        
        # 等待2秒
        time.sleep(2)
        
        # 启动前端
        start_frontend()
        print("前端服务已启动 (http://localhost:5173)")
        print()
        print("=" * 50)
        print("前后端服务已启动完成！")
        print("=" * 50)
        print()
        print("提示：")
        print("  - 后端API文档: http://127.0.0.1:8000/docs")
        print("  - 前端应用: http://localhost:5173")
        print()
        print("服务已在独立窗口中运行")
        print("要停止服务，请使用 stop.bat 或 stop.py")
        print()
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

