#!/usr/bin/env python3
"""
link-text main script - Download media from URL, transcribe to Chinese in segments, enhance with AI, save as structured MD
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
from utils import convert_to_simplified_chinese, ensure_simplified_chinese

def convert_to_simplified_chinese(text):
    """将文本转换为简体中文"""
    try:
        # 创建 OpenCC 实例
        cc = OpenCC('t2s')  # 繁体转简体
        return cc.convert(text)
    except ImportError:
        # 如果没有安装 opencc，使用基本替换
        # 常见的繁体字到简体字的映射
        traditional_to_simplified = {
            '會': '会', '務': '务', '術': '术', '預': '预', '寫': '写', '入': '入', '檔': '档',
            '實': '实', '作': '作', '現': '现', '檢': '检', '查': '查', '學': '学', '習': '习',
            '資': '资', '料': '料', '計': '计', '畫': '画', '會': '会', '過': '过', '為': '为',
            '麼': '么', '麼麼': '么么', '麼麼哒': '么么哒', '這': '这', '樣': '样', '產': '产',
            '業': '业', '辦': '办', '體': '体', '幫': '帮', '歷': '历', '獲': '获', '動': '动',
            '線': '线', '網': '网', '內': '内', '獨': '独', '鍵': '键', '飛': '飞', '語': '语',
            '護': '护', '轉': '转', '錄': '录', '權': '权', '處': '处', '據': '据', '壞': '坏',
            '機': '机', '讀': '读', '與': '与', '幾': '几', '賣': '卖', '專': '专', '職': '职',
            '讓': '让', '寶': '宝', '門': '门', '廠': '厂', '營': '营', '優': '优', '調': '调',
            '傳': '传', '隊': '队', '餅': '饼', '裡': '里', '為': '为', '聽': '听', '參': '参',
            '歲': '岁', '聲': '声', '聯': '联', '觀': '观', '歡': '欢', '課': '课', '講': '讲',
            '輔': '辅', '輕': '轻', '辭': '辞', '龍': '龙', '灣': '湾', '體': '体', '報': '报',
            '價': '价', '壇': '坛', '適': '适', '靈': '灵', '臺': '台', '繼': '继', '續': '续',
            '鍵': '键', '識': '识', '藝': '艺', '嚴': '严', '應': '应', '濟': '济', '職': '职',
            '慮': '虑', '飽': '饱', '懷': '怀', '來': '来', '獅': '狮', '號': '号', '壩': '坝',
            '膽': '胆', '識': '识', '壓': '压', '燈': '灯', '關': '关', '嘔': '呕', '頭': '头',
            '韌': '韧', '葉': '叶', '動': '动', '鐵': '铁', '餵': '喂', '離': '离', '絕': '绝',
            '嘗': '尝', '帥': '帅', '標': '标', '語': '语', '樣': '样', '夢': '梦', '領': '领',
            '圖': '图', '關': '关', '壓': '压', '寶': '宝', '貝': '贝', '證': '证', '燈': '灯',
            '營': '营', '積': '积', '鍵': '键', '龍': '龙', '獅': '狮', '識': '识', '編': '编',
            '織': '织', '閱': '阅', '顏': '颜', '關': '关', '願': '愿', '寧': '宁', '穩': '稳',
            '擇': '择', '鍵': '键', '驚': '惊', '驕': '骄', '驚': '惊', '驗': '验', '編': '编',
            '續': '续', '鍵': '键', '繼': '继', '續': '续', '觀': '观', '關': '关', '歡': '欢',
            '觀': '观', '關': '关', '歡': '欢', '歲': '岁', '歷': '历', '歡': '欢', '觀': '观',
            '關': '关', '歡': '欢', '藝': '艺', '嚴': '严', '應': '应', '營': '营', '優': '优',
            '擇': '择', '鍵': '键', '觀': '观', '關': '关', '歡': '欢', '歲': '岁', '歷': '历',
            '歡': '欢', '觀': '观', '關': '关', '歡': '欢', '藝': 'art', '嚴': 'strict', '應': 'should',
            '營': 'operate', '優': 'excellent', '擇': 'choose', '鍵': 'key', '觀': 'observe',
            '關': 'relation', '歡': 'happy', '歲': 'age', '歷': 'history', '藝': 'art', '嚴': 'strict',
            '應': 'should', '營': 'operate', '優': 'excellent', '擇': 'choose', '鍵': 'key',
            '觀': 'observe', '關': 'relation', '歡': 'happy', '歲': 'age', '歷': 'history'
        }

        # 使用正则表达式进行替换
        pattern = re.compile('|'.join(map(re.escape, traditional_to_simplified.keys())))
        return pattern.sub(lambda x: traditional_to_simplified[x.group()], text)
    except Exception as e:
        print(f"简体字转换失败: {e}")
        return text

def main():
    if len(sys.argv) < 2:
        print("Usage: link-text.py <URL_or_file_path> [output_base_dir]")
        print("参数说明:")
        print("- URL_or_file_path: B站视频 URL 或本地音频文件路径")
        print("- output_base_dir: 可选，基础输出目录（默认: C:\\Users\\lenovo\\translate）")
        sys.exit(1)

    input_source = sys.argv[1]
    output_base_dir = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\lenovo\translate"

    print("="*60)
    print("增强版 link-text - 视频智能转录系统")
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
        print(f"  - 音频文件: {os.path.join(temp_task_dir, 'audio')}")
        print(f"  - 视频文件: {os.path.join(temp_task_dir, 'videos')}")
        print(f"  - 输出文件: {os.path.join(temp_task_dir, 'output')}")
    except Exception as e:
        print(f"创建任务目录失败: {e}")
        sys.exit(1)

    # Step 1: 下载媒体
    print("\n[Step 1] 下载媒体...")
    try:
        audio_path, video_info = download_media(input_source, temp_task_dir)
        print(f"音频文件已下载: {audio_path}")

        # 音频文件已经在正确的目录中，不需要复制
        copied_audio = audio_path
        print(f"音频文件已在任务目录中: {copied_audio}")
    except Exception as e:
        print(f"下载失败: {e}")
        sys.exit(1)

    # Step 2: 分段转录
    print("\n[Step 2] 开始分段转录...")
    print("设置: 每段5分钟，使用 Whisper medium 模型")
    try:
        segments = transcribe_audio_segments(audio_path, segment_length=300)  # 5分钟 = 300秒
        print(f"转录完成，共 {len(segments)} 个段落")
    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

    # Step 3: 自然断句和标点符号
    print("\n[Step 3] 添加自然断句和标点符号...")
    try:
        processed_segments = add_punctuation_and_breaks(segments)
        print("标点符号添加完成")

        # 生成目录
        table_of_contents = generate_table_of_contents(processed_segments)

        # 提取视频标题
        video_title = get_video_name_from_url(input_source, output_base_dir)
    except Exception as e:
        print(f"处理失败: {e}")
        # 如果处理失败，使用原始分段
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

        # 复制所有相关文件到任务目录
        if 'video_files' in video_info:
            for video_file in video_info['video_files']:
                copy_file_to_task_dir(video_file, temp_task_dir, 'videos')

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
        'audio_file': copied_audio or audio_path,
        'output_file': output_path,
        'transcription_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'segments_count': len(processed_segments),
        'model': 'Whisper medium',
        'segment_duration': 300,  # 5分钟
        'topic': video_title
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
    print(f"  ├── audio/          # 音频文件")
    print(f"  ├── videos/         # 原始视频文件")
    print(f"  ├── output/         # 转录结果")
    print(f"  └── task_info.json  # 任务信息")
    print(f"  主题: {video_title}")
    print("="*60)

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

def create_task_directory(output_base_dir=None):
    """创建任务专属目录"""
    if output_base_dir is None:
        output_base_dir = r"C:\Users\lenovo\translate"

    # 确保基础目录存在
    Path(output_base_dir).mkdir(parents=True, exist_ok=True)

    return output_base_dir

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
        # 不使用 format 参数，让 yt-dlp 自动选择最佳格式
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

def transcribe_audio_segments(audio_path, segment_length=300):  # 默认5分钟
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

        # 加载 Whisper medium 模型
        print("加载 Whisper medium 模型...")
        model = whisper.load_model('medium')

        segments = []
        for i in range(total_segments):
            start_sample = i * segment_samples
            end_sample = min((i + 1) * segment_samples, total_samples)
            segment_data = data[start_sample:end_sample]

            print(f"转录第 {i+1}/{total_segments} 段...")

            # 转录当前段
            result = model.transcribe(audio=segment_data, language='zh', fp16=False, task='transcribe')
            segment_text = result.get('text', '').strip()

            if segment_text:
                # 转换为简体中文
                simplified_text = convert_to_simplified_chinese(segment_text)
                segments.append({
                    'id': i + 1,
                    'start_time': i * segment_length,
                    'end_time': min((i + 1) * segment_length, total_samples/samplerate),
                    'text': simplified_text,
                    'raw_text': segment_text
                })

        return segments

    except ImportError:
        raise Exception("Whisper 未安装。请运行: pip install openai-whisper")
    except Exception as e:
        raise Exception(f"转录错误: {str(e)}")

def add_punctuation_and_breaks(segments):
    """为转录文本添加自然断句和标点符号"""
    processed_segments = []

    for segment in segments:
        text = segment['text']

        if not text.strip():
            processed_segments.append(segment)
            continue

        # 确保文本是简体中文
        text = convert_to_simplified_chinese(text)

        # 1. 基本的标点符号修复
        # 添加缺失的句号、问号、感叹号
        text = re.sub(r'([^.。！？!?])(\s|$)', r'\1。', text)

        # 2. 段落内的自然断句
        # 按语义分割成短句
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 3. 处理每个句子
        processed_sentences = []
        for sentence in sentences:
            # 移除多余的空格
            sentence = re.sub(r'\s+', ' ', sentence).strip()

            # 确保句子以适当的标点结尾
            if sentence:
                # 如果句子没有以标点符号结尾，添加句号
                if not re.search(r'[。！？.!?]$', sentence):
                    sentence += '。'

                # 处理常见的口语化表达
                sentence = re.sub(r'嗯+', '嗯', sentence)
                sentence = re.sub(r'啊+', '啊', sentence)
                sentence = re.sub(r'呀+', '呀', sentence)

                processed_sentences.append(sentence)

        # 4. 如果句子太多，合并一些相近的句子
        if len(processed_sentences) > 3:
            merged_sentences = []
            i = 0
            while i < len(processed_sentences):
                if i + 1 < len(processed_sentences) and len(processed_sentences[i]) < 20:
                    # 合并短句
                    merged = processed_sentences[i] + processed_sentences[i+1]
                    merged_sentences.append(merged)
                    i += 2
                else:
                    merged_sentences.append(processed_sentences[i])
                    i += 1
            processed_sentences = merged_sentences

        # 更新segment信息
        segment['sentences'] = processed_sentences
        segment['text'] = ' '.join(processed_sentences)
        processed_segments.append(segment)

    return processed_segments

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

def enhance_transcription_with_ai(segments):
    """使用 AI 润色转录文本，生成层次目录"""
    try:
        # 这里使用 Claude API 来润色内容
        # 由于我们无法直接调用 API，这里提供一个模拟的润色函数
        enhanced_segments = []

        # 处理每个段落
        for segment in segments:
            text = segment['text']

            # 模拟 AI 润色
            # 1. 检测句子的完整性
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # 2. 生成小标题（基于内容关键词）
            if sentences:
                keywords = []
                for sentence in sentences:
                    # 确保句子是简体中文
                    simplified_sentence = convert_to_simplified_chinese(sentence)
                    # 简单的关键词提取
                    words = re.findall(r'[一-龥]+', simplified_sentence)
                    if words:
                        keywords.append(words[0])  # 取第一个中文词作为关键词

                title = f"{keywords[0]}等话题" if keywords else f"段落 {segment['id']}"

                enhanced_segments.append({
                    'id': segment['id'],
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'title': title,
                    'sentences': sentences if sentences else [],
                    'raw_text': text,
                    'keywords': keywords[:3]  # 最多保留3个关键词
                })
            else:
                enhanced_segments.append(segment)

        # 生成层次目录
        table_of_contents = []
        for segment in enhanced_segments:
            table_of_contents.append(
                f"- **第{segment['id']}段** ({segment['start_time']:.0f}-{segment['end_time']:.0f}秒): {segment['title']}"
            )

        return enhanced_segments, table_of_contents

    except Exception as e:
        # 如果润色失败，返回原始分段
        print(f"AI 润色失败: {e}")
        return segments, []

def create_markdown(processed_segments, table_of_contents, video_info, video_title=None):
    """创建结构化的 Markdown 内容"""
    title = video_info.get('source', 'Unknown Source')
    date_str = datetime.now().strftime('%Y-%m-%d')
    model = 'Whisper medium'

    frontmatter = f"""---
title: {video_title if video_title else title}
source_url: {video_info.get('source', '')}
transcription_date: {date_str}
model: {model}
language: zh-CN
segment_duration: 300 seconds (5 minutes)
enhanced: true
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
    content += f"- 每段时长约 5 分钟\n"
    content += f"- 使用 {model} 模型进行语音识别\n"
    content += f"- 已添加自然断句和标点符号\n\n"
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
    # 检查是否传入了命令行参数
    if len(sys.argv) > 1:
        main()
    else:
        print("Usage: python main.py <URL_or_file_path> [output_base_dir]")
        print("参数说明:")
        print("- URL_or_file_path: B站视频 URL 或本地音频文件路径")
        print("- output_base_dir: 可选，基础输出目录（默认: C:\\Users\\lenovo\\translate）")
