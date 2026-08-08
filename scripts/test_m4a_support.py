#!/usr/bin/env python3
"""
测试Whisper是否直接支持m4a格式
"""

import os
import sys
import soundfile as sf
import numpy as np

def test_audio_format(audio_path):
    """测试音频格式是否被Whisper支持"""
    print(f"测试文件: {audio_path}")

    if not os.path.exists(audio_path):
        print("❌ 文件不存在")
        return False

    try:
        # 使用soundfile读取音频文件
        data, samplerate = sf.read(audio_path)
        print(f"✅ 成功读取音频")
        print(f"   - 采样率: {samplerate} Hz")
        print(f"   - 通道数: {data.ndim if data.ndim > 1 else 1}")
        print(f"   - 时长: {len(data)/samplerate:.2f} 秒")
        print(f"   - 数据类型: {data.dtype}")

        # 如果是立体声，转换为单声
        if data.ndim > 1:
            data = np.mean(data, axis=1).astype(np.float32)
            print(f"   - 已转换为单声")

        return True

    except Exception as e:
        print(f"❌ 读取失败: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_m4a_support.py <audio_file>")
        print("参数说明:")
        print("- audio_file: 音频文件路径（支持m4a、wav、mp3等）")
        sys.exit(1)

    audio_file = sys.argv[1]

    print("="*60)
    print("Whisper音频格式支持测试")
    print("="*60)

    # 测试文件
    success = test_audio_format(audio_file)

    print("\n" + "="*60)
    if success:
        print("✅ 该音频格式可以被Whisper直接使用")
        print("   建议直接使用此文件进行转录，无需转换")
    else:
        print("❌ 该音频格式可能不被支持")
        print("   需要转换为WAV格式后再进行转录")
    print("="*60)

if __name__ == '__main__':
    main()