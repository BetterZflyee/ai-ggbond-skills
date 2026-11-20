#!/usr/bin/env python3
"""Offline WeChat layout compiler. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from layout_design import design_report, image_dimensions, table_plan, numeric_column

OWNER = "ai-ggbond-wechat-layout"
VERSION = "2.1.0"
TYPES = {"paragraph", "heading", "quote", "list", "steps", "table", "image",
         "code", "timeline", "callout", "faq", "comparison", "metrics", "chart", "reveal"}


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: str) -> str:
    return "".join(value.split())


def require(value, label, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"{label} 需要{'文字' if empty else '非空文字'}")
    if any(ord(c) < 32 and c not in "\n\r\t" for c in value):
        raise ValueError(f"{label} 含控制字符")
    return value


def safe_url(value, image=False):
    value = require(value, "链接")
    if any(ord(c) < 32 for c in value) or "\\" in value:
        raise ValueError("链接含控制字符或反斜杠")
    parsed = urlsplit(value)
    allowed = {"https"} if image else {"https", "http", "mailto"}
    if parsed.scheme not in allowed or (parsed.scheme in {"http", "https"} and not parsed.netloc):
        if not image and value.startswith("#"):
            return value
        raise ValueError(f"不支持的链接协议：{value[:90]}")
    return value


class TextReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")


def visible(value):
    parser = TextReader()
    parser.feed(value)
    return "".join(parser.parts)


INLINE = re.compile(r"(`+)(.+?)\1|\*\*(.+?)\*\*|__(.+?)__|\[([^\]\n]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)|(?<!\*)\*([^*\n]+)\*(?!\*)|\\([\\`*{}\[\]()#+.!_|>~-])", re.S)


def inline(value, depth=0):
    require(value, "正文", empty=True)
    if depth > 8:
        raise ValueError("行内标记嵌套过深")
    out, pos = [], 0
    for match in INLINE.finditer(value):
        out.append(html.escape(value[pos:match.start()]))
        code, strong1, strong2, label, url, em, escaped = (match.group(i) for i in [2, 3, 4, 5, 6, 7, 8])
        if code is not None:
            out.append('<code style="font-family:monospace;background-color:#F3F4F6;padding:1px 3px;overflow-wrap:anywhere;">' + html.escape(code) + '</code>')
        elif strong1 is not None or strong2 is not None:
            out.append('<strong>' + inline(strong1 if strong1 is not None else strong2, depth + 1) + '</strong>')
        elif label is not None:
            out.append('<a href="' + html.escape(safe_url(url), quote=True) + '" style="color:inherit;text-decoration:underline;overflow-wrap:anywhere;">' + inline(label, depth + 1) + '</a>')
        elif em is not None:
            out.append('<em>' + inline(em, depth + 1) + '</em>')
        else:
            out.append(html.escape(escaped))
        pos = match.end()
    out.append(html.escape(value[pos:]))
    return "".join(out).replace("\n", "<br>")


def split_cells(line):
    # Pipes inside inline code and escaped pipes are data, not column separators.
    line = line.strip().strip("|")
    cells, cell, code, escaped = [], [], False, False
    for c in line:
        if escaped:
            cell.extend(["\\", c]); escaped = False
        elif c == "\\":
            escaped = True
        elif c == "`":
            code = not code; cell.append(c)
        elif c == "|" and not code:
            cells.append("".join(cell).strip()); cell = []
        else:
            cell.append(c)
    if escaped:
        cell.append("\\")
    cells.append("".join(cell).strip())
    return cells


def parse_markdown(text):
    """Conservative Markdown import. Unsupported structures fail instead of disappearing."""
    lines = text.replace("\r\n", "\n").splitlines()
    meta, blocks, changes = {}, [], []
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            line = lines[i]
            if line.strip() and not line.lstrip().startswith("#"):
                m = re.fullmatch(r"([\w-]+):\s*(.*)", line)
                if not m or m[2] in {"|", ">"}:
                    raise ValueError(f"第 {i+1} 行：仅支持平铺的 YAML 元信息；复杂配置请使用 JSON")
                value = m[2].strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                meta[m[1]] = value
            i += 1
        if i == len(lines):
            raise ValueError("YAML 元信息缺少结束分隔线")
        i += 1
        changes.append("YAML 元信息存入 meta，未进入正文")
    if "digest" in meta and "summary" not in meta:
        meta["summary"] = meta["digest"]

    def add(kind, line_no, **kwargs):
        blocks.append({"id": f"b{len(blocks)+1:03}", "type": kind, "source_line": line_no + 1, **kwargs})

    def special(index):
        s = lines[index].strip()
        return not s or bool(re.match(r"^(#{1,6}\s|>|[-*+]\s|\d+[.)]\s|```|~~~|!\[|\|)", s)) or s in {"---", "***", "___"}

    while i < len(lines):
        s, start = lines[i].strip(), i
        if not s:
            i += 1; continue
        if s in {"---", "***", "___"}:
            changes.append(f"第 {i+1} 行装饰分隔线未进入正文")
            i += 1; continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", s)
        subtitle = re.fullmatch(r"(?:\*\*)?(?:副标题|摘要)[：:]\s*(.+?)(?:\*\*)?", s)
        if heading and len(heading[1]) == 1 and not blocks:
            if meta.get("title") and meta["title"] != heading[2]:
                raise ValueError("YAML 标题与首行标题不一致，请明确保留哪一个")
            meta["title"] = heading[2]
            changes.append(f"第 {i+1} 行主标题移入 meta.title")
            i += 1; continue
        if subtitle and not blocks:
            meta["summary"] = subtitle[1]
            changes.append(f"第 {i+1} 行副标题移入 meta.summary")
            i += 1; continue
        if heading:
            if len(heading[1]) > 3:
                changes.append(f"第 {i+1} 行标题层级映射为 h3，文字保留")
            add("heading", start, level=2 if len(heading[1]) <= 2 else 3, text=heading[2])
            i += 1; continue
        fence = re.match(r"^(`{3,}|~{3,})(.*)$", s)
        if fence:
            code, i = [], i + 1
            while i < len(lines) and lines[i].strip() != fence[1]:
                code.append(lines[i]); i += 1
            if i == len(lines):
                raise ValueError(f"第 {start+1} 行代码块未闭合")
            add("code", start, text="\n".join(code), language=fence[2].strip())
            i += 1; continue
        image = re.fullmatch(r"!\[([^\]]*)\]\((.+)\)", s)
        if image:
            src = image[2]
            if src.startswith("<") and src.endswith(">"):
                src = src[1:-1]
            add("image", start, src=src, alt=image[1])
            i += 1; continue
        if "![" in s:
            raise ValueError(f"第 {i+1} 行：图片请单独成行，避免丢失周围文字")
        if s.startswith(">"):
            parts = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                part = re.sub(r"^\s*>\s?", "", lines[i])
                if part.startswith(">"):
                    raise ValueError(f"第 {i+1} 行：嵌套引用请转换为 JSON")
                parts.append(part); i += 1
            add("quote", start, text="\n".join(parts)); continue
        if i + 1 < len(lines) and "|" in s and re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*", lines[i+1]):
            headers, rows = split_cells(s), []
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_cells(lines[i])); i += 1
            add("table", start, headers=headers, rows=rows); continue
        item = re.match(r"^([-*+]|\d+[.)])\s+(.+)", s)
        if item:
            ordered = item[1][0].isdigit()
            items = []
            list_start = int(re.match(r"\d+", item[1])[0]) if ordered else 1
            while i < len(lines):
                m = re.match(r"^([-*+]|\d+[.)])\s+(.+)", lines[i])
                if not m or m[1][0].isdigit() != ordered:
                    break
                if ordered and int(re.match(r"\d+", m[1])[0]) != list_start + len(items):
                    raise ValueError(f"第 {i+1} 行列表编号不连续，请使用 JSON 保留特殊编号")
                items.append(m[2]); i += 1
                if i < len(lines) and lines[i].startswith(("  ", "\t")) and lines[i].strip():
                    raise ValueError(f"第 {i+1} 行：多层列表请转换为 JSON，原文未改动")
            if not items:
                raise ValueError(f"第 {i+1} 行：缩进列表请使用 JSON")
            add("list", start, items=items, ordered=ordered, start=list_start); continue
        if re.match(r"^\s*<[/!A-Za-z]", s) or re.match(r"^\[.+\]:\s", s):
            raise ValueError(f"第 {i+1} 行包含原始 HTML 或引用式链接，请先转为显式 JSON/行内链接")
        if s.startswith("|"):
            raise ValueError(f"第 {i+1} 行表格缺少合法分隔行")
        paragraph = [s]
        i += 1
        while i < len(lines) and not special(i):
            if i + 1 < len(lines) and re.match(r"^\s*[-=]{3,}\s*$", lines[i+1]):
                raise ValueError("Setext 标题请改用 ##，避免误读")
            if "![" in lines[i] or re.match(r"^\s*<[/!A-Za-z]", lines[i]):
                raise ValueError(f"第 {i+1} 行的图片或 HTML 需要单独处理")
            paragraph.append(lines[i].strip()); i += 1
        add("paragraph", start, text=" ".join(paragraph))
    return {"schema_version": 1, "meta": meta, "blocks": blocks}, changes


class FieldReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values, self.active, self.stack, self.counts = {}, [], [], {}
        self.tags, self.images, self.links, self.event_attrs = [], [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        self.event_attrs.extend(k for k in attrs if k.startswith("on"))
        if tag == "img":
            self.images.append(attrs.get("src", ""))
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        key = attrs.get("data-layout-field")
        if key:
            self.counts[key] = self.counts.get(key, 0) + 1
            self.values.setdefault(key, [])
            self.active.append(key)
        if tag not in {"img", "br", "hr", "meta", "link", "input", "wbr"}:
            self.stack.append((tag, key))
        if tag == "br":
            self.handle_data("\n")

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            _, key = self.stack.pop()
            if key:
                self.active.remove(key)

    def handle_data(self, data):
        for key in self.active:
            self.values[key].append(data)


class Renderer:
    def __init__(self, profile, source, stage):
        self.p, self.source, self.stage = profile, source, stage
        self.expected, self.assets, self.warnings, self.types = {}, [], [], []
        self.experimental = []
        self.image_reviews, self.table_reviews = [], []
        self.previous_kind = None
        self.spacing = {}

    def field(self, value, key, raw=False, copy=False):
        require(value, key, empty=True)
        rendered = html.escape(value) if raw else inline(value)
        rendered = rendered.replace('color:inherit;text-decoration:underline;', f'color:{self.p["link_color"]};text-decoration:underline;')
        if key in self.expected and copy:
            if self.expected[key] != (value if raw else visible(rendered)):
                raise ValueError(f"重复字段内容不一致 {key}")
            return f'<span data-layout-copy-of="{key}">{rendered}</span>'
        if key in self.expected:
            raise ValueError(f"重复字段 {key}")
        self.expected[key] = value if raw else visible(rendered)
        return f'<span data-layout-field="{key}">{rendered}</span>'

    def image(self, value, role):
        value = require(value, role)
        parsed = urlsplit(value)
        if parsed.scheme:
            url = safe_url(value, image=True)
            self.assets.append({"role": role, "src": url, "kind": "remote", "reachability": "not_checked", "rights": "not_checked"})
            self.warnings.append(f"{role} 使用远程图片，未下载或验证授权：{url}")
            return url
        if value.startswith("//") or parsed.query or parsed.fragment:
            raise ValueError(f"{role} 本地图片路径不应有协议相对地址、查询串或片段")
        original = Path(unquote(value)).expanduser()
        original = original if original.is_absolute() else self.source.parent / original
        original = original.resolve()
        if not original.is_file() or original.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            raise ValueError(f"{role} 图片不存在或格式不支持：{original}")
        data = original.read_bytes()
        dimensions = image_dimensions(data)
        checksum = digest(data)
        relative = f"assets/{checksum[:20]}{original.suffix.lower()}"
        destination = self.stage / relative
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(data)
        self.assets.append({"role": role, "src": relative, "original": str(original), "sha256": checksum, "bytes": len(data), "kind": "local", "dimensions": list(dimensions) if dimensions else None, "rights": "not_checked"})
        return relative

    def render_table(self, b, identifier):
        headers, rows = b.get('headers'), b.get('rows')
        if not isinstance(headers,list) or not headers or not isinstance(rows,list) or not rows:
            raise ValueError('表格需要非空 headers 和 rows')
        if any(not isinstance(row,list) or len(row)!=len(headers) for row in rows):
            raise ValueError('表格每行列数必须与表头一致')
        for value in headers:
            require(value,identifier+'.header')
        for row in rows:
            for value in row:
                require(value,identifier+'.cell',True)
        plain_headers=[visible(inline(h)) for h in headers]
        plain_rows=[[visible(inline(v)) for v in row] for row in rows]
        plan=table_plan(b,plain_headers,plain_rows,self.p)
        self.table_reviews.append({'block':identifier,'intent':b.get('intent','comparison'),**plan})
        f=lambda value,name:self.field(value,identifier+'.'+name,copy=True)
        border=self.p['border']
        body=''
        if b.get('title'):
            body=f'<p style="margin:0 0 12px;font-weight:600;">{f(b["title"],"title")}</p>'
        if plan['layout']=='records':
            for i,row in enumerate(rows):
                body+=f'<section style="margin:0;padding:{16 if i else 0}px 0 12px;border-bottom:1px solid {border};">'
                for j,(header,value) in enumerate(zip(headers,row)):
                    body+=f'<p style="margin:0;padding-top:6px;"><strong>{f(header,"h"+str(j))}</strong>：{f(value,f"r{i}c{j}")}</p>'
                body+='</section>'
        else:
            for part,group in enumerate(plan['groups']):
                total=sum(plan['column_weights'][j] for j in group)
                body+=f'<section data-table-part="{part+1}" style="margin:0;padding-top:{20 if part else 0}px;overflow-x:auto;">'
                body+=f'<table style="width:100%;table-layout:auto;border-collapse:collapse;font-size:{self.p["table_size"]}px;line-height:1.7;margin:0;"><thead><tr>'
                for j in group:
                    width=100*plan['column_weights'][j]/total
                    body+=f'<th scope="col" style="width:{width:.5f}%;padding:10px 6px;border-bottom:1px solid {border};background-color:{self.p["surface"]};text-align:{plan["align"][j]};overflow-wrap:anywhere;">{f(headers[j],"h"+str(j))}</th>'
                body+='</tr></thead><tbody>'
                for i,row in enumerate(rows):
                    body+='<tr>'
                    for j in group:
                        tag='th' if j==plan['key_column'] else 'td'
                        scope=' scope="row"' if tag=='th' else ''
                        numeric=numeric_column([plain_rows[i][j]])
                        nowrap='white-space:nowrap;' if numeric else 'overflow-wrap:anywhere;'
                        numeric_attr=' data-layout-number="true"' if numeric else ''
                        body+=f'<{tag}{scope}{numeric_attr} style="padding:10px 6px;border-bottom:1px solid {border};vertical-align:top;text-align:{plan["align"][j]};font-weight:400;font-variant-numeric:tabular-nums;{nowrap}">{f(row[j],f"r{i}c{j}")}</{tag}>'
                    body+='</tr>'
                body+='</tbody></table></section>'
        if b.get('source'):
            body+=f'<p style="margin:10px 0 0;font-size:{self.p["small_size"]}px;color:{self.p["muted"]};">{f(b["source"],"source")}</p>'
        return body

    def block(self, b, index):
        if not isinstance(b, dict) or b.get("type") not in TYPES:
            raise ValueError(f"第 {index+1} 个组件类型不支持")
        identifier = b.get("id", f"b{index+1:03}")
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", identifier):
            raise ValueError("组件 id 只用字母、数字、下划线或短横线")
        kind, p = b["type"], self.p
        self.types.append(kind)
        f = lambda value, name, raw=False: self.field(value, identifier + "." + name, raw)
        accent, muted, border = p["accent"], p["muted"], p["border"]
        body = ""
        if kind in {"paragraph", "callout"}:
            text = require(b.get("text"), identifier + ".text")
            if len(visible(inline(text))) > 420:
                self.warnings.append(f"{identifier} 段落较长，请按语义判断是否拆分；脚本未改写")
            weight = "font-weight:600;" if kind == "callout" else ""
            alignment = b.get('align',p['align'])
            if alignment not in {'left','justify'}:
                raise ValueError('paragraph.align 应为 left 或 justify')
            body = f'<p style="margin:0;text-align:{alignment};{weight}">{f(text,"text")}</p>'
        elif kind == "heading":
            level = b.get("level", 2)
            if level not in {2, 3}:
                raise ValueError("正文标题仅支持 h2/h3；主标题放 meta.title")
            size = p["heading_size"] if level == 2 else p["subheading_size"]
            body = f'<h{level} style="margin:0;font-size:{size}px;line-height:1.5;font-weight:700;text-wrap:balance;color:{p["text"]};">{f(require(b.get("text"),identifier),"text")}</h{level}>'
        elif kind == "quote":
            body = f'<blockquote style="margin:0;padding:12px 16px;border-left:3px solid {accent};background-color:{p["quote_bg"]};">'
            body += f'<p style="margin:0;font-weight:600;">{f(require(b.get("text"),identifier),"text")}</p>'
            if b.get("attribution"):
                body += f'<p style="margin:8px 0 0;font-size:13px;color:{muted};">{f(b["attribution"],"attribution")}</p>'
            body += '</blockquote>'
        elif kind == "image":
            src = self.image(b.get("src"), identifier)
            alt = require(b.get("alt", ""), "alt", empty=True)
            role=b.get('role','auto')
            if role not in {'auto','photo','screenshot','diagram','illustration','decorative'}:
                raise ValueError('图片 role 应为 auto/photo/screenshot/diagram/illustration/decorative')
            asset=self.assets[-1]
            dimensions=asset.get('dimensions')
            original_width=dimensions[0] if dimensions else None
            source_font=b.get('source_min_text_px')
            if source_font is not None and (type(source_font) not in {int,float} or not 1<=source_font<=1000):
                raise ValueError('source_min_text_px 需要 1～1000 之间的原图字号')
            fraction=b.get('width_percent',100)
            if type(fraction) not in {int,float} or not 20<=fraction<=100:
                raise ValueError('width_percent 需要 20～100')
            rendered_width=min(original_width,(320-2*p['padding'])*fraction/100) if original_width else None
            estimated=source_font*rendered_width/original_width if source_font and original_width else None
            self.image_reviews.append({'block':identifier,'role':role,'alt':alt,'dimensions':dimensions,'source_min_text_px':source_font,'estimated_min_text_px_at_320':estimated,'upscale':False})
            maximum=f'{original_width}px' if original_width else '100%'
            radius=p['image_radius'] if role=='photo' else 0
            image_style=f'display:block;width:{fraction}%;max-width:{maximum};height:auto;margin:0 auto;border-radius:{radius}px;'
            font_attr=f' data-source-min-text-px="{source_font}"' if source_font else ''
            if b.get("caption") and b.get("show_caption") is not True:
                raise ValueError(f"{identifier} 含 caption；请明确 show_caption:true 或将图注保留在素材记录中")
            body = f'<p style="margin:0;"><img src="{html.escape(src,quote=True)}" alt="{html.escape(alt,quote=True)}" data-image-role="{role}"{font_attr} style="{image_style}"></p>'
            if b.get("caption"):
                body += f'<p style="font-size:{p["small_size"]}px;color:{muted};margin:8px 0 0;">{f(b["caption"],"caption")}</p>'
        elif kind == "code":
            body = f'<pre style="box-sizing:border-box;max-width:100%;margin:0;white-space:pre-wrap;white-space:break-spaces;overflow-wrap:anywhere;word-break:break-all;background-color:#F6F7F9;padding:14px;font-size:{p["small_size"]}px;line-height:1.7;">{f(b.get("text",""),"text",True)}</pre>'
        elif kind == "list":
            items = b.get("items")
            if not isinstance(items, list) or not items:
                raise ValueError(f"{identifier}.items 需要非空列表")
            tag = "ol" if b.get("ordered") else "ul"
            start = b.get("start", 1)
            if type(start) is not int or start < 0:
                raise ValueError("列表起始编号必须是非负整数")
            start_attr=f' start="{start}"' if tag=='ol' else ''
            body = f'<{tag}{start_attr} style="padding-left:1.55em;margin:0;">'
            body += ''.join(f'<li style="margin:0;padding-top:{8 if i else 0}px;">{f(require(v,identifier),str(i))}</li>' for i,v in enumerate(items)) + f'</{tag}>'
        elif kind == "table":
            body = self.render_table(b,identifier)
        elif kind in {"steps", "timeline", "faq", "comparison", "metrics"}:
            items = b.get("items")
            if not isinstance(items,list) or not items:
                raise ValueError(f"{kind}.items 需要非空列表")
            field_names = {"steps":("title","text"),"timeline":("label","text"),"faq":("question","answer"),"comparison":("title","text"),"metrics":("label","value")}[kind]
            for i,item in enumerate(items):
                if not isinstance(item,dict):
                    raise ValueError(f"{kind}.items 中每项需要对象")
                a,c = field_names
                prefix = f'{i+1:02}　' if kind == "steps" else ""
                if kind == 'metrics':
                    body += f'<section style="margin:0;padding-top:{16 if i else 0}px;"><p style="margin:0;color:{muted};font-size:{p["small_size"]}px;">{f(require(item.get(a),identifier),f"{i}.{a}")}</p><p style="margin:4px 0 0;font-size:{p["metric_size"]}px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.5;">{f(require(item.get(c),identifier),f"{i}.{c}")}</p></section>'
                    continue
                body += f'<section style="margin:0;padding-top:{16 if i else 0}px;"><p style="margin:0 0 6px;font-weight:600;color:{accent if kind in {"steps","timeline"} else p["text"]};">{prefix}{f(require(item.get(a),identifier),f"{i}.{a}")}</p>'
                body += f'<p style="margin:0;">{f(require(item.get(c),identifier),f"{i}.{c}")}</p></section>'
        elif kind == "chart":
            items = b.get("items")
            if not isinstance(items,list) or not 2 <= len(items) <= 12:
                raise ValueError("chart.items 需要 2～12 项")
            for item in items:
                if not isinstance(item,dict) or type(item.get("value")) not in {int,float} or not 0 <= item["value"] <= 1e100 or not math.isfinite(item["value"]):
                    raise ValueError("柱形图数值必须是有限非负数；负值请使用表格或适当图型")
                require(item.get("label"),"图表标签")
            maximum = b.get("max_value",max(1,max(v["value"] for v in items)))
            if type(maximum) not in {int,float} or not 0 < maximum <= 1e100 or not math.isfinite(maximum) or maximum < max(v["value"] for v in items):
                raise ValueError("图表 max_value 必须有限且不小于最大数据")
            body = f'<section style="margin:0;"><p style="font-weight:600;margin:0 0 12px;">{f(require(b.get("title"),identifier),"title")}</p>'
            if b.get("unit"):
                body += f'<p style="margin:0 0 12px;font-size:13px;color:{muted};">{f(b["unit"],"unit")}</p>'
            for i,item in enumerate(items):
                width = 100 * item["value"] / maximum
                body += f'<p style="margin:10px 0 5px;">{f(item["label"],f"{i}.label")}　<strong>{f(str(item["value"]),f"{i}.value")}</strong></p><section style="background-color:{p["surface"]};height:10px;width:100%;"><section style="width:{width:.6f}%;height:10px;background-color:{accent};"></section></section>'
            if b.get("source"):
                body += f'<p style="font-size:13px;color:{muted};margin:12px 0 0;">{f(b["source"],"source")}</p>'
            body += '</section>'
        elif kind == "reveal":
            body = f'<section style="margin:0;"><p style="font-weight:600;margin:0 0 8px;">{f(require(b.get("prompt"),identifier),"prompt")}</p><p style="margin:0;">{f(require(b.get("answer"),identifier),"answer")}</p></section>'
        if 'interactive' in b and type(b['interactive']) is not bool:
            raise ValueError('interactive 需要 true 或 false')
        if b.get("interactive"):
            if kind not in {"reveal", "chart"}:
                raise ValueError("当前内置互动仅支持 reveal 和 chart；其他效果查组件目录")
            self.experimental.append((identifier,b))
        if index==0:
            gap=p['first_gap']
        elif kind=='heading':
            gap=p['section_gap'] if b.get('level',2)==2 else p['subsection_gap']
        elif self.previous_kind=='heading':
            gap=p['heading_follow_gap']
        elif kind in {'paragraph','list'} and self.previous_kind in {'paragraph','list'}:
            gap=p['paragraph_gap']
        else:
            gap=p['block_gap']
        self.previous_kind=kind
        self.spacing[identifier]=gap
        return f'<section id="{identifier}" data-layout-block="{identifier}" data-layout-kind="{kind}" style="margin:0;padding:{gap}px 0 0;">{body}</section>'


def profile_load(name):
    path = Path(name)
    if not path.is_file():
        path = ROOT / "assets" / "profiles" / (name + ".json")
    profile = json.loads(path.read_text(encoding="utf-8"))
    for key,value in {'first_gap':18,'section_gap':34,'subsection_gap':26,'heading_follow_gap':10,'block_gap':24,'small_size':13,'table_size':14,'metric_size':22,'link_color':profile.get('accent')}.items():
        profile.setdefault(key,value)
    for key in ["accent","text","muted","border","surface","quote_bg","link_color"]:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(profile.get(key,""))):
            raise ValueError(f"风格 {key} 应为六位 HEX")
    for key,low,high in [("font_size",14,20),("line_height",1.5,2.3),("heading_size",16,28),("subheading_size",15,24),("paragraph_gap",8,32),("image_radius",0,16),("padding",8,28),("first_gap",0,32),("section_gap",16,64),("subsection_gap",12,48),("heading_follow_gap",4,24),("block_gap",12,40),("small_size",12,16),("table_size",13,18),("metric_size",18,28)]:
        value = profile.get(key)
        if type(value) not in {int,float} or not low <= value <= high or not math.isfinite(value):
            raise ValueError(f"风格 {key} 范围应为 {low}～{high}")
    if profile.get("align") not in {"left","justify"}:
        raise ValueError("align 应为 left 或 justify")
    return profile


def document(title, body):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + '</title></head><body style="margin:0;background-color:#FFFFFF;">' + body + '</body></html>'


def preview(title, advanced=False):
    advanced_link = '<a href="interactive.html" target="_blank">互动候选</a>' if advanced else ''
    buttons = ''.join(f'<button type="button" data-width="{w}" aria-pressed="{str(w==375).lower()}">{w} px</button>' for w in [320,375,390,430])
    return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>手机排版预览</title><style>
*{box-sizing:border-box}body{margin:0;background:#F2F4F7;color:#20252D;font-family:system-ui,-apple-system,"PingFang SC",sans-serif}header{max-width:1000px;margin:auto;padding:22px 16px 18px}h1{font-size:20px;line-height:1.5;margin:0 0 14px}nav,.reading{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.reading{margin-top:12px;font-size:13px}button,a,select{font:inherit;font-size:13px;min-height:36px;padding:7px 10px;border:1px solid #B9C3D2;border-radius:5px;background:white;color:#30445E;text-decoration:none;cursor:pointer}button[aria-pressed=true]{background:#2459AD;color:white;border-color:#2459AD}button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #2459AD;outline-offset:3px}.viewport-scroller{padding:0 16px 24px;overflow-x:auto}iframe{box-sizing:content-box;display:block;width:375px;height:780px;max-width:none;margin:0 auto;border:1px solid #D9DEE8;background:white;border-radius:4px}footer{max-width:1000px;margin:auto;padding:0 16px 24px;font-size:13px;line-height:1.8;color:#596577}</style></head><body><header><h1>''' + html.escape(title) + '''</h1><nav aria-label="正文画布宽度">''' + buttons + '''<a href="article.html" target="_blank">打开正文</a><a href="review.html" target="_blank">查看排版检查</a>''' + advanced_link + '''</nav><div class="reading"><label>文字大小 <select id="text-scale"><option value="100">100%</option><option value="125">125%</option><option value="150">150%</option><option value="200">200%</option></select></label><label><input id="text-spacing" type="checkbox"> 加大文字间距</label></div></header><main class="viewport-scroller"><iframe src="reading-preview.html" title="公众号正文阅读预览"></iframe></main><footer>画布保持选定宽度，窗口较窄时可横向查看。文字调整仅用于检查阅读效果，不改动发布正文。</footer><script>
const frame=document.querySelector('iframe');const send=()=>frame.contentWindow.postMessage({type:'layout-preview-settings',scale:Number(document.querySelector('#text-scale').value)/100,spacing:document.querySelector('#text-spacing').checked},'*');
document.querySelectorAll('[data-width]').forEach(b=>b.addEventListener('click',()=>{frame.style.width=b.dataset.width+'px';document.querySelectorAll('[data-width]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}));
frame.addEventListener('load',send);document.querySelector('#text-scale').addEventListener('change',send);document.querySelector('#text-spacing').addEventListener('change',send);
</script></body></html>'''


def reading_preview(title, body):
    script = '''<script>
const elements=[...document.querySelectorAll('body *')];const sizes=new Map(elements.map(e=>[e,parseFloat(getComputedStyle(e).fontSize)]));const spacing=document.createElement('style');document.head.appendChild(spacing);
window.addEventListener('message',event=>{if(event.source!==parent||event.data?.type!=='layout-preview-settings')return;const factor=event.data.scale;if(![1,1.25,1.5,2].includes(factor))return;elements.forEach(e=>e.style.fontSize=(sizes.get(e)*factor)+'px');spacing.textContent=event.data.spacing?'body * {line-height:1.5!important;letter-spacing:0.12em!important;word-spacing:0.16em!important}p{margin-bottom:2em!important}':'';});
</script>'''
    return document(title,body).replace('</body>',script+'</body>')


def review_page(title, report):
    rows=''.join('<li><strong>'+html.escape(f.get('block') or '全稿')+'</strong>：'+html.escape(f['message'])+'</li>' for f in report['findings'])
    if not rows:
        rows='<li>自动检查未发现需要提示的项目，仍需查看实际页面。</li>'
    body='<main style="max-width:720px;margin:28px auto;padding:0 20px;font:16px/1.8 system-ui;color:#2B2B2B;"><h1 style="font-size:24px;">排版检查</h1><p>'+html.escape(title)+'</p><ul>'+rows+'</ul><p>本页提供本地阅读检查建议。图中文字、中文行尾、手机微信与深色模式仍需查看实际效果。</p><p><a href="preview.html">返回预览</a></p></main>'
    return document('排版检查',body)


def write_json(path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2) + "\n",encoding="utf-8")


def advanced_fragment(identifier, block, renderer):
    # Vendored, pinned upstream renderers. No network or browser is started.
    import importlib.util
    from types import SimpleNamespace
    component = "wechat-svg-click-reveal" if block["type"] == "reveal" else "wechat-svg-data-chart"
    path = ROOT / "vendor" / component / "render.py"
    spec = importlib.util.spec_from_file_location(component.replace("-","_"),path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if block["type"] == "reveal":
        prompt, answer = visible(inline(block["prompt"])), visible(inline(block["answer"]))
        before, after = mod.split_lines(prompt), mod.split_lines(answer)
        if len(before)>3 or len(after)>5:
            raise ValueError(f"{identifier} 互动画布容不下文字；请取消 interactive 或明确修改内容，脚本不会截断")
        fragment = mod.component(SimpleNamespace(prompt=prompt,answer=answer,color=renderer.p["accent"],background="#FFFFFF"),before,after)
    else:
        config = {k:block[k] for k in ["title","items","unit","max_value","duration"] if k in block}
        for key in ['title','unit']:
            if key in config:
                config[key]=visible(inline(config[key]))
        config['items']=[{**item,'label':visible(inline(item['label']))} for item in config['items']]
        config.update(accent=renderer.p["accent"],background="#FFFFFF")
        fragment,_,_ = mod.build(config,renderer.source)
        if block.get("source"):
            fragment += '<p style="font-size:13px;">' + inline(block["source"]) + '</p>'
    fragment=fragment.replace('style="margin:20px 0;padding:0;line-height:0;"','style="margin:0;padding:0;line-height:0;"')
    return f'<section id="{identifier}" data-layout-interactive="{identifier}" style="margin:0;padding:{renderer.spacing[identifier]}px 0 0;">{fragment}</section>'


def compile_bundle(source, output, profile_name, overwrite=False, title=None):
    source, output = source.resolve(), output.absolute()
    if output.is_symlink():
        raise ValueError("输出不可指向符号链接")
    output = output.resolve()
    if output == source.parent or output in source.parents or output == ROOT or output in ROOT.parents:
        raise ValueError("输出目录不可覆盖输入目录、Skill 源码目录或符号链接")
    if output.exists():
        if not overwrite:
            raise ValueError("输出目录已存在，请换目录或显式使用 --overwrite")
        manifest = output / "manifest.json"
        if not manifest.is_file() or json.loads(manifest.read_text()).get("owner") != OWNER:
            raise ValueError("只允许覆盖本工具生成的完整交付目录")
    raw = source.read_bytes()
    if source.suffix.lower() in {".md", ".markdown"}:
        data, changes = parse_markdown(raw.decode("utf-8-sig"))
    elif source.suffix.lower() == ".json":
        data, changes = json.loads(raw.decode("utf-8-sig")), []
    else:
        raise ValueError("输入支持 Markdown 或结构化 JSON；已有 HTML 请先提取正文并核对内容")
    if not isinstance(data,dict) or data.get("schema_version") != 1 or not isinstance(data.get("meta"),dict) or not isinstance(data.get("blocks"),list) or not data["blocks"]:
        raise ValueError("输入需要 schema_version:1、meta 对象与非空 blocks")
    if any(not isinstance(b,dict) for b in data["blocks"]):
        raise ValueError("每个正文组件都需要 JSON 对象")
    meta = data["meta"]
    if title:
        meta["title"] = title
    require(meta.get("title"),"meta.title")
    for key in ["author","summary"]:
        require(meta.get(key,""),"meta."+key,True)
    if data["blocks"][0].get("text") and canonical(visible(inline(data["blocks"][0]["text"]))) == canonical(visible(inline(meta["title"]))) and not meta.get("allow_title_in_body"):
        raise ValueError("正文首块重复主标题，请放入 meta.title")
    profile = profile_load(profile_name)
    output.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="."+output.name+"-",dir=output.parent))
    backup = None
    try:
        renderer = Renderer(profile,source,stage)
        ids = [b.get("id",f"b{i+1:03}") for i,b in enumerate(data["blocks"]) if isinstance(b,dict)]
        if len(ids) != len(set(ids)):
            raise ValueError("组件 id 必须唯一")
        parts = [renderer.block(b,i) for i,b in enumerate(data["blocks"])]
        cover = renderer.image(meta["cover"],"cover") if meta.get("cover") else None
        body_images = {x["src"] for x in renderer.assets if x["role"] != "cover"}
        if cover and cover in body_images and not meta.get("allow_cover_in_body"):
            raise ValueError("封面已进入正文；请移除正文封面或显式允许复用")
        container = f'<section style="box-sizing:border-box;width:100%;max-width:680px;margin:0 auto;padding:0 {profile["padding"]}px;font-family:-apple-system,BlinkMacSystemFont,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;font-size:{profile["font_size"]}px;line-height:{profile["line_height"]};color:{profile["text"]};overflow-wrap:break-word;word-break:normal;line-break:strict;">'
        body = container + ''.join(parts) + '</section>'
        audit = FieldReader(); audit.feed(body)
        missing = [key for key,value in renderer.expected.items() if audit.counts.get(key) != 1 or value != ''.join(audit.values.get(key,[]))]
        if missing or audit.stack or any(tag in audit.tags for tag in ["script","iframe","svg","form","input","h1","style"]) or audit.event_attrs:
            raise ValueError(f"正文结构或文字保真检查失败：{missing}")
        for phrase in ["金句断点","建议阅读","点击右上角","全文核心信息图","图片说明：","配图："]:
            if phrase in visible(body):
                renderer.warnings.append(f"正文包含既有偏好中需复核的文字“{phrase}”，未擅自删除")
        if len(meta.get("summary","")) > 120:
            renderer.warnings.append("摘要超过现有推送器的 120 字处理范围，请由作者决定精简，排版阶段未改写")
        review=design_report(data,profile,renderer,lambda value:visible(inline(value)))
        # Exact source content is kept for future diffs; no credentials are loaded.
        (stage / ("source"+source.suffix.lower())).write_bytes(raw)
        (stage / "article.html").write_text(document(meta["title"],body),encoding="utf-8")
        (stage / "body.html").write_text(body,encoding="utf-8")
        (stage / "preview.html").write_text(preview(meta["title"],bool(renderer.experimental)),encoding="utf-8")
        (stage / "reading-preview.html").write_text(reading_preview(meta['title'],body),encoding='utf-8')
        (stage / "review.html").write_text(review_page(meta['title'],review),encoding='utf-8')
        write_json(stage/'design-review.json',review)
        if renderer.experimental:
            advanced = list(parts)
            for identifier,block in renderer.experimental:
                advanced[ids.index(identifier)] = advanced_fragment(identifier,block,renderer)
            (stage / "interactive.html").write_text(document(meta["title"],container+''.join(advanced)+'</section>'),encoding="utf-8")
        write_json(stage/"article.json",data)
        write_json(stage/"profile.json",profile)
        checks = {"content_fidelity":{"status":"passed","scope":"exact parsed field text including code whitespace; Markdown import transformations listed separately","fields":len(renderer.expected)},"structure":{"status":"passed","blocks":len(parts),"images":len(audit.images)},"design_review":{"status":review['status'],'findings':len(review['findings']),'file':'design-review.json'},"transformations":changes,"warnings":renderer.warnings,"validation":{"local_generation":"passed","browser_visual":"not_tested","xiumi_reopen":"not_tested","wechat_draft_readback":"not_tested","phone_wechat":"not_tested"}}
        write_json(stage/"checks.json",checks)
        write_json(stage/"handoff.json",{"owner":OWNER,"article_html":str(output/"article.html"),"body_html":str(output/"body.html"),"meta":meta,"cover":str(output/cover) if cover and not cover.startswith("https:") else cover,"assets":renderer.assets,"draft_target":{"account":None,"existing_media_id":None},"route":"existing publisher with article.html; do not run Markdown theme conversion","interactive_candidate":str(output/"interactive.html") if renderer.experimental else None,"next_checks":["inspect mobile preview","confirm target account and existing draft","read back saved draft","check phone WeChat"],"publish_authorized":False})
        manifest = {"owner":OWNER,"version":VERSION,"source":{"path":str(source),"sha256":digest(raw)},"profile":profile_name,"components":renderer.types,"files":{str(p.relative_to(stage)):digest(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()}}
        write_json(stage/"manifest.json",manifest)
        if output.exists():
            backup = Path(tempfile.mkdtemp(prefix="."+output.name+"-previous-",dir=output.parent))
            backup.rmdir(); output.rename(backup)
        stage.rename(output)
        if backup:
            shutil.rmtree(backup)
        return {"status":"created","output":str(output),"blocks":len(parts),"images":len(audit.images),"fidelity_fields":len(renderer.expected),"warnings":renderer.warnings,"validation":checks["validation"]}
    except Exception:
        if backup and backup.exists() and not output.exists():
            backup.rename(output)
        if stage.exists():
            shutil.rmtree(stage)
        raise


def audit_bundle(output):
    manifest = json.loads((output/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("owner") != OWNER:
        raise ValueError("不是本工具的交付包")
    changed = []
    for name,expected in manifest["files"].items():
        path = (output/name).resolve()
        if output.resolve() not in path.parents or not path.is_file() or digest(path.read_bytes()) != expected:
            changed.append(name)
    return {"status":"passed" if not changed else "failed","changed_or_missing":changed,"note":"checks.json 内的生成时检查不代表后续微信端验收"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command",required=True)
    build = commands.add_parser("build")
    build.add_argument("--input",type=Path,required=True)
    build.add_argument("--out",type=Path,required=True)
    build.add_argument("--profile",default="felix-clean")
    build.add_argument("--title")
    build.add_argument("--overwrite",action="store_true")
    audit = commands.add_parser("audit")
    audit.add_argument("bundle",type=Path)
    catalog = commands.add_parser("catalog")
    catalog.add_argument("--query",default="")
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = compile_bundle(args.input,args.out,args.profile,args.overwrite,args.title)
        elif args.command == "audit":
            result = audit_bundle(args.bundle)
        else:
            entries = json.loads((ROOT/"references"/"upstream-catalog.json").read_text())
            result = [x for x in entries if args.query.lower() in json.dumps(x,ensure_ascii=False).lower()]
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if isinstance(result,dict) and result.get("status") == "failed" else 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({"status":"needs_input","error":str(error)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
