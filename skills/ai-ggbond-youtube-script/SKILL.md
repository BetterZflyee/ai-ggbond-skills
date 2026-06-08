---
name: ai-ggbond-youtube-script
description: Downloads YouTube video transcripts/subtitles and cover images by URL or video ID. Supports multiple languages, translation, chapters, and speaker identification. Caches raw data for fast re-formatting. Use when user asks to "get YouTube transcript", "download subtitles", "get captions", "YouTube字幕", "YouTube封面", "视频封面", "video thumbnail", "video cover image", or provides a YouTube URL and wants the transcript/subtitle text or cover image extracted.
version: 1.1.0
metadata:
  openclaw:
    homepage: https://github.com/BetterZflyee/ai-ggbond-skills#ai-ggbond-youtube-script
    requires:
      anyBins:
        - bun
        - npx
---

# YouTube Transcript

Downloads transcripts (subtitles/captions) from YouTube videos. Works with both manually created and auto-generated transcripts. No API key or browser required — uses YouTube's InnerTube API directly and automatically falls back to `yt-dlp` when YouTube blocks the direct API path.

Fetches video metadata and cover image on first run, caches raw data for fast re-formatting.

## Script Directory

Scripts in `scripts/` subdirectory. `{baseDir}` = this SKILL.md's directory path. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun. Replace `{baseDir}` and `${BUN_X}` with actual values.

| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | Transcript download CLI |

## Usage

```bash
# Default: markdown with timestamps (English)
${BUN_X} {baseDir}/scripts/main.ts <youtube-url-or-id>

# Specify languages (priority order)
${BUN_X} {baseDir}/scripts/main.ts <url> --languages zh,en,ja

# Without timestamps
${BUN_X} {baseDir}/scripts/main.ts <url> --no-timestamps

# With chapter segmentation
${BUN_X} {baseDir}/scripts/main.ts <url> --chapters

# With speaker identification (requires AI post-processing)
${BUN_X} {baseDir}/scripts/main.ts <url> --speakers

# SRT subtitle file
${BUN_X} {baseDir}/scripts/main.ts <url> --format srt

# Translate transcript
${BUN_X} {baseDir}/scripts/main.ts <url> --translate zh-Hans

# List available transcripts
${BUN_X} {baseDir}/scripts/main.ts <url> --list

# Force re-fetch (ignore cache)
${BUN_X} {baseDir}/scripts/main.ts <url> --refresh
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<url-or-id>` | YouTube URL or video ID (multiple allowed) | Required |
| `--languages <codes>` | Language codes, comma-separated, in priority order | `en` |
| `--format <fmt>` | Output format: `text`, `srt` | `text` |
| `--translate <code>` | Translate to specified language code | |
| `--list` | List available transcripts instead of fetching | |
| `--timestamps` | Include `[HH:MM:SS → HH:MM:SS]` timestamps per paragraph | on |
| `--no-timestamps` | Disable timestamps | |
| `--chapters` | Chapter segmentation from video description | |
| `--speakers` | Raw transcript with metadata for speaker identification | |
| `--exclude-generated` | Skip auto-generated transcripts | |
| `--exclude-manually-created` | Skip manually created transcripts | |
| `--refresh` | Force re-fetch, ignore cached data | |
| `-o, --output <path>` | Save to specific file path | auto-generated |
| `--output-dir <dir>` | Base output directory | `youtube-transcript` |

## Optional Environment Variables

| Variable | Description |
|----------|-------------|
| `YOUTUBE_TRANSCRIPT_COOKIES_FROM_BROWSER` | Passed to `yt-dlp --cookies-from-browser` during fallback, e.g. `chrome`, `safari`, `firefox`, or `chrome:Profile 1` |

## Input Formats

Accepts any of these as video input:
- Full URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URL: `https://youtu.be/dQw4w9WgXcQ`
- Embed URL: `https://www.youtube.com/embed/dQw4w9WgXcQ`
- Shorts URL: `https://www.youtube.com/shorts/dQw4w9WgXcQ`
- Video ID: `dQw4w9WgXcQ`

