# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-08-03

### Added
- 智能2分钟分段转录系统
- 自动质量检测和重录机制
- CPU自适应优化，根据硬件自动选择模型
- 智能主题识别和分类（9大主题）
- 自动标点符号添加
- 静默监控机制，减少系统开销
- 超时限制取消（smart_transcribe.py）

### Changed
- 简化代码结构，移除冗余功能
- 优化依赖管理
- 文档全面重构和合并
- 插件版本升级到3.0.0

### Fixed
- KeyError: 'sentences' 错误处理
- 监控策略过于频繁的问题
- 并发任务互相干扰的问题

## [2.0.0] - 2026-07-31

### Added
- 质量优先转录系统
- 多线程CPU优化
- 基础监控功能
- YAML frontmatter支持
- 智能文件命名

### Changed
- 重构转录流程
- 添加依赖管理
- 完善错误处理

## [1.0.0] - 2026-07-30

### Added
- 基础视频下载功能
- Whisper转录集成
- 简体中文转换
- 基本输出格式

---

*格式说明：*
- **Added**: 新功能
- **Changed**: 功能变更
- **Fixed**: Bug修复
- **Deprecated**: 废弃功能
- **Removed**: 删除功能
- **Security**: 安全修复