# AI GGBond Skills · Focus on Making AI Your Automated Money-Making & IP Operations System

<p align="center">
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/stargazers"><img src="https://img.shields.io/github/stars/BetterZflyee/ai-ggbond-skills?style=for-the-badge&color=facc15" alt="Stars"></a>
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="https://zflyee.com/"><img src="https://img.shields.io/badge/built%20by-AI%20GGBond-8b5cf6?style=for-the-badge" alt="AI GGBond"></a>
  <a href="#changelog"><img src="https://img.shields.io/badge/version-1.0-0891b2?style=for-the-badge" alt="Version"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/中文版-📖-dc2626?style=for-the-badge" alt="中文版"></a>
</p>

> **A curated collection of Hermes Agent skills for the AI Native solopreneur.**
>
> Every skill is a complete, battle-tested automation workflow — not a chatbot toy, but an AI workforce that publishes articles, runs social media, tracks trends, and builds knowledge. Plug-and-play. Continuously refined. All lessons learned are preserved in `references/`.

---

## Why AI GGBond Skills

Built on [Hermes Agent](https://github.com/NousResearch/hermes-agent) — the only AI agent with a **built-in learning loop**: autonomous skill creation from experience, self-improvement during use, and persistent memory across sessions. AI GGBond Skills takes it further: instead of just "chatting," each skill delivers **end-to-end automation for revenue generation and IP operations**.

Bring your own model — OpenAI, DeepSeek, OpenRouter (200+ models), Nous Portal, or your own endpoint. Switch models anytime with `hermes model`. The skills don't care.

---

## Skill Matrix

| Skill | Category | What It Does |
|:---|:---|:---|
| `ai-ggbond-article-writer` | 📝 Creative | Full pipeline: topic → outline → draft → typesetting → images → publish to WeChat |
| `ai-ggbond-post-to-wechat` | 🚀 Publishing | One-click push to WeChat Official Account drafts. API + Browser CDP modes |
| `ai-ggbond-sticker-writer` | 🎨 Creative | Convert content to social-ready image cards (Xiaohongshu-style stickers) |
| `ai-ggbond-github-trending` | 🔍 Research | GitHub Trending discovery + AI-powered analysis for AI/Agent/MCP trends |
| `ai-ggbond-x-followings-feed` | 📡 Signal | X/Twitter followings scraper + AI-structured daily digest with curation scoring |
| `ai-ggbond-publish-to-x` | 📢 Social | Full-featured X/Twitter publishing: posts, quotes, long-form, Threads |
| `ai-ggbond-run-xiaohongshu` | 📕 Social | End-to-end Xiaohongshu ops: positioning → ideation → creation → publishing → engagement → iteration |
| `ai-ggbond-brain-setup` | 🧠 Knowledge | GBrain memory layer integration — give your AI long-term memory and knowledge retrieval |

> All skills support **persona-adaptive output** (v1.0 milestone) — they automatically read your profile from Hermes Memory and tailor content to your unique voice, instead of producing generic AI-sounding text.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Hermes Agent                      │
│           (AI 朱朱侠 · Command Center)              │
│                                                    │
│  Memory ←→ GBrain (ai-ggbond-brain-setup)          │
└──────┬────────────┬─────────────┬─────────────────┘
       │            │             │
  ┌────▼─────┐ ┌───▼────┐ ┌─────▼──────┐
  │ Content   │ │ Signal  │ │ Distribution│
  │ Creation  │ │ Capture │ │             │
  └────┬─────┘ └───┬────┘ └─────┬──────┘
       │            │             │
  ┌────┼─────┐      │      ┌─────┼──────┐
  ▼    ▼     ▼      ▼      ▼     ▼      ▼
Article Sticker GitHub   X    WeChat   X   Xiaohong
Writer  Writer Trending Feed  Publish Publish shuOps
       │            │             │
       └────────────┴─────────────┘
                    │
          Persona Adaptation Layer
        (Hermes Memory — Your Voice)
```

**Design Philosophy: Composable Workflows**

Skills are not isolated tools — they chain into automation pipelines:

```
X Following Feed ──→ Topic Ideas ──→ Article Writer ──→ WeChat Publish
       │                              │
       └──→ X Post/Comment ←─────────┘

GitHub Trending ──→ Topic Ideas ──→ Article Writer ──→ WeChat Publish
```

---

## Quick Install

### Prerequisites

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed and running
- macOS / Linux / WSL2 (all skills are CLI-based; OS-agnostic)

### Install All Skills

```bash
# Clone the repository
git clone https://github.com/BetterZflyee/ai-ggbond-skills.git /tmp/ai-ggbond-skills

# Install all skills to Hermes
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.hermes/skills/

# Verify installation
hermes skills list | grep ai-ggbond
```

### Install Individual Skills

```bash
# Example: install only the article writer
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-article-writer ~/.hermes/skills/creative/
```

### Update Skills

```bash
cd /tmp/ai-ggbond-skills && git pull
cp -r skills/ai-ggbond-* ~/.hermes/skills/
```

---

## Usage

### Natural Language Triggers (Recommended)

Just talk to your Hermes Agent naturally:

| You Say | Skill Triggered |
|:---|:---|
| "Write an article about AI Agents" | `ai-ggbond-article-writer` |
| "Push this to my WeChat blog" | `ai-ggbond-post-to-wechat` |
| "Turn this into image stickers" | `ai-ggbond-sticker-writer` |
| "What's trending on GitHub today?" | `ai-ggbond-github-trending` |
| "X digest" / "Summarize my followings" | `ai-ggbond-x-followings-feed` |
| "Tweet this" / "Publish to X" | `ai-ggbond-publish-to-x` |
| "Help me run Xiaohongshu" | `ai-ggbond-run-xiaohongshu` |
| "Set up gbrain" / "Configure brain" | `ai-ggbond-brain-setup` |

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

GBrain memory layer integration — give your AI long-term memory.

**Capabilities**: PGLite local vector storage · bridges upstream skills (signal-detector / brain-ops / conventions) · knowledge base ingestion workflow

---

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
-wechat   -to-x      publishing)
```

### Workflow Examples

| Workflow | Skill Chain |
|:---|:---|
| Daily signal → article → publish | `x-followings-feed` → `article-writer` → `post-to-wechat` |
| Hot take → X thread | `x-followings-feed` → `publish-to-x` |
| Open-source project → article | `github-trending` → `article-writer` → `post-to-wechat` |
| Knowledge capture → memory | `article-writer` output → `brain-setup` ingest to GBrain |

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
| 2026-05-26 | 📦 `ai-ggbond-brain-setup` released · `push-to-x` deprecated, replaced by `publish-to-x` |
| 2026-05-20 | 🔍 `ai-ggbond-github-trending` released · All skills achieve persona-adaptive "千人千面" v1.0 |
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
