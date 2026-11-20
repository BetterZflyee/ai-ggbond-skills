'''Render an original, configurable SVG article component using Python stdlib.'''

import argparse
import html
import json
import math
import os
import re
import tempfile
import unicodedata
import uuid
from pathlib import Path

COMPONENT = "wechat-svg-data-chart"


def text(value, field, allow_empty=False):
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{field} 需要非空文字")
    for character in value:
        point = ord(character)
        valid = point in (9, 10, 13) or 32 <= point <= 0xD7FF or 0xE000 <= point <= 0xFFFD or 0x10000 <= point <= 0x10FFFF
        if not valid or 0xFDD0 <= point <= 0xFDEF or (point & 0xFFFF) in (0xFFFE, 0xFFFF):
            raise ValueError(f"{field} 含不能写入 XML 的字符 U+{point:04X}")
    return value


def numeric(value, field, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} 需要有限数字")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} 需要有限数字")
    if not minimum <= value <= maximum:
        raise ValueError(f"{field} 须在 {minimum:g} 到 {maximum:g} 之间")
    return value


def color(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise ValueError(f"{field} 需要六位 HEX 颜色，例如 #167E99")
    return value.upper()


def theme(config):
    return (color(config.get("accent", "#167E99"), "accent"),
            color(config.get("background", "#FFF9EE"), "background"))


def em_width(character):
    if unicodedata.combining(character) or character in ("\u200d", "\ufe0f"):
        return 0
    if unicodedata.east_asian_width(character) in ("F", "W"):
        return 1
    if character in "WM@#%&":
        return 1
    if character in "ilI.,;:!'| `":
        return 0.4
    if character.isascii():
        return 0.65
    return 1


def wrapped(value, field, width, maximum_lines):
    value = text(value, field)
    result = []
    for paragraph in value.split("\n"):
        line = ""
        used = 0
        for character in paragraph:
            advance = em_width(character)
            if line and used + advance > width:
                result.append(line)
                line = ""
                used = 0
            line += character
            used += advance
        result.append(line)
    if len(result) > maximum_lines:
        raise ValueError(f"{field} 排成 {len(result)} 行，当前画布容纳 {maximum_lines} 行，请精简或拆分")
    return result


def labels(lines, x, y, size=32, step=42, fill="#24343B", weight="400"):
    return "\n".join(
        f'<text x="{x:g}" y="{y + index * step:g}" font-size="{size:g}" fill="{fill}" font-weight="{weight}" xml:space="preserve">{html.escape(line)}</text>'
        for index, line in enumerate(lines)
    )


def button(identifier, action, label, x, y, width, accent):
    return f'''<g id="{identifier}" data-action="{action}" style="cursor:pointer;">
<rect x="{x:g}" y="{y:g}" width="{width:g}" height="58" rx="13" fill="{accent}" />
<text x="{x + width / 2:g}" y="{y + 39:g}" text-anchor="middle" font-size="30" fill="#FFFFFF" style="pointer-events:none;">{html.escape(label)}</text>
</g>'''


def frame(content, height, background, description):
    return f'''<section style="margin:20px 0;padding:0;line-height:0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 {height}" width="100%" style="display:block;width:100%;height:auto;overflow:hidden;" font-family="sans-serif" data-component="{COMPONENT}">
<desc>{html.escape(description)}</desc>
<rect x="1" y="1" width="598" height="{height - 2}" rx="20" fill="{background}" />
{content}
</svg></section>'''


def preview(fragment, title):
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<body style="margin:0;background:#F3F2EC;font-family:system-ui,sans-serif;color:#24343B;">
<main style="box-sizing:border-box;max-width:632px;margin:24px auto;padding:16px;">
<h1 style="font-size:24px;line-height:1.5;">{html.escape(title)}</h1>
{fragment}</main></body></html>'''


def write_outputs(outputs, overwrite):
    staged = []
    committed = []
    backups = {}
    try:
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            if overwrite and path.exists():
                with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".bak", delete=False) as backup:
                    backup.write(path.read_bytes())
                    backups[path] = Path(backup.name)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as stage:
                staged.append((path, Path(stage.name)))
                stage.write(content)
        for path, temporary in staged:
            if overwrite:
                os.replace(temporary, path)
            else:
                os.link(temporary, path)
            committed.append(path)
    except OSError as error:
        recovery_errors = []
        for path in reversed(committed):
            try:
                if path in backups:
                    os.replace(backups[path], path)
                    del backups[path]
                else:
                    path.unlink(missing_ok=True)
            except OSError as recovery:
                saved = backups.pop(path, None)
                recovery_errors.append(f"{path} 恢复失败，备份 {saved}，{recovery}")
        detail = "\n".join(recovery_errors)
        raise OSError(f"输出写入失败，{error}\n{detail}") from error
    finally:
        for _, temporary in staged:
            temporary.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--preview-out", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    targets = [args.out] + ([args.preview_out] if args.preview_out else [])
    resolved = [path.resolve() for path in targets]
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict):
            raise ValueError("配置顶层需要 JSON 对象")
        if len(set(resolved)) != len(resolved):
            raise ValueError("片段与预览需要不同输出文件")
        if any(path.is_dir() for path in targets):
            raise ValueError("输出指向目录，请指定文件名")
        if not args.overwrite and any(path.exists() for path in targets):
            raise ValueError("输出已存在，请换路径或使用 --overwrite")
        fragment, metadata, input_files = build(config, args.config)
        if {args.config.resolve(), *input_files}.intersection(resolved):
            raise ValueError("输出不能覆盖配置文件或原始图片")
        outputs = [(args.out, fragment)]
        if args.preview_out:
            outputs.append((args.preview_out, preview(fragment, metadata["title"])))
        write_outputs(outputs, args.overwrite)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({"status": "created", "component": COMPONENT,
                      "files": [str(path) for path in resolved], **metadata}, ensure_ascii=False))


def build(config, config_path):
    accent, background = theme(config)
    title = wrapped(config.get("title"), "title", 15, 1)
    unit = wrapped(config.get("unit", "数量"), "unit", 8, 1)
    items = config.get("items")
    if not isinstance(items, list) or not 2 <= len(items) <= 5:
        raise ValueError("items 需要2～5项，每项包含 label 与非负 value")
    prepared = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{index}] 需要对象")
        label = wrapped(item.get("label"), f"items[{index}].label", 3, 2)
        value = numeric(item.get("value"), f"items[{index}].value", 0, 1e100)
        prepared.append((label, value))
    largest = max(value for _, value in prepared)
    maximum = numeric(config.get("max_value", max(1, largest)), "max_value", 1e-100, 1e100)
    if maximum < largest:
        raise ValueError("max_value 不能小于数据中的最大值")
    seconds = numeric(config.get("duration", 1), "duration", 0.1, 5)
    prefix = "chart_" + uuid.uuid4().hex
    start = f"{prefix}_play.click"
    content = labels(title, 36, 59, 34, weight="700") + labels(unit, 36, 101, 26)
    content += '<path d="M40 348 H560" stroke="#80999E" stroke-width="2" />'
    cell_width = 520 / len(prepared)
    legend = []
    for index, (label, value) in enumerate(prepared):
        center = 40 + (index + 0.5) * cell_width
        bar_width = min(76, cell_width * 0.6)
        bar_height = 200 * value / maximum
        top = 348 - bar_height
        original_value = str(value)
        display_value = original_value
        if len(display_value) > 7:
            concise = f"{value:.3g}"
            display_value = concise if float(concise) == value else "≈" + concise
        number_size = min(32, (cell_width - 6) / (max(1, len(display_value)) * 0.65))
        content += f'''<g id="{prefix}_bar_{index}" data-chart-bar="{index}">
<rect x="{center - bar_width / 2:g}" y="{top:g}" width="{bar_width:g}" height="{bar_height:g}" rx="8" fill="{accent}">
<animate attributeName="height" from="0" to="{bar_height:g}" begin="{start}" dur="{seconds:g}s" fill="freeze" restart="always" />
<animate attributeName="y" from="348" to="{top:g}" begin="{start}" dur="{seconds:g}s" fill="freeze" restart="always" />
</rect><text x="{center:g}" y="{max(130, top - 13):g}" text-anchor="middle" font-size="{number_size:g}" fill="#24343B" data-true-value="{html.escape(original_value, quote=True)}">{html.escape(display_value)}</text>'''
        for line_index, line in enumerate(label):
            content += f'<text x="{center:g}" y="{391 + line_index * 35}" text-anchor="middle" font-size="30" fill="#24343B">{html.escape(line)}</text>'
        content += '</g>'
        legend.append(f'<p style="margin:5px 0;font-size:16px;line-height:1.7;overflow-wrap:anywhere;">{html.escape("".join(label))}　{html.escape(original_value)} {html.escape(config.get("unit", "数量"))}</p>')
    content += button(prefix + "_play", "play", "点击播放 / 重新播放", 36, 454, 528, accent)
    fragment = frame(content, 540, background, "按输入数值绘制柱形图，数值标签持续可见。点击按钮播放柱形入场。")
    fragment += '<section data-chart-values="true" style="margin:0 0 18px;font-family:sans-serif;color:#24343B;">' + ''.join(legend) + '</section>'
    return fragment, {
        "title": config["title"], "canvas": [600, 540], "items": len(prepared),
        "max_value": maximum, "duration": seconds,
    }, set()


if __name__ == "__main__":
    main()
