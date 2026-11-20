"""Render a fixed-height, single-click SVG reveal component using stdlib."""

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path


def hex_color(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise argparse.ArgumentTypeError("颜色请使用六位十六进制值，例如 #D97706")
    return value.upper()


def character_width(character):
    """Estimate a conservative width in em for the system sans-serif font."""
    if unicodedata.combining(character) or character == "\u200d":
        return 0
    if unicodedata.east_asian_width(character) in {"F", "W"}:
        return 1
    if character in "ilI.,;:!'| `":
        return 0.4
    if character in "WM@#%&":
        return 1
    if character.isascii():
        return 0.8
    return 1


def split_lines(value):
    lines = []
    for paragraph in value.split("\n"):
        line = ""
        width = 0
        for character in paragraph:
            advance = character_width(character)
            if line and width + advance > 14:
                lines.append(line)
                line = ""
                width = 0
            line += character
            width += advance
        lines.append(line)
    return lines


def text_lines(lines, first_y, size, line_height, color):
    nodes = []
    for index, line in enumerate(lines):
        y = first_y + index * line_height
        nodes.append(f'    <text x="40" y="{y}" fill="{color}" font-size="{size}" font-family="sans-serif" xml:space="preserve">{html.escape(line)}</text>')
    return "\n".join(nodes)


def component(args, prompt_lines, answer_lines):
    prompt = text_lines(prompt_lines, 142, 36, 44, "#1F2937")
    answer = text_lines(answer_lines, 120, 36, 44, "#1F2937")
    label = html.escape(args.prompt, quote=True)
    return f'''<section style="margin:20px 0;padding:0;line-height:0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="100%" style="display:block;width:100%;height:auto;cursor:pointer;" data-component="wechat-svg-click-reveal" role="img" aria-label="{label}">
  <desc>点击画面，在固定区域内显示答案。刷新后可重新体验。</desc>
  <rect x="1" y="1" width="598" height="358" rx="16" fill="{args.background}" stroke="{args.color}" stroke-width="2" />
  <path d="M40 58 H100" fill="none" stroke="{args.color}" stroke-width="5" stroke-linecap="round" />
{prompt}
  <g opacity="0" data-reveal-layer="answer">
    <rect x="1" y="1" width="598" height="358" rx="16" fill="{args.background}" stroke="{args.color}" stroke-width="2" />
    <text x="40" y="58" fill="#1F2937" font-size="36" font-weight="700" font-family="sans-serif">答案</text>
{answer}
    <animate attributeName="opacity" begin="click" dur="0.28s" from="0" to="1" fill="freeze" restart="never" />
    <rect x="0" y="0" width="600" height="360" fill="#000000" fill-opacity="0" pointer-events="all" data-reveal-trigger="tap" />
  </g>
</svg>
</section>
'''


def preview(fragment):
    return f'''<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>固定画面点击揭秘示例</title>
<body style="margin:0;background:#F7F5F0;color:#1F2937;font-family:system-ui,sans-serif;">
<main style="max-width:640px;margin:40px auto;padding:24px;">
  <h1 style="font-size:24px;">固定画面点击揭秘</h1>
  <p style="font-size:16px;line-height:1.8;">点击下方画面查看答案，前后占位高度相同。刷新页面可重新体验。</p>
  {fragment}
</main>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer", required=True, help="点击后显示的文字")
    parser.add_argument("--prompt", default="点一下，查看答案")
    parser.add_argument("--color", type=hex_color, default="#D97706")
    parser.add_argument("--background", type=hex_color, default="#FFF8EE")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--preview-out", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not args.answer.strip():
        parser.error("请补充点击后显示的文字，通过 --answer 传入")
    if not args.prompt.strip():
        parser.error("请补充点击前提示，通过 --prompt 传入")
    prompt_lines = split_lines(args.prompt)
    answer_lines = split_lines(args.answer)
    if len(prompt_lines) > 3:
        parser.error(f"提示按当前宽度排成{len(prompt_lines)}行，固定画面可容纳3行。请提供更短提示，或确认拆成多个组件")
    if len(answer_lines) > 5:
        parser.error(f"答案按当前宽度排成{len(answer_lines)}行，固定画面可容纳5行。请提供精简版本，或确认拆成多个组件后再生成")
    targets = [args.out] + ([args.preview_out] if args.preview_out else [])
    if len({path.resolve() for path in targets}) != len(targets):
        parser.error("片段和预览须使用不同输出文件")
    if not args.overwrite and any(path.exists() for path in targets):
        parser.error("输出已存在，请换路径，或确认替换后使用 --overwrite")
    fragment = component(args, prompt_lines, answer_lines)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(fragment, encoding="utf-8")
    if args.preview_out:
        args.preview_out.parent.mkdir(parents=True, exist_ok=True)
        args.preview_out.write_text(preview(fragment), encoding="utf-8")
    print(json.dumps({"files": [str(path.resolve()) for path in targets],
                      "answer_lines": len(answer_lines), "prompt_lines": len(prompt_lines),
                      "canvas": [600, 360], "font_size": 36,
                      "line_width_em": 14}, ensure_ascii=False))


if __name__ == "__main__":
    main()
