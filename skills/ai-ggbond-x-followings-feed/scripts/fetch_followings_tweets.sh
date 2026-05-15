#!/usr/bin/env bash
# fetch_followings_tweets.sh - 获取 Home Timeline 最新推文
# 用法: ./fetch_followings_tweets.sh [数量] [天数]
# 示例: ./fetch_followings_tweets.sh 50 1  (获取50条推文)
# 输出: JSON 格式的推文数据，每条附带 url 字段
#
# ⚠️ 重要：使用 `bird home` 而非 `bird following`
# - `bird home`   → Home Timeline 推文（正确）
# - `bird following` → 关注用户列表/Profile（不是推文）

set -e

LIMIT="${1:-20}"
DAYS="${2:-1}"

# 检查环境变量
if [ -z "$AUTH_TOKEN" ] || [ -z "$CT0" ]; then
    echo '{"error": "Missing AUTH_TOKEN or CT0 environment variables. Export from ~/.hermes/.env or set directly."}' >&2
    exit 1
fi

# 网络连通性预检（bird 遇到网络不通会挂起30秒+）
if ! curl -s -o /dev/null -w "" --max-time 5 https://x.com 2>/dev/null; then
    echo '{"error": "Cannot reach x.com — check network/VPN. bird CLI will timeout without connectivity."}' >&2
    exit 1
fi

# 获取 Following 关注流推文（--following 获取关注列表，不加则获取推荐流）
if ! TWEETS=$(bird home --following --json -n "$LIMIT" 2>/dev/null) || [ -z "$TWEETS" ]; then
    echo '{"error": "Failed to fetch tweets from home timeline"}' >&2
    exit 1
fi

# 后处理：为每条推文添加 url 字段（从 author.username + id 拼接）
# 通过 stdin 管道传 JSON 给 python，避免 shell 变量注入
PROCESSED=$(echo "$TWEETS" | python3 -c "
import json, sys
tweets = json.load(sys.stdin)
for t in tweets:
    uid = t.get('author', {}).get('username', '')
    tid = t.get('id', '')
    if uid and tid:
        t['url'] = f'https://x.com/{uid}/status/{tid}'
    qt = t.get('quotedTweet')
    if qt:
        quid = qt.get('author', {}).get('username', '')
        qtid = qt.get('id', '')
        if quid and qtid:
            qt['url'] = f'https://x.com/{quid}/status/{qtid}'
json.dump(tweets, sys.stdout, ensure_ascii=False)
" 2>/dev/null)

if [ -z "$PROCESSED" ]; then
    # python 后处理失败，回退原始输出
    echo "{\"days\": $DAYS, \"limit\": $LIMIT, \"tweets\": $TWEETS}"
else
    echo "{\"days\": $DAYS, \"limit\": $LIMIT, \"tweets\": $PROCESSED}"
fi
