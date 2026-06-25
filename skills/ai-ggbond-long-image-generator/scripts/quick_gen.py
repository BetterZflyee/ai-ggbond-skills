#!/usr/bin/env python3
"""
AI朱朱侠长图生成器 - 快速生成脚本
根据模板和内容快速生成长图

使用方法:
    python quick_gen.py --template report --title "AI工具推荐" --content "内容..."
    python quick_gen.py --template steps --title "如何使用AI" --items "步骤1,步骤2,步骤3"
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# 模板类型
TEMPLATES = {
    "report": "数据报告卡片",
    "steps": "教程步骤图",
    "quote": "观点卡片",
    "compare": "对比分析图",
    "list": "清单列表图",
}

def generate_report_html(title: str, subtitle: str, metrics: list, sections: list, style: str = "dark"):
    """生成数据报告卡片 HTML"""
    
    # 配色方案
    if style == "dark":
        colors = {
            "bg": "#0F1419",
            "card": "#1A2332",
            "text": "#FFFFFF",
            "text2": "#8B95A5",
            "accent1": "#00D4FF",
            "accent2": "#FF6B35",
            "accent3": "#00E676",
        }
    else:
        colors = {
            "bg": "#F8F9FA",
            "card": "#FFFFFF",
            "text": "#1A1A2E",
            "text2": "#6C757D",
            "accent1": "#0066FF",
            "accent2": "#FF4757",
            "accent3": "#2ED573",
        }
    
    # 生成指标卡片
    metrics_html = ""
    for m in metrics[:3]:
        metrics_html += f"""
        <div class="metric-card">
            <div class="metric-value">{m.get('value', '0')}</div>
            <div class="metric-label">{m.get('label', '')}</div>
        </div>"""
    
    # 生成内容区块
    sections_html = ""
    for i, s in enumerate(sections[:5], 1):
        sections_html += f"""
        <section class="section">
            <div class="section-header">
                <div class="section-number">{i}</div>
                <h2 class="section-title">{s.get('title', '')}</h2>
            </div>
            <div class="card">
                <p class="card-description">{s.get('content', '')}</p>
            </div>
        </section>"""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: {colors['bg']};
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', sans-serif;
    color: {colors['text']};
    line-height: 1.6;
  }}
  .canvas {{
    width: 100%;
    min-height: 100vh;
    padding: 48px;
  }}
  .header {{ margin-bottom: 32px; }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }}
  .logo {{
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, {colors['accent1']}, {colors['accent2']});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
  }}
  .brand-name {{ font-size: 14px; color: {colors['text2']}; }}
  .title {{
    font-size: 42px;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 16px;
    background: linear-gradient(135deg, {colors['text']}, {colors['accent1']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .subtitle {{ font-size: 20px; color: {colors['text2']}; }}
  .divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {colors['accent1']}, transparent);
    margin: 32px 0;
    opacity: 0.3;
  }}
  .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
  }}
  .metric-card {{
    background: {colors['card']};
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.05);
  }}
  .metric-value {{
    font-size: 36px;
    font-weight: 800;
    color: {colors['accent1']};
    margin-bottom: 8px;
  }}
  .metric-label {{ font-size: 14px; color: {colors['text2']}; }}
  .section {{ margin-bottom: 32px; }}
  .section-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }}
  .section-number {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: {colors['accent1']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: {colors['bg']};
  }}
  .section-title {{ font-size: 28px; font-weight: 700; }}
  .card {{
    background: {colors['card']};
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.05);
  }}
  .card-description {{ font-size: 16px; color: {colors['text2']}; line-height: 1.8; }}
  .footer {{
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.05);
    font-size: 12px;
    color: {colors['text2']};
    display: flex;
    justify-content: space-between;
  }}
</style>
</head>
<body>
<div class="canvas">
  <header class="header">
    <div class="brand">
      <div class="logo">AI</div>
      <span class="brand-name">AI朱朱侠</span>
    </div>
    <h1 class="title">{title}</h1>
    <p class="subtitle">{subtitle}</p>
  </header>
  <div class="divider"></div>
  <div class="metrics-grid">{metrics_html}</div>
  {sections_html}
  <footer class="footer">
    <span>© {datetime.now().year} AI朱朱侠</span>
    <span>专注让AI成为自动化搞钱和IP运营系统</span>
  </footer>
</div>
</body>
</html>"""
    
    return html

