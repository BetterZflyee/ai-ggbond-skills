# 2026-05-21：X 长文转 Google 风格微信贴图经验

## 场景
用户给 X/Twitter 链接，要求把内容转换成微信贴图，并指定「图片风格与 Google 风格一致」。目标内容是 Peter Diamandis 的 X Article：`https://x.com/PeterDiamandis/status/2056843054359687465`。

## 有效抓取路径
本机没有 `xurl` 命令时，不要停在官方 API 工具缺失；可用 `api.fxtwitter.com` 读取公开 Tweet/Article 内容：

```bash
python - <<'PY'
import requests
url='https://api.fxtwitter.com/PeterDiamandis/status/2056843054359687465'
data=requests.get(url, timeout=20).json()['tweet']
art=data.get('article', {})
print('TITLE:', art.get('title'))
for b in art.get('content', {}).get('blocks', []):
    if b.get('text'):
        print(b['text'])
print('COVER:', art.get('cover_media',{}).get('media_info',{}).get('original_img_url'))
PY
```

返回结构要点：
- `tweet.article.title`：长文标题
- `tweet.article.preview_text`：预览摘要
- `tweet.article.content.blocks[].text`：正文段落
- `tweet.article.cover_media.media_info.original_img_url`：封面图

## Google 风格提示词要点
用户说「Google 风格」时，不要套默认小红书高饱和模板；应明确为：
- Google Material Design 3 + Google Doodle 科技插画
- 白底/极浅灰背景、高留白、圆角卡片、柔和阴影
- Google 蓝 `#4285F4`、红 `#EA4335`、黄 `#FBBC05`、绿 `#34A853` 少量点缀
- 干净、可信、科技感、乐观，像 Google 官方活动海报 / Gemini 产品发布信息图

## 本次生成与质检
- 生成命令显式指定 `--model gpt-image-2`，符合用户偏好。
- 输出尺寸为 `1792×1024`，横版，比例约 `1.75:1`，接近但非数学严格 16:9。
- Vision 质检：主体中文清晰，无明显乱码/错字；风格接近 Google 彩色扁平插画，但略偏中文知识信息图。

## Pitfalls
1. `sticker_manager.py --content` 会把传入内容原样写入，若内容自身包含 `# 标题`，同时 `--title` 又会生成标题，可能出现重复一级标题。生成后必须读取 Markdown 检查并修复。
2. 不要在生图完成前返回空消息。长工具链任务中，后台生图结束后应继续质检、汇总并返回交付物。
3. `xurl` 不存在或未配置时，不要让任务中断；公开 X 链接可先试 `api.fxtwitter.com/<handle>/status/<id>`。
4. 用户给定单条 X 链接并要求“围绕这一条信息”时，不要误触发 X 关注流/全量资讯简报；这属于“单链接内容转微信贴图”，边界是该 tweet/article 本身。