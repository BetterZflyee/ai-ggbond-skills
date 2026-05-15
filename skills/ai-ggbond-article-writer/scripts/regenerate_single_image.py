#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单独重新生成某一张图片的脚本
"""

import sys
import os
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from generate_images_v4 import (
    YunwuImageGenerator,
    ArticleAnalyzer,
    download_image_with_watermark
)

def regenerate_section_image(article_path, section_index, output_dir):
    """
    重新生成指定章节的图片
    
    Args:
        article_path: 文章路径
        section_index: 章节索引（从0开始）
        output_dir: 输出目录
    """
    
    # 读取并分析文章
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analyzer = ArticleAnalyzer()
    analysis = analyzer.extract_content_and_brands(content)
    
    sections = analysis.get('sections', [])
    if section_index >= len(sections):
        print(f"❌ 章节索引 {section_index} 超出范围，文章只有 {len(sections)} 个章节")
        return False
    
    section = sections[section_index]
    section_heading = section.get('heading', f'主题{section_index+1}')
    section_points = section.get('points', [])
    content_summary = section.get('content_summary', section_heading)
    file_name_summary = section.get('file_name_summary', f'主题{section_index+1}')
    full_content = section.get('full_content', [])
    
    print(f"✅ 准备重新生成章节 {section_index+1}: {content_summary}")
    
    # 构建章节配图提示词（使用优化后的提示词）
    section_prompt = f"""创建一张干净整洁的章节配图。

【基本信息】
- 比例：16:9横版
- 分辨率：8K超高清
- 主题：{content_summary}

【核心内容】
- 主标题：{section_heading}
- 核心要点（全部展示）：
"""
    for j, point in enumerate(section_points[:6]):
        section_prompt += f"  {j+1}. {point}\n"
    
    # 添加额外的内容摘要
    if full_content:
        section_prompt += f"\n- 补充内容：{' '.join(full_content[:3])}\n"
    
    section_prompt += f"""
【视觉风格】
- 整体风格：手账风格，简洁专业
- 线条特征：清晰克制，层级分明
- 配色方案：低饱和主色+1个强调色
- 背景色：米白色#FAF9F6

【布局结构】（16:9横版）
- 标题区：顶部简洁标题，不超过14字
- 主内容区：最多3个信息模块，不拥挤
- 视觉元素：1个主视觉 + 2~3个辅助图标
- 留白区：保留15%-20%留白，确保整洁

【重要：避免便利贴效果】
- 不使用便利贴、便签等会产生小字体手写文字的元素
- 所有文字都直接展示在清晰的卡片或标签上
- 确保所有文字都有足够的空间和字体大小

【插图元素】
- 与主题相关的专业图标系统
- 手绘风格的箭头、连接线、框线
- 标签效果、高亮框
- 数据可视化图表
- 装饰性元素增强视觉吸引力

【信息密度要求】
- 除信息图外，保持中低信息密度
- 仅保留3个核心要点，禁止重复表达
- 禁止堆叠过多文本框与装饰元素

【中文文字要求】（极其重要！绝对不能忽略！）
- 所有文字必须使用标准、清晰的简体中文
- 绝对禁止出现任何乱码、模糊不清的文字、或无法辨认的字符
- 每个对话框、卡片、标签上的文字都必须是清晰可认的中文
- 禁止文字变形、重影、字符粘连、乱码
- 字体层级：主标题 > 要点 > 说明
- 标题醒目，正文短句，单个文本块不超过两行
- 如果发现文字模糊或乱码，必须重生成
- 所有文字都直接展示在清晰的卡片或标签上，不要使用便利贴或便签

【重要提示】
- 不要使用"章节X"、"Section X"、"Part X"等标题
- 直接使用内容主题作为标题
- 聚焦于内容本身，不使用章节编号
- 保持布局干净，避免拥挤与重复元素
- 所有中文文字必须100%清晰可认，绝对不能有任何乱码"""
    
    # 生成图片
    api_key = os.environ.get("YUNWU_API_KEY")
    if not api_key:
        print("❌ 请设置 YUNWU_API_KEY 环境变量")
        return False
    
    generator = YunwuImageGenerator(api_key=api_key)
    
    try:
        section_result = generator.generate(
            prompt=section_prompt,
            model="gpt-image-2",
            size="1792x1024",
            quality="hd"
        )
        
        # 保存图片
        import re
        safe_file_name = re.sub(r'[<>:"/\\\\|?*]', '', file_name_summary)
        section_path = Path(output_dir) / f"{section_index+1:02d}-{safe_file_name[:30]}.png"
        
        download_image_with_watermark(generator, section_result.url, str(section_path))
        print(f"✅ 图片已重新生成并保存: {section_path}")
        return True
        
    except Exception as e:
        print(f"❌ 重新生成图片失败: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python regenerate_single_image.py <文章路径> <章节索引> <输出目录>")
        print("示例: python regenerate_single_image.py article.md 3 ./images")
        sys.exit(1)
    
    article_path = sys.argv[1]
    section_index = int(sys.argv[2])
    output_dir = sys.argv[3]
    
    regenerate_section_image(article_path, section_index, output_dir)
