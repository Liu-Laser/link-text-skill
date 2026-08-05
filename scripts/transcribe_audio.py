#!/usr/bin/env python3
"""
音频转录脚本 - 直接处理本地音频文件
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def transcribe_audio(audio_path, output_dir):
    """转录音频文件"""
    print("="*60)
    print("音频转录工具")
    print("="*60)

    # 检查音频文件是否存在
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)

    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Step 0] 准备目录...")
    task_dir = output_dir / "BV1PHmoBHE7q_audio"
    task_dir.mkdir(exist_ok=True)

    audio_dir = task_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    # 复制音频文件到音频目录
    audio_filename = "BV1PHmoBHE7q_audio.m4a"
    audio_dest = audio_dir / audio_filename
    print(f"[Step 1] 复制音频文件...")
    subprocess.run(['cp', audio_path, str(audio_dest)], check=True)

    # 创建任务信息
    task_info = {
        "task_id": "BV1PHmoBHE7q_audio",
        "source_file": str(audio_path),
        "output_dir": str(task_dir),
        "audio_file": str(audio_dest),
        "status": "transcribing"
    }

    with open(task_dir / "task_info.json", "w", encoding="utf-8") as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)

    print(f"[Step 2] 开始转录...")

    # 使用智能监控脚本进行转录
    cmd = [
        'python', 'main_simplified.py',
        str(audio_dest),
        str(output_dir)
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(__file__)
    )

    # 实时捕获输出
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # 等待进程完成
    process.wait()

    # 更新任务状态
    task_info["status"] = "completed" if process.returncode == 0 else "failed"
    task_info["exit_code"] = process.returncode

    with open(task_dir / "task_info.json", "w", encoding="utf-8") as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)

    print(f"[完成] 转录任务 {'成功' if process.returncode == 0 else '失败'}")

    if process.returncode == 0:
        # 查找转录结果文件
        transcript_file = task_dir / "output" / "transcript.md"
        if transcript_file.exists():
            print(f"转录结果保存在: {transcript_file}")
            return transcript_file
        else:
            print("警告: 未找到转录结果文件")
            return None
    else:
        print(f"转录失败，错误代码: {process.returncode}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <audio_file> [output_dir]")
        sys.exit(1)

    audio_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "C:\\Users\\lenovo\\translate"

    result = transcribe_audio(audio_file, output_dir)
    sys.exit(0 if result else 1)