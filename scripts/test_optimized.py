#!/usr/bin/env python3
"""
测试优化后的音频处理
"""

import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_simplified import load_audio_directly

def test_audio_loading():
    """测试音频文件加载"""
    test_files = [
        r"C:\Users\lenovo\translate\BV1jeUbBYELu\audio\BV1jeUbBYELu.m4a",
        r"C:\Users\lenovo\translate\BV1jeUbBYELu\audio\BV1jeUbBYELu.wav"
    ]

    print("音频加载测试")
    print("=" * 50)

    for audio_file in test_files:
        if os.path.exists(audio_file):
            print(f"\n测试文件: {os.path.basename(audio_file)}")
            try:
                data, samplerate = load_audio_directly(audio_file)
                print(f"SUCCESS: 加载成功")
                print(f"   采样率: {samplerate}Hz")
                print(f"   数据长度: {len(data)}")
                print(f"   时长: {len(data)/samplerate:.1f}秒")
                print(f"   数据类型: {data.dtype}")
            except Exception as e:
                print(f"ERROR: 加载失败 - {e}")

if __name__ == '__main__':
    test_audio_loading()