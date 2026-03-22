#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章排版优化器
将 Markdown 文章转换为适合手机端阅读的 HTML 格式。

功能特点：
1. 标题结构优化：实现清晰的层级标题结构（H1-H6）
2. 响应式设计：适配各种移动设备屏幕
3. 正文字体设置：15px字体、1.75em行距、0.04em字间距
4. 整体排版优化：段落清晰、间距合理、阅读舒适
"""

import os
import re
import sys
import argparse
import base64
from pathlib import Path
from datetime import datetime


def image_to_base64(image_path: str) -> str:
    """
    将图片转换为base64编码
    
    Args:
        image_path: 图片路径
        
    Returns:
        base64编码的图片数据URI
    """
    try:
        path = Path(image_path)
        if not path.exists():
            return None
        
        # 读取图片文件
        with open(path, 'rb') as f:
            image_data = f.read()
        
        # 确定MIME类型
        suffix = path.suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        mime_type = mime_types.get(suffix, 'image/png')
        
        # 转换为base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
        
    except Exception as e:
        print(f"⚠️ 图片转换失败: {image_path}, 错误: {e}")
        return None


class ArticleFormatter:
    """文章排版优化器类"""

    MOBILE_CSS = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 15px;
            line-height: 1.75em;
            letter-spacing: 0.04em;
            color: #333;
            background-color: #f5f5f5;
            -webkit-font-smoothing: antialiased;
        }
        .article-container {
            max-width: 680px;
            margin: 0 auto;
            background-color: #fff;
            min-height: 100vh;
        }
        @media screen and (min-width: 768px) {
            .article-container {
                padding: 40px 50px;
                margin: 20px auto;
                border-radius: 8px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            }
        }
        @media screen and (max-width: 767px) {
            .article-container {
                padding: 24px 20px;
            }
        }
        @media screen and (max-width: 375px) {
            .article-container {
                padding: 20px 16px;
            }
        }
        h1 {
            font-size: 26px;
            font-weight: 700;
            line-height: 1.4;
            color: #1a1a1a;
            margin: 0 0 24px 0;
            padding-bottom: 16px;
            border-bottom: 2px solid #e8e8e8;
        }
        h2 {
            font-size: 22px;
            font-weight: 600;
            line-height: 1.4;
            color: #222;
            margin: 36px 0 18px 0;
            padding-left: 12px;
            border-left: 4px solid #07c160;
        }
        h3 {
            font-size: 19px;
            font-weight: 600;
            line-height: 1.45;
            color: #333;
            margin: 28px 0 14px 0;
        }
        h4 {
            font-size: 17px;
            font-weight: 600;
            line-height: 1.5;
            color: #444;
            margin: 22px 0 12px 0;
        }
        h5 {
            font-size: 15px;
            font-weight: 600;
            line-height: 1.5;
            color: #555;
            margin: 18px 0 10px 0;
        }
        h6 {
            font-size: 15px;
            font-weight: 500;
            line-height: 1.5;
            color: #666;
            margin: 16px 0 8px 0;
            font-style: italic;
        }
        p {
            margin: 0 0 16px 0;
            text-align: justify;
            word-break: break-word;
        }
        p + p {
            margin-top: 12px;
        }
        ul, ol {
            margin: 16px 0;
            padding-left: 24px;
        }
        li {
            margin: 8px 0;
            line-height: 1.75em;
        }
        blockquote {
            margin: 20px 0;
            padding: 16px 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #07c160;
            border-radius: 0 4px 4px 0;
            color: #555;
            font-style: italic;
        }
        blockquote p {
            margin: 0;
        }
        code {
            font-family: "SF Mono", Monaco, Inconsolata, "Fira Code", "Courier New", monospace;
            font-size: 13px;
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            color: #e83e8c;
        }
        pre {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0;
        }
        pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
            font-size: 13px;
            line-height: 1.6;
        }
        a {
            color: #576b95;
            text-decoration: none;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e8e8e8;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        hr {
            border: none;
            border-top: 1px solid #e8e8e8;
            margin: 32px 0;
        }
        strong, b {
            font-weight: 600;
            color: #1a1a1a;
        }
        em, i {
            font-style: italic;
            color: #555;
        }
    </style>
    """

    def __init__(self):
        self.html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    {css}
</head>
<body>
    <div class="article-container">
        {content}
    </div>
