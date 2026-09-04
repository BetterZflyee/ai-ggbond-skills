# 图片生成脚本模板

本文档提供了生成文章配图的标准化脚本模板。

## 使用方式

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章配图生成脚本模板
基于 ai-ggbond-article-writer 技能

使用方法:
1. 将此脚本复制到文章目录下
2. 修改 images 数组中的内容
3. 运行脚本: python generate_article_images.py
"""

import os
import sys
from pathlib import Path

# 1. 正确添加技能脚本目录到路径
skill_scripts_dir = r'F:\AI Workstation\AI\Super_OPC\ai-ggbond-skills\skills\ai-ggbond-article-writer\scripts'
sys.path.insert(0, skill_scripts_dir)

# 2. 正确加载配置
try:
    from config_loader import load_all_env, apply_env_to_os
    load_all_env()
    apply_env_to_os()
    print("✅ 配置文件加载成功")
except ImportError as e:
    print(f"⚠️ 配置加载器导入失败: {e}")
    # 使用环境变量作为后备
    pass

# 3. 导入生成器
from generate_images_v4 import YunwuImageGenerator

# 4. 使用配置文件中的设置创建生成器
api_key = os.environ.get('YUNWU_API_KEY')
model = os.environ.get('YUNWU_DEFAULT_MODEL')  # 使用配置文件中的模型

if not api_key:
    print("❌ 未找到 YUNWU_API_KEY，请检查配置")
    sys.exit(1)

generator = YunwuImageGenerator(api_key=api_key)

# 5. 定义图片列表
images = [
    {
        'filename': '01-image.png',
        'prompt': '''
            图片描述...
            要求:
            - MINIMALIST风格
            - 纯色背景
            - 清晰的图形
            - 中文标签
        '''
    }
]

# 6. 生成并保存图片
import base64 as b64_module

def save_image(result, filename):
    """保存图片到文件"""
    if not result or not result.url:
        print(f"❌ {filename}: 未返回图片数据")
        return False

    try:
        url = result.url
        if url.startswith('data:'):
            # Base64 格式，需要解码
            base64_data = url.split(',', 1)[1]
            image_bytes = b64_module.b64decode(base64_data)
            with open(filename, 'wb') as f:
                f.write(image_bytes)
            print(f"✅ {filename} (Base64)")
            return True
        else:
            # URL 格式，需要下载
            import requests as req
            img_response = req.get(url, timeout=60)
            if img_response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                print(f"✅ {filename} (Downloaded)")
                return True
            else:
                print(f"❌ {filename}: 下载失败 {img_response.status_code}")
                return False
    except Exception as e:
        print(f"❌ {filename}: 保存失败 {e}")
        return False

# 生成所有图片
output_dir = Path(__file__).parent / 'images'
output_dir.mkdir(exist_ok=True)

for i, img in enumerate(images, 1):
    print(f"\n[{i}/{len(images)}] 生成 {img['filename']}...")
    result = generator.generate(
        prompt=img['prompt'].strip(),
        size='1792x1024'
    )
    save_image(result, output_dir / img['filename'])

print("\n完成!")
```

## 关键要点

### 0. API 端点策略

`YunwuImageGenerator` 根据模型自动选择最佳 API 端点：

| 模型 | API 端点 | 说明 |
|------|---------|------|
| `gpt-image-2`, `gpt-image-1`, `dall-e-3` | `/v1/images/generations` | OpenAI Images API，中文渲染最佳 |
| 其他模型（Gemini 系列等） | Gemini + OpenAI chat 双模式 | 自动回退机制 |

```python
# gpt-image-2 会自动使用 Images API
result = generator.generate(prompt="...", model="gpt-image-2")

# 其他模型使用 Gemini/chat 双模式
result = generator.generate(prompt="...", model="gemini-3.1-flash-image-preview")
```

### 1. 配置加载
```python
# 正确方式: 使用 config_loader
from config_loader import load_all_env, apply_env_to_os
load_all_env()
apply_env_to_os()

# 获取配置
api_key = os.environ.get('YUNWU_API_KEY')
model = os.environ.get('YUNWU_DEFAULT_MODEL')  # 不要硬编码模型
```

### 2. YunwuImageGenerator 使用
```python
# 创建生成器
generator = YunwuImageGenerator(api_key=api_key)

# 生成图片
result = generator.generate(
    prompt="图片描述",
    size="1792x1024"  # 可选尺寸: 1792x1024, 1024x1024, 1024x1792
)

# 错误方式:
# generator.generate_image(...) ❌
# generator.generate(..., output_path="...") ❌
```

### 3. 处理返回结果
```python
# result.url 可能是:
# 1. Base64 格式: "data:image/png;base64,...."
# 2. URL 格式: "https://example.com/image.png"

if result and result.url:
    if result.url.startswith('data:'):
        # Base64 格式
        base64_data = result.url.split(',', 1)[1]
        image_bytes = b64_module.b64decode(base64_data)
        with open('output.png', 'wb') as f:
            f.write(image_bytes)
    else:
        # URL 格式，需要下载
        import requests
        img_response = requests.get(result.url)
        with open('output.png', 'wb') as f:
            f.write(img_response.content)
```

### 4. 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `generate_image() got unexpected keyword argument 'output_path'` | 方法参数错误 | 使用 `generate()` 而不是 `generate_image()` |
| `YunwuImageGenerator.__init__() got an unexpected keyword argument 'base_url'` | 初始化参数错误 | 只传递 `api_key` |
| 生成的图片为空 | API返回base64但未解码 | 检查并正确处理 base64 数据 |
| API返回429/403 | IP不在白名单或配额用完 | 检查API配置和网络 |

## 完整示例

参考 `scripts/generate_images_v4.py` 中的实现。

## 配置文件位置

按优先级依次查找:
1. 系统环境变量
2. 项目级配置: `{project}/.ai-ggbond-skills/.env`
3. 用户级配置: `~/.ai-ggbond-skills/.env`
4. 技能目录配置: `{skill_dir}/.env`

关键配置项:
- `YUNWU_API_KEY`: 云雾API密钥
- `YUNWU_BASE_URL`: API端点(默认 https://api.openlux.ai)
- `YUNWU_DEFAULT_MODEL`: 默认模型(默认 gpt-image-2，使用 /v1/images/generations 端点)
