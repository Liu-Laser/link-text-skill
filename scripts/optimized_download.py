#!/usr/bin/env python3
"""
优化的音频下载函数 - 支持智能格式选择
"""

import os
import subprocess
import json
import glob
import re
from datetime import datetime

def find_tool_paths():
    """在系统中查找工具软件的路径"""
    # 查找 ffmpeg
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

    # 查找 yt-dlp
    yt_dlp_paths = [
        "python",
        "python.exe",
        "python3",
        "python3.exe"
    ]

    yt_dlp_path = None
    for path in yt_dlp_paths:
        try:
            subprocess.run([path, "-m", "yt_dlp", "--version"], capture_output=True, check=True)
            yt_dlp_path = f"{path} -m yt_dlp"
            break
        except:
            continue

    return ffmpeg_path, yt_dlp_path

def test_audio_support(audio_path):
    """测试音频文件是否被Whisper直接支持"""
    try:
        import soundfile as sf
        import numpy as np

        # 读取音频文件
        data, samplerate = sf.read(audio_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1).astype(np.float32)

        print(f"✅ 支持格式: {os.path.splitext(audio_path)[1][1:]}")
        print(f"   采样率: {samplerate}Hz, 时长: {len(data)/samplerate:.1f}秒")
        return True
    except Exception as e:
        print(f"❌ 不支持格式: {os.path.splitext(audio_path)[1][1:]} ({e})")
        return False

def smart_download_media(source, task_dir):
    """智能下载音频，支持直接使用Whisper兼容格式"""
    ffmpeg_path, yt_dlp_path = find_tool_paths()

    if not yt_dlp_path:
        raise Exception("未找到 yt-dlp。请先安装：pip install yt-dlp")

    if not ffmpeg_path:
        raise Exception("未找到 ffmpeg。请确保 ffmpeg 在系统路径中或指定路径。")

    try:
        # 生成文件名
        output_name = source.split('/')[-1].split('?')[0]
        audio_dir = os.path.join(task_dir, 'audio')
        video_dir = os.path.join(task_dir, 'videos')

        # 检查链接类型并制定下载策略
        print(f"[信息] 分析视频链接: {source}")

        # 优先尝试下载Whisper直接兼容的格式
        print("[策略1] 尝试下载Whisper兼容的音频格式...")

        # 优先选择MP3（兼容性好）
        mp3_cmd = yt_dlp_path.split() + [
            source,
            '--no-playlist',
            '-f', 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio',
            '-o', os.path.join(audio_dir, f'{output_name}.%(ext)s')
        ]

        try:
            print(f"尝试命令: {' '.join(mp3_cmd)}")
            subprocess.run(mp3_cmd, check=True, timeout=120)

            # 查找下载的文件
            audio_files = glob.glob(os.path.join(audio_dir, f'{output_name}.*'))
            if audio_files:
                downloaded_file = audio_files[0]
                print(f"✅ 下载成功: {os.path.basename(downloaded_file)}")

                # 测试是否被Whisper直接支持
                if test_audio_support(downloaded_file):
                    print("[成功] 使用原始格式，无需转换")
                    return downloaded_file, {
                        'source': source,
                        'downloaded': True,
                        'ffmpeg_path': ffmpeg_path,
                        'video_files': [],
                        'audio_only': True,
                        'direct_support': True
                    }
                else:
                    print("[转换] 需要转换为WAV格式")
                    wav_file = os.path.join(audio_dir, f'{output_name}.wav')
                    subprocess.run([
                        ffmpeg_path,
                        '-i', downloaded_file,
                        '-vn',
                        '-acodec', 'pcm_s16le',
                        '-ar', '16000',
                        wav_file,
                        '-y'
                    ], check=True)
                    return wav_file, {
                        'source': source,
                        'downloaded': True,
                        'ffmpeg_path': ffmpeg_path,
                        'video_files': [],
                        'audio_only': True,
                        'direct_support': False
                    }
        except Exception as e:
            print(f"❌ 下载失败: {e}")

        # 如果优先格式失败，尝试其他格式
        print("[策略2] 尝试下载其他音频格式...")
        fallback_cmd = yt_dlp_path.split() + [
            source,
            '--no-playlist',
            '-f', 'bestaudio',
            '-o', os.path.join(audio_dir, f'{output_name}.m4a')
        ]

        print(f"尝试命令: {' '.join(fallback_cmd)}")
        subprocess.run(fallback_cmd, check=True)

        m4a_file = os.path.join(audio_dir, f'{output_name}.m4a')
        wav_file = os.path.join(audio_dir, f'{output_name}.wav')

        # 测试m4a是否被支持
        if test_audio_support(m4a_file):
            print("[成功] 直接使用m4a格式")
            return m4a_file, {
                'source': source,
                'downloaded': True,
                'ffmpeg_path': ffmpeg_path,
                'video_files': [],
                'audio_only': True,
                'direct_support': True
            }
        else:
            print("[转换] 转换m4a为wav")
            subprocess.run([
                ffmpeg_path,
                '-i', m4a_file,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                wav_file,
                '-y'
            ], check=True)
            return wav_file, {
                'source': source,
                'downloaded': True,
                'ffmpeg_path': ffmpeg_path,
                'video_files': [],
                'audio_only': True,
                'direct_support': False
            }

    except Exception as e:
        print(f"下载错误: {e}")
        raise

    raise Exception("音频文件下载失败")

def main():
    """主函数用于测试"""
    if len(sys.argv) < 2:
        print("Usage: python optimized_download.py <URL_or_file_path> [output_dir]")
        sys.exit(1)

    source = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "C:\\Users\\lenovo\\translate"

    print("="*60)
    print("智能音频下载测试")
    print("="*60)

    try:
        audio_path, info = smart_download_media(source, output_dir)
        print(f"\n✅ 下载成功: {audio_path}")
        print(f"直接支持: {info.get('direct_support', False)}")
    except Exception as e:
        print(f"❌ 失败: {e}")

if __name__ == '__main__':
    main()