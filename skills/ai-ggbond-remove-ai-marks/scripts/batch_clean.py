#!/usr/bin/env python3
"""AI朱朱侠 — 批量水印清除 + 管线集成

自动扫描文章/贴图目录，清除所有 AI 生成图片的水印。
集成到 ai-ggbond-article-writer 和 ai-ggbond-sticker-writer 管线中。

用法:
  scripts/batch_clean.py /path/to/images/
  scripts/batch_clean.py /path/to/images/ --dry-run
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ── 切换到 uv 环境 Python ──
_UV_PYTHON = Path.home() / ".local/share/uv/tools/remove-ai-watermarks/bin/python"
if Path(sys.executable).resolve() != _UV_PYTHON.resolve() and _UV_PYTHON.exists():
    os.execv(str(_UV_PYTHON), [str(_UV_PYTHON), __file__] + sys.argv[1:])

from remove_ai_watermarks.noai.cleaner import has_ai_content

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def scan_images(directory: Path) -> list[Path]:
    """递归扫描目录下所有图片。"""
    images = []
    for ext in SUPPORTED:
        images.extend(directory.glob(f"*{ext}"))
        images.extend(directory.glob(f"*{ext.upper()}"))
    return sorted(set(images))


def check_image(image: Path) -> dict:
    """快速检查单张图片的水印状态。"""
    result = {
        "file": str(image),
        "name": image.name,
        "size_kb": round(image.stat().st_size / 1024, 1),
        "has_metadata": False,
        "needs_cleaning": False,
    }
    try:
        result["has_metadata"] = has_ai_content(str(image))
    except Exception:
        pass
    result["needs_cleaning"] = result["has_metadata"]
    return result


def clean_single(source: Path, output: Path) -> bool:
    """清洗单张图片（调用 clean.py 的 clean_all）。"""
    import subprocess

    script = Path(__file__).parent / "clean.py"
    r = subprocess.run(
        [sys.executable, str(script), str(source), "-o", str(output)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return r.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="AI朱朱侠 批量水印清除")
    parser.add_argument("directory", type=Path, help="图片目录")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描，不修改")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--output-dir", type=Path, default=None, help="输出目录（默认：原地覆盖或 <dir>/clean/）")

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"✗ 目录不存在: {args.directory}")
        sys.exit(1)

    images = scan_images(args.directory)
    if not images:
        print(f"📭 {args.directory} 中没有图片")
        return

    print(f"🔍 扫描到 {len(images)} 张图片\n")

    results = []
    needs_clean = []

    for img in images:
        r = check_image(img)
        results.append(r)
        if r["needs_cleaning"]:
            needs_clean.append(img)
            print(f"  ⚠️ {r['name']} — 检测到 AI 元数据")
        else:
            print(f"  ✅ {r['name']} — 干净")

    if args.dry_run:
        summary = {
            "total": len(images),
            "clean": len(images) - len(needs_clean),
            "needs_cleaning": len(needs_clean),
            "details": results,
        }
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"\n📊 {'='*40}")
            print(f"   总数: {summary['total']}")
            print(f"   干净: {summary['clean']}")
            print(f"   需处理: {summary['needs_cleaning']}")
        return

    if not needs_clean:
        print("\n✨ 所有图片已干净，无需处理。")
        return

    # 确定输出目录
    if args.output_dir:
        out_dir = args.output_dir
    else:
        out_dir = args.directory / "clean"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🧹 开始清洗 {len(needs_clean)} 张…")
    t0 = time.monotonic()
    success = 0

    for img in needs_clean:
        out = out_dir / img.name
        print(f"  → {img.name}…", end=" ")
        if clean_single(img, out):
            print("✓")
            success += 1
        else:
            print("✗")

    elapsed = time.monotonic() - t0
    print(f"\n✅ 完成: {success}/{len(needs_clean)} ({elapsed:.1f}s)")
    print(f"📁 输出: {out_dir}")


if __name__ == "__main__":
    main()
