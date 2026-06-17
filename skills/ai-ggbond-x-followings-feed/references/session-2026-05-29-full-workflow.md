# Session 2026-05-29: 完整抓取-精选-日报工作流

## 背景
飞哥在飞书会话中要求"给一下我今天的x上的推文"。触发了完整的 X 关注流日报生成流程。

## 踩坑记录

### 1. 路径展开问题
```bash
# 失败：~ 被展开为错误路径
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5
# 错误: can't open file '/Users/admin/.hermes/profiles/touyan/home/.hermes/skills/...'

# 成功：使用绝对路径
python3 /Users/admin/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5
```

### 2. requests 模块缺失
```bash
# 错误: ModuleNotFoundError: No module named 'requests'
# 解决:
pip3 install requests -q
```

## 成功执行的完整流程

### Step 1: 代理预检
```bash
curl -I --max-time 5 -x http://127.0.0.1:7897 https://x.com
# 预期: HTTP/1.1 200 Connection established
```

### Step 2: 抓取数据（5页约200-280条）
```bash
export HTTPS_PROXY=http://127.0.0.1:7897
python3 /Users/admin/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5 > /tmp/x_following_latest.json 2>&1
# 输出: DONE: 136075 bytes
```

### Step 3: 精选打分（execute_code）
```python
import json
from datetime import datetime

with open('/tmp/x_following_latest.json') as f:
    raw = f.read()

# 提取JSON数组（处理日志污染）
idx = raw.rfind('\n[')
if idx == -1:
    idx = raw.rfind('[')
data = json.loads(raw[idx:])

SIGNAL_KEYWORDS = [
    'gpt', 'claude', 'gemini', 'llama', 'qwen', 'mistral', 'phi', 'yi',
    'benchmark', 'score', 'performance', 'version', 'v1', 'v2', 'v3', 'v4',
    'release', 'launch', 'announce', 'new', 'update', 'api', 'sdk',
    'open-source', 'open source', 'github', 'huggingface', 'hf',
    'agent', 'rag', 'fine-tune', 'finetune', 'lora', 'qlora',
    'price', 'pricing', 'free', 'discount', 'deal',
    'paper', 'arxiv', 'research', 'model', 'llm', 'ai'
]

def score_tweet(tweet):
    text = tweet.get('text', '').lower()
    if text.startswith('rt @') or len(text) < 20:
        return 0
    likes = tweet.get('likeCount') or 0
    retweets = tweet.get('retweetCount') or 0
    replies = tweet.get('replyCount') or 0
    engagement = likes + 2 * retweets + replies
    keyword_boost = sum(5 for kw in SIGNAL_KEYWORDS if kw in text)
    return engagement + keyword_boost

scored_tweets = [(score_tweet(t), t) for t in data if score_tweet(t) > 0]
scored_tweets.sort(key=lambda x: x[0], reverse=True)
top_tweets = [t for _, t in scored_tweets[:50]]

with open('/tmp/x_curated_tweets.json', 'w') as f:
    json.dump(top_tweets, f, ensure_ascii=False, indent=2)
```

### Step 4: 生成日报
读取精选结果，按 analyst_prompt_template.md 格式生成，包含：
- 🔥 重大事件
- 🚀 产品发布与更新
- 💡 技术洞察
- 🔗 资源汇总
- 🎯 个人视角（从 Memory 读取用户状态）

## 本次结果
- 总推文: 277 条
- 精选: 50 条（分数范围 23089 - 1）
- 日报长度: 4817 字符
- 高信号来源: @PeterDiamandis (多次), @gregisenberg, @zoomerfied, @ClementDelangue, @openclaw

## 关键发现
- PeterDiamandis 是高频高信号来源，多条推文被选中
- Anthropic Mythos 即将公开是重要信号
- Claude Code 动态工作流是产品发布亮点
- HF 异步 RL 权重同步成本降低 100 倍是技术突破