## Output Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `text` | `.md` | Markdown with frontmatter (incl. `description`), title heading, summary, optional TOC/cover/timestamps/chapters/speakers |
| `srt` | `.srt` | SubRip subtitle format for video players |

## Output Directory

```
youtube-transcript/
├── .index.json                          # Video ID → directory path mapping (for cache lookup)
└── {channel-slug}/{title-full-slug}/
    ├── meta.json                        # Video metadata (title, channel, description, duration, chapters, etc.)
    ├── transcript-raw.json              # Raw transcript snippets from YouTube API (cached)
    ├── transcript-sentences.json        # Sentence-segmented transcript (split by punctuation, merged across snippets)
    ├── imgs/
    │   └── cover.jpg                    # Video thumbnail
    ├── transcript.md                    # Markdown transcript (generated from sentences)
    └── transcript.srt                   # SRT subtitle (generated from raw snippets, if --format srt)
```

- `{channel-slug}`: Channel name in kebab-case
- `{title-full-slug}`: Full video title in kebab-case

The `--list` mode outputs to stdout only (no file saved).

## Caching

On first fetch, the script saves:
- `meta.json` — video metadata, chapters, cover image path, language info
- `transcript-raw.json` — raw transcript snippets from YouTube API (`{ text, start, duration }[]`)
- `transcript-sentences.json` — sentence-segmented transcript (`{ text, start: "HH:mm:ss", end: "HH:mm:ss" }[]`), split by sentence-ending punctuation (`.?!…。？！` etc.), timestamps proportionally allocated by character length, CJK-aware text merging
- `imgs/cover.jpg` — video thumbnail

Subsequent runs for the same video use cached data (no network calls). Use `--refresh` to force re-fetch. If a different language is requested, the cache is automatically refreshed.

When YouTube returns anti-bot / blocked responses on the direct InnerTube path, the script retries with alternate client identities and then falls back to `yt-dlp` if available. If fallback is needed but `yt-dlp` is unavailable, the agent should decide how to make `yt-dlp` available and continue rather than pushing the installation decision to the user.

SRT output (`--format srt`) is generated from `transcript-raw.json`. Text/markdown output uses `transcript-sentences.json` for natural sentence boundaries.

## Workflow

When user provides a YouTube URL and wants the transcript:

1. Run with `--list` first if the user hasn't specified a language, to show available options
2. **Always single-quote the URL** when running the script — zsh treats `?` as a glob wildcard, so an unquoted YouTube URL causes "no matches found": use `'https://www.youtube.com/watch?v=ID'`
3. Default: run with `--chapters --speakers` for the richest output (chapters + speaker identification)
3. The script auto-saves cached data + output file and prints the file path
4. For `--speakers` mode: after the script saves the raw file, follow the speaker identification workflow below to post-process with speaker labels

When user only wants a cover image or metadata, running the script with any option will also cache `meta.json` and `imgs/cover.jpg`.

When re-formatting the same video (e.g., first text then SRT), the cached data is reused — no re-fetch needed.

## Chapter & Speaker Workflow

### Chapters (`--chapters`)

The script parses chapter timestamps from the video description (e.g., `0:00 Introduction`), segments the transcript by chapter boundaries, groups snippets into readable paragraphs, and saves as `.md` with a Table of Contents. No further processing needed.

If no chapter timestamps exist in the description, the transcript is output as grouped paragraphs without chapter headings.

### Speaker Identification (`--speakers`)

Speaker identification requires AI processing. The script outputs a raw `.md` file containing:
- YAML frontmatter with video metadata (title, channel, date, cover, description, language)
- Video description (for speaker name extraction)
- Chapter list from description (if available)
- Raw transcript in SRT format (pre-computed start/end timestamps, token-efficient)

After the script saves the raw file, spawn a sub-agent (use a cheaper model like Sonnet for cost efficiency) to process speaker identification:

