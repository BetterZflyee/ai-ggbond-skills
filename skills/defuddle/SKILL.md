---
name: defuddle
description: Extract clean article content from web pages using defuddle - removes ads, sidebars, and clutter. Triggers - "defuddle", "extract article", "clean this page", "get content from URL"
github_url: https://github.com/joeseesun/defuddle-skill.git
version: 0.1.0
created_at: 2026-03-07
entry_point: scripts/wrapper.py
dependencies: ["defuddle"]
---

# Defuddle Skill

A Claude Code skill that wraps defuddle — extract clean article content from web pages, removing ads, sidebars, and clutter.

## What it does

Once installed, Claude Code can automatically extract clean content from any URL:

- **Triggers**: "defuddle", "extract article", "clean this page", "get content from URL"
- **Output**: Clean Markdown or JSON with metadata (title, author, date, word count)

## Usage examples

Ask Claude Code:
- `Extract the article from https://example.com/blog-post`
- `defuddle this page and give me the markdown: https://example.com/article`
- `Get the title and author from https://example.com/post`

## CLI Reference

The skill uses defuddle CLI under the hood:

```bash
defuddle parse <url-or-file> [options]

Options:
  -m, --markdown         Convert to Markdown
  -j, --json             Output as JSON with metadata
  -o, --output <file>    Save to file
  -p, --property <name>  Extract single field (title, author, published, etc.)
  --debug                Verbose logging
```

## Installation

### Option 1: npx (recommended)
```bash
npx defuddle-skill
```
This will:
- Install defuddle CLI globally (if not already installed)
- Copy the skill to ~/.claude/skills/defuddle/

### Option 2: Manual
```bash
git clone https://github.com/joeseesun/defuddle-skill.git
cd defuddle-skill
bash install.sh
```

## Credits

- defuddle by @kepano — the core extraction engine
- Built for Claude Code by Anthropic

## License

MIT
