#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云雾API图像生成器 - 公众号专业版 V4
支持 gpt-image-2 等多种模型
用于微信公众号文章配图生成 - 高级版

API 端点策略：
- gpt-image-2 / gpt-image-1 / dall-e-3 → OpenAI Images API
  - 图片生成: POST /v1/images/generations
  - 图片编辑: POST /v1/images/edits
- 其他模型（Gemini 系列等）→ Gemini + OpenAI chat 双模式回退

优化点：
1. 封面图：提升视觉冲击力，使用官方品牌Logo，专业级效果
2. 信息图：强化图表逻辑关联，构建复杂深度结构，专业图标展示
3. 风格选择：支持封面图和信息图的风格定制
"""

import os
import sys
import re
import logging
import requests
import time
import base64
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 导入配置加载器
try:
    from config_loader import load_all_env, apply_env_to_os
    apply_env_to_os()
except ImportError:
    # 如果 config_loader 不存在，使用简单的环境变量加载
    def load_all_env():
        return dict(os.environ)
    load_all_env()


# 导入风格选择器
try:
    from style_selector import StyleSelector, STYLE_PRESETS
except ImportError:
    StyleSelector = None
    STYLE_PRESETS = {}


@dataclass
class ImageResult:
    url: str
    model: str = ""
    created: int = 0


def select_cover_strategy(
    title: str,
    brands: List[str],
    core_concept: str,
    palette: Optional[str] = None,
    rendering: Optional[str] = None
) -> Dict[str, str]:
    """
    选择封面图策略
    
    Args:
        palette: 指定的配色方案，如果提供则使用指定值
        rendering: 指定的渲染风格，如果提供则使用指定值
    """
    text = f"{title} {core_concept}".lower()
    
    # 如果提供了风格参数，直接使用
    if palette and rendering:
        return {
            "palette": palette,
            "rendering": rendering,
            "composition": "根据指定风格自动适配构图",
            "focus": "聚焦文章核心主题"
        }
    
    # 自动检测策略
    if any(x in text for x in ["对比", "冲突", "争议", "辩论", "opinion", "versus", "vs"]):
        return {
            "palette": palette or "duotone",
            "rendering": rendering or "screen-print",
            "composition": "双主体对峙构图，强调对比张力",
            "focus": "高反差色块+负空间表达核心冲突"
        }
    if any(x in text for x in ["系统", "架构", "框架", "workflow", "流程", "architecture"]):
        return {
            "palette": palette or "cool",
            "rendering": rendering or "digital",
            "composition": "中心枢纽+模块化分层构图",
            "focus": "结构关系清晰、视觉引导明确"
        }
    if any(x in text for x in ["故事", "成长", "复盘", "经历", "journey"]):
        return {
            "palette": palette or "warm",
            "rendering": rendering or "hand-drawn",
            "composition": "主视觉偏左，右侧标题叙事",
            "focus": "情绪表达与场景氛围"
        }
    if brands:
        return {
            "palette": palette or "mono",
            "rendering": rendering or "screen-print",
            "composition": "品牌锚点 + 抽象符号平衡布局",
            "focus": "强化识别但保持非广告化表达"
        }
    return {
        "palette": palette or "retro",
        "rendering": rendering or "flat-vector",
        "composition": "单核心主体 + 辅助信息层级",
        "focus": "主题聚焦和阅读入口清晰"
    }


def select_infographic_layout(
    analysis: Dict[str, Any],
    layout: Optional[str] = None,
    style: Optional[str] = None
) -> Dict[str, str]:
    """
    选择信息图布局
    
    Args:
        layout: 指定的布局类型，如果提供则使用指定值
        style: 指定的视觉风格，如果提供则使用指定值
    """
    # 如果提供了布局参数，直接使用
    if layout:
        layout_rules = {
            "comparison-matrix": "左右或矩阵对照，统一评价维度",
            "binary-comparison": "左右分屏对比，突出差异",
            "winding-roadmap": "路径化叙事，节点递进+分支提示",
            "linear-progression": "线性顺序展示，清晰流程",
            "dense-modules": "高密度模块化拼版，分层标注主次信息",
            "hub-spoke": "中心概念+辐射分支，显示依赖关系",
            "hierarchical-layers": "主张-论据-细节三层递进",
            "bento-grid": "模块化网格布局，多主题概览",
            "structural-breakdown": "结构分解展示，内部细节",
            "tree-branching": "树状分支结构，层级关系",
        }
        return {
            "layout": layout,
            "style": style or "craft-handmade",
            "rule": layout_rules.get(layout, "根据内容自动适配布局规则")
        }
    
    # 自动检测布局
    sections = analysis.get("sections", [])
    title = analysis.get("title", "")
    points_count = sum(len(s.get("points", [])) for s in sections)
    signals = f"{title} {' '.join(s.get('heading', '') for s in sections)}".lower()
    
    if any(x in signals for x in ["对比", "vs", "优劣", "比较"]):
        return {"layout": "comparison-matrix", "style": style or "corporate-memphis", "rule": "左右或矩阵对照，统一评价维度"}
    if any(x in signals for x in ["流程", "步骤", "路线", "阶段"]):
        return {"layout": "winding-roadmap", "style": style or "craft-handmade", "rule": "路径化叙事，节点递进+分支提示"}
    if len(sections) >= 8 or points_count >= 20:
        return {"layout": "dense-modules", "style": style or "morandi-journal", "rule": "高密度模块化拼版，分层标注主次信息"}
    if any(x in signals for x in ["框架", "系统", "架构", "模型"]):
        return {"layout": "hub-spoke", "style": style or "technical-schematic", "rule": "中心概念+辐射分支，显示依赖关系"}
    return {"layout": "hierarchical-layers", "style": style or "craft-handmade", "rule": "主张-论据-细节三层递进"}


def select_section_style(heading: str, points: List[str], index: int) -> Dict[str, str]:
    signals = f"{heading} {' '.join(points[:4])}".lower()
    style_cycle = ["vector-illustration", "notion", "screen-print", "editorial"]
    fallback_style = style_cycle[index % len(style_cycle)]
    if any(x in signals for x in ["对比", "优劣", "选择", "vs"]):
        return {"style": "screen-print", "layout": "binary-comparison", "key": "双栏对比+高反差符号"}
    if any(x in signals for x in ["流程", "步骤", "方法", "路径"]):
        return {"style": "vector-illustration", "layout": "linear-progression", "key": "流程箭头+关键节点图标"}
    if any(x in signals for x in ["数据", "指标", "实验", "统计", "%"]):
        return {"style": "editorial", "layout": "dashboard", "key": "图表主导+结论卡片"}
    if any(x in signals for x in ["框架", "系统", "模型", "结构"]):
        return {"style": "blueprint", "layout": "structural-breakdown", "key": "结构分解+依赖连接"}
    return {"style": fallback_style, "layout": "structural-breakdown", "key": "单主视觉+三卡片层级"}


def build_seed(title: str, section_heading: str = "") -> int:
    raw = f"{title}::{section_heading}"
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return int(digest[:6], 16)


class ArticleAnalyzer:
    """文章分析器 - 深度提取文章核心信息和品牌元素"""
    
    @staticmethod
    def extract_content_and_brands(content: str) -> Dict[str, Any]:
        """提取文章核心内容和品牌元素"""
        result = {
            'title': '',
            'subtitle': '',
            'brands': [],  # 品牌/产品列表
            'core_conflict': '',
            'key_concepts': [],
            'sections': [],
            'section_relationships': [],  # 章节间关系
            'key_data': [],
            'visual_flow': [],  # 视觉流程
            'full_content_summary': ''  # 全文摘要用于信息图
        }
        
        # 常见品牌/产品识别
        brand_patterns = [
            r'Claude(?:\s+Code)?',
            r'GLM(?:-\d+)?',
            r'GPT(?:-\d+)?',
            r'OpenAI',
            r'Gemini',
            r'OpenViking',
            r'LangChain',
            r'Llama',
            r'ChatGPT',
            r'Copilot',
            r'Midjourney',
            r'Stable\s+Diffusion',
            r'Anthropic',
            r'火山引擎',
            r'智谱',
            r'文心一言',
            r'通义千问',
            r'OpenClaw',
            r'Clawdbot',
            r'Moltbot'
        ]
        
        lines = content.split('\n')
        current_section = None
        prev_section = None
        all_section_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 提取标题
            if line.startswith('# ') and not result['title']:
                result['title'] = re.sub(r'^#\s*', '', line).strip()
                result['title'] = re.sub(r'^《|》$', '', result['title'])
            
            # 识别品牌/产品
            for pattern in brand_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if match not in result['brands']:
                            result['brands'].append(match)
            
            # 提取章节
            if line.startswith('## '):
                if current_section:
                    result['sections'].append(current_section)
                    # 记录章节关系
                    if prev_section:
                        result['section_relationships'].append({
                            'from': prev_section['heading'],
                            'to': current_section['heading'],
                            'type': 'sequence'
                        })
                    prev_section = current_section
                
                current_section = {
                    'heading': re.sub(r'^##\s*', '', line).strip(),
                    'points': [],
                    'icon': '',
                    'level': 1,
                    'content_summary': '',  # 章节内容摘要用于文件名
                    'full_content': []  # 章节完整内容
                }
            
            # 提取章节要点
            elif current_section:
                # 收集所有段落内容
                if not line.startswith('**') and not line.startswith('•') and not line.startswith('-'):
                    current_section['full_content'].append(line)
                
                # 提取要点
                if '•' in line or '-' in line or '**' in line:
                    point = re.sub(r'^[•\-]\s*', '', line).replace('**', '').strip()
                    if 5 < len(point) < 100:
                        current_section['points'].append(point)
                        all_section_points.append(point)
        
        if current_section:
            result['sections'].append(current_section)
        
        # 为每个章节生成内容摘要（用于文件名）
        for section in result['sections']:
            heading = section['heading']
            points = section['points']
            if points:
                # 使用前2-3个要点组合成摘要
                summary_points = points[:2] if len(points) >= 2 else points
                section['content_summary'] = '; '.join(summary_points)[:40]  # 限制长度
            else:
                # 如果没有要点，使用章节标题
                section['content_summary'] = heading[:40]
            
            # 生成简短的标题摘要（用于文件名）
            section['file_name_summary'] = ArticleAnalyzer._generate_filename_summary(
                heading, section.get('content_summary', '')
            )
        
        # 生成全文摘要（用于信息图）
        result['full_content_summary'] = ' | '.join(all_section_points[:20])
        
        # 去重品牌
        result['brands'] = list(set(result['brands']))[:6]
        
        # 构建视觉流程
        result['visual_flow'] = ArticleAnalyzer._build_visual_flow(result)
        
        return result
    
    @staticmethod
    def _generate_filename_summary(heading: str, content_summary: str) -> str:
        """生成章节的文件名摘要（一句话缩写总结）"""
        # 移除特殊字符，简化文件名
        summary = heading.replace(' ', '_').replace('：', '_').replace(':', '_')
        summary = re.sub(r'[^\w\u4e00-\u9fa5_]', '', summary)
        # 限制长度
        return summary[:30]
    
    @staticmethod
    def _build_visual_flow(analysis: Dict) -> List[Dict]:
        """构建视觉流程图结构"""
        flow = []
        sections = analysis.get('sections', [])
        
        for i, section in enumerate(sections):
            node = {
                'id': i + 1,
                'title': section['heading'],
                'icon': ArticleAnalyzer._suggest_icon(section['heading']),
                'connections': []
            }
            
            # 添加连接关系
            if i < len(sections) - 1:
                node['connections'].append({
                    'to': i + 2,
                    'type': 'flow',
                    'label': 'next'
                })
            
            flow.append(node)
        
        return flow
    
    @staticmethod
    def _suggest_icon(heading: str) -> str:
        """根据标题建议图标"""
        icon_map = {
            '为什么': 'question_mark',
            '是什么': 'lightbulb',
            '实战': 'tools',
            '坑': 'warning',
            '场景': 'scene',
            '判断': 'target',
            '结论': 'check',
            '方案': 'solution',
            '流程': 'flow',
            '对比': 'balance'
        }
        
        for key, icon in icon_map.items():
            if key in heading:
                return icon
        
        return 'document'


class YunwuImageGenerator:
    """云雾API图像生成器 - 公众号专业版 V4"""
    
    API_BASE_URLS = [
        "https://api.openlux.ai",
        "https://api3.wai.vip",
        "https://api.openlux.ai"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("YUNWU_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 YUNWU_API_KEY 或 GEMINI_API_KEY 环境变量")
    
    # 支持通过 OpenAI Images API 生图的模型列表
    OPENAI_IMAGE_MODELS = {"gpt-image-2", "gpt-image-1", "dall-e-3"}

    def generate(
        self,
        prompt: str,
        model: str = "gpt-image-2",
        size: str = "1792x1024",
        quality: str = "standard",
        max_retries: int = 3,
        timeout: int = 300
    ) -> ImageResult:
        """生成图片

        根据模型类型自动选择最佳 API 端点：
        - gpt-image-2 / gpt-image-1 / dall-e-3 → OpenAI Images API (/v1/images/generations)
        - 其他模型（Gemini 系列等）→ 保留原有的 Gemini + OpenAI chat 双模式回退
        """

        if model in self.OPENAI_IMAGE_MODELS:
            return self._generate_via_images_api(prompt, model, size, quality, max_retries, timeout)
        else:
            return self._generate_via_dual_mode(prompt, model, size, quality, max_retries, timeout)

    def _generate_via_images_api(
        self,
        prompt: str,
        model: str,
        size: str,
        quality: str,
        max_retries: int,
        timeout: int
    ) -> ImageResult:
        """通过 OpenAI Images API 生成图片 (/v1/images/generations)"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 映射尺寸为 OpenAI Images API 支持的格式
        size_map = {
            "1792x1024": "1792x1024",
            "1024x1024": "1024x1024",
            "1024x1792": "1024x1792",
            "2350x1000": "1792x1024",  # 2.35:1 近似映射
        }
        api_size = size_map.get(size, "1792x1024")

        last_error = None
        for attempt in range(max_retries):
            for base_url in self.API_BASE_URLS:
                base_url = base_url.rstrip("/")
                api_url = f"{base_url}/v1/images/generations"
                data = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": api_size,
                    "quality": quality,
                    "response_format": "b64_json"
                }
                try:
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=data,
                        timeout=timeout
                    )
                    if response.status_code == 200:
                        result = response.json()
                        image_url = self._extract_image_url(result)
                        if image_url:
                            logger.info(f"✅ 图片生成成功！(Images API, model={model})")
                            return ImageResult(url=image_url, model=model)
                        last_error = "未在 Images API 响应中提取到图片数据"
                    else:
                        last_error = f"Images API HTTP {response.status_code}: {response.text[:300]}"
                except Exception as e:
                    last_error = str(e)
                time.sleep(1)
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)

        raise RuntimeError(f"图片生成失败 (Images API, model={model}): {last_error}")

    def _generate_via_dual_mode(
        self,
        prompt: str,
        model: str,
        size: str,
        quality: str,
        max_retries: int,
        timeout: int
    ) -> ImageResult:
        """通过 Gemini + OpenAI chat 双模式生成图片（用于非 Images API 模型）"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        last_error = None
        for attempt in range(max_retries):
            for base_url in self.API_BASE_URLS:
                base_url = base_url.rstrip("/")
                request_modes = ("gemini", "openai")
                for request_mode in request_modes:
                    if request_mode == "gemini":
                        api_url = f"{base_url}/v1beta/models/{model}:generateContent"
                        data = {
                            "contents": [
                                {
                                    "parts": [
                                        {"text": prompt}
                                    ]
                                }
                            ],
                            "generationConfig": {
                                "responseModalities": ["TEXT", "IMAGE"]
                            }
                        }
                    else:
                        api_url = f"{base_url}/v1/chat/completions"
                        data = {
                            "model": model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt}
                                    ]
                                }
                            ],
                            "temperature": 0.7
                        }
                    try:
                        response = requests.post(
                            api_url,
                            headers=headers,
                            json=data,
                            timeout=timeout
                        )
                        if response.status_code == 200:
                            result = response.json()
                            image_url = self._extract_image_url(result)
                            if image_url:
                                logger.info(f"✅ 图片生成成功！(dual mode, model={model})")
                                return ImageResult(url=image_url, model=model)
                            last_error = "未在响应中提取到图片数据"
                        else:
                            last_error = f"HTTP {response.status_code}: {response.text[:300]}"
                    except Exception as e:
                        last_error = str(e)
                    time.sleep(1)
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)

        raise RuntimeError(f"图片生成失败 (dual mode, model={model}): {last_error}")

    def _extract_url_from_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        matches = re.findall(r'https?://[^\s"\')\]]+', text)
        if matches:
            return matches[0].rstrip(".,;")
        return ""

    def _extract_image_url(self, result: Dict[str, Any]) -> str:
        # OpenAI Images API 响应: {"data": [{"b64_json": "..."} or {"url": "..."}]}
        data = result.get("data", [])
        if isinstance(data, list) and data:
            first = data[0] if isinstance(data[0], dict) else {}
            if first.get("b64_json"):
                return f"data:image/png;base64,{first['b64_json']}"
            if first.get("url"):
                return first["url"]

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
                file_data = part.get("fileData") or part.get("file_data")
                if isinstance(file_data, dict) and file_data.get("fileUri"):
                    return file_data["fileUri"]
                if isinstance(part.get("text"), str):
                    text_url = self._extract_url_from_text(part["text"])
                    if text_url:
                        return text_url

        choices = result.get("choices", [])
        for choice in choices:
            message = choice.get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                text_url = self._extract_url_from_text(content)
                if text_url:
                    return text_url
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    image_url = item.get("image_url")
                    if isinstance(image_url, dict) and image_url.get("url"):
                        return image_url["url"]
                    if isinstance(item.get("url"), str):
                        return item["url"]
                    if isinstance(item.get("b64_json"), str):
                        return f"data:image/png;base64,{item['b64_json']}"
                    if isinstance(item.get("text"), str):
                        text_url = self._extract_url_from_text(item["text"])
                        if text_url:
                            return text_url

        if isinstance(result.get("b64_json"), str):
            return f"data:image/png;base64,{result['b64_json']}"

        return ""
    
    def generate_impactful_cover(
        self,
        title: str,
        brands: List[str] = None,
        core_concept: str = "",
        model: str = "gpt-image-2",
        include_brand_logos: bool = False,
        palette: Optional[str] = None,
        rendering: Optional[str] = None
    ) -> ImageResult:
        """
        生成高冲击力封面图
        
        特点：
        - 强烈视觉冲击力
        - 可选使用官方品牌Logo/图标（默认不包含）
        - 专业级视觉效果
        - 强制中文输出，确保文字清晰可读
        - 支持自定义配色和渲染风格
        
        Args:
            include_brand_logos: 是否在封面中包含品牌Logo，默认为False
            palette: 配色方案（如 warm, cool, elegant 等）
            rendering: 渲染风格（如 hand-drawn, digital, flat-vector 等）
        """
        
        # 构建品牌元素描述（仅在明确要求时添加）
        brand_elements = ""
        
        if include_brand_logos and brands:
            brand_list = ", ".join(brands[:4])
            brand_elements = f"""
