#!/usr/bin/env python3
"""
云雾 API 测试脚本
测试 API 连接和图片生成
"""

import requests
import json
import base64
import yaml
from PIL import Image
from io import BytesIO

def load_config():
    """从配置文件加载 API 设置"""
    config_path = '/Users/admin/.hermes/profiles/gongcheng/config.yaml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    image_gen = config.get('image_gen', {})
    return {
        'api_key': image_gen.get('api_key', ''),
        'base_url': image_gen.get('base_url', 'https://yunwu.ai/v1'),
        'model': image_gen.get('model', 'gpt-image-2')
    }

def test_api():
    """测试 API 连接"""
    config = load_config()
    
    print('=' * 50)
    print('🧪 云雾 API 测试')
    print('=' * 50)
    print(f'📏 Key 长度: {len(config["api_key"])} 字符')
    print(f'🌐 Base URL: {config["base_url"]}')
    print(f'🎨 Model: {config["model"]}')
    print()
    
    if len(config['api_key']) < 20:
        print('❌ API Key 长度不足，请重新配置')
        return False
    
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': config['model'],
        'prompt': 'A simple blue circle on white background, minimalist design',
        'n': 1,
        'size': '1024x1024'
    }
    
    print('🧪 测试图片生成...')
    try:
        response = requests.post(
            f'{config["base_url"]}/images/generations',
            headers=headers,
            json=data,
            timeout=120
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ API 连接成功!')
            result = response.json()
            if result.get('data'):
                image_data = result['data'][0]
                if 'b64_json' in image_data:
                    image_bytes = base64.b64decode(image_data['b64_json'])
                    img = Image.open(BytesIO(image_bytes))
                    img.save('/tmp/api_test_success.png')
                    print(f'✅ 测试图片已保存: /tmp/api_test_success.png')
                    print(f'   尺寸: {img.size[0]}x{img.size[1]}')
                elif 'url' in image_data:
                    print(f'图片 URL: {image_data["url"][:80]}...')
            return True
        else:
            error = response.json().get('error', {})
            print(f'❌ API 错误: {error.get("message", "")[:200]}')
            return False
            
    except Exception as e:
        print(f'❌ 请求异常: {e}')
        return False

if __name__ == '__main__':
    test_api()