</body>
</html>"""
        self.code_blocks = []

    def markdown_to_html(self, markdown_text):
        html = markdown_text
        html = self._escape_code_blocks(html)
        html = self._convert_headers(html)
        html = self._convert_emphasis(html)
        html = self._convert_inline_code(html)
        html = self._convert_blockquotes(html)
        html = self._convert_unordered_lists(html)
        html = self._convert_ordered_lists(html)
        html = self._convert_images(html)
        html = self._convert_links(html)
        html = self._convert_hr(html)
        html = self._convert_tables(html)
        html = self._convert_paragraphs(html)
        html = self._restore_code_blocks(html)
        html = self._cleanup_code_block_paragraphs(html)
        return html

    def _escape_code_blocks(self, text):
        self.code_blocks = []
        pattern = r'```(\w*)\n(.*?)```'
        def replace_code_block(match):
            lang = match.group(1) or 'text'
            code = match.group(2)
            placeholder = f"«CODEBLOCK{len(self.code_blocks)}»"
            self.code_blocks.append((lang, code))
            return placeholder
        return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)

    def _restore_code_blocks(self, text):
        for i, (lang, code) in enumerate(self.code_blocks):
            placeholder = f"«CODEBLOCK{i}»"
            escaped_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            code_html = f'<pre><code class="language-{lang}">{escaped_code}</code></pre>'
            text = text.replace(placeholder, code_html)
        return text

    def _cleanup_code_block_paragraphs(self, text):
        text = re.sub(r'<p>\s*(<pre>.*?</pre>)\s*</p>', r'\1', text, flags=re.DOTALL)
        return text

    def _convert_headers(self, text):
        text = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
        text = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
        return text

    def _convert_emphasis(self, text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        return text

    def _convert_inline_code(self, text):
        return re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    def _convert_blockquotes(self, text):
        lines = text.split('\n')
        result = []
        in_blockquote = False
        blockquote_content = []
        for line in lines:
            if line.startswith('>'):
                if not in_blockquote:
                    in_blockquote = True
                    blockquote_content = []
                content = line[1:].strip() if line.startswith('> ') else line[1:]
                blockquote_content.append(content)
            else:
                if in_blockquote:
                    result.append('<blockquote>')
                    result.append('<br>'.join(blockquote_content))
                    result.append('</blockquote>')
                    in_blockquote = False
                    blockquote_content = []
                result.append(line)
        if in_blockquote:
            result.append('<blockquote>')
            result.append('<br>'.join(blockquote_content))
            result.append('</blockquote>')
        return '\n'.join(result)

    def _convert_unordered_lists(self, text):
        lines = text.split('\n')
        result = []
        in_list = False
        list_items = []
        for line in lines:
            match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            if match:
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(match.group(2))
            else:
                if in_list:
                    result.append('<ul>')
                    for item in list_items:
                        result.append(f'<li>{item}</li>')
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('<ul>')
            for item in list_items:
                result.append(f'<li>{item}</li>')
            result.append('</ul>')
        return '\n'.join(result)

    def _convert_ordered_lists(self, text):
        lines = text.split('\n')
        result = []
        in_list = False
        list_items = []
        for line in lines:
            match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
            if match:
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(match.group(2))
            else:
                if in_list:
                    result.append('<ol>')
                    for item in list_items:
                        result.append(f'<li>{item}</li>')
                    result.append('</ol>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('<ol>')
            for item in list_items:
                result.append(f'<li>{item}</li>')
            result.append('</ol>')
        return '\n'.join(result)

    def _convert_images(self, text):
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)

    def _convert_links(self, text):
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    def _convert_hr(self, text):
        return re.sub(r'^(---|\*\*\*|___)$', '<hr>', text, flags=re.MULTILINE)

    def _convert_tables(self, text):
        lines = text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if '|' in line and i + 1 < len(lines) and re.match(r'^[\s|\-:]+$', lines[i + 1]):
                table_lines = [line]
                i += 1
                if re.match(r'^[\s|\-:]+$', lines[i]):
                    i += 1
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                result.append(self._build_table(table_lines))
            else:
                result.append(line)
                i += 1
        return '\n'.join(result)

    def _build_table(self, table_lines):
        if not table_lines:
            return ''
        html = ['<table>']
        headers = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]
        html.append('<thead><tr>')
        for header in headers:
            html.append(f'<th>{header}</th>')
        html.append('</tr></thead>')
        if len(table_lines) > 1:
            html.append('<tbody>')
            for line in table_lines[1:]:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    html.append('<tr>')
                    for cell in cells:
                        html.append(f'<td>{cell}</td>')
                    html.append('</tr>')
            html.append('</tbody>')
        html.append('</table>')
        return '\n'.join(html)

    def _convert_paragraphs(self, text):
        lines = text.split('\n')
        result = []
        paragraph_lines = []
        block_tags = ('<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>',
                      '<ul>', '<ol>', '<li>', '</ul>', '</ol>', '</li>',
                      '<blockquote>', '</blockquote>',
                      '<pre>', '</pre>', '<table>', '</table>',
                      '<thead>', '</thead>', '<tbody>', '</tbody>',
                      '<tr>', '</tr>', '<th>', '</th>', '<td>', '</td>',
                      '<hr>', '<img', '<div', '</div>')
        code_placeholder_pattern = re.compile(r'«CODEBLOCK\d+»')
        for line in lines:
            stripped = line.strip()
            is_block = stripped.startswith(block_tags)
            is_code_placeholder = code_placeholder_pattern.match(stripped)
            if not stripped or is_block or is_code_placeholder:
                if paragraph_lines:
                    paragraph = ' '.join(paragraph_lines)
                    if paragraph and not paragraph.startswith('<'):
                        result.append(f'<p>{paragraph}</p>')
                    else:
                        result.append(paragraph)
                    paragraph_lines = []
                result.append(line)
            else:
                paragraph_lines.append(line)
        if paragraph_lines:
            paragraph = ' '.join(paragraph_lines)
            if paragraph and not paragraph.startswith('<'):
                result.append(f'<p>{paragraph}</p>')
            else:
                result.append(paragraph)
        return '\n'.join(result)

    def format_article(self, markdown_text, title=None, images_dir=None):
        """
        格式化文章为HTML
        
        Args:
            markdown_text: Markdown文本
            title: 文章标题
            images_dir: 图片目录路径（用于嵌入图片）
        """
        content_html = self.markdown_to_html(markdown_text)
        
        # 如果提供了图片目录，将图片嵌入到HTML中
        if images_dir:
            content_html = self._embed_images(content_html, images_dir)
        
        if not title:
            title_match = re.search(r'<h1>(.+?)</h1>', content_html)
            if title_match:
                title = title_match.group(1)
            else:
                title = "文章"
        return self.html_template.format(title=title, css=self.MOBILE_CSS, content=content_html)

    def _embed_images(self, html_content: str, images_dir) -> str:
        """
        将HTML中的图片引用替换为base64嵌入
        
        Args:
            html_content: HTML内容
            images_dir: 图片目录路径
            
        Returns:
            嵌入图片后的HTML内容
        """
        images_dir = Path(images_dir)
        
        # 匹配图片标签
        pattern = r'<img src="([^"]+)" alt="([^"]*)">'
        
        def replace_image(match):
            src = match.group(1)
            alt = match.group(2)
            
            # 如果已经是base64或外部链接，不处理
            if src.startswith('data:') or src.startswith('http'):
                return match.group(0)
            
            # 构建图片路径
            if src.startswith('images/'):
                image_path = images_dir.parent / src
            else:
                image_path = images_dir / src
            
            # 转换为base64
            base64_data = image_to_base64(image_path)
            if base64_data:
                return f'<img src="{base64_data}" alt="{alt}">'
            else:
                # 如果转换失败，尝试其他路径
                # 检查images_dir下是否有同名文件
                for img_file in images_dir.glob('*.png'):
                    if src in str(img_file) or img_file.name in src:
                        base64_data = image_to_base64(img_file)
                        if base64_data:
                            return f'<img src="{base64_data}" alt="{alt}">'
                
                return match.group(0)
        
        return re.sub(pattern, replace_image, html_content)

    def format_file(self, input_path, output_path=None):
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        html_content = self.format_article(markdown_text, title=input_path.stem)
        if not output_path:
            output_path = input_path.with_suffix('.html')
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='文章排版优化器')
    parser.add_argument('-i', '--input', required=True, help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出的HTML文件路径')
    parser.add_argument('-t', '--title', help='文章标题')
    args = parser.parse_args()
    try:
        formatter = ArticleFormatter()
        output_path = formatter.format_file(args.input, args.output)
        print(f"✅ 文章排版优化完成！")
        print(f"📄 输出文件: {output_path}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