BRAND ELEMENTS (Optional - Only if relevant to article):
- Featured brands: {brand_list}
- Display official brand logos/icons subtly and professionally
- Use recognizable brand colors and visual identity
- Position brand elements in balanced composition
- Logos must be sharp, professional, and instantly recognizable
"""
        else:
            brand_elements = """
BRAND ELEMENTS:
- NO brand logos or brand-specific icons
- Focus on abstract visual metaphors and concepts
- Use universal symbols and imagery
- Keep design clean and brand-neutral
"""
        strategy = select_cover_strategy(
            title=title,
            brands=brands or [],
            core_concept=core_concept,
            palette=palette,
            rendering=rendering
        )
        seed = build_seed(title)
        
        prompt = f"""创建一张高冲击力的微信公众号封面图，具有震撼的视觉效果。

【主标题】（核心元素）
标题："{title}"

{brand_elements}

【推荐视觉策略】
- 调色策略：{strategy['palette']}
- 渲染策略：{strategy['rendering']}
- 构图策略：{strategy['composition']}
- 表达重点：{strategy['focus']}
- 生成随机种子：{seed}

【画面简洁策略】
- 单一主视觉主体，不堆叠多个主题
- 仅保留主标题，不添加多段说明文字
- 不重复同一图标、同一短语或同类装饰
- 保持干净背景，留白适中

