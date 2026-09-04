#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信贴图图片生成器 V2 - 优化版
基于 ai-super-individual-wechat-writer 的 generate_images_v4.py 优化

核心优化：
1. 内容分析器 (ContentAnalyzer) - 深度提取贴图核心信息
2. 多API端点支持 - 自动切换，提高成功率
3. 水印功能 - 支持自定义水印文字
4. 风格模板系统 - 6种信息图风格完整支持
5. 更好的错误处理和重试机制
6. Base64图片数据支持
"""

import os
import sys

import re
import json
import base64
import logging
import requests
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入配置加载器
try:
    from config_loader import load_all_env, apply_env_to_os, get_config_status
    apply_env_to_os()
except ImportError:
    # 如果 config_loader 不存在，使用简单的环境变量加载
    def load_all_env():
        return dict(os.environ)

# 加载配置并设置默认值
_env = load_all_env()
DEFAULT_MODEL = _env.get("YUNWU_DEFAULT_MODEL", "gpt-image-2")
DEFAULT_BASE_URLS = [
    "https://api.openlux.ai",
    "https://api.openlux.ai",
    "https://api.openlux.ai",
]
DEFAULT_IMAGE_ENDPOINT = "/v1/images/generations"
DEFAULT_MAX_RETRIES = int(_env.get("YUNWU_MAX_RETRIES", "3") or 3)
DEFAULT_RETRY_DELAY = int(_env.get("YUNWU_RETRY_DELAY", "8") or 8)
DEFAULT_IMAGE_INTERVAL = int(_env.get("YUNWU_IMAGE_INTERVAL", "20") or 20)
DEFAULT_TIMEOUT = int(_env.get("YUNWU_IMAGE_TIMEOUT", "300") or 300)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


# 默认尊重系统/VPN代理；仅在显式配置时禁用代理。
if _truthy(_env.get("YUNWU_DISABLE_PROXY", "0")):
    for _proxy_key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(_proxy_key, None)


@dataclass
class ImageResult:
    """图片生成结果"""
    url: Optional[str] = None
    b64_data: Optional[str] = None
    model: str = ""
    created: int = 0
    
    def get_image_data(self) -> Optional[str]:
        """获取图片数据（URL或base64）"""
        return self.url if self.url else self.b64_data


@dataclass
class StickerStyle:
    """贴图风格定义"""
    name: str
    name_cn: str
    description: str
    color_palette: Dict[str, str]
    layout_features: List[str]
    density: str  # "high" | "medium" | "low"
    best_for: List[str]


# 6种信息图风格定义
STICKER_STYLES = {
    "high-density": StickerStyle(
        name="high-density",
        name_cn="高密度信息大图",
        description="实验室精密手册感 + 波普实验风格，信息密度极高",
        color_palette={
            "background": "#F2F2F2",
            "accent": "#E91E63",
            "highlight": "#FFF200",
            "grid": "#E0E0E0",
            "text": "#333333"
        },
        layout_features=[
            "超精细技术网格线",
            "坐标化标签(R-20, G-02)",
            "6-7个高密度模块",
            "大粗体标题 vs 超精细注释"
        ],
        density="high",
        best_for=["干货清单", "数据报告", "技术拆解"]
    ),
    "retro-pop": StickerStyle(
        name="retro-pop",
        name_cn="复古波普网格",
        description="70年代复古波普艺术 + 瑞士网格系统，对比鲜明",
        color_palette={
            "background": "#F5F0E6",
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "tertiary": "#FFE66D",
            "text": "#2C3E50"
        },
        layout_features=[
            "粗黑线描边",
            "统一2D扁平风格",
            "严格网格布局",
            "反转对比（黑底白字）"
        ],
        density="medium",
        best_for=["对比评测", "清单类内容", "效率工具"]
    ),
    "folder": StickerStyle(
        name="folder",
        name_cn="文件夹/档案风格",
        description="新拟物化文具风格，专业可信",
        color_palette={
            "background": "#F5F5DC",
            "primary": "#002FA7",
            "accent": "#FF6B35",
            "paper": "#FFFFFF",
            "shadow": "#D4D4D4"
        },
        layout_features=[
            "3D文件夹/档案袋元素",
            "标签页设计",
            "纸质纹理背景",
            "阴影层次感"
        ],
        density="medium",
        best_for=["方法论", "流程说明", "入门教程"]
    ),
    "receipt": StickerStyle(
        name="receipt",
        name_cn="打印热敏纸风格",
        description="现代票据/收据美学，清晰易读",
        color_palette={
            "background": "#FFFFFF",
            "text": "#333333",
            "accent": "#FF6B6B",
            "border": "#E0E0E0",
            "highlight": "#FFF9E6"
        },
        layout_features=[
            "票据/收据形式",
            "虚线分隔",
            "条形码/二维码元素",
            "等宽字体效果"
        ],
        density="medium",
        best_for=["步骤清单", "入门教程", "操作指南"]
    ),
    "vintage-journal": StickerStyle(
        name="vintage-journal",
        name_cn="复古手帐风格",
        description="复古剪贴簿 + 手绘日记美学，温暖亲切",
        color_palette={
            "background": "#FAF9F6",
            "primary": "#D4A5A5",
            "secondary": "#9FB4CC",
            "accent": "#F4E4C1",
            "text": "#5D4E37"
        },
        layout_features=[
            "手绘抖动感线条",
            "胶带/贴纸元素",
            "手写风格字体",
            "便签纸效果"
        ],
        density="low",
        best_for=["经验分享", "个人故事", "生活方式"]
    ),
    "vector-illustration": StickerStyle(
        name="vector-illustration",
        name_cn="矢量插图风格",
        description="扁平化矢量插画，统一黑色轮廓线",
        color_palette={
            "background": "#FFFFFF",
            "primary": "#3498DB",
            "secondary": "#E74C3C",
            "accent": "#2ECC71",
            "outline": "#2C3E50"
        },
        layout_features=[
            "统一黑色轮廓线",
            "扁平化设计",
            "简洁几何形状",
            "图标化元素"
        ],
        density="medium",
        best_for=["概念解释", "教育内容", "PPT风格"]
    )
}


class ContentAnalyzer:
    """贴图内容分析器 - 深度提取核心信息和关键元素"""
    
    @staticmethod
    def extract_content(content: str) -> Dict[str, Any]:
        """提取贴图核心内容"""
        result = {
            'title': '',
            'subtitle': '',
            'key_points': [],
            'emotions': [],
            'hashtags': [],
            'sections': [],
            'core_message': '',
            'target_audience': '',
            'tone': ''
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 提取标题
            if line.startswith('# ') and not result['title']:
                result['title'] = re.sub(r'^#\s*', '', line).strip()
            
            # 提取副标题/引言
            elif line.startswith('> ') and not result['subtitle']:
                result['subtitle'] = re.sub(r'^>\s*', '', line).strip()
            
            # 提取章节
            elif line.startswith('## '):
                if current_section:
                    result['sections'].append(current_section)
                
                heading = re.sub(r'^##\s*', '', line).strip()
                current_section = {
                    'heading': heading,
                    'points': [],
                    'emoji': ContentAnalyzer._extract_emoji(line)
                }
            
            # 提取要点
            elif current_section and ('•' in line or '-' in line):
                point = re.sub(r'^[•\-]\s*', '', line).replace('**', '').strip()
                if 3 < len(point) < 80:
                    current_section['points'].append(point)
                    result['key_points'].append(point)
            
            # 提取标签
            elif '#' in line and not line.startswith('# '):
                hashtags = re.findall(r'#([^#\s]+)', line)
                result['hashtags'].extend(hashtags)
            
            # 提取情感词
            emotion_words = ['😭', '🔥', '💡', '🤫', '⚠️', '💔', '😱', '🥳', '😤', '🤔']
            for emoji in emotion_words:
                if emoji in line and emoji not in result['emotions']:
                    result['emotions'].append(emoji)
        
        if current_section:
            result['sections'].append(current_section)
        
        # 生成核心信息摘要
        if result['key_points']:
            result['core_message'] = ' | '.join(result['key_points'][:5])
        
        return result
    
    @staticmethod
    def _extract_emoji(text: str) -> str:
        """从文本中提取emoji"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        return emojis[0] if emojis else '💡'


