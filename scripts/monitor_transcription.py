#!/usr/bin/env python3
"""
转录任务监控器
基于新的监控策略：静默等待，只检查结果
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def monitor_transcription(task_dir, timeout_minutes=30):
    """
    监控转录任务完成情况

    Args:
        task_dir: 任务目录路径
        timeout_minutes: 超时时间（分钟）

    Returns:
        bool: True表示任务完成，False表示超时
    """
    start_time = time.time()
    max_wait_time = timeout_minutes * 60

    print(f"[监控] 开始监控任务目录: {task_dir}")
    print(f"[监控] 设置超时时间: {timeout_minutes} 分钟")
    print(f"[监控] 静默等待中...")

    # 等待5分钟后开始检查
    initial_wait = 5 * 60
    time.sleep(initial_wait)

    # 检查任务是否完成的标志
    completed = False
    output_file = None
    info_file = os.path.join(task_dir, 'task_info.json')

    while time.time() - start_time < max_wait_time:
        # 检查任务信息文件是否存在
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    task_info = json.load(f)

                # 获取输出文件路径
                output_file = task_info.get('output_file')
                if output_file and os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"[监控] 发现转录文件: {output_file}")
                    print(f"[监控] 文件大小: {file_size / 1024 / 1024:.1f} MB")
                    completed = True
                    break

                # 检查是否有任何.md文件
                output_dir = os.path.join(task_dir, 'output')
                if os.path.exists(output_dir):
                    md_files = list(Path(output_dir).glob('*.md'))
                    if md_files:
                        output_file = md_files[0]
                        file_size = os.path.getsize(output_file)
                        print(f"[监控] 发现转录文件: {output_file}")
                        print(f"[监控] 文件大小: {file_size / 1024 / 1024:.1f} MB")
                        completed = True
                        break

            except Exception as e:
                print(f"[警告] 读取任务信息失败: {e}")

        # 检查是否超时
        elapsed = time.time() - start_time
        if elapsed >= max_wait_time:
            print(f"[监控] 超时等待 {timeout_minutes} 分钟")
            break

        # 计算剩余等待时间
        remaining = max_wait_time - elapsed
        if remaining > 0:
            # 每5分钟检查一次
            wait_time = min(300, remaining)
            time.sleep(wait_time)

    if completed:
        print(f"[成功] 转录任务已完成")
        print(f"[成功] 输出文件: {output_file}")
        return True
    else:
        print(f"[失败] 转录任务未能在 {timeout_minutes} 分钟内完成")

        # 检查是否有部分结果
        if os.path.exists(info_file):
            print("[提示] 任务信息文件存在，但输出文件未找到")
            print("[提示] 可能程序仍在处理中，请稍后查看")
        else:
            print("[提示] 任务信息文件不存在")
            print("[提示] 可能程序出现错误，请检查日志")

        return False

def estimate_processing_time(audio_duration_minutes):
    """
    估算处理时间

    Args:
        audio_duration_minutes: 音频时长（分钟）

    Returns:
        tuple: (建议等待时间分钟, 超时时间分钟)
    """
    # 基于经验：1分钟音频约需2-3分钟处理
    # 加上模型加载时间
    base_time = audio_duration_minutes * 2.5  # 基础处理时间
    model_load_time = 3  # 模型加载时间（分钟）

    # 建议等待时间：基础时间 + 5分钟缓冲
    suggest_wait = min(base_time + 5, 20)  # 最多20分钟

    # 超时时间：建议等待时间 + 10分钟缓冲
    timeout = min(suggest_wait + 10, 45)  # 最多45分钟

    return int(suggest_wait), int(timeout)

def get_audio_duration(audio_path):
    """
    获取音频时长（分钟）

    Args:
        audio_path: 音频文件路径

    Returns:
        float: 音频时长（分钟）
    """
    try:
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries',
            'format=duration', '-of', 'csv=p=0', audio_path
        ], capture_output=True, text=True)

        if result.returncode == 0:
            duration_seconds = float(result.stdout.strip())
            return duration_seconds / 60
    except:
        pass

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python monitor_transcription.py <task_dir> [audio_duration_minutes]")
        sys.exit(1)

    task_dir = sys.argv[1]
    audio_duration = float(sys.argv[2]) if len(sys.argv) > 2 else None

    # 如果没有提供音频时长，尝试从音频文件获取
    if not audio_duration:
        audio_path = os.path.join(task_dir, 'audio', os.listdir(os.path.join(task_dir, 'audio'))[0])
        audio_duration = get_audio_duration(audio_path)

    if audio_duration:
        suggest_wait, timeout = estimate_processing_time(audio_duration)
        print(f"[信息] 音频时长: {audio_duration:.1f} 分钟")
        print(f"[信息] 建议等待: {suggest_wait} 分钟")
        print(f"[信息] 设置超时: {timeout} 分钟")

        success = monitor_transcription(task_dir, timeout)
    else:
        # 如果无法获取音频时长，使用默认值
        print("[信息] 无法获取音频时长，使用默认设置")
        success = monitor_transcription(task_dir, 30)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()