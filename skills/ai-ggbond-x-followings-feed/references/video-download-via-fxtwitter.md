# X/Twitter 视频下载 via fxtwitter API

## 背景

X 的 GraphQL API 经常更换 query ID，且需要 auth token。对于只需要下载推文视频/图片的场景，`api.fxtwitter.com` 是更可靠的免认证方案。

## 用法

```bash
export HTTPS_PROXY=http://127.0.0.1:7897  # 中国大陆必需

# 获取推文媒体信息
curl -s --max-time 15 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  "https://api.fxtwitter.com/{username}/status/{tweet_id}"
```

## 响应结构

```json
{
  "tweet": {
    "text": "推文文本",
    "author": { "name": "显示名", "screen_name": "用户名" },
    "media": {
      "videos": [
        {
          "url": "https://video.twimg.com/amplify_video/.../vid/avc1/3840x2160/xxx.mp4?tag=27",
          "duration": 78.413,
          "type": "video"
        }
      ],
      "photos": [
        { "url": "https://pbs.twimg.com/media/xxx.jpg" }
      ]
    },
    "article": {  // X Article（长文）
      "title": "文章标题",
      "content": { "blocks": [...] }
    }
  }
}
```

## 完整下载脚本

```bash
#!/bin/bash
# Usage: ./download_x_video.sh <tweet_url>
export HTTPS_PROXY=http://127.0.0.1:7897

TWEET_URL="$1"
# Extract username and tweet_id from URL
USERNAME=$(echo "$TWEET_URL" | grep -oP 'x\.com/\K[^/]+')
TWEET_ID=$(echo "$TWEET_URL" | grep -oP '/status/\K\d+')

# Get video URL
VIDEO_URL=$(curl -s --max-time 15 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  "https://api.fxtwitter.com/$USERNAME/status/$TWEET_ID" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
videos = data.get('tweet', {}).get('media', {}).get('videos', [])
if videos:
    # Pick highest quality (first in list is usually best)
    print(videos[0].get('url', ''))
")

if [ -z "$VIDEO_URL" ]; then
  echo "No video found in tweet"
  exit 1
fi

# Download
OUTPUT="/tmp/${USERNAME}_${TWEET_ID}.mp4"
curl -L --max-time 300 -x $HTTPS_PROXY \
  -H "User-Agent: Mozilla/5.0" \
  -o "$OUTPUT" "$VIDEO_URL"

ls -lh "$OUTPUT"
echo "Saved to: $OUTPUT"
```

## 注意事项

- fxtwitter 是第三方服务，非官方 API，可能随时失效
- 视频 URL 指向 `video.twimg.com`，下载时需要代理（中国大陆）
- 大文件（>100MB）下载可能超时，建议用 `--max-time 300`
- X Article 长文内容也在 `tweet.article.content.blocks` 中，可提取完整文本
- 如果 fxtwitter 也不可用，备选方案：`api.vxtwitter.com`（同系列服务）

## 成功案例

- NousResearch Hermes Desktop 演示视频：4K 3840x2160, 78s, 19MB ✅
- Riley Brown Codex Paper 演示：3340x2160, 143s, 68MB ✅
