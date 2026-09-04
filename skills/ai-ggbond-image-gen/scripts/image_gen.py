#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-Image-2 通用内容生图 CLI（OpenLux 链路）
=============================================
用法:
  文生图
    python3 image_gen.py --prompt "内容" --style tech-neon --ratio 16:9 -o out.png
    python3 image_gen.py --raw --prompt "完整提示词" --size 2160x3840 --quality high -o big.png

  图生图/编辑 (GPT-Image-2 /v1/images/edits multipart；不要带 format)
    python3 image_gen.py --edit --image input.png --prompt "把第6项 import reqestb 改成 import requests" -o fixed.png

Key 解析优先级: 环境变量 YUNWU_API_KEY/OPENAI_API_KEY
              -> ~/.ai-ggbond-skills/.env (YUNWU_API_KEY)
              -> ~/.hermes/profiles/*/config.yaml 与 ~/.hermes/config.yaml image_gen.api_key
"""
import argparse
import base64
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("image_gen")

ENV_PATHS = [
    Path.home() / ".ai-ggbond-skills" / ".env",
]

# 风格名称映射到内部 key（用于校验）；具体模板在 style_bundle()
STYLE_ALIASES = {
    "high-density": "high-density",
    "retro-pop": "retro-pop",
    "folder": "folder",
    "receipt": "receipt",
    "vintage-journal": "vintage-journal",
    "vector-illustration": "vector-illustration",
    "tech-neon": "tech-neon",
    "tech": "tech-neon",
    "editorial-notes": "editorial-notes",
    "editorial": "editorial-notes",
}

# 比例 -> 尺寸（OpenLux 支持范围）
RATIO_SIZES = {
    "1:1": "1024x1024",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
    "4:3": "1536x1152",
    "3:4": "1152x1536",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
}


def _load_dotenv(path: Path) -> Dict[str, str]:
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            vals[k.strip()] = v.strip().strip("\"'")
    return vals


def _load_env() -> Dict[str, str]:
    out = {}
    for p in ENV_PATHS:
        out.update(_load_dotenv(p))
    return out


def _scan_profile_configs() -> List[dict]:
    """扫描 ~/.hermes/config.yaml 与 ~/.hermes/profiles/*/config.yaml 的 image_gen"""
    results = []
    candidates = [Path.home() / ".hermes" / "config.yaml"]
    profiles_dir = Path.home() / ".hermes" / "profiles"
    if profiles_dir.is_dir():
        for p in sorted(profiles_dir.glob("*/config.yaml")):
            candidates.append(p)
    for path in candidates:
        if not path.exists():
            continue
        try:
            text = path.read_text(errors="ignore")
            # 轻量 yaml 提取 image_gen 段
            m = re.search(r"image_gen:\s*(.*?)(?=\n\S|\Z)", text, re.DOTALL)
            if not m:
                continue
            block = m.group(1)
            def _val(key):
                mm = re.search(rf"^\s*{key}:\s*['\"]?([^'\n\"]+)['\"]?\s*$", block, re.M)
                return mm.group(1).strip() if mm else None
            entry = {"path": str(path)}
            api_key = _val("api_key")
            base_url = _val("base_url")
            model = _val("model")
            if api_key and api_key != "dummy":
                entry["api_key"] = api_key
            if base_url:
                entry["base_url"] = base_url
            if model:
                entry["model"] = model
            if entry.get("api_key"):
                results.append(entry)
        except Exception:
            continue
    return results


def resolve_credentials() -> Dict[str, str]:
    """解析 api_key / base_url / model"""
    env = _load_env()
    key = os.environ.get("YUNWU_API_KEY") or os.environ.get("OPENAI_API_KEY") or env.get("YUNWU_API_KEY") or env.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or env.get("YUNWU_BASE_URL") or ""

    # 扫 profile config 作为第二来源
    for cfg in _scan_profile_configs():
        if not key:
            key = cfg.get("api_key")
        if not base_url:
            base_url = cfg.get("base_url", "")

    if not key or key == "dummy":
        raise RuntimeError("未找到有效 API Key：请设置环境变量 YUNWU_API_KEY / OPENAI_API_KEY，或编辑 ~/.hermes/profiles/*/config.yaml 的 image_gen.api_key")
    if not base_url:
        base_url = "https://api.openlux.ai/v1"

    # 归一化 base_url：允许带 /v1 或不带
    base_url = base_url.strip().rstrip("/")
    for suffix in ("/v1/images/generations", "/v1/images/edits", "/images/generations", "/images/edits"):
        if base_url.endswith(suffix):
            base_url = base_url[: -len(suffix)]
    if not base_url.endswith("/v1"):
        base_url = base_url + "/v1"
    return {"api_key": key, "base_url": base_url}


def _truthy(v) -> bool:
    return str(v or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_size(ratio: Optional[str], size: Optional[str]) -> str:
    if size:
        return size.strip().lower()
    if ratio:
        r = ratio.strip().lower()
        if r in RATIO_SIZES:
            return RATIO_SIZES[r]
        # 支持 "1792x1024" 之类的直接透传
        if re.fullmatch(r"\d+x\d+", r):
            return r
    return "1024x1024"


def style_bundle(style_key: str) -> str:
    """返回风格中文描述文本（拼进模板提示词）"""
    bundles = {
        "high-density": "高密度信息大图：实验室精密手册感 + 波普实验风格；灰白蓝图网格背景(#F2F2F2)、荧光粉(#E91E63)、柠檬黄(#FFF200)、炭黑细线；6-7个高密度模块、坐标化标签、超大粗体标题配超精细注释",
        "retro-pop": "复古波普网格：1970s复古波普艺术 + 瑞士网格系统；奶油底(#F5F0E6)、鲑鱼粉/天蓝/芥末黄平涂色块、粗黑线描边、统一2D扁平、4-6模块网格、关键警告黑底白字",
        "folder": "文件夹/档案风格：新拟物化文具风；奶油米底、克莱因蓝主色、3D文件夹/档案袋元素、标签页、纸质纹理、柔和阴影；专业可信、中等密度",
        "receipt": "打印热敏纸风格：现代票据美学；白底、深灰文字、红色强调、虚线分隔、条码元素、等宽字体效果；清晰易读、适合步骤清单",
        "vintage-journal": "复古手帐风格：复古剪贴簿 + 手绘日记；米白纸底、暖粉/雾蓝/焦糖色、手绘抖动线、胶带贴纸、手写字体、便签纸；温暖亲切、低密度高留白",
        "vector-illustration": "矢量插图风格：扁平化矢量插画；白底、统一黑色轮廓线、简洁几何形状、图标化元素；蓝/红/绿三色点缀；概念清晰、教育感",
        "tech-neon": "科技风：深色背景(#0A1628) + 霓虹蓝(#00D4FF)/霓虹紫(#A855F7)点缀、细线网格、发光边框、半透明层、科技元件图标；高密度、适合AI工具与技术主题",
        "editorial-notes": "技术杂志/编辑手帐风：像资深开发者亲手整理的技术笔记；暖灰白纸张底、石墨黑文字、克制的工程蓝与便签橙、网格纸/铅笔圈线/荧光笔、编辑器小窗、手写箭头、便利贴；专业克制、有留白、去AI生硬模板感",
    }
    return bundles.get(style_key, bundles["editorial-notes"])


def build_style_prompt(title: str, content: str, style_key: str, ratio: str) -> str:
    desc = style_bundle(style_key)
    return f"""创建一张{ratio}的{title}。

