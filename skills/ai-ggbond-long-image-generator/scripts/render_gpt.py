#!/usr/bin/env python3
"""
AI朱朱侠长图生成器 - GPT-Image-2 版本
使用云雾 API 的 GPT-Image-2 生成高质量长图

特点：
- 使用 GPT-Image-2 生成有实际内容的图片
- 分段生成 + 智能拼接，支持超长图
- 保持风格一致性
- 自动重试机制

使用方法:
    python render_gpt.py --prompt "AI工具使用指南" --preset xiaohongshu --output output.png
    python render_gpt --prompt "内容" --width 1080 --height 4320 --output output.png
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image

# 云雾 API 配置
YUNWU_API_URL = "https://yunwu.ai/v1/images/generations"

def get_api_key():
    """从配置文件读取 API Key"""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # 尝试从 fallback_providers 获取
            fallback_providers = config.get('fallback_providers', [])
            for provider in fallback_providers:
                if provider.get('base_url', '').startswith('https://yunwu.ai'):
                    return provider.get('api_key', '')
            # 尝试从 providers.openai 获取
            return config.get('providers', {}).get('openai', {}).get('api_key', '')
    except:
        # 尝试从环境变量获取
        return os.environ.get('OPENAI_API_KEY', '')

def generate_image_segment(prompt: str, size: str = "1024x1536", quality: str = "high",
                           style: str = "vivid", api_key: str = None, max_retries: int = 3):
    """
    使用 GPT-Image-2 生成单张图片
    
    Args:
        prompt: 图片描述
        size: 尺寸 (1024x1024, 1024x1536, 1536x1024)
        quality: 质量 (standard, high)
        style: 风格 (vivid, natural)
        api_key: API Key
        max_retries: 最大重试次数
    
    Returns:
        PIL.Image 对象或 None
    """
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        print("❌ 未找到 API Key，请配置 ~/.hermes/config.yaml 或设置 OPENAI_API_KEY 环境变量")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality
    }
    
    for attempt in range(max_retries):
        try:
            print(f"    🎨 生成中... (尝试 {attempt + 1}/{max_retries})")
            response = requests.post(YUNWU_API_URL, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and len(result['data']) > 0:
                    image_data = result['data'][0]
                    
                    # 处理 b64_json 或 url
                    if 'b64_json' in image_data:
                        image_bytes = base64.b64decode(image_data['b64_json'])
                        return Image.open(BytesIO(image_bytes))
                    elif 'url' in image_data:
                        img_response = requests.get(image_data['url'], timeout=30)
                        return Image.open(BytesIO(img_response.content))
            else:
                print(f"    ⚠️ API 错误: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"    ⚠️ 请求失败: {e}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"    ⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    return None

def generate_long_image(prompt: str, width: int, height: int, 
                        quality: str = "high", style: str = "vivid",
                        segment_height: int = 1536, overlap: int = 100):
    """
    生成长图
    
    策略：
    1. 将长图分成多个 1024x1536 的段
    2. 每段单独生成，保持风格一致性
    3. 智能拼接
    
    Args:
        prompt: 图片描述
        width: 目标宽度
        height: 目标高度
        quality: 质量
        style: 风格
        segment_height: 每段高度
        overlap: 重叠区域
    """
    api_key = get_api_key()
    if not api_key:
        print("❌ 未找到 API Key")
        return None
    
    # GPT-Image-2 支持的尺寸
    supported_sizes = {
        "1024x1024": (1024, 1024),
        "1024x1536": (1024, 1536),
        "1536x1024": (1536, 1024),
    }
    
    # 根据目标尺寸选择最佳生成尺寸
    if width <= 1024 and height <= 1024:
        gen_size = "1024x1024"
        gen_width, gen_height = 1024, 1024
    elif height > width:
        gen_size = "1024x1536"
        gen_width, gen_height = 1024, 1536
    else:
        gen_size = "1536x1024"
        gen_width, gen_height = 1536, 1024
    
    print(f"📐 目标尺寸: {width} × {height} px")
    print(f"🎨 生成尺寸: {gen_size}")
    print(f"✨ 质量: {quality}, 风格: {style}")
    print()
    
    # 计算需要的段数
    if height <= gen_height:
        # 单张图即可
        num_segments = 1
        actual_segment_height = height
    else:
        # 需要多段拼接
        effective_height = gen_height - overlap
        num_segments = max(1, (height + effective_height - 1) // effective_height)
        actual_segment_height = gen_height
    
    print(f"📊 需要生成 {num_segments} 个片段")
    print()
    
    segments = []
    
    for i in range(num_segments):
        print(f"  🎨 生成片段 {i + 1}/{num_segments}")
        
        # 构建提示词
        if num_segments == 1:
            segment_prompt = f"""Create a detailed infographic image with the following theme: {prompt}