def generate_steps_html(title: str, subtitle: str, steps: list, style: str = "dark"):
    """生成教程步骤图 HTML"""
    
    if style == "dark":
        colors = {"bg": "#0F1419", "card": "#1A2332", "text": "#FFF", "text2": "#8B95A5", "accent": "#00D4FF"}
    else:
        colors = {"bg": "#F8F9FA", "card": "#FFF", "text": "#1A1A2E", "text2": "#6C757D", "accent": "#0066FF"}
    
    steps_html = ""
    for i, step in enumerate(steps, 1):
        steps_html += f"""
        <div class="step">
            <div class="step-number">{i}</div>
            <div class="step-content">
                <h3 class="step-title">{step.get('title', '')}</h3>
                <p class="step-desc">{step.get('desc', '')}</p>
            </div>
        </div>"""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: {colors['bg']};
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
    color: {colors['text']};
    line-height: 1.6;
  }}
  .canvas {{ width: 100%; min-height: 100vh; padding: 48px; }}
  .header {{ margin-bottom: 48px; text-align: center; }}
  .title {{
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 16px;
    background: linear-gradient(135deg, {colors['text']}, {colors['accent']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .subtitle {{ font-size: 20px; color: {colors['text2']}; }}
  .step {{
    display: flex;
    gap: 24px;
    margin-bottom: 32px;
    padding: 24px;
    background: {colors['card']};
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
  }}
  .step-number {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: {colors['accent']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 700;
    color: {colors['bg']};
    flex-shrink: 0;
  }}
  .step-content {{ flex: 1; }}
  .step-title {{ font-size: 22px; font-weight: 700; margin-bottom: 8px; }}
  .step-desc {{ font-size: 16px; color: {colors['text2']}; }}
</style>
</head>
<body>
<div class="canvas">
  <header class="header">
    <h1 class="title">{title}</h1>
    <p class="subtitle">{subtitle}</p>
  </header>
  {steps_html}
</div>
</body>
</html>"""
    
    return html

def main():
    parser = argparse.ArgumentParser(description="AI朱朱侠长图快速生成器")
    parser.add_argument("--template", "-t", choices=list(TEMPLATES.keys()), required=True, help="模板类型")
    parser.add_argument("--title", required=True, help="标题")
    parser.add_argument("--subtitle", default="", help="副标题")
    parser.add_argument("--style", choices=["dark", "light"], default="dark", help="风格")
    parser.add_argument("--output", "-o", default=None, help="输出 HTML 文件路径")
    
    # report 模板参数
    parser.add_argument("--metrics", help="指标数据 JSON: [{\"value\":\"100+\",\"label\":\"指标\"}]")
    parser.add_argument("--sections", help="内容区块 JSON: [{\"title\":\"标题\",\"content\":\"内容\"}]")
    
    # steps 模板参数
    parser.add_argument("--steps", help="步骤数据 JSON: [{\"title\":\"标题\",\"desc\":\"描述\"}]")
    
    args = parser.parse_args()
    
    # 生成 HTML
    if args.template == "report":
        metrics = json.loads(args.metrics) if args.metrics else []
        sections = json.loads(args.sections) if args.sections else []
        html = generate_report_html(args.title, args.subtitle, metrics, sections, args.style)
    elif args.template == "steps":
        steps = json.loads(args.steps) if args.steps else []
        html = generate_steps_html(args.title, args.subtitle, steps, args.style)
    else:
        print(f"❌ 模板 {args.template} 暂未实现")
        sys.exit(1)
    
    # 输出文件
    if args.output:
        output_path = args.output
    else:
        output_path = f"output_{args.template}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML 已生成: {output_path}")
    print(f"📐 下一步: 使用 render.py 渲染为图片")

if __name__ == "__main__":
    main()
