#!/bin/bash
# ============================================
# 云雾 API 配置与测试脚本
# 使用方法: bash setup_yunwu.sh <你的API_KEY>
# 示例: bash setup_yunwu.sh sk-xxxxxx
# ============================================

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 请提供 API Key"
    echo "用法: bash setup_yunwu.sh <API_KEY>"
    echo "示例: bash setup_yunwu.sh sk-xxxxxx"
    exit 1
fi

API_KEY="$1"...CONFIG_FILE="$HOME/.hermes/profiles/gongcheng/config.yaml"

echo "🔧 配置云雾 API..."
echo "📏 Key 长度: ${#API_KEY} 字符"

# 备份配置文件
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"
echo "✅ 已备份配置文件"

# 更新配置
python3 << PYEOF
import re

API_KEY='***'
CONFIG_PATH = '$CONFIG_FILE'

with open(CONFIG_PATH, 'r') as f:
    content = f.read()

# 替换 image_gen 部分的 api_key
lines = content.split('\n')
new_lines = []
in_image_gen = False

for line in lines:
    if 'image_gen:' in line:
        in_image_gen = True
        new_lines.append(line)
    elif in_image_gen and 'api_key:' in line:
        new_lines.append(f'  api_key: {API_KEY}')
        in_image_gen = False
    else:
        new_lines.append(line)

with open(CONFIG_PATH, 'w') as f:
    f.write('\n'.join(new_lines))

print('✅ 配置文件已更新')
PYEOF

# 验证配置
echo ""
echo "📋 当前配置:"
grep -A 4 "image_gen:" "$CONFIG_FILE"

echo ""
echo "🧪 测试 API 连接..."

python3 << 'PYEOF'
import requests
import json
import yaml

config_path = '/Users/admin/.hermes/profiles/gongcheng/config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

api_key = config.get('image_gen', {}).get('api_key', '')
base_url = config.get('image_gen', {}).get('base_url', '')

print(f'📏 Key 长度: {len(api_key)} 字符')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'model': 'gpt-image-2',
    'prompt': 'A blue circle on white background',
    'n': 1,
    'size': '1024x1024'
}

try:
    response = requests.post(
        f'{base_url}/images/generations',
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        print('✅ API 连接成功!')
    else:
        error = response.json().get('error', {})
        print(f'❌ API 错误: {error.get("message", "")[:100]}')
        exit(1)
except Exception as e:
    print(f'❌ 连接失败: {e}')
    exit(1)
PYEOF

echo ""
echo "✅ 配置完成! 现在可以使用长图生成功能了"
