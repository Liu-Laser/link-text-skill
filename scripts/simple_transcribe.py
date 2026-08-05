#!/usr/bin/env python3
"""
简化的转录脚本 - 直接使用 Whisper 转录音频文件
"""

import sys
import os
from pathlib import Path
import whisper

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_transcribe.py <audio_path> [output_path]")
        print("参数说明:")
        print("- audio_path: 音频文件路径")
        print("- output_path: 可选，输出文件路径（默认: transcript.md）")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "transcript.md"

    print("="*60)
    print("Whisper 音频转录")
    print("="*60)

    # 检查音频文件是否存在
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)

    print(f"[Step 1] 加载 Whisper 模型...")
    try:
        # 使用 medium 模型平衡质量和速度
        model = whisper.load_model("medium")
        print("模型加载完成")
    except Exception as e:
        print(f"模型加载失败: {e}")
        sys.exit(1)

    print(f"\n[Step 2] 开始转录音频...")
    print(f"音频文件: {audio_path}")

    try:
        # 转录音频
        result = model.transcribe(audio_path, language="zh", verbose=True)

        print(f"\n[Step 3] 保存转录结果...")

        # 创建转录文本
        transcript_text = f"""# 音频转录结果

## 基本信息
- **音频文件**: {os.path.basename(audio_path)}
- **转录语言**: 中文
- **模型**: Whisper medium
- **转录时间**: {result['text']}

## 转录内容

{result['text']}

## 详细时间戳

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
            transcript_text += f"{timestamp} {text}\n\n"

        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript_text)

        print(f"转录完成！结果已保存到: {output_path}")
        print(f"总时长: {len(result['segments'])} 个段落")

    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()