1. Read the saved `.md` file
2. Read the prompt template at `{baseDir}/prompts/speaker-transcript.md`
3. Process the raw transcript following the prompt:
   - Identify speakers using video metadata (title → guest, channel → host, description → names)
   - Detect speaker turns from conversation flow, question-answer patterns, and contextual cues
   - Segment into chapters (use description chapters if available, else create from topic shifts)
   - Format with `**Speaker Name:**` labels, paragraph grouping (2-4 sentences), and `[HH:MM:SS → HH:MM:SS]` timestamps
4. Overwrite the `.md` file with the processed transcript (keep the YAML frontmatter)

When `--speakers` is used, `--chapters` is implied — the processed output always includes chapter segmentation.

## Pitfalls

1. **Agent loads wrong skill**: The library has two YouTube skills — `youtube-content` (Python, older) and `ai-ggbond-youtube-script` (TypeScript/Bun, preferred). Always load `ai-ggbond-youtube-script` when the user says "YouTube 技能" or provides a YouTube URL. The skill name contains `youtube-script`, not just `youtube`.
2. **Proxy required (Hermes VM / China)**: The script's Bun runtime does NOT inherit shell `HTTP_PROXY`/`HTTPS_PROXY` env vars reliably. If direct fetch fails with "Unable to connect", set proxy vars AND verify with `curl -x http://127.0.0.1:7897 -s -o /dev/null -w "%{http_code}" https://www.youtube.com` before retrying.
3. **yt-dlp PATH not found by Bun subprocess**: After `pip install --user yt-dlp`, the binary lands in `~/Library/Python/3.9/bin/` (macOS) which is NOT on Bun's PATH. The script will still say "yt-dlp fallback unavailable". Workaround: either symlink to `/usr/local/bin/yt-dlp` or use yt-dlp directly for metadata extraction.
4. **"bot detected" even with yt-dlp**: YouTube aggressively blocks. Don't retry endlessly — pivot to the fallback pattern below.

## Fallback Pattern: Metadata + Third-Party Summaries (Verified 2026-06-07)

When both InnerTube API and yt-dlp transcript extraction fail (bot detection, no captions, IP blocked), use this proven 3-step pattern:

### Step 1: Extract video metadata with yt-dlp
```bash
/Users/admin/.hermes/profiles/neirong/home/Library/Python/3.9/bin/yt-dlp \
  --proxy http://127.0.0.1:7897 \
  --print title --print channel --print description --print duration \
  'https://youtu.be/VIDEO_ID' 2>/dev/null | head -50
```
This gives you: title, channel, description (often includes chapter timestamps), duration.

### Step 2: Search for third-party transcripts/summaries
```
web_search → '"speaker name" "video title" transcript summary'
web_search → '"video title" complete summary key points'
```
High-yield sources (in priority order):
- **LinkedIn posts** by curators with large followings — often contain structured summaries with key quotes, frameworks, and comment debates
- **Medium/Substack blog posts** — usually restructured with analysis
- **Conference recap pages** — for talks at events
- **CompleteRPABootcamp, TowardsAI** — frequently summarize YC videos

### Step 3: Extract and cross-reference
```
web_extract → [LinkedIn post URL, blog post URL]
```
Cross-reference at least 2 sources. Blog summaries are often MORE useful than raw transcripts for article writing — they've already been structured and key points extracted.

**Note to user:** Always disclose that content is based on third-party summaries, not word-for-word transcript.

### Real Example (2026-06-07)
Video: "How to Build a Self-Improving Company with AI" (Y Combinator, Tom Blomfield)
- yt-dlp confirmed: no captions available on the video
- LinkedIn search found: Linas Beliūnas post with 141 comments, comprehensive summary with 5-layer framework
- Blog search found: CompleteRPABootcamp detailed chapter-by-chapter breakdown
- Combined: full coverage of all 12 chapters with direct quotes and critical counterpoints from comments

## Proxy Configuration (Hermes VM / Network-Restricted Environments)

