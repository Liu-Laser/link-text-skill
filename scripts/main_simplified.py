#!/usr/bin/env python3
"""
Link-Text 主脚本 - 下载媒体并转录为简体中文
"""

import sys
import os
import subprocess
import json
import glob
import re
import uuid
from datetime import datetime
from pathlib import Path
from utils import convert_to_simplified_chinese, ensure_simplified_chinese, clean_and_normalize_text

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_simplified.py <URL_or_file_path> [output_base_dir]")
        print("参数说明:")
        print("- URL_or_file_path: B站视频 URL 或本地音频文件路径")
        print("- output_base_dir: 可选，基础输出目录（默认: C:\\Users\\lenovo\\translate）")
        sys.exit(1)

    input_source = sys.argv[1]
    output_base_dir = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\lenovo\translate"

    print("="*60)
    print("Link-Text 智能转录系统 - 简体中文版")
    print("="*60)

    # Step 0: 创建任务目录
    print("\n[Step 0] 创建任务目录...")
    try:
        # 使用输入源作为目录名称（去掉协议和特殊字符）
        if input_source.startswith('http'):
            # 从URL提取文件名
            video_name = input_source.split('/')[-1].split('?')[0]
        else:
            # 使用本地文件名
            video_name = os.path.basename(input_source)

        # 清理文件名，移除特殊字符
        video_name = re.sub(r'[^\w\-_\.]', '_', video_name)

        # 创建基于视频名称的临时目录
        temp_task_dir = os.path.join(output_base_dir, video_name)
        Path(temp_task_dir).mkdir(parents=True, exist_ok=True)

        # 创建子目录
        Path(os.path.join(temp_task_dir, 'audio')).mkdir(exist_ok=True)
        Path(os.path.join(temp_task_dir, 'videos')).mkdir(exist_ok=True)
        Path(os.path.join(temp_task_dir, 'output')).mkdir(exist_ok=True)

        print(f"临时任务目录已创建: {temp_task_dir}")
    except Exception as e:
        print(f"创建任务目录失败: {e}")
        sys.exit(1)

    # Step 1: 下载媒体
    print("\n[Step 1] 下载媒体...")
    try:
        audio_path, video_info = download_media(input_source, temp_task_dir)
        print(f"音频文件已下载: {audio_path}")
    except Exception as e:
        print(f"下载失败: {e}")
        sys.exit(1)

    # Step 2: 分段转录
    print("\n[Step 2] 开始分段转录...")
    print("设置: 每段2分钟，使用 Whisper large-v3 模型")
    try:
        segments = transcribe_audio_segments(audio_path, segment_length=120)  # 2分钟 = 120秒
        print(f"转录完成，共 {len(segments)} 个段落")
    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

    # Step 3: 确保简体中文
    print("\n[Step 3] 确保文本为简体中文...")
    try:
        processed_segments = []
        for segment in segments:
            # 转换为简体中文并清理文本
            text = convert_to_simplified_chinese(segment['text'])
            text = clean_and_normalize_text(text)
            segment['text'] = text
            segment['raw_text'] = text
            processed_segments.append(segment)

        print("简体中文转换完成")

        # 生成目录
        table_of_contents = generate_table_of_contents(processed_segments)

        # 提取视频标题
        video_title = get_video_name_from_url(input_source, output_base_dir)
    except Exception as e:
        print(f"处理失败: {e}")
        processed_segments = segments
        table_of_contents = []
        video_title = get_video_name_from_url(input_source, output_base_dir)

    # Step 4: 生成结构化 Markdown
    print("\n[Step 4] 生成结构化 Markdown...")
    md_content = create_markdown(processed_segments, table_of_contents, video_info, video_title)

    # Step 5: 保存文件
    print("\n[Step 5] 保存文件...")
    try:
        # 创建基于视频标题的最终目录
        final_dir = os.path.join(output_base_dir, video_title)
        if final_dir != temp_task_dir:
            # 移动临时目录到标题目录
            if os.path.exists(final_dir):
                # 如果目录已存在，添加时间戳
                timestamp_suffix = datetime.now().strftime('_%Y%m%d_%H%M%S')
                final_dir = final_dir + timestamp_suffix

            os.rename(temp_task_dir, final_dir)
            temp_task_dir = final_dir

        # 生成文件名（使用视频标题）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'转录_{video_title}_{timestamp}.md'

        output_path = save_markdown(md_content, temp_task_dir, filename)

        print(f"转录文件已保存: {output_path}")
        print(f"最终目录: {temp_task_dir}")
    except Exception as e:
        print(f"保存文件失败: {e}")
        sys.exit(1)

    # 生成任务信息文件
    task_info = {
        'video_name': video_title,
        'input_source': input_source,
        'task_dir': temp_task_dir,
        'audio_file': audio_path,
        'output_file': output_path,
        'transcription_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'segments_count': len(processed_segments),
        'model': 'Whisper large-v3',
        'segment_duration': 120,  # 2分钟
        'topic': video_title,
        'language': 'zh-CN'
    }

    info_file = os.path.join(temp_task_dir, 'task_info.json')
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)

    print(f"\n任务信息已保存: {info_file}")

    print("\n" + "="*60)
    print(f"[完成] 所有文件已保存到目录: {temp_task_dir}")
    print("="*60)
    print("\n文件结构:")
    print(f"  {temp_task_dir}/")
    print(f"  ├── audio/          # 音频文件（每2分钟一段）")
    print(f"  ├── videos/         # 原始视频文件")
    print(f"  ├── output/         # 转录结果")
    print(f"  └── task_info.json  # 任务信息")
    print(f"  主题: {video_title}")
    print("  语言: 简体中文")
    print("="*60)

    # 启动监控器
    print("\n[监控] 启动任务监控...")
    try:
        import subprocess
        import time

        # 获取音频时长用于估算处理时间
        audio_duration = None
        audio_file = None

        # 查找音频文件
        audio_dir = os.path.join(temp_task_dir, 'audio')
        if os.path.exists(audio_dir):
            audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.wav', '.mp3', '.m4a'))]
            if audio_files:
                audio_file = os.path.join(audio_dir, audio_files[0])
                # 尝试获取音频时长
                try:
                    result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio_file],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        duration_seconds = float(result.stdout.strip())
                        audio_duration = duration_seconds / 60
                except:
                    pass

        # 构建监控器命令
        monitor_cmd = ['python', 'monitor_transcription.py', temp_task_dir]
        if audio_duration:
            monitor_cmd.append(str(audio_duration))

        # 在后台启动监控器
        process = subprocess.Popen(monitor_cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        print(f"[监控] 监控器已启动 (PID: {process.pid})")
        print(f"[信息] 如需监控进度，请查看输出文件: {output_path}")

    except Exception as e:
        print(f"[警告] 启动监控器失败: {e}")
        print("[提示] 任务已完成，请手动检查输出文件")

def get_video_name_from_url(input_source, output_base_dir):
    """从URL获取视频名称"""
    if input_source.startswith('http'):
        # 从URL提取文件名
        video_name = input_source.split('/')[-1].split('?')[0]
        # 清理文件名，移除特殊字符
        video_name = re.sub(r'[^\w\-_\.]', '_', video_name)
        if len(video_name) < 3:
            video_name = f"转录_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        # 使用本地文件名
        video_name = os.path.basename(input_source)
        video_name = re.sub(r'[^\w\-_\.]', '_', video_name)

    return video_name

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

def download_media(source, task_dir):
    """从 URL 下载视频音频，使用系统中的工具路径"""
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

        # 使用 yt-dlp 下载音频 - 添加 --no-playlist 避免下载合集
        cmd = yt_dlp_path.split() + [source, '--no-playlist', '-o', os.path.join(video_dir, f'{output_name}.%(ext)s')]

        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        # 查找下载的文件
        video_files = glob.glob(os.path.join(video_dir, f'{output_name}.*'))

        # 优先查找音频文件
        audio_files = glob.glob(os.path.join(video_dir, f'{output_name}.*m4a'))
        if audio_files:
            # 直接使用 M4A 音频文件
            audio_file = os.path.join(audio_dir, f'{output_name}.wav')
            # 转换 M4A 到 WAV
            subprocess.run([
                ffmpeg_path,
                '-i', audio_files[0],
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                audio_file,
                '-y'
            ], check=True)
            return audio_file, {'source': source, 'downloaded': True, 'ffmpeg_path': ffmpeg_path, 'video_files': video_files}
        elif video_files:
            # 提取音频为 WAV
            audio_file = os.path.join(audio_dir, f'{output_name}.wav')
            subprocess.run([
                ffmpeg_path,
                '-i', video_files[0],
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                audio_file,
                '-y'
            ], check=True)

            return audio_file, {'source': source, 'downloaded': True, 'ffmpeg_path': ffmpeg_path, 'video_files': video_files}

    except Exception as e:
        print(f"下载错误: {e}")
        raise

    raise Exception("音频文件下载失败")

def transcribe_audio_segments(audio_path, segment_length=120):  # 默认2分钟
    """分段转录音频，每 segment_length 秒一段"""
    if not audio_path or not os.path.exists(audio_path):
        raise Exception("音频文件未找到")

    try:
        import whisper
        import numpy as np
        import soundfile as sf

        # 读取音频文件
        data, samplerate = sf.read(audio_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1).astype(np.float32)

        # 计算分段数量
        total_samples = len(data)
        segment_samples = segment_length * samplerate
        total_segments = int(total_samples / segment_samples) + (1 if total_samples % segment_samples > 0 else 0)

        total_minutes = total_samples / samplerate / 60
        print(f"音频总时长: {total_minutes:.1f} 分钟，将分为 {total_segments} 段，每段 {segment_length//60} 分钟")

        # 加载 Whisper large-v3 模型
        print("加载 Whisper large-v3 模型...")
        model = whisper.load_model('large-v3')

        segments = []
        for i in range(total_segments):
            start_sample = i * segment_samples
            end_sample = min((i + 1) * segment_samples, total_samples)
            segment_data = data[start_sample:end_sample]

            print(f"转录第 {i+1}/{total_segments} 段...")

            # 转录当前段
            result = model.transcribe(audio=segment_data, language='zh', fp16=False, task='transcribe', beam_size=5, best_of=5, temperature=0.0)
            segment_text = result.get('text', '').strip()

            # 转换为简体中文
            simplified_text = convert_to_simplified_chinese(segment_text)

            # 即使没有识别出文字，也要保留段落信息
            segments.append({
                'id': i + 1,
                'start_time': i * segment_length,
                'end_time': min((i + 1) * segment_length, total_samples/samplerate),
                'text': simplified_text,
                'raw_text': simplified_text
            })

        return segments

    except ImportError:
        raise Exception("Whisper 未安装。请运行: pip install openai-whisper")
    except Exception as e:
        raise Exception(f"转录错误: {str(e)}")

def generate_table_of_contents(processed_segments):
    """生成目录"""
    table_of_contents = []

    for segment in processed_segments:
        # 获取第一句作为标题
        if 'sentences' in segment and segment['sentences'] and len(segment['sentences']) > 0:
            # 取第一句的前15个字符作为标题
            title = segment['sentences'][0][:15]
            if len(segment['sentences'][0]) > 15:
                title += '...'
        else:
            title = f"第{segment['id']}段"

        table_of_contents.append(
            f"- **第{segment['id']}段** ({segment['start_time']//60:.0f}-{segment['end_time']//60:.0f}分钟): {title}"
        )

    return table_of_contents

def create_markdown(processed_segments, table_of_contents, video_info, video_title=None):
    """创建结构化的 Markdown 内容"""
    title = video_info.get('source', 'Unknown Source')
    date_str = datetime.now().strftime('%Y-%m-%d')
    model = 'Whisper large-v3'

    frontmatter = f"""---
title: {video_title if video_title else title}
source_url: {video_info.get('source', '')}
transcription_date: {date_str}
model: {model}
language: zh-CN
segment_duration: 120 seconds (2 minutes)
enhanced: true
simplified: true
topic: {video_title if video_title else '未知主题'}
---

"""

    # 生成目录
    toc_content = "\n\n## 目录\n\n" + "\n".join(table_of_contents) + "\n"

    # 生成转录内容
    content = "# 视频转录\n\n"
    content += toc_content
    content += "\n---\n\n"

    # 添加转录内容
    if processed_segments and len(processed_segments) > 0:
        content += "## 转录内容\n\n"

        for segment in processed_segments:
            # 转换时间为分钟显示
            start_min = segment['start_time'] // 60
            end_min = segment['end_time'] // 60
            content += f"\n### 第 {segment['id']} 段 ({start_min}-{end_min}分钟)\n\n"

            # 显示分句
            if 'sentences' in segment and segment['sentences']:
                for i, sentence in enumerate(segment['sentences'], 1):
                    content += f"{i}. {sentence}\n\n"
            else:
                # 如果没有分句，显示原始文本
                content += f"{segment['text']}\n\n"

            content += "---\n\n"

    # 添加总结
    content += "## 总结\n\n"
    content += f"- 本视频共转录了 {len(processed_segments)} 个段落\n"
    content += f"- 每段时长约 2 分钟\n"
    content += f"- 使用 {model} 模型进行语音识别\n"
    content += f"- 已添加自然断句和标点符号\n"
    content += f"- 确保所有内容均为简体中文\n\n"
    content += "*Generated by simplified link-text skill*"

    return frontmatter + content

def save_markdown(content, task_dir, filename=None):
    """保存 Markdown 到任务目录中。"""
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'transcript_{timestamp}.md'

    filepath = os.path.join(task_dir, filename)

    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)

    return filepath

def copy_file_to_task_dir(source_path, task_dir, subdir=None):
    """将文件复制到任务目录中"""
    if not os.path.exists(source_path):
        return None

    if subdir:
        target_dir = os.path.join(task_dir, subdir)
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        target_path = os.path.join(target_dir, os.path.basename(source_path))
    else:
        target_path = os.path.join(task_dir, os.path.basename(source_path))

    import shutil
    shutil.copy2(source_path, target_path)

    return target_path

if __name__ == '__main__':
    main()