【核心内容】
{content}

【视觉风格规范】
{desc}

【文字要求】（极其重要）
- 所有文字使用简体中文，清晰无乱码、无变形
- 标题大而醒目，正文字号合适可读
- 只呈现给定内容，不额外添加无关文字、Logo、二维码、水印
- 严禁出现随机英文乱码

【强制要求】
- 严格按{ratio}构图，所有元素在安全区内，不裁切
"""


@dataclass
class ImageResult:
    url: Optional[str] = None
    b64_data: Optional[str] = None
    model: str = ""


def _extract(result: Dict) -> Optional[str]:
    data = result.get("data", [])
    if isinstance(data, list) and data and isinstance(data[0], dict):
        if data[0].get("url"):
            return data[0]["url"]
        if data[0].get("b64_json"):
            return "data:image/png;base64," + data[0]["b64_json"]
    return None


class ImageGenerator:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _save(self, item: ImageResult, save_path: str) -> str:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if item.url:
            r = requests.get(item.url, timeout=180)
            r.raise_for_status()
            data = r.content
        elif item.b64_data:
            data = base64.b64decode(item.b64_data)
        else:
            raise RuntimeError("响应中没有图片数据")
        out.write_bytes(data)
        logger.info("✅ 已保存: %s (%d bytes)", out, out.stat().st_size)
        return str(out)

    def generate(self, prompt: str, size: str, quality: str, model: str, timeout: int = 360, max_retries: int = 2, retry_delay: int = 10) -> ImageResult:
        url = f"{self.base_url}/images/generations"
        payload = {"model": model, "prompt": prompt, "n": 1, "size": size, "quality": quality}
        last = None
        for attempt in range(max_retries):
            try:
                r = requests.post(url, headers=self.headers, json=payload, timeout=timeout)
                if r.status_code == 200:
                    raw = r.json()
                    got = _extract(raw)
                    if got:
                        if got.startswith("data:"):
                            return ImageResult(b64_data=got.split(",", 1)[1], model=model)
                        return ImageResult(url=got, model=model)
                    last = "响应中没有图片字段: " + str(raw)[:300]
                else:
                    last = f"HTTP {r.status_code}: {r.text[:400]}"
                    if r.status_code == 429:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
            except Exception as e:
                last = f"{type(e).__name__}: {e}"
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        raise RuntimeError(f"生图失败: {last}")

    def edit(self, image_path: str, prompt: str, size: str, quality: str, model: str, timeout: int = 600, max_retries: int = 2, retry_delay: int = 10) -> ImageResult:
        url = f"{self.base_url}/images/edits"
        src = Path(image_path)
        last = None
        # multipart: image + prompt + model + n + size + quality；不带 format
        for attempt in range(max_retries):
            try:
                with src.open("rb") as fh:
                    files = {"image": (src.name, fh, "image/png")}
                    data = {"model": model, "prompt": prompt, "n": "1", "size": size, "quality": quality}
                    r = requests.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, files=files, data=data, timeout=timeout)
                if r.status_code == 200:
                    got = _extract(r.json())
                    if got:
                        if got.startswith("data:"):
                            return ImageResult(b64_data=got.split(",", 1)[1], model=model)
                        return ImageResult(url=got, model=model)
                    last = "响应中没有图片字段"
                else:
                    last = f"HTTP {r.status_code}: {r.text[:500]}"
                    if r.status_code == 429:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
            except Exception as e:
                last = f"{type(e).__name__}: {e}"
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        raise RuntimeError(f"编辑失败: {last}")


def main():
    ap = argparse.ArgumentParser(description="GPT-Image-2 通用内容生图 (OpenLux)")
    ap.add_argument("--prompt", required=True, help="内容描述（raw 模式=完整提示词；非 raw 模式会拼风格模板）")
    ap.add_argument("--raw", action="store_true", help="prompt 即完整提示词，不套模板")
    ap.add_argument("--style", default=None, help="风格: high-density/retro-pop/folder/receipt/vintage-journal/vector-illustration/tech-neon/editorial-notes")
    ap.add_argument("--ratio", default=None, help="1:1 / 16:9 / 9:16 / 4:3 / 3:4 / 3:2 / 2:3")
    ap.add_argument("--size", default=None, help="直接指定尺寸如 1536x1024 / 2160x3840（优先于 ratio）")
    ap.add_argument("--quality", default="high", help="low/medium/high/auto")
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--edit", action="store_true", help="图生图编辑模式")
    ap.add_argument("--image", default=None, help="编辑模式源图")
    ap.add_argument("-o", "--output", default="output.png")
    ap.add_argument("--title", default="信息图", help="非 raw 模式下的主题名")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    creds = resolve_credentials()
    size = _resolve_size(args.ratio, args.size)
    gen = ImageGenerator(creds["api_key"], creds["base_url"])

    if args.edit:
        if not args.image:
            sys.exit("--edit 需要 --image 源图")
        result = gen.edit(args.image, args.prompt, size, args.quality, args.model, timeout=args.timeout)
    else:
        if args.raw:
            final_prompt = args.prompt
        else:
            style_key = (args.style or "editorial-notes").lower()
            style_key = STYLE_ALIASES.get(style_key, style_key)
            if style_key not in style_bundle:
                sys.exit(f"未知风格 {args.style}，可选: {', '.join(STYLE_ALIASES)}")
            ratio_display = args.ratio or (size if re.fullmatch(r"\d+x\d+", size or "") else "16:9")
            final_prompt = build_style_prompt(args.title, args.prompt, style_key, ratio_display)
        result = gen.generate(final_prompt, size, args.quality, args.model, timeout=args.timeout)

    saved = gen._save(result, args.output)
    print(saved)


if __name__ == "__main__":
    main()
