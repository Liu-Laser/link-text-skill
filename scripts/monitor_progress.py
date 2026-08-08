#!/usr/bin/env python3
"""
实时转录进度监控器
"""

import os
import sys
import time
import json
from datetime import datetime

def check_transcription_progress(task_dir):
    """检查转录进度"""
    if not os.path.exists(task_dir):
        print(f"任务目录不存在: {task_dir}")
        return

    # 检查日志文件
    log_file = os.path.join(task_dir, 'transcription.log')
    if os.path.exists(log_file):
        print("\n" + "="*60)
        print("📋 实时转录进度")
        print("="*60)

        # 读取最新的日志
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 显示最后10行日志
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            for line in recent_lines:
                print(line.rstrip())

            print(f"\n📊 总日志条数: {len(lines)}")
        except Exception as e:
            print(f"读取日志文件失败: {e}")

    # 检查任务信息
    info_file = os.path.join(task_dir, 'task_info.json')
    if os.path.exists(info_file):
        print("\n" + "="*60)
        print("📄 任务信息")
        print("="*60)

        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)

            for key, value in info.items():
                if key != 'input_source':  # URL可能很长
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"读取任务信息失败: {e}")

    # 检查输出文件
    output_files = []
    # 首先检查任务根目录下的 .md 文件
    for file in os.listdir(task_dir):
        if file.endswith('.md') and file != 'README.md':
            output_files.append(os.path.join(task_dir, file))

    # 然后递归检查子目录
    for root, dirs, files in os.walk(task_dir):
        for file in files:
            if file.endswith('.md') and file != 'README.md':
                file_path = os.path.join(root, file)
                if file_path not in output_files:  # 避免重复添加
                    output_files.append(file_path)

    if output_files:
        print("\n" + "="*60)
        print("📁 输出文件")
        print("="*60)
        for file in output_files:
            # 获取文件大小和修改时间
            stat = os.stat(file)
            size_kb = stat.st_size / 1024
            mtime = datetime.fromtimestamp(stat.st_mtime)
            print(f"📄 {os.path.basename(file)}")
            print(f"   路径: {file}")
            print(f"   大小: {size_kb:.1f} KB")
            print(f"   修改: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

def monitor_task(task_dir, interval=5):
    """持续监控任务"""
    print(f"🔍 开始监控任务: {task_dir}")
    print(f"⏱️  检查间隔: {interval} 秒")
    print("按 Ctrl+C 停止监控")
    print("\n" + "="*60)

    last_log_size = 0

    try:
        while True:
            # 检查是否有新的日志输出
            log_file = os.path.join(task_dir, 'transcription.log')
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size > last_log_size:
                    # 显示新增的日志内容
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            f.seek(last_log_size)
                            new_content = f.read()
                            if new_content.strip():
                                print(f"\n📝 [新日志] {datetime.now().strftime('%H:%M:%S')}")
                                print(new_content.rstrip())
                            last_log_size = current_size
                    except Exception as e:
                        print(f"读取新日志失败: {e}")

            # 显示当前状态
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 监控中... (按 Ctrl+C 退出)")
            sys.stdout.flush()

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n⏹️  监控已停止")
    except Exception as e:
        print(f"\n❌ 监控错误: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python monitor_transcription.py <task_dir> [interval_seconds]")
        print("参数说明:")
        print("- task_dir: 任务目录")
        print("- interval_seconds: 检查间隔（默认5秒）")
        sys.exit(1)

    task_dir = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    # 先检查一次当前状态
    check_transcription_progress(task_dir)

    # 然后开始持续监控
    monitor_task(task_dir, interval)