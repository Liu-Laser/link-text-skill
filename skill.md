---
name: link-text
description: 智能视频转录系统 - 将视频/音频转换为中文文本记录，支持智能分段、质量优化和主题分类
version: 3.0.0
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#link-text
    requires:
      anyBins:
        - python
        - pip
---

# Link Text - 智能视频转录系统

将视频/音频转换为中文文本记录，支持智能分段、质量优化和主题分类。

## Script Directory

Scripts in `scripts/` subdirectory. `{baseDir}` = this SKILL.md's directory path.

| Script | Purpose |
|--------|---------|
| `scripts/main_simplified.py` | 核心转录脚本 |
| `scripts/smart_transcribe.py` | 智能监控版本（推荐） |
| `scripts/monitor_transcription.py` | 任务监控器 |
| `scripts/utils.py` | 工具函数库 |
| `scripts/install_requirements.py` | 依赖安装脚本 |

## Usage

```bash
# 基础使用
{baseDir}/scripts/main_simplified.py <URL>

# 智能监控版本（推荐）
{baseDir}/scripts/smart_transcribe.py <URL>

# 指定输出目录
{baseDir}/scripts/smart_transcribe.py <URL> D:/输出目录

# 示例
{baseDir}/scripts/smart_transcribe.py https://www.bilibili.com/video/BV1xxx
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<URL>` | 视频URL（支持B站、YouTube等） | Required |
| `<output_dir>` | 输出目录（可选） | auto-generated |
| `--model` | 模型选择：large-v3/medium/base | 自动检测最佳模型 |

## 支持的网站

- Bilibili (B站)
- YouTube
- 其他主流视频平台

## 输出目录结构

```
translate/{video-id}/
├── task_info.json      # 任务信息
├── transcript.md       # 转录结果
├── audio/              # 音频文件
└── videos/             # 视频文件
```

## 功能特点

- 智能分段
- 无超时限制
- 自动检测并发任务
- 实时状态显示
- 自动重试机制
- 智能断句
- 生成结构化输出

## 环境变量配置

```bash
# 模型选择
export TRANSCRIBE_MODEL=large-v3  # 最高质量
export TRANSCRIBE_MODEL=medium    # 平衡
export TRANSCRIBE_MODEL=base      # 基础质量

# 输出目录
export TRANSCRIBE_OUTPUT_DIR=~/transcripts

# 语言设置
export TRANSCRIBE_LANGUAGE=zh
```

## 故障排除

1. **找不到模块** - 运行 `python install_requirements.py`
2. **FFmpeg未找到** - 下载并添加到系统PATH
3. **内存不足** - 使用 base 模型
4. **网络问题** - 检查网络连接