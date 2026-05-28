#!/usr/bin/env python3
"""AI朱朱侠 — 图片水印清除脚本（单张）

直接调用 remove-ai-watermarks 的 GeminiEngine / InvisibleEngine / metadata cleaner。
通过 uv 环境 Python 运行（UV_PYTHON），兼容飞哥的配图管线。

用法:
  scripts/clean.py input.png -o clean.png          # 全清
  scripts/clean.py input.png --visible-only         # 仅可见水印
  scripts/clean.py input.png --metadata-only        # 仅元数据
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

# ── 找到 uv 环境的 Python（Python 3.10+，依赖齐全）──
_UV_PYTHON = Path.home() / ".local/share/uv/tools/remove-ai-watermarks/bin/python"

# 如果当前 Python 就是 uv 环境的，直接运行；否则自动切换到 uv Python
if Path(sys.executable).resolve() != _UV_PYTHON.resolve() and _UV_PYTHON.exists():
    # 用 uv Python 重新执行自己
    os.execv(str(_UV_PYTHON), [str(_UV_PYTHON), __file__] + sys.argv[1:])

# ── 以下代码在 uv Python 3.10 环境中运行 ──
from remove_ai_watermarks.gemini_engine import GeminiEngine
from remove_ai_watermarks.noai.cleaner import remove_ai_metadata, has_ai_content
import cv2


def _verbose_print(msg: str) -> None:
    print(f"  {msg}")


def identify(source: Path) -> dict:
    """识别图片水印，返回结构化结果。"""
    result = {
        "file": str(source),
        "visible": False,
        "metadata": False,
        "gemini_confidence": 0.0,
    }

    try:
        img = cv2.imread(str(source), cv2.IMREAD_COLOR)
        if img is not None:
            engine = GeminiEngine()
            det = engine.detect_watermark(img)
            result["visible"] = det.detected
            result["gemini_confidence"] = round(det.confidence, 4)
    except Exception as e:
        result["visible_error"] = str(e)

    try:
        result["metadata"] = has_ai_content(source)
    except Exception as e:
        result["metadata_error"] = str(e)

    return result


def clean_all(source: Path, output: Path, humanize: float = 0.0) -> Path:
    """完整清洗管线：可见水印 → 不可见水印 → 元数据。"""
    import tempfile

    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    tmp_path = Path(tmp)
    if img is None:
        print(f"  ✗ 无法读取图片: {source}")
        return source

    engine = GeminiEngine()
    det = engine.detect_watermark(img)
    if det.detected:
        cleaned = engine.remove_watermark(img)
        cleaned = engine.inpaint_residual(cleaned, det.region)
        _verbose_print(f"  ✓ 已清除（置信度 {det.confidence:.2%}）")
    else:
        cleaned = img
        _verbose_print("  跳过（未检测到可见水印）")

    # 写入临时文件
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    cv2.imwrite(tmp, cleaned)

    # ── Step 2: 不可见水印 ──
    _verbose_print("② 不可见水印…")
    from remove_ai_watermarks.invisible_engine import is_available as invisible_available

    if invisible_available():
        from remove_ai_watermarks.invisible_engine import InvisibleEngine

        inv_engine = InvisibleEngine(device="auto")
        inv_engine.process(tmp, tmp, strength=0.05, steps=50)
        _verbose_print("  ✓ 已处理")
    else:
        _verbose_print("  跳过（GPU 依赖未安装）")

    # ── Step 3: 元数据 ──
    _verbose_print("③ AI 元数据…")
    remove_ai_metadata(tmp_path, output)
    _verbose_print(f"  ✓ 已剥离")

    # ── Step 4: 模拟胶片颗粒（可选）──
    if humanize > 0:
        _verbose_print(f"④ 模拟胶片颗粒（强度 {humanize}）…")
        try:
            from remove_ai_watermarks.humanizer import humanize_image

            humanize_image(str(output), str(output), intensity=humanize)
            _verbose_print("  ✓")
        except ImportError:
            _verbose_print("  ✗ humanizer 不可用，跳过")

    # 清理临时文件
    try:
        os.unlink(tmp)
    except OSError:
        pass

    return output


def clean_visible(source: Path, output: Path) -> Path:
    """仅清除可见水印（Gemini 火花）。"""
    img = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"✗ 无法读取: {source}")
        return source

    engine = GeminiEngine()
    det = engine.detect_watermark(img)
    if det.detected:
        cleaned = engine.remove_watermark(img)
        cleaned = engine.inpaint_residual(cleaned, det.region)
        _verbose_print(f"✓ 可见水印已清除（置信度 {det.confidence:.2%}）")
    else:
        cleaned = img
        _verbose_print("未检测到可见水印")

    cv2.imwrite(str(output), cleaned)
    return output


def clean_metadata(source: Path, output: Path) -> Path:
    """仅剥离 AI 元数据。"""
    remove_ai_metadata(source, output)
    _verbose_print("✓ 元数据已剥离")
    return output


def main():
    parser = argparse.ArgumentParser(description="AI朱朱侠 图片水印清除")
    parser.add_argument("source", type=Path, help="输入图片路径")
    parser.add_argument("-o", "--output", type=Path, default=None, help="输出路径")
    parser.add_argument("--visible-only", action="store_true", help="仅清除可见水印")
    parser.add_argument("--metadata-only", action="store_true", help="仅剥离元数据")
    parser.add_argument("--identify", action="store_true", help="仅识别水印")
    parser.add_argument("--humanize", type=float, default=0.0, help="胶片颗粒强度 (0-6)")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if not args.source.exists():
        print(f"✗ 文件不存在: {args.source}")
        sys.exit(1)

    t0 = time.monotonic()

    if args.identify:
        result = identify(args.source)
        if args.json:
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            status = []
            if result["visible"]:
                status.append(f"可见水印 (置信度 {result['gemini_confidence']:.2%})")
            if result["metadata"]:
                status.append("AI 元数据")
            print(f"📷 {result['file']}")
            print(f"   水印: {' | '.join(status) if status else '未检测到'}")
        return

    # 确定输出路径
    if args.output:
        output = args.output
    else:
        output = args.source.with_stem(args.source.stem + "_clean")

    if args.metadata_only:
        clean_metadata(args.source, output)
    elif args.visible_only:
        clean_visible(args.source, output)
    else:
        clean_all(args.source, output, humanize=args.humanize)

    elapsed = time.monotonic() - t0
    print(f"\n✅ {output}  ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
