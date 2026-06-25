# AI GGBond Skills<br><small>Focus on Making AI Your Automated Money-Making & IP Operations System</small>

<p align="center">
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/stargazers"><img src="https://img.shields.io/github/stars/BetterZflyee/ai-ggbond-skills?style=for-the-badge&color=facc15" alt="Stars"></a>
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="https://zflyee.com/"><img src="https://img.shields.io/badge/built%20by-AI%20GGBond-8b5cf6?style=for-the-badge" alt="AI GGBond"></a>
  <a href="#changelog"><img src="https://img.shields.io/badge/version-1.5-0891b2?style=for-the-badge" alt="Version"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/中文版-📖-dc2626?style=for-the-badge" alt="中文版"></a>
</p>

<p align="center">
  <img src="assets/banner.jpg" alt="AI GGBond Skills" width="800">
</p>

> **A curated collection of Agent Skills for the AI Native solopreneur & OPC.**
>
> Every skill is a complete, battle-tested automation workflow — not a chatbot toy, but an AI workforce that publishes articles, runs social media, tracks trends, and builds knowledge. Plug-and-play. Continuously refined. All lessons learned are preserved in `references/`.

---

## Why AI GGBond Skills

Runs on [Hermes Agent](https://github.com/NousResearch/hermes-agent), [Claude Code](https://claude.ai), [Codex](https://github.com/openai/codex), [OpenClaw](https://github.com/nousresearch/openclaw), and other major AI Agent platforms. Every skill supports **memory & conversation adaptation** — automatically reads your preferences and history for personalized, persona-matched output.

Bring your own model — OpenAI, DeepSeek, OpenRouter (200+ models), Nous Portal, or your own endpoint. Switch models anytime with `hermes model`. The skills don't care.

---

## Skill Matrix

| Skill | Category | What It Does |
|:---|:---|:---|
| `ai-ggbond-article-writer` | 📝 Creative | Full pipeline: topic → outline → draft → typesetting → images → publish to WeChat |
| `ai-ggbond-post-to-wechat` | 🚀 Publishing | One-click push to WeChat Official Account drafts. API + Browser CDP modes |
| `ai-ggbond-sticker-writer` | 🎨 Creative | Convert content to social-ready image cards (Xiaohongshu-style stickers) |
| `ai-ggbond-poster-portrait` | 🎨 Creative | GPT Image 2 portrait poster generation — cinematic, emotional, photography-style female portraits with safety-compliant prompts |
| `ai-ggbond-worldcup-kv-poster` | 🎨 Creative | World Cup country concept KV posters — treat countries as visual brands with high commercial sports aesthetics |
| `ai-ggbond-skill-matrix` | 🧭 Meta | 181-skill routing table across 7 scenarios — trigger words, skill chains, full-pipeline orchestration |
| `ai-ggbond-github-trending` | 🔍 Research | GitHub Trending discovery + AI-powered analysis for AI/Agent/MCP trends |
| `ai-ggbond-x-followings-feed` | 📡 Signal | X/Twitter followings scraper + AI-structured daily digest with curation scoring |
| `ai-ggbond-publish-to-x` | 📢 Social | Full-featured X/Twitter publishing: posts, quotes, long-form, Threads |
| `ai-ggbond-run-xiaohongshu` | 📕 Social | End-to-end Xiaohongshu ops: positioning → ideation → creation → publishing → engagement → iteration |
| `ai-ggbond-brain-setup` | 🧠 Knowledge | GBrain memory layer with DashScope/Qwen3-Embedding support — 9 documented pitfalls, proxy config, recipe patching |
| `ai-ggbond-remove-ai-marks` | 🧹 Utility | Remove visible (Gemini sparkle) & invisible (SynthID/C2PA) AI watermarks from images |
| `ai-ggbond-youtube-script` | 🎬 Media | Download YouTube transcripts, subtitles & cover images. InnerTube + yt-dlp fallback + web search triple-fallback |
| `ai-ggbond-long-image-generator` | 🎨 Creative | Generate long infographic images using GPT-Image-2 (Yunwu API). Supports Xiaohongshu, WeChat, super-long presets up to 7200px |

> All skills support **persona-adaptive output** (v1.0 milestone) — they automatically read your profile from Hermes Memory and tailor content to your unique voice, instead of producing generic AI-sounding text.

---

## Architecture

### Skill Ecosystem Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI GGBond Skills                                   │
│                    (13 Skills × 7 Categories)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        🧭 META LAYER                                │   │
│  │  skill-matrix ──→ Routes tasks to skill chains                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────────────┐ │
│  │    📡 SIGNAL LAYER    │  │  🧠 MEMORY LAYER  │  │    🔍 RESEARCH LAYER  │ │
│  │                      │  │                  │  │                       │ │
│  │  x-followings-feed   │  │   brain-setup    │  │   github-trending     │ │
│  │  (X/Twitter digest)  │  │   (GBrain KB)    │  │   (Open source scan)  │ │
│  └──────────┬───────────┘  └────────┬─────────┘  └───────────┬───────────┘ │
│             │                       │                        │             │
│             └───────────────────────┼────────────────────────┘             │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     📝 CONTENT CREATION LAYER                        │   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────────┐ │   │
│  │  │ article-    │  │ sticker-     │  │ Visual Content              │ │   │
│  │  │ writer      │  │ writer       │  │                             │ │   │
│  │  │ (Long-form) │  │ (Image cards)│  │  poster-portrait            │ │   │
│  │  └──────┬──────┘  └──────┬───────┘  │  (Portrait posters)         │ │   │
│  │         │                │          │                             │ │   │
│  │         │                │          │  worldcup-kv-poster          │ │   │
│  │         │                │          │  (Sports KV posters)         │ │   │
│  │         │                │          └─────────────┬───────────────┘ │   │
│  └─────────┼────────────────┼────────────────────────┼─────────────────┘   │
│            │                │                        │                      │
│            ▼                ▼                        ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     🚀 DISTRIBUTION LAYER                            │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────┐│   │
│  │  │ post-to-     │  │ publish-to-x │  │ run-xiaohongshu             ││   │
│  │  │ wechat       │  │              │  │ (Full-ops, built-in publish)││   │
│  │  │ (WeChat OA)  │  │ (X/Twitter)  │  │                             ││   │
│  │  └──────────────┘  └──────────────┘  └─────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      🧹 UTILITY LAYER                                │   │
│  │                                                                      │   │
│  │  ┌──────────────────┐  ┌──────────────────────────────────────────┐ │   │
│  │  │ remove-ai-marks  │  │ youtube-script                          │ │   │
│  │  │ (Watermark clean)│  │ (Transcript/Subtitle download)          │ │   │
│  │  └──────────────────┘  └──────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   🎯 PERSONA ADAPTATION LAYER                        │   │
│  │                  (Hermes Memory / User Profile)                       │   │
│  │        Auto-reads your voice, style, positioning for output          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Chains

Every skill can be used standalone or chained into automation pipelines:

#### Content Pipeline Chains

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRIMARY CONTENT PIPELINE                          │
│                                                                      │
│  Signal Sources          Content Creation         Distribution       │
│  ──────────────         ────────────────         ────────────       │
│                                                                      │
│  x-followings-feed ──┐                                               │
│                      ├──→ article-writer ──→ post-to-wechat          │
│  github-trending ────┘        │                                      │
│                               │                                      │
│                               ├──→ sticker-writer ──→ (manual share) │
│                               │                                      │
│                               └──→ publish-to-x                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Visual Content Chains

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VISUAL CONTENT PIPELINE                           │
│                                                                      │
│  article-writer ──→ poster-portrait (cover image)                    │
│                                                                      │
│  article-writer ──→ worldcup-kv-poster (event-themed cover)          │
│                                                                      │
│  article-writer ──→ sticker-writer (social cards)                    │
│                                                                      │
│  poster-portrait ──→ remove-ai-marks ──→ publish                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Research & Memory Chains

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESEARCH & MEMORY PIPELINE                        │
│                                                                      │
│  github-trending ──→ article-writer ──→ brain-setup (ingest)         │
│                                                                      │
│  x-followings-feed ──→ article-writer ──→ brain-setup (ingest)       │
│                                                                      │
│  youtube-script ──→ article-writer (reference material)              │
│                                                                      │
│  brain-setup ──→ article-writer (recall knowledge)                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Full-Stack Operations Chains

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FULL-STACK OPERATIONS                             │
│                                                                      │
│  Xiaohongshu Ops:                                                    │
│  run-xiaohongshu ──→ (internal: ideation → content → publish)        │
│       ↑                                                              │
│       └── brain-setup (persona positioning)                          │
│                                                                      │
│  X/Twitter Full Loop:                                                │
│  x-followings-feed ──→ publish-to-x (hot take)                       │
│       │                                                              │
│       └── article-writer ──→ publish-to-x (long-form)                │
│                                                                      │
│  Multi-Platform Syndication:                                         │
│  article-writer ──┬──→ post-to-wechat (primary)                      │
│                   ├──→ sticker-writer ──→ run-xiaohongshu             │
│                   └──→ publish-to-x (cross-post)                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Complete Skill Combination Matrix

| Source Skill | → Target Skill(s) | Use Case |
|:---|:---|:---|
| `x-followings-feed` | `article-writer`, `publish-to-x` | Signal → article or hot take |
| `github-trending` | `article-writer` | Open source → trend article |
| `youtube-script` | `article-writer` | Video transcript → article reference |
| `article-writer` | `post-to-wechat` | Long-form → WeChat publish |
| `article-writer` | `publish-to-x` | Long-form → X post or thread |
| `article-writer` | `sticker-writer` | Article → social image cards |
| `article-writer` | `poster-portrait` | Article → cinematic cover image |
| `article-writer` | `worldcup-kv-poster` | Article → event-themed KV poster |
| `article-writer` | `brain-setup` | Knowledge → long-term memory |
| `article-writer` | `run-xiaohongshu` | Article → Xiaohongshu content |
| `poster-portrait` | `remove-ai-marks` | Generated image → clean for publish |
| `worldcup-kv-poster` | `remove-ai-marks` | Generated image → clean for publish |
| `sticker-writer` | `remove-ai-marks` | Generated image → clean for publish |
| `run-xiaohongshu` | `brain-setup` | Engagement data → memory |
| `brain-setup` | `article-writer`, `sticker-writer`, `run-xiaohongshu` | Memory → persona-adaptive output |
| `skill-matrix` | ALL | Task routing → skill chain selection |

---

## Quick Install

### Universal Installation (All Platforms)

Skills are standard `SKILL.md` files with `references/` directories. Copy them to your AI Agent's skill directory:

```bash
# Clone the repository
git clone https://github.com/BetterZflyee/ai-ggbond-skills.git /tmp/ai-ggbond-skills

# Copy skills to your agent's skill directory
# Replace <SKILL_DIR> with your platform's skill path (see below)
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* <SKILL_DIR>/
```

### Platform-Specific Setup

#### Hermes Agent

```bash
# Skill directory: ~/.hermes/skills/
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.hermes/skills/

# Verify
hermes skills list | grep ai-ggbond

# Update
cd /tmp/ai-ggbond-skills && git pull
cp -r skills/ai-ggbond-* ~/.hermes/skills/
```

#### Claude Code

```bash
# Skill directory: ~/.claude/skills/ or project .claude/skills/
mkdir -p ~/.claude/skills
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.claude/skills/

# Or install to a specific project
mkdir -p /path/to/your/project/.claude/skills
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* /path/to/your/project/.claude/skills/
```

#### Codex (OpenAI)

```bash
# Skill directory: ~/.codex/skills/ or project .codex/skills/
mkdir -p ~/.codex/skills
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.codex/skills/
```

#### OpenClaw

```bash
# Skill directory: ~/.openclaw/skills/
mkdir -p ~/.openclaw/skills
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.openclaw/skills/
```

#### Generic Agent (Custom)

```bash
# Any agent that reads SKILL.md files from a skill directory
# Just copy the skills to wherever your agent looks for them
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* /your/agent/skill/path/
```

### Install Individual Skills

```bash
# Install only the skills you need
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-article-writer <SKILL_DIR>/
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-post-to-wechat <SKILL_DIR>/
```

### Update All Skills

```bash
cd /tmp/ai-ggbond-skills && git pull
cp -r skills/ai-ggbond-* <SKILL_DIR>/
```

---

## Usage

### Natural Language Triggers (Recommended)

Just talk to your AI Agent naturally — skills are triggered by intent, not commands:

| You Say | Skill Triggered |
|:---|:---|
| "Write an article about AI Agents" | `ai-ggbond-article-writer` |
| "Push this to my WeChat blog" | `ai-ggbond-post-to-wechat` |
| "Turn this into image stickers" | `ai-ggbond-sticker-writer` |
| "Generate a portrait poster" / "CCD style photo" | `ai-ggbond-poster-portrait` |
| "World Cup poster" / "Country KV poster" | `ai-ggbond-worldcup-kv-poster` |
| "Which skill should I use?" / "Skill routing" | `ai-ggbond-skill-matrix` |
| "What's trending on GitHub today?" | `ai-ggbond-github-trending` |
| "X digest" / "Summarize my followings" | `ai-ggbond-x-followings-feed` |
| "Tweet this" / "Publish to X" | `ai-ggbond-publish-to-x` |
| "Help me run Xiaohongshu" | `ai-ggbond-run-xiaohongshu` |
| "Set up gbrain" / "Configure brain" | `ai-ggbond-brain-setup` |
| "Remove AI watermark" / "Clean this image" | `ai-ggbond-remove-ai-marks` |
| "YouTube transcript" / "Get subtitles" / "YouTube字幕" | `ai-ggbond-youtube-script` |

### CLI Command Reference

```bash
# List all installed skills
hermes skills list

# Filter to AI GGBond skills only
hermes skills list | grep ai-ggbond

# View detailed documentation for a skill
hermes skills view ai-ggbond-article-writer

# Update Hermes Agent itself
hermes update

# Diagnose any issues
hermes doctor
```

---

## Skill Details

### ai-ggbond-article-writer

End-to-end WeChat long-form article creation. Written from an AI Native solopreneur's perspective.

**Capabilities**: Topic selection → outline → first draft → semantic rhythm typesetting → AI illustration → push to WeChat drafts

**Highlights**:
- Dual typesetting themes: Anthropic warm beige & Tech Blue v3
- Auto-generated infographics (syllabus metaphor, terracotta orange / sage green palette)
- Image OCR quality checks, golden-quote breakpoints, blockquote conventions
- Persona-adaptive: output depth and style auto-matched to your profile

### ai-ggbond-post-to-wechat

Push articles to WeChat Official Account drafts.

**Dual Mode**:
- **API Mode** (recommended): AppID + AppSecret, fast and reliable
- **Browser CDP Mode** (fallback): connects to your Chrome session, bypasses content-sensitive API blocks

**Automation**: in-body image upload, cover extraction, HTML style injection, Tailscale exit-IP adaptation for China network environments

### ai-ggbond-sticker-writer

Convert articles or key points into social-ready image cards (Xiaohongshu-style).

**Pipeline**: Input content → auto-summarize → title generation → Markdown layout → AI image generation

**Formats**: Knowledge cards, checklists, comparison charts, step diagrams, opinion cards

### ai-ggbond-poster-portrait

GPT Image 2 portrait poster generation system for cinematic, emotional, photography-style female portraits.

**Capabilities**: Cinematic portrait generation · CCD street photography style · Emotional mood shots · Safety-compliant prompt engineering (avoids GPT Image 2 content policy blocks) · YunWu API direct integration for stable generation

**Highlights**:
- Structured grid-based prompts (not narrative paragraphs) to prevent model drift
- Multiple photography styles: CCD, film grain, street photography, studio
- Portrait-specific negative prompts to ensure consistent quality
- Direct API call workflow bypassing script auto-analysis

### ai-ggbond-worldcup-kv-poster

World Cup country concept KV poster generation — treat each country as a complete visual brand.

**Capabilities**: Country visual asset auto-recognition · Star player / football babe integration · Multi-aspect ratio support (9:16, 16:9, 4:5, 1:1, 2.35:1) · Commercial sports poster aesthetics · High-recognition design language

**Highlights**:
- Not flag + football collage — full brand identity treatment
- Auto-identifies country colors, cultural symbols, typography style
- Supports both star player portraits and mascot/brand ambassador modes
- Designed for social media virality and commercial print quality

### ai-ggbond-skill-matrix

Meta-routing table covering 181 skills across 7 scenarios with trigger-word mapping and workflow orchestration.

**Capabilities**: 181 skills × 7 scenarios × 22 categories · Trigger word → skill mapping · Full-pipeline orchestration (topic → research → writing → publishing) · Skill chain recommendations

**Use cases**:
- "Which skill should I use for X?" — scans the matrix and recommends
- "Full pipeline from topic to publish" — chains the right skills in order
- "What skills do I have?" — categorized overview of entire skill ecosystem

### ai-ggbond-github-trending

GitHub Trending discovery and AI-powered analysis.

**Capabilities**: daily / weekly / monthly time windows · AI / Agent / MCP / LLM domain filtering · P0 / P1 / P2 automatic prioritization · Markdown report + topic suggestion output

### ai-ggbond-x-followings-feed

X/Twitter AI daily digest from your followings.

**Capabilities**: Fetches tweets from accounts you follow (not algorithmic feed) · 200+ per batch · 1 / 3 / 7 day windows · AI auto-classification (breaking news / product launches / technical insights / resources / sentiment signals) · Built-in `curate_and_score.py` curation engine

### ai-ggbond-publish-to-x

Full-featured X/Twitter publishing client.

**Capabilities**: Regular posts (text + images + video) · quote retweets · long-form (X Articles / Markdown) · Threads · Integrates with article-writer and followings-feed for content loops

### ai-ggbond-run-xiaohongshu

End-to-end Xiaohongshu operations.

**Capabilities**: Auto-reads Hermes Memory for persona positioning → topic research → content creation → publishing → comment replies → viral replication → retrospective · CDP browser adaptation

### ai-ggbond-brain-setup

GBrain memory layer integration — DashScope text-embedding-v4 (Qwen3) + balanced search mode + proxy-aware config.

**Capabilities**: PGLite local vector storage · DashScope text-embedding-v4 (Qwen3-Embedding, 1024d) · balanced search mode · proxy-aware fetch (uppercase HTTPS_PROXY) · recipe patching for China-region keys · 9 documented pitfalls with fixes · bridges upstream skills (signal-detector / brain-ops / conventions) · knowledge base ingestion workflow

### ai-ggbond-remove-ai-marks

Remove AI-generated watermarks and metadata from images.

**Capabilities**: Visible watermark removal (Gemini sparkle, Alpha-channel reconstruction) · invisible watermark removal (SynthID v1+v2, DWT-DCT, diffusion regeneration) · metadata stripping (C2PA/EXIF/XMP) · batch scanning + cleaning · humanization (film grain anti-AI-detection) · single-image deep inspection

**Use cases**: Pre-publish image sanitation for WeChat, X, Xiaohongshu · batch clean article cover images · anti-AI-detection for social platforms

### ai-ggbond-youtube-script

Download YouTube video transcripts, subtitles and cover images. No API key required — uses YouTube's InnerTube API directly with automatic yt-dlp fallback and web search triple-fallback.

**Capabilities**: Multi-language subtitle download · translation · chapter segmentation · speaker identification (AI post-processing) · SRT/text output · cover image caching · auto-generated & manual transcript support

**Highlights**:
- Triple-fallback: InnerTube API → yt-dlp → web search for third-party summaries
- Sentence-level timestamp segmentation (CJK-aware)
- Smart caching — re-fetch only on language change or `--refresh`
- Proxy-aware for network-restricted environments (China, Hermes VM)
- 6 documented pitfalls with verified workarounds

---



### ai-ggbond-long-image-generator

Generate professional long infographic images using GPT-Image-2 via Yunwu API. Supports multiple social media presets and super-long images up to 7200px.

**Capabilities**: Xiaohongshu vertical (1080×1440) · WeChat cover (900×383) · Super-long images (1080×3200 to 1080×7200) · Custom sizes · Multi-segment stitching

**Highlights**:
- GPT-Image-2 powered — generates real visual content, not placeholder graphics
- Smart segmentation for super-long images (auto-split + overlap stitching)
- Multiple rendering backends: Playwright, PIL lightweight, GPT-Image-2
- Dark tech theme with neon blue/orange accents (configurable)
- 3-step quick start: setup API key → test connection → generate
- 19 size presets for different platforms

**Usage**:
```bash
# Setup API key
bash ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/setup_yunwu.sh YOUR_API_KEY

# Generate Xiaohongshu image
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/generate_long_image.py \
    --prompt "AI Tools Guide" --preset xiaohongshu --output /tmp/test.png

# Generate super-long image (4x height)
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/generate_long_image.py \
    --prompt "Complete Tutorial" --preset super_long_medium --output /tmp/long.png
```


## Ecosystem Integration

### Skill Dependencies

```
ai-ggbond-brain-setup (Memory Foundation)
        ↓
Hermes Memory (User Profile)
        ↓
┌───────┼──────────┬──────────────┐
↓       ↓          ↓              ↓
article  sticker   xiaohongshu   github
writer   writer    ops           trending
   ↓       ↓          ↓
post-to   publish    (built-in
|-wechat   -to-x      publishing)
```

### Workflow Examples

| Workflow | Skill Chain |
|:---|:---|
| Daily signal → article → publish | `x-followings-feed` → `article-writer` → `post-to-wechat` |
| Hot take → X thread | `x-followings-feed` → `publish-to-x` |
| Open-source project → article | `github-trending` → `article-writer` → `post-to-wechat` |
| Knowledge capture → memory | `article-writer` output → `brain-setup` ingest to GBrain |
| Portrait poster for article | `article-writer` → `poster-portrait` for cover image |
| World Cup content series | `worldcup-kv-poster` → `article-writer` → `post-to-wechat` |
| Multi-platform syndication | `article-writer` → `post-to-wechat` + `publish-to-x` + `sticker-writer` → `run-xiaohongshu` |
| Video → article → publish | `youtube-script` → `article-writer` → `post-to-wechat` |
| Image cleanup pipeline | `poster-portrait` → `remove-ai-marks` → publish |
| Full research cycle | `github-trending` + `x-followings-feed` → `article-writer` → `brain-setup` |

---

## Migration Guide

### Migrating from ai-ggbond-push-to-x to ai-ggbond-publish-to-x

`ai-ggbond-push-to-x` was deprecated on May 26, 2026. Migrate to `ai-ggbond-publish-to-x`:

```bash
# 1. Remove the deprecated skill
rm -rf ~/.hermes/skills/ai-ggbond-push-to-x

# 2. Install the replacement
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-publish-to-x ~/.hermes/skills/social-media/

# 3. Verify
hermes skills list | grep publish-to-x
```

**What changed**: The new skill is backward-compatible with all original trigger words. New capabilities: X Articles long-form Markdown publishing, Thread support.

---

## Changelog

| Date | Milestone |
|:---|:---|
| 2026-06-25 | 🎨 `ai-ggbond-long-image-generator` released — GPT-Image-2 powered long infographic generation with 19 presets (up to 7200px super-long) |
| 2026-06-17 | 🎯 `ai-ggbond-poster-portrait` + `ai-ggbond-worldcup-kv-poster` + `ai-ggbond-skill-matrix` synced — portrait posters, World Cup KV, 181-skill routing table |
| 2026-06-08 | 🎬 `ai-ggbond-youtube-script` released — YouTube transcript/subtitle/cover download with triple-fallback (InnerTube + yt-dlp + web search) |
| 2026-06-04 | 🧠 `ai-ggbond-brain-setup` v1.2 — DashScope/Qwen3-Embedding support, 9 pitfalls documented, proxy config, recipe patching |
| 2026-05-28 | 🧹 `ai-ggbond-remove-ai-marks` released — visible + invisible watermark removal for AI-generated images |
| 2026-05-26 | 📦 `ai-ggbond-brain-setup` released · `push-to-x` deprecated, replaced by `publish-to-x` |
| 2026-05-20 | 🔍 `ai-ggbond-github-trending` released · All skills achieve persona-adaptive v1.0 |
| 2026-04-20 | 🏗️ Repository created — skill system formalized |
| 2026-02-28 | ✍️ `ai-ggbond-article-writer` debut — first end-to-end automated article published |

---

## Contributing

This is the battle-tested skill collection of an AI Native solopreneur. The `references/` directory in each skill preserves real-session lessons and iteration logs — that's where the real value lives.

**Iteration loop**: Use in production → discover issues → update SKILL.md + references/ → sync to GitHub

Issues and discussions welcome. Fork to create your own customized skill variants.

---

## Connect

<p align="center">
  <table>
    <tr align="center">
      <td><b>WeChat</b></td>
      <td><b>X / Twitter</b></td>
      <td><b>Blog</b></td>
    </tr>
    <tr align="center">
      <td><img src="assets/wechat-qr.jpg" width="140" alt="AI 朱朱侠 WeChat"></td>
      <td><a href="https://x.com/Zflyee">𝕏 · @Zflyee</a></td>
      <td><a href="https://zflyee.com/">🌐 · zflyee.com</a></td>
    </tr>
  </table>
</p>

---

## License

[MIT](LICENSE) · No restrictions. Use freely, modify, distribute. Build in public.