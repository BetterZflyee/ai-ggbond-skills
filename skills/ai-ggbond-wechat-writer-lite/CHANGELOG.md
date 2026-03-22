# Changelog

All notable changes to this skill will be documented in this file.

## [1.1.0] - 2026-03-19

### Fixed
- 移除SKILL.md中重复的风格选择流程章节（10.0.1/10.0.2重复出现）
- 移除10.3.1章节与10.0章节重复的风格选择界面
- 移除10.4.1章节重复的API密钥配置标题

### Improved
- 优化SKILL.md结构，提升可读性
- 精简冗余内容，减少约200行重复代码

### Changed
- 更新evolution.json，添加版本记录和changelog字段

## [1.0.0] - 2026-02-13

### Added
- 初始版本发布
- 整合封面图、信息图、章节配图三大系统
- 支持云雾API V4版本图片生成
- 添加品牌Logo智能识别与展示规则
- 实现文章管理器（article_manager.py）
- 实现文章排版优化器（format_article.py）
- 实现图片生成器（generate_images_v4.py）

### Features
- 五维度封面图定制系统（Type, Palette, Rendering, Text, Mood）
- 21种布局×20种风格的信息图系统
- Type×Style章节配图系统
- 智能文章分析器（自动提取标题、品牌、章节结构）
- 风格一致性检查机制
- 移动端优化的HTML排版
