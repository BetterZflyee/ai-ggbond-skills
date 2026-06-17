# curl 直接调 X GraphQL API 工作流

## 背景

当 `requests` 模块不可用（系统 Python 3.9 无 requests，pip 因网络问题无法安装）且 Python `urllib` + `ProxyHandler` 返回 401 时，curl 是唯一可靠的 fallback。

## 完整 curl 命令

```bash
export HTTPS_PROXY=http://127.0.0.1:7897

curl -s --max-time 20 -x $HTTPS_PROXY \
  -H "Cookie: auth_token=${AUTH_TOKEN}; ct0=${CT0}" \
  -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA" \
  -H "x-csrf-token: ${CT0}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -H "x-twitter-active-user: yes" \
  -H "x-twitter-client-language: en" \
  -X POST \
  -d '{"variables":{"count":40,"includePromotedContent":false,"latestControlAvailable":true,"requestContext":"launch"},"features":{"profile_label_improvements_pcf_label_in_post_enabled":false,"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}}' \
  "https://x.com/i/api/graphql/iOEZpOdfekFsxSlPQCQtPg/HomeLatestTimeline"
```

## 分页获取

分页需要从上一页响应中提取 Bottom cursor，然后作为 `variables.cursor` 传入下一页请求。

### Shell 分页脚本核心逻辑

```bash
# 第一页
page1=$(fetch_page "")

# 用 python3 提取 cursor（不依赖 requests）
cursor2=$(echo "$page1" | python3 -c "
import json,sys
data=json.load(sys.stdin)
for inst in data.get('data',{}).get('home',{}).get('home_timeline_urt',{}).get('instructions',[]):
    for e in inst.get('entries',[]):
        c=e.get('content',{})
        if c.get('entryType')=='TimelineTimelineCursor' and c.get('cursorType')=='Bottom':
            print(c.get('value',''))
            break
")

# 带 cursor 请求第二页
page2=$(fetch_page "$cursor2")
```

### 注意：cursor 中有特殊字符

X 的 cursor 值包含 `=` 和 `%` 等特殊字符，传入 curl `-d` 的 JSON 时需要正确转义。建议用 python3 生成完整的 JSON body 再传给 curl，或用 heredoc。

## 数据解析

响应结构：
```json
{
  "data": {
    "home": {
      "home_timeline_urt": {
        "instructions": [{
          "type": "TimelineAddEntries",
          "entries": [
            { "content": { "entryType": "TimelineTimelineItem", "itemContent": { ... } } },
            { "content": { "entryType": "TimelineTimelineCursor", "cursorType": "Bottom", "value": "..." } }
          ]
        }]
      }
    }
  }
}
```

解析要点：
- 跳过 `promotedMetadata`（广告）
- 跳过 `RT @` 开头的纯转推
- 用户信息优先 `.core`（Following 流），fallback `.legacy`（For You 流）
- 去重 by `id_str`

## 已验证数据

- 2026-06-03 测试：3 页共 161 条推文，111 条原创
- 代理：`http://127.0.0.1:7897`（Clash Verge）
- 认证：环境变量 AUTH_TOKEN + CT0

## urllib 401 问题

同一组 Cookie + Bearer Token + Headers：
- curl `-x` → 200 ✅
- Python urllib + ProxyHandler → 401 ❌

原因未完全确认，可能与 urllib 的 HTTPS CONNECT 代理握手方式有关。**不要浪费时间调试，直接用 curl。**
