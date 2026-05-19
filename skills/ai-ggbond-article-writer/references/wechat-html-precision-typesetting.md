# 微信公众号 HTML 精排版：金句断点与长文节奏

## 触发场景

当用户反馈公众号草稿“排版累、读起来不舒服、需要金句断点、不要默认主题、要 HTML 精排版”时使用。

## 关键纠偏

- “金句断点”是编辑术语，不是正文标题。严禁在正文中出现“金句断点”四个字。
- `ai-ggbond-post-to-wechat` 主要是发布/图片上传/Markdown 或 HTML 推送工具，不是精细排版器。精排需求应先生成自定义 HTML，再用发布技能推送。
- 不要把每句话都独立成段。公众号长文应长短交替：普通论述合并成中段，强观点/金句单独成段。
- 用户要求先沟通清楚再做时，必须停止写文件和推送，先确认排版选项。

## 飞哥确认过的偏好

1. 金句形式：A 为主、B 少量、C 少量点缀。
   - A：正文自然加粗短句，嵌入上下文。
   - B：少量独立金句卡片，用于强转折或结尾。
   - C：少量引用块，引经据典增强厚度。
2. 段落：大量合并，长短交替，读起来有节奏。
3. 图片：数量可保持不变，但位置要合适，最好放在每一小节/章节开头。
4. 视觉：白底黑字高留白为主，少量技术蓝。
5. 交付：先做 HTML 精排版预览，不要直接推新草稿。

## 推荐流程

1. 从原版正文恢复，不要基于错误排版版继续叠改。
2. 先确认需求：金句形式、段落合并、图片数量与位置、视觉风格、交付方式。
3. 生成 HTML 精排预览文件：
   - 白底，正文 `15-16px`，行高 `1.85-1.95`。
   - 主色少量用技术蓝，如 `#2563EB`。
   - 普通段落合并到约 140-260 字，避免碎句墙。
   - 强观点单独成段，加粗，不加“金句断点”标签。
   - 独立卡片控制在 2-4 个，引用块控制在 1-3 个。
4. 图片 `<img>` 使用相对路径，放在章节标题或关键小节标题后，样式建议：`width:100%; border-radius:12px; margin:18px 0 28px`。
5. 本地校验：图片数量、路径存在、无“金句断点”字样、HTML 可被发布脚本 dry-run。
6. 用户确认预览后，再用 `ai-ggbond-post-to-wechat` 推送 HTML 到公众号草稿箱。

## 校验命令示例

```bash
python3 - <<'PY'
from pathlib import Path
import re
p=Path('/path/to/article-HTML精排预览版.html')
s=p.read_text(encoding='utf-8')
print('imgs=', len(re.findall(r'<img\\b', s)))
print('h2=', len(re.findall(r'<h2\\b', s)))
print('blockquotes=', len(re.findall(r'<blockquote\\b', s)))
print('bad=', '金句断点' in s)
print('local imgs missing=', [m for m in re.findall(r'src="([^"]+)"', s) if not (p.parent/m).exists()][:5])
PY
```

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts
npx -y bun wechat-api.ts /path/to/article.html \
  --title '标题' \
  --summary '摘要' \
  --author 'AI朱朱侠' \
  --cover /path/to/cover.png \
  --dry-run
```
