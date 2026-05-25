# Curation heuristics for X followings digest

Session-derived notes for producing a useful digest from a user's Following feed.

## Retrieval default
- Prefer the paginated following-feed script, not `bird home`.
- Default to **3 pages (~120 tweets)**; increase to **5 pages (~200 tweets)** when the user wants a fuller daily digest.
- Keep `HTTPS_PROXY` configured when in mainland China.

## Automated scoring & filtering
- Use inline Python (via `execute_code`) to filter and rank tweets:
  - Load JSON from `/tmp/x_following_latest.json`
  - Remove pure RTs and tweets < 20 chars
  - Score by `engagement (like + 2×retweet + reply)` + `signal keyword boost (×5 weight)`
  - Signal keywords include: model names (GPT, Claude, Gemini, Llama, Qwen...), benchmark terms, version numbers, pricing, product launch terms, open-source indicators, agent/RAG/fine-tuning terms
- Output top 40-60 high-signal tweets for digest generation.
- **Prefer execute_code** over a separate script — it keeps the scoring logic visible and editable in-session.

## Selection heuristics
- **De-emphasize pure retweets** (`RT @...`) unless the retweet itself is the strongest signal.
- Rank by a simple engagement score: `likeCount + 2*retweetCount + replyCount`.
- Prefer items with concrete nouns, versions, benchmarks, pricing, names, or URLs over vague commentary.
- Bucket items into class-level categories:
  - Major events
  - Product releases / updates
  - Technical insights
  - Resources
  - Deals / freebies
  - Sentiment / warning signals

## Memory-driven Personal Lens workflow (v1.5.0)

The digest now includes a `🎯 个人视角` section that maps today's signals to the **current user's** actual priorities. This is **user-agnostic** — no user state is hardcoded in the skill.

**Before generating the Personal Lens section:**
1. Read the MEMORY and USER PROFILE blocks from the system prompt — these contain the current user's identity, main threads, focus areas, and style preferences.
2. Map each high-signal tweet from the digest to the user's actual threads (e.g., job hunting → interview talking points; side project → applicable cases; content IP → article topics).
3. Generate action items that are immediately doable within the user's current threads.
4. Follow the user's stored response style (e.g., classic quotes as anchors, mathematical theories for rigor).

**Key pitfall to avoid:** Do NOT fabricate user threads. If Memory says "job hunting 70%, manufacturing 20%, content 10%", use those exact threads. If Memory says something else, use that instead. The template is the same — the content is user-specific.

## Output hygiene
- Preserve and surface the original tweet URL.
- Keep links as **bare URLs**, not code-formatted text, for Feishu/Lark clickability.
- If a tweet text is noisy or multi-line, normalize whitespace before summarizing.

## Parsing / tooling pitfall
- X response payloads and tweet text can contain characters that make naive `json.loads` on captured stdout brittle.
- Prefer reading the script's JSON output directly, or use a parser with `strict=False` if you must decode captured stdout.
- If the response is truncated, rerun the fetch with more careful capture rather than summarizing partial data.
