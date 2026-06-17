# fxtwitter API — 免 Auth 的推文数据获取方案

> `api.fxtwitter.com` 是第三方 X/Twitter 数据 API，无需认证即可获取推文详情、视频URL、图片URL。

## 核心用途

- 获取单条推文的完整数据（文字、媒体、互动数据）
- 获取视频/图片的直接下载 URL
- 作为 X GraphQL API 的 fallback（当 auth 失效时）
- 获取推文详情用于文章写作、素材收集

## API 格式

```
GET https://api.fxtwitter.com/{username}/status/{tweet_id}
```

**无需任何 Header、Cookie、Bearer Token。** 通过代理访问：

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
curl -s --max-time 15 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  "https://api.fxtwitter.com/NousResearch/status/2061843507417944552"
```

## 返回结构

```json
{
  "tweet": {
    "url": "https://x.com/...",
    "id": "2061843507417944552",
    "text": "推文正文",
    "raw_text": { "text": "含 t.co 链接的原始文本" },
    "author": {
      "screen_name": "NousResearch",
      "name": "Nous Research",
      "followers": 123456,
      "avatar_url": "..."
    },
    "likes": 1000,
    "retweets": 200,
    "bookmarks": 500,
    "views": 50000,
    "created_at": "Wed Jun 03 09:16:21 +0000 2026",
    "media": {
      "videos": [
        {
          "url": "https://video.twimg.com/amplify_video/...",
          "duration": 78.413,
          "sources": [
            { "url": "...mp4", "quality": "1080p" }
          ]
        }
      ],
      "photos": [
        { "url": "https://pbs.twimg.com/media/..." }
      ]
    },
    "article": {
      "title": "X Article 标题",
      "preview_text": "预览文字",
      "content": { "blocks": [...] }
    }
  }
}
```

## 关键字段路径

| 数据 | 路径 |
|------|------|
| 推文文字 | `tweet.text` 或 `tweet.raw_text.text` |
| 作者名 | `tweet.author.name` |
| 作者 handle | `tweet.author.screen_name` |
| 视频 URL（最高质量） | `tweet.media.videos[0].url` |
| 视频时长 | `tweet.media.videos[0].duration`（秒） |
| 图片 URL | `tweet.media.photos[0].url` |
| X Article 标题 | `tweet.article.title` |
| X Article 内容 | `tweet.article.content.blocks[]` |
| 点赞数 | `tweet.likes` |
| 浏览量 | `tweet.views` |

## 视频下载完整流程

```bash
export HTTPS_PROXY=http://127.0.0.1:7897

# Step 1: 获取视频 URL
VIDEO_URL=$(curl -s --max-time 15 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  "https://api.fxtwitter.com/{user}/status/{tweet_id}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['tweet']['media']['videos'][0]['url'])")

# Step 2: 下载视频
curl -L --max-time 180 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  -o /tmp/video.mp4 \
  "$VIDEO_URL"
```

**注意事项**：
- 视频文件通常较大（50-100MB），设置较长 timeout
- `curl -L` 必须（跟随重定向）
- 下载后用 `ls -lh` 检查文件大小确认完整性
- 4K 视频（3840x2160）约 1 分钟 = 19MB，2 分钟 = 68MB

## X Article 内容提取

fxtwitter 可以获取 X Article（长文推文）的完整内容：

```python
import json, urllib.request

proxy_handler = urllib.request.ProxyHandler({'https': 'http://127.0.0.1:7897'})
opener = urllib.request.build_opener(proxy_handler)

req = urllib.request.Request(
    'https://api.fxtwitter.com/{user}/status/{tweet_id}',
    headers={'User-Agent': 'Mozilla/5.0'}
)
data = json.loads(opener.open(req, timeout=15).read())

article = data['tweet']['article']
print(f'Title: {article["title"]}')

for block in article['content']['blocks']:
    text = block.get('text', '')
    btype = block.get('type', '')
    if text.strip():
        if btype == 'header-two':
            print(f'\n## {text}')
        elif btype == 'unordered-list-item':
            print(f'  • {text}')
        else:
            print(text)
```

## 局限性

- 非官方 API，可能随时失效
- 不支持搜索/时间线/关注列表，只支持单条推文查询
- 偶尔返回空数据（推文被删或被保护时）
- X Article 的 blocks 结构是 Draft.js 格式，需要手动解析

## 与 X GraphQL API 的关系

| 场景 | 用哪个 |
|------|--------|
| 批量获取关注流（40-200条） | X GraphQL API（需要 auth） |
| 获取单条推文详情 | fxtwitter（无需 auth） |
| 获取视频/图片下载 URL | fxtwitter（直接给 URL） |
| 获取 X Article 全文 | fxtwitter（结构化 JSON） |
| auth 失效时的 fallback | fxtwitter |
