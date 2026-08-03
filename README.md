# Link-Text Skill - 智能视频转录系统 🎯

将视频/音频转换为中文文本记录，支持智能分段、质量优化和主题分类。

## 🚀 快速开始

### 安装依赖
```bash
pip install yt-dlp openai-whisper soundfile psutil
# 下载 FFmpeg: https://ffmpeg.org/
```

### 使用方法
1. **简单触发（推荐）**
   ```
   将视频转为文字 https://www.bilibili.com/video/xxx
   ```

2. **命令行方式**
   ```bash
   # 基础使用
   python scripts/main_simplified.py <URL>
   
   # 指定输出目录
   python scripts/main_simplified.py <URL> D:/MyTranscripts
   
   # 使用智能监控版本（推荐）
   python scripts/smart_transcribe.py <URL>
   ```

## ✨ 核心特性

### ⚡ 质量优化
- **自动系统检测**：根据硬件自动选择最佳 Whisper 模型
- **智能重转录**：自动识别并重录质量差的段落
- **CPU 优化**：多线程处理，提升速度

### 🔄 2分钟分段转录
- 将长音频按**2分钟**分段处理
- 每段独立转录，提高准确性
- 保持精确时间戳

### ✍️ 智能断句和标点
- 自动添加标点符号（？。！）
- 合并间隔短的句子
- 保持原文完整性

### 🏷️ 智能主题识别
- 自动识别9大主题：
  - **教程**、**技术**、**娱乐**、**新闻**
  - **科技**、**教育**、**商业**、**生活**、**体育**
- 按主题+日期组织文件

## 📁 输出格式

### 目录结构
```
~/translate/
├── 技术_20250731/
│   ├── audio/          # 分段音频文件
│   ├── videos/         # 原始视频
│   ├── output/         # 其他输出
│   ├── task_info.json  # 任务信息
│   └── 转录_技术_20250731_1430.md
└── ...
```

### 转录文件示例
```markdown
---
title: Python编程教程
source_url: https://xxx
transcription_date: 2025-07-31
model: Whisper large-v3
language: zh-CN
segment_duration: 120 seconds
topic: 技术
---

# 视频转录

## 目录
- **第1段** (0-2分钟): 介绍Python基础
- **第2段** (2-4分钟): 变量和数据类型

## 转录内容

### 第 1 段 (0-2分钟)
1. 大家好！今天我们来学习Python编程。
2. Python是一种非常流行的编程语言。
3. 它语法简洁，容易上手。

### 第 2 段 (2-4分钟)
1. 在Python中，变量是用来存储数据的。
2. Python有几种基本的数据类型...
```

## ⚙️ 高级配置

### 环境变量
```bash
# 模型选择（默认自动选择）
export TRANSCRIBE_MODEL=large-v3  # 最高质量
export TRANSCRIBE_MODEL=medium    # 平衡
export TRANSCRIBE_MODEL=base      # 基础质量

# 自定义输出目录
export TRANSCRIBE_OUTPUT_DIR=~/transcripts

# 语言设置
export TRANSCRIBE_LANGUAGE=zh
```

### 自动模型选择逻辑
- **8核+16GB内存** → large-v3（最高质量）
- **4核+8GB内存** → medium（平衡）
- **其他配置** → base（基础质量）

## 🔧 支持的平台

- Bilibili (https://www.bilibili.com/video/...)
- YouTube (https://www.youtube.com/watch?v=...)
- Weibo、TikTok、Vimeo等
- 任何 yt-dlp 支持的URL

## 📊 监控策略

### 智能监控特点
- **静默等待**：启动后等待5分钟再检查
- **动态超时**：根据音频长度自动调整超时时间
- **节省资源**：减少90%的不必要检查

### 处理时间估算
| 音频时长 | 初始等待 | 超时时间 |
|---------|---------|---------|
| < 5分钟 | 10分钟 | 20分钟 |
| 5-20分钟 | 20分钟 | 35分钟 |
| 20-60分钟 | 30分钟 | 45分钟 |
| > 60分钟 | 40分钟 | 60分钟 |

## ❗ 注意事项

1. **首次使用**：会自动下载 Whisper 模型（1.5-3GB）
2. **网络要求**：需要稳定的网络连接
3. **磁盘空间**：确保有足够的存储空间
4. **内存要求**：大模型需要大量内存

## 🔍 故障排除

### 常见问题
1. **无法下载**：检查网络和URL
2. **模型下载失败**：检查防火墙
3. **FFmpeg未找到**：添加到系统PATH
4. **内存不足**：使用较小的模型

### 性能优化
- 长视频可考虑使用 `base` 模型
- 关闭占用内存的程序
- 确保C盘有足够空间

## 📞 技术支持

遇到问题请检查：
1. 是否安装所有依赖
2. 系统工具是否在PATH中
3. URL是否有效
4. 磁盘空间是否充足

---
*Link-Text Skill v3.0.0 - 智能视频转录系统*