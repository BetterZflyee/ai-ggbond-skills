#!/usr/bin/env python3
"""
AI朱朱侠超长图生成器 - GPT-Image-2 版本
使用云雾 API 生成高质量长图

使用方法:
    python generate_long_image.py --prompt "主题" --preset xiaohongshu --output output.png
    python generate_long_image.py --prompt "主题" --width 1080 --height 4320 --output output.png
"""

import argparse
import requests
import json
import base64
import time
import yaml
from PIL import Image
from io import BytesIO

# 尺寸预设
PRESETS = {
    'xiaohongshu': {'width': 1080, 'height': 1440, 'name': '小红书竖图'},
    'xhs': {'width': 1080, 'height': 1440, 'name': '小红书竖图'},
    'xiaohongshu_long': {'width': 1080, 'height': 2400, 'name': '小红书长图'},
    'super_long_small': {'width': 1080, 'height': 3200, 'name': '超长图-小号'},
    'super_long_medium': {'width': 1080, 'height': 4320, 'name': '超长图-中号'},
    'super_long_large': {'width': 1080, 'height': 5400, 'name': '超长图-大号'},
    'super_long_extreme': {'width': 1080, 'height': 7200, 'name': '超长图-极限'},
}

def load_config():
    """加载 API 配置"""
    config_path = '/Users/admin/.hermes/profiles/gongcheng/config.yaml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    image_gen = config.get('image_gen', {})
    return {
        'api_key': image_gen.get('api_key', ''),
        'base_url': image_gen.get('base_url', 'https://yunwu.ai/v1'),
        'model': image_gen.get('model', 'gpt-image-2')
    }

def generate_image(prompt, size='1024x1536', config=None):
    """生成单张图片"""
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': config['model'],
        'prompt': prompt,
        'n': 1,
        'size': size,
        'quality': 'high'
    }
    
    for attempt in range(3):
        try:
            response = requests.post(
                f'{config["base_url"]}/images/generations',
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('data'):
                    image_data = result['data'][0]
                    if 'b64_json' in image_data:
                        image_bytes = base64.b64decode(image_data['b64_json'])
                        return Image.open(BytesIO(image_bytes))
                    elif 'url' in image_data:
                        img_response = requests.get(image_data['url'], timeout=30)
                        return Image.open(BytesIO(img_response.content))
            else:
                error = response.json().get('error', {})
                print(f'    ⚠️ API 错误: {error.get("message", "")[:80]}')
                
        except Exception as e:
            print(f'    ⚠️ 请求异常: {str(e)[:60]}')
        
        if attempt < 2:
            time.sleep(2 ** attempt)
    
    return None

def main():
    parser = argparse.ArgumentParser(description='AI朱朱侠超长图生成器')
    parser.add_argument('--prompt', '-p', required=True, help='图片主题/描述')
    parser.add_argument('--output', '-o', default='output.png', help='输出文件路径')
    parser.add_argument('--width', '-W', type=int, help='图片宽度')
    parser.add_argument('--height', '-H', type=int, help='图片高度')
    parser.add_argument('--preset', choices=list(PRESETS.keys()), help='使用预设')
    
    args = parser.parse_args()
    
    # 确定尺寸
    if args.preset:
        preset = PRESETS[args.preset]
        width = args.width or preset['width']
        height = args.height or preset['height']
        print(f'📐 使用预设: {preset["name"]}')
    elif args.width and args.height:
        width = args.width
        height = args.height
    else:
        width, height = 1080, 1440
        print('📐 使用默认尺寸: 1080x1440')
    
    # 加载配置
    config = load_config()
    
    if len(config['api_key']) < 20:
        print('❌ API Key 未配置或长度不足')
        print('请先运行: bash setup_yunwu.sh <你的API_KEY>')
        return
    
    print(f'📝 主题: {args.prompt}')
    print(f'📐 尺寸: {width}x{height}')
    print(f'🎨 模型: {config["model"]}')
    print()
    
    # 根据高度决定生成策略
    if height <= 1536:
        # 单张图
        print('🎨 生成图片...')
        enhanced_prompt = f"""Create a professional infographic: {args.prompt}

Style: Dark tech theme with neon blue (#00D4FF) and orange (#FF6B35) accents
Layout: Vertical, modern, high information density
Include: Clear typography, visual hierarchy, icons/charts where appropriate"""
        
        image = generate_image(enhanced_prompt, '1024x1536', config)
        if image:
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            image.save(args.output)
            print(f'✅ 图片已保存: {args.output}')
        else:
            print('❌ 生成失败')
    else:
        # 多段拼接
        segment_height = 1536
        overlap = 100
        num_segments = max(1, (height + segment_height - overlap - 1) // (segment_height - overlap))
        
        print(f'📊 需要生成 {num_segments} 个片段')
        
        segments = []
        for i in range(num_segments):
            print(f'\n  🎨 生成片段 {i+1}/{num_segments}...')
            
            section_hint = ''
            if i == 0:
                section_hint = 'HEADER section with title and introduction.'
            elif i == num_segments - 1:
                section_hint = 'FOOTER section with summary and call-to-action.'
            else:
                section_hint = f'CONTENT section {i} with detailed information.'
            
            prompt = f"""Create a segment of a long infographic: {args.prompt}

Section: {section_hint} (Part {i+1} of {num_segments})
Style: Dark tech theme with neon blue (#00D4FF) and orange (#FF6B35) accents
Layout: Vertical, continuous flow for scrolling infographic"""
            
            segment = generate_image(prompt, '1024x1536', config)
            if segment:
                segments.append(segment)
                print(f'    ✅ 成功')
            else:
                print(f'    ❌ 失败')
        
        if segments:
            print(f'\n🔧 拼接 {len(segments)} 个片段...')
            
            # 创建最终图片
            final = Image.new('RGB', (1024, height), color=(15, 20, 25))
            
            current_y = 0
            for i, seg in enumerate(segments):
                if i == 0:
                    final.paste(seg, (0, 0))
                    current_y = seg.size[1]
                else:
                    cropped = seg.crop((0, overlap, seg.size[0], seg.size[1]))
                    final.paste(cropped, (0, current_y - overlap))
                    current_y += cropped.size[1] - overlap
            
            # 裁剪到目标高度
            if final.size[1] > height:
                final = final.crop((0, 0, 1024, height))
            
            # 调整宽度
            final = final.resize((width, height), Image.Resampling.LANCZOS)
            
            final.save(args.output)
            print(f'\n✅ 超长图已保存: {args.output}')
            print(f'   尺寸: {width}x{height}')
        else:
            print('❌ 所有片段生成失败')

if __name__ == '__main__':
    main()