【设计规范】
- 比例：2.35:1电影级超宽画幅
- 分辨率：8K超高清
- 风格：高级专业插画，现代美学
- 背景：动态渐变或抽象科技图案
- 深度：分层元素创造视觉深度
- 除非明确要求，否则不包含品牌Logo

【标题处理】
- 位置：画面中央或中顶部
- 字数：尽量短，建议不超过14个汉字
- 字体：粗体，现代中文字体
- 颜色：与背景高对比

【中文文字要求】（极其重要）
- 标题"{title}"必须清晰、有冲击力、100%可读
- 使用标准简体中文，禁止变形、重影、乱码
- 每个汉字边缘清晰，笔画完整，不粘连
- 若文字质量不足，必须重生成直到清晰

【强制要求】
- 所有文字必须使用简体中文
- 绝对禁止出现英文文字
- 绝对禁止出现乱码或无法识别的字符
- 绝对禁止出现拼音代替中文

【禁止事项】
- 绝对禁止出现任何动物图案，特别是龙虾、小龙虾、鳌虾等
- 禁止出现与主题无关的元素
- 禁止出现模糊或无法辨认的文字
- 禁止出现英文或混合语言

输出：一张高冲击力但简洁干净的封面图，聚焦单一主题，不重复元素。除非明确要求，否则不包含品牌Logo。中文文字清晰无重影、无变形、无乱码。"""
        
        return self.generate(prompt=prompt, model=model, size="1792x1024", quality="standard")
    
    def generate_advanced_infographic(
        self,
        analysis: Dict[str, Any],
        model: str = "gpt-image-2",
        layout: Optional[str] = None,
        style: Optional[str] = None
    ) -> ImageResult:
        """
        生成高级信息图 - 完整覆盖全文，复杂深度结构，强化逻辑关联
        
        特点：
        - 完整覆盖全文所有核心内容
        - 复杂的层级结构
        - 清晰的逻辑关联和流向
        - 丰富的专业图标
        - 深度信息展示，信息密度最大化
        - 强制中文输出，确保内容与文章高度相关
        - 支持自定义布局和视觉风格
        
        Args:
            layout: 布局类型（如 dense-modules, hub-spoke 等）
            style: 视觉风格（如 craft-handmade, morandi-journal 等）
        """
        
        title = analysis.get('title', '文章主题')
        sections = analysis.get('sections', [])
        brands = analysis.get('brands', [])
        visual_flow = analysis.get('visual_flow', [])
        full_content_summary = analysis.get('full_content_summary', '')
        layout_strategy = select_infographic_layout(analysis, layout=layout, style=style)
        seed = build_seed(title, layout_strategy["layout"])
        
        # 构建章节结构描述（包含所有章节，而不仅是前6个）
        section_structure = []
        for i, section in enumerate(sections, 1):
            heading = section.get('heading', f'节点{i}')
            points = section.get('points', [])[:3]  # 每个章节展示3个要点
            content_summary = section.get('content_summary', '')
            icon = section.get('icon', 'document')
            section_structure.append(f"""
