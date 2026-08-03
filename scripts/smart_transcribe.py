#!/usr/bin/env python3
"""
智能转录工具
无超时限制版本，取消超时机制
"""

import sys
import os
import subprocess
import time
import signal
import json
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python smart_transcribe.py <URL_or_file_path> [output_base_dir]")
        print("参数说明:")
        print("- URL_or_file_path: B站视频 URL 或本地音频文件路径")
        print("- output_base_dir: 可选，基础输出目录（默认: C:\\Users\\lenovo\\translate）")
        sys.exit(1)

    input_source = sys.argv[1]
    output_base_dir = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\lenovo\translate"

    print("="*60)
    print("智能转录工具 - 无超时限制")
    print("="*60)

    # 检查是否已经有正在运行的任务
    check_running_tasks()

    # 启动转录任务
    task_process = None
    try:
        # 构建命令
        cmd = ['python', 'main_simplified.py', input_source, output_base_dir]

        print("[执行] 启动转录任务...")
        task_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时捕获输出
        print("[监控] 任务已启动，等待完成...")
        while True:
            # 检查进程是否完成
            return_code = task_process.poll()
            if return_code is not None:
                print(f"\n[完成] 转录任务结束 (退出码: {return_code})")
                break

            time.sleep(10)  # 每10秒检查一次

        # 获取输出
        stdout, stderr = task_process.communicate()

        # 显示输出
        if stdout:
            print("\n[输出] 任务执行结果:")
            print(stdout)

        if stderr:
            print("\n[错误] 任务执行错误:")
            print(stderr)

    except KeyboardInterrupt:
        print("\n[中断] 用户中断任务")
        if task_process:
            task_process.terminate()
    except Exception as e:
        print(f"\n[错误] 任务执行异常: {e}")
    finally:
        if task_process:
            task_process.terminate()

def check_running_tasks():
    """检查是否有正在运行的任务"""
    try:
        # 查找相关的Python进程
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            python_lines = [line for line in result.stdout.split('\n')
                          if 'python.exe' in line and 'main_simplified.py' in line]

            if python_lines:
                print("\n[警告] 检测到正在运行的转录任务:")
                for line in python_lines:
                    print(f"  {line}")
                print("\n[提示] 如果需要运行新任务，请先终止现有任务")
                print("使用: taskkill /F /PID <进程ID>")
                print("\n[提示] 按Ctrl+C取消，或等待现有任务完成...")
                time.sleep(10)  # 等待10秒让用户看到警告
    except:
        pass

def monitor_task_directory(task_dir):
    """
    监控任务目录（简化版本）
    """
    start_time = time.time()
    timeout = 45 * 60  # 45分钟超时

    print(f"[监控] 监控目录: {task_dir}")

    while time.time() - start_time < timeout:
        # 检查任务信息文件
        info_file = os.path.join(task_dir, 'task_info.json')
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    task_info = json.load(f)
                    output_file = task_info.get('output_file')
                    if output_file and os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        print(f"\n[成功] 转录完成!")
                        print(f"输出文件: {output_file}")
                        print(f"文件大小: {file_size / 1024 / 1024:.1f} MB")
                        return True
            except Exception as e:
                print(f"[警告] 读取任务信息失败: {e}")

        time.sleep(30)  # 每30秒检查一次

    print(f"[超时] 监控超时 ({timeout/60} 分钟)")
    return False

if __name__ == '__main__':
    main()