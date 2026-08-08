#!/usr/bin/env python3
"""
改进的音频转录函数 - 支持更多格式
"""

import os
import subprocess
import json
import glob
import re
import time
import numpy as np
from datetime import datetime
from pathlib import Path

def find_tool_paths():
    """在系统中查找工具软件的路径"""
    ffmpeg_paths = [
        r"C:\Users\lenovo\ffmpeg_extracted\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        "ffmpeg.exe",
        "ffmpeg"
    ]

    ffmpeg_path = None
    for path in ffmpeg_paths:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            ffmpeg_path = path
            break
        except:
            continue

    return ffmpeg_path

def load_audio_with_best_method(audio_path, target_sr=16000):
    """
    使用最佳方法加载音频文件
    优先尝试librosa，失败则使用ffmpeg+soundfile
    """
    try:
        # 首先尝试librosa（支持更多格式）
        import librosa

        print(f"尝试使用librosa加载: {os.path.basename(audio_path)}")
        data, sr = librosa.load(audio_path, sr=target_sr, mono=True)
        print(f"SUCCESS: librosa加载成功，采样率: {sr}Hz")
        return data, sr

    except ImportError:
        print("librosa未安装，回退到ffmpeg+soundfile")
        pass
    except Exception as e:
        print(f"librosa加载失败: {e}")
        print("回退到ffmpeg+soundfile")

    # 回退方案：使用ffmpeg转换为wav，然后用soundfile读取
    ffmpeg_path = find_tool_paths()
    if not ffmpeg_path:
        raise Exception("未找到ffmpeg")

    # 创建临时wav文件
    temp_wav = os.path.splitext(audio_path)[0] + "_temp.wav"

    try:
        # 使用ffmpeg转换为wav
        subprocess.run([
            ffmpeg_path,
            '-i', audio_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', str(target_sr),
            temp_wav,
            '-y'
        ], check=True, capture_output=True)

        # 使用soundfile读取
        import soundfile as sf
        data, sr = sf.read(temp_wav)
        if data.ndim > 1:
            data = np.mean(data, axis=1).astype(np.float32)

        print(f"SUCCESS: ffmpeg+soundfile加载成功，采样率: {sr}Hz")

        # 删除临时文件
        os.remove(temp_wav)

        return data, sr

    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
        raise Exception(f"所有方法都失败了: {e}")

def transcribe_audio_segments(audio_path, segment_length=120, task_dir=None):
    """
    分段转录音频，支持更多格式
    """
    if not audio_path or not os.path.exists(audio_path):
        raise Exception("音频文件未找到")

    try:
        import whisper

        # 使用改进的音频加载方法
        data, samplerate = load_audio_with_best_method(audio_path)
        print(f"音频总时长: {len(data)/samplerate/60:.1f} 分钟")

        # 计算分段数量
        segment_samples = segment_length * samplerate
        total_segments = int(len(data) / segment_samples) + (1 if len(data) % segment_samples > 0 else 0)

        print(f"将分为 {total_segments} 段，每段 {segment_length//60} 分钟")
        log_progress(f"开始转录: {total_segments} 段音频", task_dir)

        # 加载 Whisper 模型
        print("加载 Whisper large-v3 模型...")
        model = whisper.load_model('large-v3')
        print("Whisper 模型加载完成")

        segments = []
        for i in range(total_segments):
            start_sample = i * segment_samples
            end_sample = min((i + 1) * segment_samples, len(data))
            segment_data = data[start_sample:end_sample]

            print(f"转录第 {i+1}/{total_segments} 段...")

            # 转录当前段
            result = model.transcribe(audio=segment_data, language='zh', fp16=False, task='transcribe')
            segment_text = result.get('text', '').strip()

            # 转换为简体中文
            from utils import convert_to_simplified_chinese
            simplified_text = convert_to_simplified_chinese(segment_text)

            # 即使没有识别出文字，也要保留段落信息
            segments.append({
                'id': i + 1,
                'start_time': i * segment_length,
                'end_time': min((i + 1) * segment_length, len(data)/samplerate),
                'text': simplified_text,
                'raw_text': simplified_text
            })

        print(f"所有 {total_segments} 段转录完成")
        return segments

    except ImportError:
        raise Exception("Whisper 未安装。请运行: pip install openai-whisper")
    except Exception as e:
        raise Exception(f"转录错误: {str(e)}")

def test_formats():
    """测试不同格式的支持"""
    test_files = [
        r"C:\Users\lenovo\translate\BV1jeUbBYELu\audio\BV1jeUbBYELu.m4a",
        r"C:\Users\lenovo\translate\BV1jeUbBYELu\audio\BV1jeUbBYELu.wav"
    ]

    print("音频格式兼容性测试")
    print("=" * 50)

    for audio_file in test_files:
        if os.path.exists(audio_file):
            print(f"\n测试文件: {os.path.basename(audio_file)}")
            try:
                # 测试加载
                data, sr = load_audio_with_best_method(audio_file)
                print(f"SUCCESS: 可以处理")
                print(f"   采样率: {sr}Hz")
                print(f"   时长: {len(data)/sr:.1f}秒")
            except Exception as e:
                print(f"ERROR: 无法处理 - {e}")

if __name__ == '__main__':
    test_formats()