Node {i}: {heading}
- Icon: {icon}
- Summary: {content_summary}
- Key points: {'; '.join(points) if points else 'Core concept'}
- Connections: Flows to next node""")
        
        # 构建品牌元素 - 只有文章明确提到品牌时才展示
        brand_section = ""
        
        if brands and len(brands) > 0:
            # 文章明确提到了品牌，可以展示
            brand_section = f"""
BRAND INTEGRATION:
- Featured brands: {', '.join(brands[:4])}
- Display brand logos ONLY for these mentioned brands
- Use brand colors consistently throughout
- Connect brands with visual flow elements"""
        else:
            # 文章未提及品牌，不展示任何品牌Logo
            brand_section = """
BRAND ELEMENTS:
- NO brand logos or brand-specific icons
- Keep design brand-neutral and professional
- Focus on the article content, not external brands"""
        
        prompt = f"""创建一张高级多层信息图，完整覆盖全文所有核心内容，具有复杂结构和深度逻辑关联。

【标题】
{title}

【全文摘要】
{full_content_summary}

{brand_section}

【推荐信息图策略】
- 布局类型：{layout_strategy['layout']}
- 布局规则：{layout_strategy['rule']}
- 生成随机种子：{seed}

【结构】（层级化和互联 - 包含所有章节）
{chr(10).join(section_structure)}