class StickerImageGenerator:
    """贴图图片生成器 V2"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_urls: Optional[List[str]] = None,
        endpoint: Optional[str] = None,
        retry_delay: Optional[int] = None,
    ):
        self.api_key = api_key or os.environ.get("YUNWU_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 YUNWU_API_KEY 环境变量")

        self.base_urls = self._resolve_base_urls(base_urls)
        self.endpoint = self._normalize_endpoint(endpoint or os.environ.get("YUNWU_IMAGE_ENDPOINT", DEFAULT_IMAGE_ENDPOINT))
        self.retry_delay = retry_delay if retry_delay is not None else DEFAULT_RETRY_DELAY
        logger.info("图片生成链路: %s", " -> ".join(self.base_urls))
        logger.info("图片生成端点: %s", self.endpoint)

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """清理 Base URL，确保不带 /v1 或具体 endpoint。"""
        base_url = (base_url or "").strip().rstrip("/")
        for suffix in ("/v1/images/generations", "/v1/images/edits", "/images/generations", "/images/edits"):
            if base_url.endswith(suffix):
                base_url = base_url[: -len(suffix)]
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]
        return base_url.rstrip("/")

    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        endpoint = (endpoint or DEFAULT_IMAGE_ENDPOINT).strip()
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return endpoint

    def _resolve_base_urls(self, base_urls: Optional[List[str]] = None) -> List[str]:
        """解析多链路，优先参数，其次 YUNWU_BASE_URLS，再单个 YUNWU_BASE_URL，最后默认三线路。"""
        raw_urls: List[str] = []
        if base_urls:
            raw_urls = base_urls
        elif os.environ.get("YUNWU_BASE_URLS"):
            raw_urls = [u.strip() for u in os.environ.get("YUNWU_BASE_URLS", "").split(",")]
        elif os.environ.get("YUNWU_BASE_URL"):
            raw_urls = [os.environ.get("YUNWU_BASE_URL", ""), *DEFAULT_BASE_URLS]
        else:
            raw_urls = DEFAULT_BASE_URLS[:]

        seen = set()
        resolved: List[str] = []
        for url in raw_urls:
            clean = self._normalize_base_url(url)
            if clean and clean not in seen:
                seen.add(clean)
                resolved.append(clean)
        return resolved or DEFAULT_BASE_URLS[:]
    
    def _extract_image_url(self, result: Dict[str, Any]) -> Optional[str]:
        """从API响应中提取图片URL或base64"""
        # 1. OpenAI 格式 (data -> url/b64_json)
        data = result.get("data", [])
        if isinstance(data, list) and data:
            first = data[0] if isinstance(data[0], dict) else {}
            if first.get("url"):
                return first["url"]
            if first.get("b64_json"):
                return f"data:image/png;base64,{first['b64_json']}"

        # 2. Gemini 格式 (candidates -> content -> parts -> inlineData)
        candidates = result.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                if not isinstance(part, dict):
                    continue
                inline_data = part.get("inlineData") or part.get("inline_data")
                if isinstance(inline_data, dict) and inline_data.get("data"):
                    mime_type = inline_data.get("mimeType", "image/png")
                    return f"data:{mime_type};base64,{inline_data['data']}"
                
                # Gemini 有时也会返回 fileUri
                file_data = part.get("fileData") or part.get("file_data")
                if isinstance(file_data, dict) and file_data.get("fileUri"):
                    return file_data["fileUri"]
        
        return None

    def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        size: str = "1024x1024",
        quality: str = "standard",
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
        retry_delay: Optional[int] = None
    ) -> ImageResult:
        """生成图片，支持多种API格式自动切换"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        last_error = None
        retry_delay = retry_delay if retry_delay is not None else self.retry_delay
        
        # 确定请求模式：如果模型名包含 gemini，优先尝试 gemini 模式，否则只尝试 openai mode
        request_modes = ["openai"]
        if "gemini" in model.lower():
            request_modes = ["gemini", "openai"]
            
        for attempt in range(max_retries):
            for base_url in self.base_urls:
                base_url = base_url.strip().rstrip("/")
                
                for mode in request_modes:
                    try:
                        if mode == "gemini":
                            api_url = f"{base_url}/v1beta/models/{model}:generateContent"
                            payload = {
                                "contents": [{"parts": [{"text": prompt}]}],
                                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
                            }
                        else:
                            if "gemini" in model.lower():
                                 api_url = f"{base_url}/v1/chat/completions"
                                 payload = {
                                    "model": model,
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.7
                                 }
                            else:
                                api_url = f"{base_url}{self.endpoint}"
                                payload = {
                                    "model": model,
                                    "prompt": prompt,
                                    "n": 1,
                                    "size": size,
                                    "quality": quality
                                }

                        logger.info(f"尝试生成 ({mode} mode): {api_url} (Attempt {attempt + 1}/{max_retries})")
                        
                        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
                        
                        if response.status_code == 200:
                            result = response.json()
                            image_url = self._extract_image_url(result)
                            
                            if image_url:
                                if image_url.startswith("data:"):
                                    return ImageResult(b64_data=image_url.split(",")[1], model=model)
                                return ImageResult(url=image_url, model=model)
                            last_error = "响应中未找到图片数据"
                        else:
                            last_error = f"HTTP {response.status_code}: {response.text[:300]}"
                            if response.status_code == 429:
                                logger.warning("⚠️ 当前链路 429 上游饱和，立即切换下一条链路: %s", base_url)
                                break
                            logger.warning("请求失败: %s", last_error)
                            
                    except Exception as e:
                        last_error = str(e)
                        logger.warning(f"请求失败: {last_error}")
                    
                    time.sleep(1)

            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"等待 {wait_time} 秒后重试下一轮链路池...")
                time.sleep(wait_time)
        
        raise RuntimeError(f"图片生成失败: {last_error}")
    
    def generate_sticker_image(
        self,
        title: str,
        content: str,
        style: StickerStyle,
        ratio: str = "1:1",
        model: str = DEFAULT_MODEL
    ) -> ImageResult:
        """生成贴图图片"""
        
        # 解析比例
        size_map = {
            "1:1": "1024x1024",
            "16:9": "1792x1024",
            "3:4": "1024x1365"
        }
        size = size_map.get(ratio, "1024x1024")
        
        # 构建风格特定的提示词
        prompt = self._build_style_prompt(title, content, style, ratio)
        
        return self.generate(prompt=prompt, model=model, size=size)
    
    def _build_style_prompt(
        self,
        title: str,
        content: str,
        style: StickerStyle,
        ratio: str
    ) -> str:
        """根据风格构建提示词"""
        
        base_prompt = f"""创建一张精美的{style.name_cn}信息图。

【基本信息】
- 比例：{ratio}
- 主题：{title}
- 风格：{style.name_cn}

【核心内容】
{content}

【视觉风格规范】
- 整体风格：{style.description}
- 配色方案：
"""
        
        # 添加配色
        for color_name, color_value in style.color_palette.items():
            base_prompt += f"  * {color_name}: {color_value}\n"
        
        # 添加布局特征
        base_prompt += "\n【布局特征】\n"
        for feature in style.layout_features:
            base_prompt += f"- {feature}\n"
        
        # 添加通用要求
        base_prompt += f"""
【信息密度要求】
- 密度级别：{style.density}
- {"6-7个高密度模块，留白≤5%" if style.density == "high" else "4-5个模块，留白10-15%" if style.density == "medium" else "3-4个模块，留白15-20%"}

【文字要求】（极其重要）
- 所有文字必须使用简体中文
- 确保中文文字清晰无乱码、无变形
- 标题字体大且醒目
- 正文字体清晰可读

【强制要求】
- 严格按比例{ratio}设计
- 必须使用【{style.name_cn}】风格
- 所有文字必须是简体中文
- 绝对禁止出现英文
"""
        
        return base_prompt
    
    def save_image(
        self,
        result: ImageResult,
        save_path: str,
        add_watermark: bool = True,
        watermark_text: str = ""
    ) -> str:
        """保存图片，支持URL和base64两种来源"""
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if result.url:
                # 从URL下载
                response = requests.get(result.url, timeout=120)
                response.raise_for_status()
                image_data = response.content
            elif result.b64_data:
                # 从base64解码
                image_data = base64.b64decode(result.b64_data)
            else:
                raise ValueError("没有可用的图片数据")
            
            # 保存图片
            with open(save_path, "wb") as f:
                f.write(image_data)
            
            logger.info(f"✅ 图片已保存: {save_path}")
            
            # 添加水印
            if add_watermark and watermark_text:
                self._add_watermark_to_file(str(save_path), watermark_text)
            
            return str(save_path)
            
        except Exception as e:
            logger.error(f"❌ 保存图片失败: {e}")
            raise
    
    def _add_watermark_to_file(
        self,
        image_path: str,
        watermark_text: str
    ) -> str:
        """为图片添加水印"""
        try:
            img = Image.open(image_path)
            
            # 转换为RGBA模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建透明图层
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 计算字体大小
            img_width, img_height = img.size
            font_size = max(12, int(img_height * 0.02))
            
            # 尝试加载字体
            font = self._load_font(font_size)
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置（右上角）
            margin = int(img_width * 0.02)
            x = img_width - text_width - margin
            y = margin
            
            # 绘制半透明背景
            padding = int(font_size * 0.3)
            bg_bbox = [
                x - padding,
                y - padding,
                x + text_width + padding,
                y + text_height + padding
            ]
            draw.rectangle(bg_bbox, fill=(255, 255, 255, 180))
            
            # 绘制文字
            draw.text((x, y), watermark_text, font=font, fill=(80, 80, 80, 200))
            
            # 合并图层
            img = Image.alpha_composite(img, overlay)
            
            # 转换回RGB并保存
            img = img.convert('RGB')
            img.save(image_path, 'PNG', quality=95)
            
            logger.info(f"✅ 水印已添加: {watermark_text}")
            return image_path
            
        except Exception as e:
            logger.warning(f"⚠️ 添加水印失败: {e}")
            return image_path
    
    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        """加载字体"""
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
        
        return ImageFont.load_default()


