# 批量生图中途被砍后的续跑模式（2026-05-25）

## 场景

用 gpt-image-2 批量生成 10 张公众号配图，脚本在后台跑到一半时被 Hermes 会话重启/超时杀死。进程退出后只剩部分图片。

## 续跑模式

不要从头重跑（会浪费已生成图片的 API 调用）。按以下步骤续跑：

1. **检查已落地文件**：`find images/ -name '*.png' -type f | sort`
2. **统计已完成数/总数**
3. **写续跑脚本**：for 循环逐个检查目标文件是否存在，存在且 >10KB 则 skip
4. **使用相同的 BASE_STYLE**（暖米白手绘等），确保前后图片风格一致
5. **仅生成缺失的图片**，跳过已完成的

## 续跑脚本模板

```python
#!/usr/bin/env python3
from pathlib import Path
import sys, time
sys.path.insert(0, str(SCRIPT_DIR))
from generate_images_v4 import YunwuImageGenerator

OUT = Path('images/')
OUT.mkdir(parents=True, exist_ok=True)
ITEMS = [
    ('04-xxx.png', '1792x1024', 'prompt...'),
    ('05-xxx.png', '1792x1024', 'prompt...'),
]

gen = YunwuImageGenerator()
for filename, size, spec in ITEMS:
    path = OUT / filename
    if path.exists() and path.stat().st_size > 10000:
        print(f'skip exists {path}')
        continue
    prompt = BASE_STYLE + '\n' + spec
    result = gen.generate(prompt=prompt, model='gpt-image-2', size=size, max_retries=3)
    gen.download_image(result.url, str(path))
    time.sleep(15)
```

## 关键原则

- **必须检查文件大小**：仅靠 `path.exists()` 不够，可能有不完整的 0 字节文件
- **续跑脚本保存到 `images/prompts/resume_remaining.py`**，方便追溯
- **不改变 prompt 内容**：续跑和首次跑的 prompt 必须一致，否则前后图片风格不统一