Style requirements:
- Modern, professional design
- Dark tech theme with neon blue (#00D4FF) and orange (#FF6B35) accents
- Clear typography and visual hierarchy
- Information-rich but well-organized layout
- Include charts, icons, or visual elements where appropriate"""
        else:
            # 多段时，为每段添加上下文
            segment_context = ""
            if i == 0:
                segment_context = "This is the HEADER section with title and introduction."
            elif i == num_segments - 1:
                segment_context = "This is the FOOTER section with summary and call-to-action."
            else:
                segment_context = f"This is CONTENT section {i} with detailed information."
            
            segment_prompt = f"""Create a detailed infographic image segment for a long scrollable infographic.

Theme: {prompt}
Section: {segment_context}

Style requirements:
- Modern, professional design
- Dark tech theme with neon blue (#00D4FF) and orange (#FF6B35) accents
- Clear typography and visual hierarchy
- Content should flow naturally for continuous scrolling
- Section {i + 1} of {num_segments} total sections"""
        
        # 生成图片
        segment = generate_image_segment(
            segment_prompt, 
            size=gen_size, 
            quality=quality, 
            style=style,
            api_key=api_key
        )
        
        if segment:
            segments.append(segment)
            print(f"    ✅ 成功")
        else:
            print(f"    ❌ 失败")
            # 创建占位图
            placeholder = Image.new('RGB', (gen_width, gen_height), color=(15, 20, 25))
            segments.append(placeholder)
    
    if not segments:
        print("❌ 所有片段生成失败")
        return None
    
    print()
    print("🔧 拼接图片...")
    
    # 拼接图片
    final_image = stitch_segments(segments, overlap, width, height)
    
    return final_image

def stitch_segments(segments: list, overlap: int, target_width: int, target_height: int):
    """
    智能拼接图片片段
    """
    if len(segments) == 1:
        image = segments[0]
        # 调整到目标尺寸
        if image.size != (target_width, target_height):
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        return image
    
    # 获取生成图片的尺寸
    gen_width, gen_height = segments[0].size
    
    # 计算最终高度
    total_gen_height = gen_height + (len(segments) - 1) * (gen_height - overlap)
    
    # 创建最终图片
    final_image = Image.new('RGB', (gen_width, total_gen_height), color=(15, 20, 25))
    
    current_y = 0
    for i, segment in enumerate(segments):
        if i == 0:
            final_image.paste(segment, (0, 0))
            current_y = gen_height
        else:
            # 裁剪掉重叠部分
            crop_top = overlap
            cropped = segment.crop((0, crop_top, gen_width, gen_height))
            final_image.paste(cropped, (0, current_y - overlap))
            current_y += gen_height - overlap
    
    # 裁剪到目标高度
    if final_image.size[1] > target_height:
        final_image = final_image.crop((0, 0, gen_width, target_height))
    
    # 调整宽度
    if gen_width != target_width:
        final_image = final_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    return final_image

def main():
    parser = argparse.ArgumentParser(
        description="AI朱朱侠长图生成器 - GPT-Image-2 版本"
    )
    parser.add_argument("--prompt", "-p", required=True, help="图片描述/主题")
    parser.add_argument("--output", "-o", default=None, help="输出 PNG 文件路径")
    parser.add_argument("--width", "-W", type=int, default=1080, help="图片宽度（默认1080）")
    parser.add_argument("--height", "-H", type=int, default=1440, help="图片高度（默认1440）")
    parser.add_argument("--quality", "-q", choices=["standard", "high"], default="high", help="图片质量")
    parser.add_argument("--style", "-s", choices=["vivid", "natural"], default="vivid", help="图片风格")
    parser.add_argument("--preset", choices=["xiaohongshu", "xhs", "xiaohongshu_long", 
                                              "wechat_cover", "wechat_body", "square", 
                                              "super_long_small", "super_long_medium", 
                                              "super_long_large", "super_long_extreme"],
                        help="使用预设尺寸")
    
    args = parser.parse_args()
    
    # 预设尺寸
    presets = {
        "xiaohongshu": (1080, 1440),
        "xhs": (1080, 1440),
        "xiaohongshu_long": (1080, 2400),
        "wechat_cover": (900, 383),
        "wechat_body": (1080, 720),
        "square": (1080, 1080),
        "super_long_small": (1080, 3200),
        "super_long_medium": (1080, 4320),
        "super_long_large": (1080, 5400),
        "super_long_extreme": (1080, 7200),
    }
    
    # 确定尺寸
    if args.preset:
        width, height = presets[args.preset]
        print(f"📐 使用预设: {args.preset}")
    else:
        width = args.width
        height = args.height
    
    # 输出文件
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"gpt_image_{width}x{height}_{timestamp}.png"
    
    print(f"📝 主题: {args.prompt}")
    print(f"📁 输出: {output_path}")
    print()
    
    # 生成图片
    start_time = time.time()
    image = generate_long_image(
        args.prompt, width, height,
        quality=args.quality, style=args.style
    )
    
    if image:
        # 保存图片
        output_path = Path(output_path)
        image.save(str(output_path), quality=95)
        
        elapsed = time.time() - start_time
        
        print()
        print(f"✅ 长图生成完成!")
        print(f"📁 文件: {output_path}")
        print(f"📐 尺寸: {image.size[0]} × {image.size[1]} px")
        print(f"📦 大小: {output_path.stat().st_size / 1024:.1f} KB")
        print(f"⏱️ 耗时: {elapsed:.1f} 秒")
    else:
        print("❌ 图片生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