【关键要求】：这张信息图必须完整覆盖整篇文章，并保持结构清晰、模块不重复、视觉整洁。

【高级设计要求】

1. 复杂结构：
- 多层布局：一级、二级、三级层次
- 中心枢纽+辐射连接（中心辐射模型）
- 或：顺序流+分支决策点
- 深度：创建3D般分层，使用阴影和重叠
- 必须包含所有文章章节，无例外

2. 逻辑关联（关键）：
- 清晰的视觉流向箭头展示关系
- 颜色编码连接类型（实线=直接，虚线=间接，点线=可选）
- 连接线标签解释关系
- 视觉层次：主线粗线，次要线细线

3. 专业图标（丰富的视觉语言）：
- 每个章节有独特、有意义的图标
- 图标风格：统一线稿或填充风格
- 图标大小：足够大以识别（占模块10-15%）
- 图标含义：直接与章节内容相关
- 使用与内容相关的图标，而非品牌Logo（除非提到品牌）

4. 信息架构（高密度但有序）：
- 标题层：文章标题
- 一级：主章节（大、突出）
- 二级：关键要点（中等、支持）
- 三级：详情/数据（小、补充）
- 视觉连接器展示所有层级间关系
- 避免重复模块与重复表述，信息集中但不拥挤

5. 高级视觉元素：
- 章节内渐变背景
- 微妙纹理或图案叠加
- 投射阴影创造深度
- 关键点发光强调
- 数据可视化：迷你图表、进度条、指标
- 重要高亮的徽章元素
- 利用每一寸可用空间展示信息

【布局】（16:9 - 精致网格）
- 标题区：8% - 清晰排版的标题
- 主内容区：84% - 复杂互联网格
  * 2-3列，宽度各异
  * 不对称平衡，视觉趣味
  * 重叠元素创造深度
  * 保持模块边界清晰，避免挤压文字
- 底部区：8% - 关键要点+支持图标

【配色与风格】
- 精致配色：深蓝、活力强调色、中性背景
- 手绘风格+专业打磨
- 统一笔画粗细，变化强调
- 高对比确保可读性
- 高信息密度与高可读性平衡

【中文文字要求】（专业排版 - 极其重要）
- 层级字体大小：标题(100%) > 章节(70%) > 要点(50%) > 详情(40%)
- 所有文字必须是清晰、完美的简体中文
- 对乱码字符、模糊文字、无法识别的字符零容忍
- 便利贴、对话框、卡片、标签上的每个字符都必须是清晰可读的中文
- 如果是手写风格文字，保持清晰可读，避免潦草变形
- 所有章节标题文字、要点文字、说明文字都必须清晰可读
- 所有章节关键要点可见且清晰，避免重复句子
- 如果发现任何文字模糊或乱码，立即重新生成直到100%清晰可读

