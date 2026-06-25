#!/usr/bin/env python3
"""
AI朱朱侠长图生成器 - 渲染脚本
将 HTML 模板渲染为高质量 PNG 图片

使用方法:
    python render.py --html input.html --output output.png --width 1080 --height 1440
    python render.py --preset xiaohongshu --html input.html --output output.png
"""

import argparse
import sys
from pathlib import Path

# 尺寸预设
PRESETS = {
    # 小红书竖图（默认）
    "xiaohongshu": {"width": 1080, "height": 1440, "name": "小红书竖图"},
    "xhs": {"width": 1080, "height": 1440, "name": "小红书竖图"},
    
    # 小红书长图
    "xiaohongshu_long": {"width": 1080, "height": 2400, "name": "小红书长图"},
    "xhs_long": {"width": 1080, "height": 2400, "name": "小红书长图"},
    
    # 公众号封面横图
    "wechat_cover": {"width": 900, "height": 383, "name": "公众号封面"},
    "gzh_cover": {"width": 900, "height": 383, "name": "公众号封面"},
    
    # 公众号正文配图
    "wechat_body": {"width": 1080, "height": 720, "name": "公众号配图"},
    "gzh_body": {"width": 1080, "height": 720, "name": "公众号配图"},
    
    # 正方形
    "square": {"width": 1080, "height": 1080, "name": "正方形"},
    
    # 手机壁纸（iPhone 15 Pro）
    "phone_wallpaper": {"width": 1170, "height": 2532, "name": "手机壁纸"},
    "iphone": {"width": 1170, "height": 2532, "name": "手机壁纸"},
    
    # 电脑壁纸
    "desktop_wallpaper": {"width": 2560, "height": 1440, "name": "电脑壁纸"},
    "desktop": {"width": 2560, "height": 1440, "name": "电脑壁纸"},
    
    # PPT
    "ppt": {"width": 1920, "height": 1080, "name": "PPT"},
    "slides": {"width": 1920, "height": 1080, "name": "PPT"},
}

def render_with_playwright(html_path: str, output_path: str, width: int, height: int):
    """使用 Playwright 渲染 HTML 为图片"""
    try:
        from playwright.sync_api import sync_playwright
        
        html_path = Path(html_path).resolve()
        output_path = Path(output_path).resolve()
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=2  # 2x 清晰度
            )
            page.goto(f"file://{html_path}", wait_until="networkidle")
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
        
        return True, str(output_path)
    except ImportError:
        return False, "playwright 未安装，请运行: pip install playwright && playwright install chromium"
    except Exception as e:
        return False, str(e)

def render_with_selenium(html_path: str, output_path: str, width: int, height: int):
    """使用 Selenium 渲染 HTML 为图片（备选方案）"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        html_path = Path(html_path).resolve()
        output_path = Path(output_path).resolve()
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-gpu")
        options.add_argument("--hide-scrollbars")
        
        driver = webdriver.Chrome(options=options)
        driver.get(f"file://{html_path}")
        
        # 设置窗口大小并截图
        driver.set_window_size(width, height)
        driver.save_screenshot(str(output_path))
        driver.quit()
        
        return True, str(output_path)
    except ImportError:
        return False, "selenium 未安装，请运行: pip install selenium"
    except Exception as e:
        return False, str(e)

def render_with_puppeteer(html_path: str, output_path: str, width: int, height: int):
    """使用 Puppeteer（Node.js）渲染 HTML 为图片"""
    import subprocess
    import tempfile
    
    html_path = Path(html_path).resolve()
    output_path = Path(output_path).resolve()
    
    # 生成 Puppeteer 脚本
    script = f"""
    const puppeteer = require('puppeteer');
    
    (async () => {{
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setViewport({{ width: {width}, height: {height}, deviceScaleFactor: 2 }});
        await page.goto('file://{html_path}', {{ waitUntil: 'networkidle0' }});
        await page.screenshot({{ path: '{output_path}', fullPage: true }});
        await browser.close();
    }})();
    """
    
    try:
        # 写入临时脚本
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        # 执行脚本
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 清理
        Path(script_path).unlink()
        
        if result.returncode == 0:
            return True, str(output_path)
        else:
            return False, result.stderr
    except FileNotFoundError:
        return False, "node 未安装"
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(
        description="AI朱朱侠长图生成器 - HTML 转图片渲染工具"
    )
    parser.add_argument(
        "--html", 
        required=True,
        help="输入 HTML 文件路径"
    )
    parser.add_argument(
        "--output", "-o",
        default="output.png",
        help="输出 PNG 文件路径（默认: output.png）"
    )
    parser.add_argument(
        "--width", "-W",
        type=int,
        help="图片宽度（像素）"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        help="图片高度（像素）"
    )
    parser.add_argument(
        "--preset", "-p",
        choices=list(PRESETS.keys()),
        help="使用预设尺寸"
    )
    parser.add_argument(
        "--engine", "-e",
        choices=["playwright", "selenium", "puppeteer"],
        default="playwright",
        help="渲染引擎（默认: playwright）"
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="列出所有可用预设"
    )
    
    args = parser.parse_args()
    
    # 列出预设
    if args.list_presets:
        print("\n📐 可用尺寸预设:\n")
        print(f"{'预设名称':<25} {'尺寸':<15} {'说明'}")
        print("-" * 60)
        for name, info in PRESETS.items():
            print(f"{name:<25} {info['width']}×{info['height']:<10} {info['name']}")
        return
    
    # 确定尺寸
    if args.preset:
        preset = PRESETS[args.preset]
        width = args.width or preset["width"]
        height = args.height or preset["height"]
        print(f"📐 使用预设: {preset['name']} ({width}×{height})")
    elif args.width and args.height:
        width = args.width
        height = args.height
        print(f"📐 自定义尺寸: {width}×{height}")
    else:
        # 默认使用小红书竖图
        preset = PRESETS["xiaohongshu"]
        width = preset["width"]
        height = preset["height"]
        print(f"📐 使用默认预设: {preset['name']} ({width}×{height})")
    
    # 检查输入文件
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"❌ HTML 文件不存在: {html_path}")
        sys.exit(1)
    
    # 选择渲染引擎
    engines = {
        "playwright": render_with_playwright,
        "selenium": render_with_selenium,
        "puppeteer": render_with_puppeteer,
    }
    
    render_func = engines[args.engine]
    
    # 渲染
    print(f"🎨 渲染引擎: {args.engine}")
    print(f"📄 输入文件: {html_path}")
    print(f"📁 输出文件: {args.output}")
    print()
    
    success, result = render_func(str(html_path), args.output, width, height)
    
    if success:
        print(f"✅ 渲染完成!")
        print(f"📁 文件位置: {result}")
        print(f"📐 图片尺寸: {width} × {height} px")
    else:
        print(f"❌ 渲染失败: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
