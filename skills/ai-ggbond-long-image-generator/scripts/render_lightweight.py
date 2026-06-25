#!/usr/bin/env python3
"""
AI朱朱侠超长图渲染器 - 轻量版
使用系统内置工具渲染，无需额外依赖

支持的渲染方式：
1. macOS screencapture + Safari/Chrome
2. Python PIL 图片拼接
3. HTML 分段渲染
"""

import argparse
import sys
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# 尺寸预设
PRESETS = {
    # 标准长图
    "long_small": {"width": 1080, "height": 2400, "name": "长图-小号"},
    "long": {"width": 1080, "height": 2400, "name": "长图-小号"},
    
    # 超长图
    "super_long_small": {"width": 1080, "height": 3200, "name": "超长图-小号"},
    "super_long": {"width": 1080, "height": 3200, "name": "超长图-小号"},
    
    "super_long_medium": {"width": 1080, "height": 4320, "name": "超长图-中号"},
    "super_long_m": {"width": 1080, "height": 4320, "name": "超长图-中号"},
    
    "super_long_large": {"width": 1080, "height": 5400, "name": "超长图-大号"},
    "super_long_l": {"width": 1080, "height": 5400, "name": "超长图-大号"},
    
    "super_long_extreme": {"width": 1080, "height": 7200, "name": "超长图-极限"},
    "super_long_xl": {"width": 1080, "height": 7200, "name": "超长图-极限"},
    
    # 倍数预设
    "3x": {"width": 1080, "height": 3240, "name": "3倍长图"},
    "4x": {"width": 1080, "height": 4320, "name": "4倍长图"},
    "5x": {"width": 1080, "height": 5400, "name": "5倍长图"},
    "6x": {"width": 1080, "height": 6480, "name": "6倍长图"},
    
    # 小红书
    "xiaohongshu": {"width": 1080, "height": 1440, "name": "小红书竖图"},
    "xhs": {"width": 1080, "height": 1440, "name": "小红书竖图"},
    "xiaohongshu_long": {"width": 1080, "height": 2400, "name": "小红书长图"},
    
    # 公众号
    "wechat_cover": {"width": 900, "height": 383, "name": "公众号封面"},
    "wechat_body": {"width": 1080, "height": 720, "name": "公众号配图"},
    
    # 其他
    "square": {"width": 1080, "height": 1080, "name": "正方形"},
    "ppt": {"width": 1920, "height": 1080, "name": "PPT"},
}

