#!/usr/bin/env python3
"""
AI朱朱侠超长图渲染器
专门处理超长图的稳定性渲染，使用分段渲染+拼接策略

解决的问题：
1. 浏览器渲染超长图时内存溢出
2. 截图出现空白或截断
3. 字体渲染不一致
4. 滚动加载导致内容缺失

使用方法:
    python render_long.py --html input.html --output output.png --height 5400
    python render_long.py --html input.html --output output.png --preset super_long_large
"""

import argparse
import sys
import tempfile
from pathlib import Path
from PIL import Image
import io

# 超长图预设
LONG_PRESETS = {
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
    
    # 自定义倍数
    "3x": {"width": 1080, "height": 3240, "name": "3倍长图"},
    "4x": {"width": 1080, "height": 4320, "name": "4倍长图"},
    "5x": {"width": 1080, "height": 5400, "name": "5倍长图"},
    "6x": {"width": 1080, "height": 6480, "name": "6倍长图"},
}

def render_segment_playwright(html_path: str, width: int, segment_height: int, 
                               scroll_position: int, device_scale: int = 2):
    """使用 Playwright 渲染单个片段"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": width, "height": segment_height},
                device_scale_factor=device_scale
            )
            page = context.new_page()
            
            # 加载页面并等待完成
            page.goto(f"file://{html_path}", wait_until="networkidle")
            page.wait_for_timeout(500)  # 额外等待渲染稳定
            
            # 滚动到指定位置
            page.evaluate(f"window.scrollTo(0, {scroll_position})")
            page.wait_for_timeout(300)  # 等待滚动完成
            
            # 截取当前视口
            screenshot_bytes = page.screenshot(full_page=False)
            
            browser.close()
            
            return Image.open(io.BytesIO(screenshot_bytes))
    except Exception as e:
        print(f"  ⚠️ 片段渲染失败: {e}")
        return None

def render_long_image_stable(html_path: str, output_path: str, width: int, 
                              total_height: int, segment_height: int = 2000,
                              overlap: int = 100, device_scale: int = 2,
                              max_retries: int = 3):
    """
    稳定渲染超长图
    
    策略：
    1. 将长图分成多个片段
    2. 每个片段独立渲染
    3. 智能拼接（带重叠区域去重）
    4. 失败自动重试
    
    Args:
        html_path: HTML 文件路径
        output_path: 输出图片路径
        width: 图片宽度
        total_height: 总高度
        segment_height: 每段高度（默认2000px）
        overlap: 重叠区域（默认100px）
        device_scale: 清晰度倍数（默认2x）
        max_retries: 最大重试次数
    """
    
    print(f"📐 目标尺寸: {width} × {total_height} px")
    print(f"📦 分段高度: {segment_height} px")
    print(f"🔄 重叠区域: {overlap} px")
    print(f"✨ 清晰度: {device_scale}x")
    print()
    
    # 计算需要的片段数
    effective_height = segment_height - overlap
    num_segments = max(1, (total_height + effective_height - 1) // effective_height)
    
    print(f"📊 需要渲染 {num_segments} 个片段")
    print()
    
    segments = []
    
    for i in range(num_segments):
        scroll_position = i * effective_height
        print(f"  🎨 渲染片段 {i+1}/{num_segments} (位置: {scroll_position}px)")
        
        # 重试机制
        for attempt in range(max_retries):
            segment = render_segment_playwright(
                html_path, width, segment_height, 
                scroll_position, device_scale
            )
            
            if segment is not None:
                segments.append(segment)
                print(f"    ✅ 成功 (尝试 {attempt+1})")
                break
            else:
                print(f"    ⚠️ 失败，重试 ({attempt+1}/{max_retries})")
        
        if segment is None:
            print(f"    ❌ 片段 {i+1} 渲染失败，已跳过")
    
    if not segments:
        print("❌ 所有片段渲染失败")
        return False
    
    print()
    print("🔧 拼接片段...")
    
    # 拼接图片
    final_image = stitch_segments(segments, overlap, total_height, device_scale)
    
    # 保存
    output_path = Path(output_path)
    final_image.save(str(output_path), quality=95)
    
    print(f"✅ 超长图渲染完成!")
    print(f"📁 文件: {output_path}")
    print(f"📐 尺寸: {final_image.size[0]} × {final_image.size[1]} px")
    print(f"📦 文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return True

def stitch_segments(segments: list, overlap: int, total_height: int, device_scale: int = 2):
    """
    智能拼接图片片段
    
    使用重叠区域进行平滑过渡
    """
    if len(segments) == 1:
        return segments[0]
    
    # 计算最终图片尺寸
    width = segments[0].size[0]
    final_height = total_height * device_scale
    
    # 创建最终图片
    final_image = Image.new('RGB', (width, final_height), color=(15, 20, 25))
    
    current_y = 0
    for i, segment in enumerate(segments):
        if i == 0:
            # 第一个片段，直接粘贴
            final_image.paste(segment, (0, 0))
            current_y = segment.size[1]
        else:
            # 后续片段，跳过重叠区域
            overlap_pixels = overlap * device_scale
            crop_top = overlap_pixels
            
            # 裁剪掉重叠部分
            cropped = segment.crop((0, crop_top, segment.size[0], segment.size[1]))
            
            # 粘贴到最终图片
            final_image.paste(cropped, (0, current_y - overlap_pixels))
            current_y += cropped.size[1] - overlap_pixels
    
    # 裁剪到目标高度
    if final_image.size[1] > final_height:
        final_image = final_image.crop((0, 0, width, final_height))
    
    return final_image

def render_single_playwright(html_path: str, output_path: str, width: int, height: int):
    """单次渲染（适用于非超长图）"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=2
            )
            page.goto(f"file://{html_path}", wait_until="networkidle")
            page.wait_for_timeout(500)
            page.screenshot(path=str(Path(output_path).resolve()), full_page=True)
            browser.close()
        
        return True
    except Exception as e:
        print(f"❌ 渲染失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="AI朱朱侠超长图渲染器 - 稳定渲染超长信息图"
    )
    parser.add_argument("--html", required=True, help="输入 HTML 文件路径")
    parser.add_argument("--output", "-o", default="output.png", help="输出 PNG 文件路径")
    parser.add_argument("--width", "-W", type=int, help="图片宽度")
    parser.add_argument("--height", "-H", type=int, help="图片高度")
    parser.add_argument("--preset", "-p", choices=list(LONG_PRESETS.keys()), help="使用预设")
    parser.add_argument("--segment-height", type=int, default=2000, help="分段高度（默认2000px）")
    parser.add_argument("--overlap", type=int, default=100, help="重叠区域（默认100px）")
    parser.add_argument("--scale", type=int, default=2, help="清晰度倍数（默认2x）")
    parser.add_argument("--list-presets", action="store_true", help="列出所有预设")
    parser.add_argument("--force-segment", action="store_true", help="强制使用分段渲染")
    
    args = parser.parse_args()
    
    # 列出预设
    if args.list_presets:
        print("\n📐 超长图预设:\n")
        print(f"{'预设名称':<30} {'尺寸':<15} {'说明'}")
        print("-" * 65)
        for name, info in LONG_PRESETS.items():
            print(f"{name:<30} {info['width']}×{info['height']:<10} {info['name']}")
        return
    
    # 确定尺寸
    if args.preset:
        preset = LONG_PRESETS[args.preset]
        width = args.width or preset["width"]
        height = args.height or preset["height"]
        print(f"📐 使用预设: {preset['name']}")
    elif args.width and args.height:
        width = args.width
        height = args.height
        print(f"📐 自定义尺寸: {width}×{height}")
    else:
        print("❌ 请指定 --preset 或 --width/--height")
        sys.exit(1)
    
    # 检查输入文件
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"❌ HTML 文件不存在: {html_path}")
        sys.exit(1)
    
    # 判断是否需要分段渲染
    # 高度超过 3000px 或强制分段时使用分段策略
    use_segmented = height > 3000 or args.force_segment
    
    print(f"📄 输入: {html_path}")
    print(f"📁 输出: {args.output}")
    print(f"🎯 模式: {'分段渲染' if use_segmented else '单次渲染'}")
    print()
    
    if use_segmented:
        success = render_long_image_stable(
            str(html_path), args.output, width, height,
            segment_height=args.segment_height,
            overlap=args.overlap,
            device_scale=args.scale
        )
    else:
        success = render_single_playwright(str(html_path), args.output, width, height)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