【强制要求】
- 所有文字必须使用简体中文
- 绝对禁止出现英文文字
- 绝对禁止出现乱码或无法识别的字符
- 绝对禁止出现拼音代替中文

【禁止事项】
- 绝对禁止出现任何动物图案，特别是龙虾、小龙虾、鳌虾等
- 禁止出现与主题无关的元素
- 禁止出现模糊或无法辨认的文字
- 禁止出现英文或混合语言

输出：一张精致、多层但干净的信息图，完整覆盖整篇文章，逻辑清晰、模块不重复、中文文字清晰无重影无乱码。"""
        
        return self.generate(prompt=prompt, model=model, size="1792x1024", quality="standard")
    
    def download_image(self, url: str, save_path: str) -> str:
        """下载图片"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(url, str) and url.startswith("data:image"):
            header, encoded = url.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            with open(save_path, "wb") as f:
                f.write(image_bytes)
        else:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
        
        logger.info(f"✅ 图片已下载: {save_path}")
        return str(save_path)


def add_watermark(image_path: str, watermark_text: str = "AI朱朱侠") -> str:
    """
    为图片添加水印
    
    Args:
        image_path: 图片路径
        watermark_text: 水印文字，默认为"AI朱朱侠"
        
    Returns:
        处理后的图片路径
    """
    try:
        img = Image.open(image_path)
        original_mode = img.mode

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        elif img.mode == "RGB":
            img = img.convert("RGBA")

        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        font_size = max(14, int(img_height * 0.022))

        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except Exception:
                    continue
        if font is None:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        margin = max(16, int(img_width * 0.015))
        x = img_width - text_width - margin
        y = margin

        padding = max(6, int(font_size * 0.35))
        bg_x1 = x - padding
        bg_y1 = y - padding
        bg_x2 = x + text_width + padding
        bg_y2 = y + text_height + padding

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [bg_x1, bg_y1, bg_x2, bg_y2],
            radius=max(4, int(font_size * 0.2)),
            fill=(255, 255, 255, 138)
        )
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)
        draw.text((x, y), watermark_text, font=font, fill=(68, 68, 68, 220))

        if original_mode == "RGBA":
            img.save(image_path, "PNG", compress_level=4)
        else:
            img = img.convert("RGB")
            img.save(image_path, "PNG", optimize=True)

        logger.info(f"✅ 水印已添加: {watermark_text}")
        return image_path
    except Exception as e:
        logger.warning(f"⚠️ 添加水印失败，保留原图: {e}")
        return image_path


def download_image_with_watermark(
    generator: 'YunwuImageGenerator',
    url: str,
    save_path: str,
    watermark_text: str = "AI朱朱侠"
) -> str:
    """
    下载图片并添加水印
    
    Args:
        generator: YunwuImageGenerator实例
        url: 图片URL
        save_path: 保存路径
        watermark_text: 水印文字
        
    Returns:
        处理后的图片路径
    """
    # 先下载图片
    generator.download_image(url, save_path)
    
    # 添加水印
    return add_watermark(save_path, watermark_text)


def find_article_folder(article_path: Path) -> Optional[Path]:
    """
    自动检测文章文件夹
    
    检测逻辑：
    1. 如果文章本身就在 YYYYMMDDHHMM-标题/ 文件夹内，直接返回该文件夹
    2. 如果文章在根目录，查找是否存在匹配的 YYYYMMDDHHMM-标题/ 文件夹
    3. 如果都不存在，返回None
    
    Args:
        article_path: 文章文件路径
        
    Returns:
        文章文件夹路径，如果不存在则返回None
    """
    import re
    from datetime import datetime
    
    article_path = Path(article_path)
    parent_dir = article_path.parent
    
    # 模式：YYYYMMDDHHMM-标题
    folder_pattern = re.compile(r'^\d{12}-.+$')
    
    # 情况1：文章已经在 YYYYMMDDHHMM-标题/ 文件夹内
    if folder_pattern.match(parent_dir.name):
        logger.info(f"✅ 检测到文章已在文件夹内: {parent_dir.name}")
        return parent_dir
    
    # 情况2：文章在根目录，查找匹配的文件夹
    # 从文章标题提取关键词
    article_title = article_path.stem  # 文件名（不含扩展名）
    
    # 查找所有匹配模式的文件夹
    candidate_folders = []
    for item in parent_dir.iterdir():
        if item.is_dir() and folder_pattern.match(item.name):
            # 检查文件夹名是否包含文章标题的关键词
            folder_title = item.name.split('-', 1)[1] if '-' in item.name else item.name
            # 简单匹配：文件夹标题和文章标题有重叠
            if folder_title in article_title or article_title in folder_title:
                candidate_folders.append(item)
    
    if candidate_folders:
        # 如果有多个候选，选择最新的
        candidate_folders.sort(key=lambda x: x.name, reverse=True)
        selected = candidate_folders[0]
        logger.info(f"✅ 找到匹配的文章文件夹: {selected.name}")
        return selected
    
    # 情况3：没有找到现有文件夹，创建新的
    logger.info(f"⚠️ 未找到现有文章文件夹，将创建新的")
    return None