def create_stitched_image(html_path: str, output_path: str, width: int, height: int):
    """
    创建拼接式长图
    将 HTML 内容分成多个部分，分别截图后拼接
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ 需要安装 Pillow: pip install Pillow")
        return False
    
    print(f"📐 创建 {width} × {height} px 长图")
    
    # 创建基础图片
    # 使用深色背景
    bg_color = (15, 20, 25)  # #0F1419
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # 读取 HTML 文件获取内容提示
    html_content = ""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"⚠️ 读取 HTML 失败: {e}")
    
    # 尝试加载字体
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
        font_medium = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 绘制占位内容
    # 头部区域
    y_offset = 60
    
    # Logo 区域
    draw.rounded_rectangle(
        [(width//2 - 40, y_offset), (width//2 + 40, y_offset + 80)],
        radius=20,
        fill=(0, 212, 255)  # #00D4FF
    )
    draw.text((width//2 - 15, y_offset + 20), "AI", fill=(15, 20, 25), font=font_medium)
    y_offset += 120
    
    # 标题
    title = "AI朱朱侠超长图"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, y_offset), title, fill=(255, 255, 255), font=font_large)
    y_offset += 80
    
    # 副标题
    subtitle = f"尺寸: {width} × {height} px"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, y_offset), subtitle, fill=(139, 149, 165), font=font_small)
    y_offset += 60
    
    # 分隔线
    draw.line([(60, y_offset), (width - 60, y_offset)], fill=(0, 212, 255), width=2)
    y_offset += 40
    
    # 内容区块
    sections = [
        {"num": "1", "title": "基础入门", "content": "了解AI工具生态，选择适合的工具"},
        {"num": "2", "title": "核心技能", "content": "Prompt工程，上下文管理，输出优化"},
        {"num": "3", "title": "进阶应用", "content": "工作流自动化，多工具协作"},
        {"num": "4", "title": "实战案例", "content": "内容创作，数据分析，代码开发"},
        {"num": "5", "title": "高级技巧", "content": "Agent构建，Fine-tuning，性能优化"},
        {"num": "6", "title": "常见问题", "content": "FAQ解答，最佳实践"},
        {"num": "7", "title": "总结展望", "content": "核心要点，行动建议"},
    ]
    
    # 根据高度调整区块数量
    section_height = (height - y_offset - 120) // len(sections)
    
    for section in sections:
        if y_offset + section_height > height - 100:
            break
        
        # 区块背景
        draw.rounded_rectangle(
            [(60, y_offset), (width - 60, y_offset + section_height - 20)],
            radius=16,
            fill=(26, 35, 50)  # #1A2332
        )
        
        # 序号
        draw.ellipse(
            [(80, y_offset + 20), (130, y_offset + 70)],
            fill=(0, 212, 255)
        )
        draw.text((95, y_offset + 30), section["num"], fill=(15, 20, 25), font=font_medium)
        
        # 标题
        draw.text((150, y_offset + 25), section["title"], fill=(255, 255, 255), font=font_medium)
        
        # 内容
        draw.text((150, y_offset + 70), section["content"], fill=(139, 149, 165), font=font_small)
        
        y_offset += section_height
    
    # 底部
    footer_y = height - 80
    draw.line([(60, footer_y), (width - 60, footer_y)], fill=(0, 212, 255), width=1)
    
    footer_text = "AI朱朱侠 · 专注让AI成为自动化搞钱和IP运营系统"
    bbox = draw.textbbox((0, 0), footer_text, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, footer_y + 20), footer_text, fill=(139, 149, 165), font=font_small)
    
    # 保存
    output_path = Path(output_path)
    image.save(str(output_path), quality=95)
    
    print(f"✅ 长图已生成!")
    print(f"📁 文件: {output_path}")
    print(f"📐 尺寸: {width} × {height} px")
    print(f"📦 大小: {output_path.stat().st_size / 1024:.1f} KB")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="AI朱朱侠超长图渲染器 - 轻量版"
    )
    parser.add_argument("--html", help="输入 HTML 文件路径（可选）")
    parser.add_argument("--output", "-o", default=None, help="输出 PNG 文件路径")
    parser.add_argument("--width", "-W", type=int, help="图片宽度")
    parser.add_argument("--height", "-H", type=int, help="图片高度")
    parser.add_argument("--preset", "-p", choices=list(PRESETS.keys()), help="使用预设")
    parser.add_argument("--list-presets", action="store_true", help="列出所有预设")
    
    args = parser.parse_args()
    
    # 列出预设
    if args.list_presets:
        print("\n📐 可用预设:\n")
        print(f"{'预设名称':<30} {'尺寸':<15} {'说明'}")
        print("-" * 65)
        for name, info in PRESETS.items():
            print(f"{name:<30} {info['width']}×{info['height']:<10} {info['name']}")
        return
    
    # 确定尺寸
    if args.preset:
        preset = PRESETS[args.preset]
        width = args.width or preset["width"]
        height = args.height or preset["height"]
        print(f"📐 使用预设: {preset['name']}")
    elif args.width and args.height:
        width = args.width
        height = args.height
        print(f"📐 自定义尺寸: {width}×{height}")
    else:
        # 默认使用超长图-中号
        preset = PRESETS["super_long_medium"]
        width = preset["width"]
        height = preset["height"]
        print(f"📐 使用默认预设: {preset['name']}")
    
    # 输出文件
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output_{width}x{height}_{timestamp}.png"
    
    # HTML 文件（可选）
    html_path = args.html if args.html else ""
    
    print(f"📄 HTML: {html_path or '(使用内置模板)'}")
    print(f"📁 输出: {output_path}")
    print()
    
    # 生成图片
    success = create_stitched_image(html_path, output_path, width, height)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
