#!/usr/bin/env python3
"""
智能下载策略演示脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def test_intelligent_download():
    """测试智能下载策略的不同场景"""

    print("=" * 60)
    print("Link-Text 智能下载策略演示")
    print("=" * 60)

    # 测试案例1：B站视频（应该只下载音频）
    print("\n[测试案例 1] B站视频（应该只下载音频）")
    print("URL: https://www.bilibili.com/video/BV1jeUbBYELu?t=1457.4&p=61")

    test_dir1 = os.path.join("D:", "test", "bilibili_audio")
    Path(test_dir1).mkdir(parents=True, exist_ok=True)

    cmd1 = ['python', 'main_simplified.py', "https://www.bilibili.com/video/BV1jeUbBYELu?t=1457.4&p=61", test_dir1]
    print(f"执行命令: {' '.join(cmd1)}")

    try:
        result1 = subprocess.run(cmd1, timeout=300, capture_output=True, text=True)
        if result1.returncode == 0:
            print("✅ B站视频测试成功！")

            # 检查输出文件
            audio_files = []
            for root, dirs, files in os.walk(test_dir1):
                for file in files:
                    if file.endswith(('.wav', '.m4a')):
                        audio_files.append(os.path.join(root, file))

            print(f"下载的音频文件: {len(audio_files)} 个")
            for f in audio_files:
                size = os.path.getsize(f) / (1024 * 1024)  # MB
                print(f"  - {os.path.basename(f)}: {size:.2f} MB")

            # 检查是否有视频文件
            video_files = []
            for root, dirs, files in os.walk(test_dir1):
                for file in files:
                    if file.endswith(('.mp4', '.avi', '.mkv', '.mov')):
                        video_files.append(os.path.join(root, file))

            if video_files:
                print("❌ 警告：下载了视频文件！")
                for f in video_files:
                    print(f"  - {os.path.basename(f)}")
            else:
                print("✅ 没有下载视频文件，智能下载策略生效！")

        else:
            print(f"❌ B站视频测试失败: {result1.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ B站视频测试超时")
    except Exception as e:
        print(f"❌ B站视频测试错误: {e}")

    # 测试案例2：本地音频文件
    print("\n[测试案例 2] 本地音频文件（应该直接复制）")
    local_audio = os.path.join("D:", "test", "sample_audio.mp3")

    # 如果不存在示例文件，创建一个简单的
    if not os.path.exists(local_audio):
        print(f"创建示例音频文件: {local_audio}")
        try:
            # 使用ffmpeg创建一个测试音频文件
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=10:size=320x240:rate=1',
                '-c:a', 'libmp3lame', '-t', '5', local_audio
            ], check=True)
            print("✅ 示例音频文件创建成功")
        except:
            print("❌ 无法创建示例音频文件，跳过测试案例2")
            local_audio = None

    if local_audio and os.path.exists(local_audio):
        test_dir2 = os.path.join("D:", "test", "local_audio")
        Path(test_dir2).mkdir(parents=True, exist_ok=True)

        cmd2 = ['python', 'main_simplified.py', local_audio, test_dir2]
        print(f"执行命令: {' '.join(cmd2)}")

        try:
            result2 = subprocess.run(cmd2, timeout=60, capture_output=True, text=True)
            if result2.returncode == 0:
                print("✅ 本地音频测试成功！")

                # 检查输出
                output_files = []
                for root, dirs, files in os.walk(test_dir2):
                    for file in files:
                        if file.endswith(('.wav', '.mp3', '.m4a')):
                            output_files.append(os.path.join(root, file))

                print(f"处理的音频文件: {len(output_files)} 个")
                for f in output_files:
                    print(f"  - {os.path.basename(f)}")
            else:
                print(f"❌ 本地音频测试失败: {result2.stderr}")
        except Exception as e:
            print(f"❌ 本地音频测试错误: {e}")

    # 测试案例3：本地视频文件
    print("\n[测试案例 3] 本地视频文件（应该提取音频）")
    local_video = os.path.join("D:", "test", "sample_video.mp4")

    # 如果不存在示例视频文件，创建一个简单的
    if not os.path.exists(local_video):
        print(f"创建示例视频文件: {local_video}")
        try:
            # 使用ffmpeg创建一个测试视频文件
            subprocess.run([
                'ffmpeg', '-f', 'lavfi',
                '-i', 'testsrc=duration=10:size=320x240:rate=1, sine=frequency=1000:duration=10',
                '-c:v', 'libx264', '-t', '5', local_video
            ], check=True)
            print("✅ 示例视频文件创建成功")
        except:
            print("❌ 无法创建示例视频文件，跳过测试案例3")
            local_video = None

    if local_video and os.path.exists(local_video):
        test_dir3 = os.path.join("D:", "test", "local_video")
        Path(test_dir3).mkdir(parents=True, exist_ok=True)

        cmd3 = ['python', 'main_simplified.py', local_video, test_dir3]
        print(f"执行命令: {' '.join(cmd3)}")

        try:
            result3 = subprocess.run(cmd3, timeout=120, capture_output=True, text=True)
            if result3.returncode == 0:
                print("✅ 本地视频测试成功！")

                # 检查输出
                audio_files = []
                video_files = []
                for root, dirs, files in os.walk(test_dir3):
                    for file in files:
                        if file.endswith(('.wav', '.mp3', '.m4a')):
                            audio_files.append(os.path.join(root, file))
                        elif file.endswith(('.mp4', '.avi', '.mkv', '.mov')):
                            video_files.append(os.path.join(root, file))

                print(f"提取的音频文件: {len(audio_files)} 个")
                for f in audio_files:
                    print(f"  - {os.path.basename(f)}")

                print(f"保留的视频文件: {len(video_files)} 个")
                for f in video_files:
                    print(f"  - {os.path.basename(f)}")
            else:
                print(f"❌ 本地视频测试失败: {result3.stderr}")
        except Exception as e:
            print(f"❌ 本地视频测试错误: {e}")

    print("\n" + "=" * 60)
    print("智能下载策略演示完成！")
    print("=" * 60)

if __name__ == '__main__':
    test_intelligent_download()