When running in Hermes VM or behind a firewall, YouTube API calls fail silently or return "Unable to connect." Fix:

```bash
# Set proxy before running the script
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897

# Then run the script
npx -y bun {baseDir}/scripts/main.ts 'https://youtu.be/VIDEO_ID' --chapters --languages zh,en
```

**Pitfall**: The script's bun process inherits proxy env vars, but YouTube may still block with "bot detected." In that case, fall back to direct yt-dlp:

```bash
# Install yt-dlp if needed (Hermes VM may not have pip working)
brew install yt-dlp || pip3 install yt-dlp

# List available subtitles first
yt-dlp --list-subs --proxy http://127.0.0.1:7897 'https://youtu.be/VIDEO_ID'

# Download subtitles if available
yt-dlp --write-sub --write-auto-sub --sub-lang en,zh --proxy http://127.0.0.1:7897 'https://youtu.be/VIDEO_ID'
```

**Pitfall**: If yt-dlp shows "no subtitles" and "no automatic captions," the video genuinely has no text transcript. Fall back to the transcript fallback pattern (web_search for third-party summaries).

## Fallback: When Neither Script Nor yt-dlp Works

When YouTube blocks all direct access (bot detection, no subtitles), use this three-step fallback:

### Step 1: Get video metadata via yt-dlp
```bash
yt-dlp --proxy http://127.0.0.1:7897 --print title --print channel --print description --print duration 'https://youtu.be/VIDEO_ID'
```

### Step 2: Search for third-party transcripts/summaries
```
web_search → '"speaker name" "talk title" transcript summary blog'
web_search → '"talk title" full transcript notes'
```

High-yield sources: LinkedIn posts (often contain detailed excerpted summaries), Medium/blog writeups, conference recap pages.

### Step 3: Extract structured content
```
web_extract → [blog post URLs, LinkedIn summary posts]
```

LinkedIn posts by curators often contain the most structured summaries (key points, quotes, frameworks) — prioritize these.

## Pitfalls

### Proxy Required for YouTube Access (Hermes VM / China)
YouTube is blocked in some network environments. Always set proxy before running:
```bash
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
```
The script itself doesn't inherit proxy from shell — pass via environment variables.

### yt-dlp Fallback Path
When YouTube InnerTube API returns "bot detected", the script falls back to yt-dlp. Ensure yt-dlp is installed:
```bash
pip3 install yt-dlp
# Installed to: ~/.hermes/profiles/neirong/home/Library/Python/3.9/bin/yt-dlp
```
The script may not find yt-dlp if it's not in PATH. Workaround: set PATH explicitly or call yt-dlp directly for subtitle listing.

### Videos Without Subtitles
Some YouTube videos have no subtitles (manual or auto-generated). When `yt-dlp --list-subs` shows "no automatic captions" and "no subtitles", fall back to **web_search + web_extract** pattern:
1. Search for `"video title" "speaker name" transcript summary blog`
2. Extract from LinkedIn posts (often contain detailed summaries), Medium articles, blog writeups
3. Cross-reference at least 2 sources
4. Note to user: "content based on third-party summaries, not word-for-word transcript"

## Error Cases

| Error | Meaning |
|-------|---------|
| Transcripts disabled | Video has no captions at all |
| No transcript found | Requested language not available |
| Video unavailable | Video deleted, private, or region-locked |
| IP blocked | Too many requests, try again later |
| Age restricted | Video requires login for age verification |
| bot detected | The script retries alternate clients and then `yt-dlp`; if fallback tooling is missing, the agent should resolve that itself, otherwise if it still fails try `YOUTUBE_TRANSCRIPT_COOKIES_FROM_BROWSER=safari` (or your browser) |

## Network & Proxy

YouTube 被墙，必须使用代理。设置环境变量：
```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
```

如果 `bun` 安装失败（Hermes VM 网络限制），用 `npx -y bun` 替代。

如果 `youtube-transcript-api` (Python) 安装失败，用 `pip3 install youtube-transcript-api` + 代理。
