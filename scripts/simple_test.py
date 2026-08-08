#!/usr/bin/env python3
"""
简单的音频格式测试
"""

import os
import sys
import soundfile as sf
import numpy as np

def test_audio_format(audio_path):
    """测试音频格式"""
    print("测试文件: " + audio_path)

    if not os.path.exists(audio_path):
        print("ERROR: 文件不存在")
        return False

    try:
        # 使用soundfile读取音频文件
        data, samplerate = sf.read(audio_path)
        print("SUCCESS: 成功读取音频")
        print("   - 采样率:", samplerate, "Hz")
        print("   - 通道数:", data.ndim if data.ndim > 1 else 1)
        print("   - 时长:", len(data)/samplerate, "秒")
        print("   - 数据类型:", data.dtype)

        # 如果是立体声，转换为单声
        if data.ndim > 1:
            data = np.mean(data, axis=1).astype(np.float32)
            print("   - 已转换为单声")

        return True

    except Exception as e:
        print("ERROR: 读取失败: " + str(e))
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_test.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    print("=" * 50)
    print("音频格式测试")
    print("=" * 50)

    # 测试文件
    success = test_audio_format(audio_file)

    print("=" * 50)
    if success:
        print("SUCCESS: 该音频格式可以被使用")
    else:
        print("ERROR: 该音频格式不支持")
    print("=" * 50)

if __name__ == '__main__':
    main()