def generate_sticker_images_from_markdown(
    markdown_path: str,
    style_name: str = "vintage-journal",
    ratio: str = "1:1",
    watermark: str = "",
    output_dir: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_images: Optional[int] = None,
    image_interval: Optional[int] = None
) -> Dict[str, str]:
    """
    从Markdown文件生成贴图图片
    
    Args:
        markdown_path: Markdown文件路径
        style_name: 风格名称（high-density/retro-pop/folder/receipt/vintage-journal/vector-illustration）
        ratio: 图片比例（1:1/16:9/3:4）
        watermark: 水印文字
        output_dir: 输出目录
        model: 模型名称
        max_images: 最多生成图片数，避免 Markdown 章节过多时超量生成
        image_interval: 图片之间等待秒数，默认读取 YUNWU_IMAGE_INTERVAL（默认20秒）
    
    Returns:
        生成的图片路径字典
    """
    markdown_path = Path(markdown_path)
    if not markdown_path.exists():
        raise FileNotFoundError(f"文件不存在: {markdown_path}")
    
    # 读取内容
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分析内容
    analyzer = ContentAnalyzer()
    analysis = analyzer.extract_content(content)
    
    logger.info(f"内容分析完成：")
    logger.info(f"  - 标题: {analysis.get('title', 'N/A')}")
    logger.info(f"  - 章节数: {len(analysis.get('sections', []))}")
    logger.info(f"  - 关键要点: {len(analysis.get('key_points', []))}")
    
    # 获取风格
    style = STICKER_STYLES.get(style_name, STICKER_STYLES["vintage-journal"])
    logger.info(f"  - 风格: {style.name_cn}")
    
    # 确定输出目录
    if output_dir:
        output_dir = Path(output_dir).expanduser()
    else:
        output_dir = markdown_path.parent / "images"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    image_interval = image_interval if image_interval is not None else DEFAULT_IMAGE_INTERVAL
    
    # 初始化生成器
    generator = StickerImageGenerator()
    results = {}
    
    # 生成章节配图
    sections = analysis.get('sections', [])
    if not sections:
        # 如果没有章节，生成一张整体图
        logger.info("\n生成整体配图...")
        try:
            result = generator.generate_sticker_image(
                title=analysis.get('title', '贴图'),
                content=analysis.get('core_message', ''),
                style=style,
                ratio=ratio,
                model=model
            )
            
            save_path = output_dir / "01-整体配图.png"
            generator.save_image(result, str(save_path), bool(watermark), watermark)
            results['整体配图'] = str(save_path)
            
        except Exception as e:
            logger.error(f"❌ 整体配图生成失败: {e}")
    else:
        # 为每个章节生成配图，可通过 max_images 限制数量
        if max_images is not None and max_images > 0:
            original_count = len(sections)
            sections = sections[:max_images]
            logger.info("已限制生成数量: %s/%s", len(sections), original_count)

        for i, section in enumerate(sections, 1):
            logger.info(f"\n生成配图 {i}/{len(sections)}: {section['heading']}")
            
            try:
                # 构建章节内容
                section_content = f"{section['heading']}\n"
                for point in section.get('points', []):
                    section_content += f"• {point}\n"
                
                result = generator.generate_sticker_image(
                    title=section['heading'],
                    content=section_content,
                    style=style,
                    ratio=ratio,
                    model=model
                )
                
                # 生成文件名
                safe_name = re.sub(r'[<>:"/\\|?*]', '', section['heading'])[:20]
                save_path = output_dir / f"{i:02d}-{safe_name}.png"
                
                generator.save_image(result, str(save_path), bool(watermark), watermark)
                results[f'配图{i}'] = str(save_path)
                
                if i < len(sections) and image_interval > 0:
                    logger.info("等待 %s 秒后生成下一张，避免上游429...", image_interval)
                    time.sleep(image_interval)
                
            except Exception as e:
                logger.error(f"❌ 配图{i}生成失败: {e}")
    
    success_count = len([v for v in results.values() if v])
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ 生成完成！成功: {success_count}/{len(results)}")
    logger.info(f"{'='*60}\n")
    
    return results


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='微信贴图图片生成器 V2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成复古手帐风格贴图
  python generate_sticker_images_v2.py --markdown 贴图.md --style vintage-journal
  
  # 生成高密度信息图
  python generate_sticker_images_v2.py --markdown 贴图.md --style high-density --ratio 16:9
  
  # 添加水印
  python generate_sticker_images_v2.py --markdown 贴图.md --watermark "我的水印"
  
  # 查看所有可用风格
  python generate_sticker_images_v2.py --list-styles
        """
    )
    
    parser.add_argument('--markdown', '-m', help='Markdown文件路径')
    parser.add_argument('--style', '-s', default='vintage-journal',
                       choices=list(STICKER_STYLES.keys()),
                       help='信息图风格（默认: vintage-journal）')
    parser.add_argument('--ratio', '-r', default='16:9',
                       choices=['1:1', '16:9', '3:4'],
                       help='图片比例（默认: 16:9）')
    parser.add_argument('--watermark', '-w', default='',
                       help='水印文字')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--model', default=os.environ.get('YUNWU_DEFAULT_MODEL', 'gpt-image-2'),
                       help='模型名称（默认: YUNWU_DEFAULT_MODEL 或 gpt-image-2）')
    parser.add_argument('--max-images', type=int, default=None,
                       help='最多生成图片数，避免章节过多时超量生成')
    parser.add_argument('--image-interval', type=int, default=DEFAULT_IMAGE_INTERVAL,
                       help=f'图片之间等待秒数，避免上游429（默认: {DEFAULT_IMAGE_INTERVAL}）')
    parser.add_argument('--list-styles', action='store_true',
                       help='列出所有可用风格')
    
    args = parser.parse_args()
    
    if args.list_styles:
        print("\n可用风格列表：\n")
        for key, style in STICKER_STYLES.items():
            print(f"{key:20s} - {style.name_cn}")
            print(f"{' '*22}  {style.description}")
            print(f"{' '*22}  适用: {', '.join(style.best_for)}\n")
        return
    
    if args.markdown:
        try:
            results = generate_sticker_images_from_markdown(
                markdown_path=args.markdown,
                style_name=args.style,
                ratio=args.ratio,
                watermark=args.watermark,
                output_dir=args.output_dir,
                model=args.model,
                max_images=args.max_images,
                image_interval=args.image_interval
            )
            
            print("\n生成结果:")
            for name, path in results.items():
                status = "✅" if path else "❌"
                print(f"  {status} {name}: {path or '失败'}")
                
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
