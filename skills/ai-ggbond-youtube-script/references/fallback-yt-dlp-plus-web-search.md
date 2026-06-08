# Fallback: yt-dlp Metadata + Web Search Third-Party Summaries

**Verified:** 2026-06-07
**Video:** `X_JsIHUfUjc` — "How to Build a Self-Improving Company with AI" (Y Combinator, Tom Blomfield, 13 min)

## What Failed
1. `youtube-content` (Python skill) — wrong skill, pip not available
2. `ai-ggbond-youtube-script` InnerTube API — "bot detected", empty snippets
3. yt-dlp subtitle list — "no automatic captions", "no subtitles"
4. Bun subprocess couldn't find yt-dlp after pip install (PATH issue)

## What Worked

### 1. yt-dlp metadata extraction (direct CLI)
```bash
/Users/admin/.hermes/profiles/neirong/home/Library/Python/3.9/bin/yt-dlp \
  --proxy http://127.0.0.1:7897 \
  --print title --print channel --print description --print duration \
  'https://youtu.be/X_JsIHUfUjc' 2>/dev/null | head -50
```
Result: Full title, channel, description with 12 chapter timestamps, duration (808s).

### 2. Web search queries that worked
```
web_search → Tom Blomfield "How to Build a Self-Improving Company with AI" Y Combinator transcript summary
```
Top results:
- YouTube original (not useful)
- YC Startup Library page (metadata only)
- **LinkedIn post by Linas Beliūnas** — comprehensive summary with 5-layer framework, 141 comments with critical counterpoints
- **Towards AI Medium post** — article format
- **CompleteRPABootcamp blog** — chapter-by-chapter breakdown with direct quotes

### 3. Web extract sources
```
web_extract → [
  "https://www.linkedin.com/posts/linasbeliunas_this-is-tom-blomfield-...",
  "https://completerpabootcamp.com/blogs/how-to-build-a-self-improving-company-with-ai"
]
```

## Quality Assessment
- LinkedIn post: Best for frameworks, key quotes, and community debate (critical counterpoints on governance, cost, security)
- Blog post: Best for structured chapter breakdown with direct quotes
- Combined coverage: All 12 chapters covered, 6 key quotes extracted, 5-layer recursive loop framework documented

## Output Format Used
Delivered as structured summary with:
1. Video metadata (title, channel, speaker, duration)
2. Chapter-by-chapter content (matching video's own chapter structure)
3. Key quotes block
4. Disclaimer: "based on third-party summaries, not word-for-word transcript"
