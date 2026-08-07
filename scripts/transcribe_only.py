#!/usr/bin/env python3
"""
简化转录脚本 - 不使用监控器，直接转录音频
"""

import sys
import os
import subprocess
import whisper
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe_only.py <audio_path> [output_dir]")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "C:/Users/lenovo/translate"

    print("=" * 60)
    print("简化音频转录工具")
    print("=" * 60)

    # 检查音频文件
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)

    print(f"[Step 1] 准备工作...")
    print(f"音频文件: {audio_path}")

    # 创建输出目录
    video_id = os.path.basename(audio_path).split('.')[0]
    task_dir = os.path.join(output_dir, video_id)
    os.makedirs(task_dir, exist_ok=True)

    # 获取音频时长
    try:
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio_path],
                              capture_output=True, text=True)
        if result.returncode == 0:
            duration_seconds = float(result.stdout.strip())
            audio_duration = duration_seconds / 60
            print(f"音频时长: {audio_duration:.1f} 分钟")
    except:
        audio_duration = None

    # 加载Whisper模型
    print(f"\n[Step 2] 加载Whisper模型...")
    try:
        # 根据音频长度选择模型
        if audio_duration and audio_duration > 30:
            model_name = "base"
        elif audio_duration and audio_duration > 10:
            model_name = "medium"
        else:
            model_name = "medium"

        print(f"使用模型: {model_name}")
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"模型加载失败: {e}")
        sys.exit(1)

    # 开始转录
    print(f"\n[Step 3] 开始转录...")
    print(f"预计需要 {audio_duration * 0.5:.1f} - {audio_duration * 1.0:.1f} 分钟")

    try:
        # 执行转录
        result = model.transcribe(audio_path, language="zh", verbose=False)

        # 保存结果
        output_file = os.path.join(task_dir, "transcript.md")

        # 创建转录内容
        content = f"""# 音频转录结果

## 基本信息
- **音频文件**: {os.path.basename(audio_path)}
- **音频时长**: {audio_duration:.1f} 分钟
- **转录语言**: 中文
- **使用模型**: Whisper {model_name}
- **转录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 转录内容

{result['text']}

## 带时间戳的详细内容

"""

        # 添加带时间戳的段落
        for segment in result['segments']:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()

            # 格式化时间
            start_min = int(start_time // 60)
            start_sec = int(start_time % 60)
            end_min = int(end_time // 60)
            end_sec = int(end_time % 60)

            timestamp = f"[{start_min:02d}:{start_sec:02d} → {end_min:02d}:{end_sec:02d}]"
            content += f"{timestamp} {text}\n\n"

        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n[完成] 转录完成！")
        print(f"输出文件: {output_file}")
        print(f"总段落数: {len(result['segments'])}")

    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()