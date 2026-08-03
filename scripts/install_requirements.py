#!/usr/bin/env python3
"""
安装 link-text 技能所需的依赖包
"""

import subprocess
import sys

def install_package(package):
    """安装Python包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    print("Link-Text 技能依赖安装程序")
    print("="*50)

    # 必需的包
    required_packages = [
        "openai-whisper",
        "opencc",
        "psutil",
        "yt-dlp",
        "soundfile"
    ]

    # 可选但推荐的包
    optional_packages = [
        "ffmpeg-python",
        "numpy",
        "scipy"
    ]

    print("\n正在安装必需的包...")
    success_count = 0
    for package in required_packages:
        if install_package(package):
            success_count += 1

    print(f"\n必需包安装完成: {success_count}/{len(required_packages)}")

    print("\n正在安装可选的包...")
    for package in optional_packages:
        install_package(package)

    print("\n" + "="*50)
    print("安装完成！")
    print("\n下一步操作:")
    print("1. 下载 FFmpeg: https://ffmpeg.org/download.html")
    print("2. 将 FFmpeg 添加到系统 PATH")
    print("3. 运行: python scripts/main_simplified.py <视频URL>")
    print("\n注意事项:")
    print("- FFmpeg 是必需的，请确保已正确安装")
    print("- 建议使用 Python 3.8 或更高版本")

if __name__ == "__main__":
    main()