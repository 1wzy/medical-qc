#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本：同时启动前后端服务
"""
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.absolute()
backend_dir = project_root / "backend"
frontend_dir = project_root / "frontend"

# 全局变量存储进程
backend_process = None
frontend_process = None

def signal_handler(sig=None, frame=None):
    """处理 Ctrl+C 信号，停止所有子进程"""
    print("\n\n正在停止服务...")
    stop_services()
    sys.exit(0)

def stop_services():
    """停止所有服务"""
    global backend_process, frontend_process
    
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
                if ('0.0.0.0:8000' in line or '127.0.0.1:8000' in line or ':8000' in line) and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids_to_kill.add(('后端', pid))
                
                if ('0.0.0.0:5173' in line or '127.0.0.1:5173' in line or ':5173' in line) and 'LISTENING' in line:
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
        # Linux/Mac: 终止进程
        if backend_process:
            try:
                backend_process.terminate()
                backend_process.wait(timeout=5)
                print("已停止后端服务")
            except:
                try:
                    backend_process.kill()
                    print("已强制停止后端服务")
                except:
                    pass
        
        if frontend_process:
            try:
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
                print("已停止前端服务")
            except:
                try:
                    frontend_process.kill()
                    print("已强制停止前端服务")
                except:
                    pass
    
    print("所有服务已停止")

def start_backend():
    """启动后端服务（使用 conda 环境）"""
    global backend_process
    print("正在启动后端服务（conda 环境: medical-qc）...")
    if sys.platform == "win32":
        # Windows: 使用 cmd 启动，先激活 conda 环境
        backend_process = subprocess.Popen(
            f'cmd /k "cd /d {backend_dir} && call conda activate medical-qc && python main.py"',
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Linux/Mac: 直接使用当前 Python（假设已经在 conda 环境中）
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            shell=True
        )
    return backend_process

def start_frontend():
    """启动前端服务"""
    global frontend_process
    print("正在启动前端服务...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    return frontend_process

def main():
    # 注册信号处理器（仅在非 Windows 系统上有效）
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
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
        print("按 Ctrl+C 可停止所有服务并退出")
        print()
        
        # 保持脚本运行，等待用户中断
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行（仅用于非 Windows 系统）
                if sys.platform != "win32":
                    if backend_process and backend_process.poll() is not None:
                        print("后端服务已停止")
                        break
                    if frontend_process and frontend_process.poll() is not None:
                        print("前端服务已停止")
                        break
        except KeyboardInterrupt:
            # Ctrl+C 被按下，停止所有服务
            signal_handler()
            
    except Exception as e:
        print(f"启动失败: {e}")
        stop_services()
        sys.exit(1)

if __name__ == "__main__":
    main()

