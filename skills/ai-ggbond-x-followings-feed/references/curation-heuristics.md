# Curation heuristics for X followings digest

Session-derived notes for producing a useful digest from a user's Following feed.

## Retrieval default
- Prefer the paginated following-feed script, not `bird home`.
- Default to **3 pages (~120 tweets)**; increase to **5 pages (~200 tweets)** when the user wants a fuller daily digest.
- Keep `HTTPS_PROXY` configured when in mainland China.

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

## Output hygiene
- Preserve and surface the original tweet URL.
- Keep links as **bare URLs**, not code-formatted text, for Feishu/Lark clickability.
- If a tweet text is noisy or multi-line, normalize whitespace before summarizing.

## Parsing / tooling pitfall
- X response payloads and tweet text can contain characters that make naive `json.loads` on captured stdout brittle.
- Prefer reading the script's JSON output directly, or use a parser with `strict=False` if you must decode captured stdout.
- If the response is truncated, rerun the fetch with more careful capture rather than summarizing partial data.