def generate_article_images(
    article_path: str,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-image-2",
    cover_palette: Optional[str] = None,
    cover_rendering: Optional[str] = None,
    infographic_layout: Optional[str] = None,
    infographic_style: Optional[str] = None
) -> Dict[str, str]:
    """
    从文章生成高级配图 - V4版（中文优化版）
    
    生成：
    1. 高冲击力封面图（强制中文输出）
    2. 高级信息图（复杂深度结构，强化逻辑关联，内容与文章高度相关）
    3. 章节配图（基于文章实际内容生成，确保内容相关性）
    
    关键改进：
    - 默认使用 gpt-image-2 模型，成本更低
    - 所有提示词使用中文，强制输出简体中文
    - 章节配图基于文章实际内容生成，确保与章节主题高度相关
    - 添加内容关联性检查，避免生成与文章无关的通用图片
    - 支持自定义封面图和信息图风格
    
    自动检测文章文件夹：
    - 如果文章在 YYYYMMDDHHMM-标题/ 文件夹内，图片保存到该文件夹的 images/ 子目录
    - 如果文章在根目录，查找匹配的文章文件夹
    - 如果都不存在，在文章同级创建 images/ 目录
    
    Args:
        article_path: 文章文件路径
        output_dir: 输出目录（可选）
        api_key: API密钥（可选）
        model: 使用的模型（默认 gpt-image-2）
        cover_palette: 封面图配色方案（如 warm, cool, elegant 等）
        cover_rendering: 封面图渲染风格（如 hand-drawn, digital 等）
        infographic_layout: 信息图布局（如 dense-modules, hub-spoke 等）
        infographic_style: 信息图视觉风格（如 craft-handmade, morandi-journal 等）
    """
    article_path = Path(article_path)
    if not article_path.exists():
        raise FileNotFoundError(f"文章文件不存在: {article_path}")
    
    # 读取并分析文章
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analyzer = ArticleAnalyzer()
    analysis = analyzer.extract_content_and_brands(content)
    
    logger.info(f"文章分析完成：")
    logger.info(f"  - 标题: {analysis.get('title', 'N/A')}")
    logger.info(f"  - 识别品牌: {analysis.get('brands', [])}")
    logger.info(f"  - 章节数: {len(analysis.get('sections', []))}")
    logger.info(f"  - 视觉流程节点: {len(analysis.get('visual_flow', []))}")
    
    # 确定输出目录（自动检测文章文件夹）
    if output_dir:
        output_dir = Path(output_dir)
        logger.info(f"使用指定的输出目录: {output_dir}")
    else:
        # 自动检测文章文件夹
        article_folder = find_article_folder(article_path)
        if article_folder:
            output_dir = article_folder / "images"
            logger.info(f"检测到文章文件夹，图片将保存到: {output_dir}")
        else:
            # 没有找到文章文件夹，在文章同级创建 images/
            output_dir = article_path.parent / "images"
            logger.info(f"未找到文章文件夹，图片将保存到: {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ 输出目录已创建: {output_dir}")
    
    generator = YunwuImageGenerator(api_key=api_key)
    results = {}
    
    # 1. 生成高冲击力封面图
    logger.info("\n" + "="*60)
    logger.info("生成高冲击力封面图（无品牌Logo，简洁设计）...")
    if cover_palette or cover_rendering:
        logger.info(f"封面图风格: 配色={cover_palette or '自动'}, 渲染={cover_rendering or '自动'}")
    logger.info("="*60)
    
    try:
        cover_result = generator.generate_impactful_cover(
            title=analysis.get('title', '文章标题'),
            brands=analysis.get('brands', []),
            core_concept=analysis.get('key_concepts', [''])[0] if analysis.get('key_concepts') else '',
            model=model,
            include_brand_logos=False,  # 默认不包含品牌Logo
            palette=cover_palette,
            rendering=cover_rendering
        )
        
        cover_path = output_dir / "cover.png"
        download_image_with_watermark(generator, cover_result.url, str(cover_path))
        results['封面图'] = str(cover_path)
        logger.info(f"✅ 封面图已保存: {cover_path}")
    except Exception as e:
        logger.error(f"❌ 封面图生成失败: {e}")
        results['封面图'] = ""
    
    time.sleep(3)
    
    # 2. 生成高级信息图（16:9横版）
    logger.info("\n" + "="*60)
    logger.info("生成高级信息图（复杂深度结构，强化逻辑关联）...")
    if infographic_layout or infographic_style:
        logger.info(f"信息图风格: 布局={infographic_layout or '自动'}, 风格={infographic_style or '自动'}")
    logger.info("="*60)

    try:
        infographic_result = generator.generate_advanced_infographic(
            analysis=analysis,
            model=model,
            layout=infographic_layout,
            style=infographic_style
        )
        
        infographic_path = output_dir / "infographic.png"
        download_image_with_watermark(generator, infographic_result.url, str(infographic_path))
        results['信息图'] = str(infographic_path)
        logger.info(f"✅ 信息图已保存: {infographic_path}")
    except Exception as e:
        logger.error(f"❌ 信息图生成失败: {e}")
        results['信息图'] = ""
    
    time.sleep(3)
    
    # 3. 生成章节配图（16:9横版，复杂信息展示，无"章节X"标题）
    sections = analysis.get('sections', [])
    if sections:
        logger.info("\n" + "="*60)
        logger.info(f"生成章节配图（共{len(sections)}张，16:9横版，复杂信息展示）...")
        logger.info("="*60)
        
        # 根据文章实际章节数量动态生成配图（不再限制为5张）
        section_count = len(sections)
        
        for i, section in enumerate(sections[:section_count]):
            section_heading = section.get('heading', f'主题{i+1}')
            section_points = section.get('points', [])
            content_summary = section.get('content_summary', section_heading)
            file_name_summary = section.get('file_name_summary', f'主题{i+1}')
            full_content = section.get('full_content', [])
            section_style = select_section_style(section_heading, section_points, i)
            section_seed = build_seed(analysis.get('title', ''), section_heading)
            
            logger.info(f"\n生成章节配图 {i+1}/{section_count}: {content_summary}")
            
            try:
                # 构建章节配图提示词（16:9横版，复杂信息展示，无"章节X"标题）
                # 提取章节核心内容，确保图片与文章高度相关
                section_prompt = f"""创建一张干净整洁的章节配图，必须与文章章节内容高度相关。

【章节主题】（必须与文章一致）
{section_heading}

【必须展示的核心内容】（基于文章实际内容）
"""
                # 添加核心要点
                for j, point in enumerate(section_points[:6]):
                    section_prompt += f"{j+1}. {point}\n"
                
                # 添加额外的内容摘要
                if full_content:
                    section_prompt += f"\n【补充内容】\n{' '.join(full_content[:3])}\n"
                
                section_prompt += f"""
【视觉元素要求】（必须与内容相关）
- 必须包含的视觉元素：与"{section_heading}"主题直接相关的图标和插图
- 必须展示的场景：文章中描述的具体场景或流程
- 必须体现的关系：章节中的逻辑关系、对比关系或递进关系

【推荐生成策略】
- 风格方向：{section_style['style']}
- 布局类型：{section_style['layout']}
- 视觉关键词：{section_style['key']}
- 生成随机种子：{section_seed}

【视觉风格】
- 整体风格：{section_style['style']}，简洁专业
- 线条特征：清晰、克制、层级分明
- 配色方案：低饱和主色+1个强调色
- 背景色：干净浅色背景

【布局结构】（16:9横版）
- 标题区：顶部简洁标题，不超过14字
- 主内容区：3个信息卡片以内，使用布局模板 {section_style['layout']}
- 视觉元素：1个主视觉 + 2~3个辅助图标
- 留白区：保留15%-20%留白，保证干净整洁

【信息密度要求】
- 仅保留本章节最核心的3个要点
- 禁止重复同义句、重复图标、重复装饰
- 不使用拥挤拼贴、过多图表、过多文本框

【文字要求】（极其重要！绝对不能忽略！）
- 标题："{section_heading}"
- 所有文字必须使用标准、清晰的简体中文
- 绝对禁止出现英文文字
- 绝对禁止出现任何乱码、模糊不清的文字、或无法辨认的字符
- 每个卡片、标签上的文字都必须是清晰可认的中文
- 禁止文字重影、字符粘连、笔画断裂、错别字乱码
- 字体层级：主标题 > 要点 > 说明
- 标题醒目，正文简短，单卡片文字不超过两行

【强制要求】
- 所有文字必须使用简体中文
- 绝对禁止出现英文文字
- 绝对禁止出现乱码或无法识别的字符
- 绝对禁止出现拼音代替中文

【禁止事项】
- 禁止使用"章节X"、"Section X"、"Part X"等标题
- 禁止出现与"{section_heading}"主题无关的元素（如动物、龙虾等）
- 禁止出现模糊或无法辨认的文字
- 禁止出现英文或混合语言
- 禁止出现与文章内容无关的通用图标或插图

【主题相关性要求】
- 图片必须与"{section_heading}"主题高度相关
- 优先展示概念关系，不堆叠细节数据
- 除信息图外，此图保持中低信息密度

【质量检查】
- 图片标题是否与"{section_heading}"一致？
- 图片是否展示了章节的核心观点？
- 图片中的文字是否都是简体中文？
- 图片视觉元素是否与"{section_heading}"主题相关？
- 如果发现任何问题，必须立即重新生成"""
                
                section_result = generator.generate(
                    prompt=section_prompt,
                    model=model,
                    size="1792x1024",  # 16:9横版
                    quality="standard"
                )
                
                # 使用内容摘要作为文件名（一句话缩写总结）
                safe_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name_summary)
                section_path = output_dir / f"{i+1:02d}-{safe_file_name[:30]}.png"
                download_image_with_watermark(generator, section_result.url, str(section_path))
                results[f'章节配图{i+1}'] = str(section_path)
                logger.info(f"✅ 章节配图已保存: {section_path}")
                
            except Exception as e:
                logger.error(f"❌ 章节配图{i+1}生成失败: {e}")
                results[f'章节配图{i+1}'] = ""
            
            time.sleep(3)
    
    success_count = len([v for v in results.values() if v])
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ 配图生成完成！成功: {success_count}/{len(results)}")
    logger.info(f"{'='*60}\n")
    
    return results


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='云雾API图像生成器 - 公众号专业版 V4')
    parser.add_argument('--article', help='从文章Markdown文件生成配图')
    parser.add_argument('--output-dir', help='指定输出目录（默认: 文章目录/images）')
    parser.add_argument('-k', '--api-key', help='云雾API密钥')
    parser.add_argument('-m', '--model', default='gpt-image-2', help='模型名称')

    # 封面图风格参数
    parser.add_argument('--cover-palette', help='封面图配色方案 (warm, cool, elegant, dark, earth, vivid, pastel, mono, retro, duotone)')
    parser.add_argument('--cover-rendering', help='封面图渲染风格 (flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print)')

    # 信息图风格参数
    parser.add_argument('--infographic-layout', help='信息图布局 (dense-modules, hub-spoke, comparison-matrix, linear-progression, hierarchical-layers, bento-grid)')
    parser.add_argument('--infographic-style', help='信息图视觉风格 (craft-handmade, morandi-journal, pop-laboratory, corporate-memphis, chalkboard, technical-schematic)')

    args = parser.parse_args()

    if args.article:
        try:
            results = generate_article_images(
                article_path=args.article,
                output_dir=args.output_dir,
                api_key=args.api_key,
                model=args.model,
                cover_palette=args.cover_palette,
                cover_rendering=args.cover_rendering,
                infographic_layout=args.infographic_layout,
                infographic_style=args.infographic_style
            )
            print(f"\n生成结果:")
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
