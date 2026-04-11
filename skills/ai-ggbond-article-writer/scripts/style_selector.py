#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配图风格选择器
用于在生成封面图和信息图之前进行风格选择
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class StyleOption:
    """风格选项"""
    name: str
    cover_palette: str
    cover_rendering: str
    infographic_layout: str
    infographic_style: str
    description: str
    best_for: str


# 预定义的风格组合
STYLE_PRESETS = {
    "warm-handmade": StyleOption(
        name="温暖手作风",
        cover_palette="warm",
        cover_rendering="hand-drawn",
        infographic_layout="bento-grid",
        infographic_style="craft-handmade",
        description="温暖亲切的手绘风格，适合个人故事、生活方式类文章",
        best_for="个人成长、生活方式、情感类内容"
    ),
    "tech-blueprint": StyleOption(
        name="科技蓝图风",
        cover_palette="cool",
        cover_rendering="digital",
        infographic_layout="structural-breakdown",
        infographic_style="technical-schematic",
        description="专业冷静的科技感，适合技术架构、系统分析类文章",
        best_for="技术教程、架构设计、产品分析"
    ),
    "elegant-minimal": StyleOption(
        name="优雅极简风",
        cover_palette="elegant",
        cover_rendering="flat-vector",
        infographic_layout="hierarchical-layers",
        infographic_style="corporate-memphis",
        description="简洁优雅的商务风格，适合专业观点、行业分析类文章",
        best_for="商业分析、行业观察、专业观点"
    ),
    "creative-journal": StyleOption(
        name="创意手帐风",
        cover_palette="earth",
        cover_rendering="hand-drawn",
        infographic_layout="dense-modules",
        infographic_style="morandi-journal",
        description="温馨可爱的手帐风格，适合产品指南、教程类文章",
        best_for="产品指南、使用教程、消费决策"
    ),
    "lab-precision": StyleOption(
        name="实验室精准风",
        cover_palette="mono",
        cover_rendering="digital",
        infographic_layout="comparison-matrix",
        infographic_style="pop-laboratory",
        description="精准专业的实验室风格，适合对比评测、数据分析类文章",
        best_for="产品对比、数据分析、规格评测"
    ),
    "retro-vintage": StyleOption(
        name="复古怀旧风",
        cover_palette="retro",
        cover_rendering="screen-print",
        infographic_layout="linear-progression",
        infographic_style="retro-pop-grid",
        description="复古怀旧的印刷风格，适合历史回顾、文化类文章",
        best_for="历史回顾、文化分析、复古主题"
    ),
}


# 封面图配色方案详解
COVER_PALETTES = {
    "warm": {"name": "暖色调", "colors": "暖橙、珊瑚、米色", "mood": "友好、亲切、生活化"},
    "elegant": {"name": "优雅色", "colors": "深蓝、金、灰", "mood": "商务、专业、高端"},
    "cool": {"name": "冷色调", "colors": "蓝、青、灰", "mood": "技术、冷静、理性"},
    "dark": {"name": "深色", "colors": "深色、霓虹", "mood": "娱乐、高端、电影感"},
    "earth": {"name": "大地色", "colors": "绿、棕、米", "mood": "自然、健康、环保"},
    "vivid": {"name": "鲜艳色", "colors": "高饱和多彩", "mood": "活力、创意、年轻"},
    "pastel": {"name": "粉彩色", "colors": "柔和粉彩", "mood": "幻想、儿童、柔和"},
    "mono": {"name": "单色", "colors": "黑白灰", "mood": "禅意、专注、极简"},
    "retro": {"name": "复古色", "colors": "复古色调", "mood": "怀旧、经典、历史"},
    "duotone": {"name": "双色调", "colors": "两种对比色", "mood": "戏剧、冲击、对比"},
}

# 封面图渲染风格详解
COVER_RENDERINGS = {
    "flat-vector": {"name": "扁平矢量", "characteristics": "干净线条，无纹理，几何形状", "feel": "现代、科技"},
    "hand-drawn": {"name": "手绘风格", "characteristics": "素描质感，抖动线条，温暖", "feel": "个人、随性"},
    "painterly": {"name": "水彩画风", "characteristics": "水彩质感，柔和边缘，梦幻", "feel": "艺术、创意"},
    "digital": {"name": "数字风格", "characteristics": "光滑渐变，3D效果，精致", "feel": "数据、企业"},
    "pixel": {"name": "像素风格", "characteristics": "8位像素，复古游戏风", "feel": "游戏、复古"},
    "chalk": {"name": "粉笔风格", "characteristics": "粉笔质感，黑板背景", "feel": "教育、教程"},
    "screen-print": {"name": "丝网印刷", "characteristics": "海报艺术，半调纹理，有限色彩", "feel": "复古、艺术"},
}

# 信息图布局详解
INFOGRAPHIC_LAYOUTS = {
    "linear-progression": {"name": "线性流程", "description": "时间线、流程、教程", "shape": "横向或纵向顺序排列"},
    "binary-comparison": {"name": "二元对比", "description": "A vs B、前后对比", "shape": "左右分屏对比"},
    "comparison-matrix": {"name": "对比矩阵", "description": "多因素对比", "shape": "表格或网格形式"},
    "hierarchical-layers": {"name": "层级结构", "description": "金字塔、优先级", "shape": "从上到下层级递减"},
    "tree-branching": {"name": "树状分支", "description": "分类、层级结构", "shape": "树状图形式"},
    "hub-spoke": {"name": "中心辐射", "description": "中心概念+关联项", "shape": "中心节点+辐射分支"},
    "structural-breakdown": {"name": "结构分解", "description": "分解图、截面图", "shape": "分层展示内部结构"},
    "bento-grid": {"name": "便当网格", "description": "多主题概览", "shape": "模块化网格布局"},
    "dense-modules": {"name": "高密度模块", "description": "高密度信息展示", "shape": "紧凑排列的模块"},
}

# 信息图风格详解
INFOGRAPHIC_STYLES = {
    "craft-handmade": {"name": "手工纸艺", "description": "手工纸艺感，温暖亲切", "best_for": "通用、教育"},
    "morandi-journal": {"name": "莫兰迪手帐", "description": "柔和莫兰迪色调，手帐风格", "best_for": "产品指南、生活方式"},
    "pop-laboratory": {"name": "实验室", "description": "蓝图网格实验室风，专业精准", "best_for": "技术指南、规格对比"},
    "corporate-memphis": {"name": "商务孟菲斯", "description": "扁平矢量商务风，现代简洁", "best_for": "企业、专业"},
    "chalkboard": {"name": "黑板", "description": "黑板粉笔风，教育感强", "best_for": "教程、知识分享"},
    "technical-schematic": {"name": "技术蓝图", "description": "工程蓝图风，技术感强", "best_for": "技术架构、系统设计"},
    "retro-pop-grid": {"name": "复古波普", "description": "70年代波普网格，复古感", "best_for": "对比评测、复古主题"},
}


class StyleSelector:
    """风格选择器"""
    
    @staticmethod
    def analyze_article(content: str) -> Dict[str, Any]:
        """分析文章内容，提取特征"""
        content_lower = content.lower()
        
        # 检测内容类型
        content_signals = {
            "technical": ["架构", "系统", "框架", "api", "代码", "技术", "工程", "设计模式"],
            "lifestyle": ["生活", "日常", "习惯", "健康", "美食", "旅行", "家居"],
            "business": ["商业", "市场", "战略", "管理", "运营", "增长", "商业模式"],
            "tutorial": ["教程", "指南", "步骤", "如何", "怎么做", "入门", "新手"],
            "review": ["评测", "对比", "哪个好", "推荐", "选择", "选购"],
            "story": ["故事", "经历", "复盘", "成长", " journey", "体验"],
        }
        
        scores = {}
        for content_type, keywords in content_signals.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            scores[content_type] = score
        
        primary_type = max(scores, key=scores.get) if max(scores.values()) > 0 else "general"
        
        # 检测情感基调
        emotion_signals = {
            "professional": ["分析", "研究", "报告", "数据", "趋势", "洞察"],
            "warm": ["分享", "感悟", "心得", "体会", "温暖", "治愈"],
            "energetic": ["突破", "创新", "革命", "颠覆", "震撼", "惊艳"],
            "calm": ["思考", "沉淀", "静下心", "慢慢来", "长期"],
        }
        
        emotion_scores = {}
        for emotion, keywords in emotion_signals.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            emotion_scores[emotion] = score
        
        primary_emotion = max(emotion_scores, key=emotion_scores.get) if max(emotion_scores.values()) > 0 else "neutral"
        
        return {
            "content_type": primary_type,
            "emotion": primary_emotion,
            "has_comparison": any(kw in content_lower for kw in ["对比", "vs", "versus", "区别", "差异"]),
            "has_timeline": any(kw in content_lower for kw in ["时间线", "历史", "发展", "演变", "阶段"]),
            "has_data": any(kw in content_lower for kw in ["数据", "统计", "百分比", "%", "增长", "下降"]),
        }
    
    @staticmethod
    def recommend_styles(analysis: Dict[str, Any]) -> List[StyleOption]:
        """基于文章分析推荐风格组合"""
        content_type = analysis.get("content_type", "general")
        emotion = analysis.get("emotion", "neutral")
        has_comparison = analysis.get("has_comparison", False)
        has_timeline = analysis.get("has_timeline", False)
        
        recommendations = []
        
        # 根据内容类型推荐
        if content_type == "technical":
            recommendations.extend([
                STYLE_PRESETS["tech-blueprint"],
                STYLE_PRESETS["lab-precision"],
            ])
        elif content_type == "lifestyle":
            recommendations.extend([
                STYLE_PRESETS["creative-journal"],
                STYLE_PRESETS["warm-handmade"],
            ])
        elif content_type == "business":
            recommendations.extend([
                STYLE_PRESETS["elegant-minimal"],
                STYLE_PRESETS["tech-blueprint"],
            ])
        elif content_type == "tutorial":
            recommendations.extend([
                STYLE_PRESETS["creative-journal"],
                STYLE_PRESETS["warm-handmade"],
            ])
        elif content_type == "review" or has_comparison:
            recommendations.extend([
                STYLE_PRESETS["lab-precision"],
                STYLE_PRESETS["elegant-minimal"],
            ])
        elif content_type == "story":
            recommendations.extend([
                STYLE_PRESETS["warm-handmade"],
                STYLE_PRESETS["creative-journal"],
            ])
        else:
            recommendations.extend([
                STYLE_PRESETS["warm-handmade"],
                STYLE_PRESETS["elegant-minimal"],
            ])
        
        # 去重并确保至少有3个推荐
        unique_recommendations = []
        seen_names = set()
        for style in recommendations:
            if style.name not in seen_names:
                unique_recommendations.append(style)
                seen_names.add(style.name)
        
        # 如果推荐不足3个，补充通用风格
        if len(unique_recommendations) < 3:
            for key in ["warm-handmade", "elegant-minimal", "creative-journal"]:
                if STYLE_PRESETS[key].name not in seen_names:
                    unique_recommendations.append(STYLE_PRESETS[key])
                    if len(unique_recommendations) >= 3:
                        break
        
        return unique_recommendations[:3]
    
    @staticmethod
    def get_style_details(style_key: str) -> Dict[str, Any]:
        """获取风格详情"""
        if style_key not in STYLE_PRESETS:
            return {}
        
        preset = STYLE_PRESETS[style_key]
        return {
            "name": preset.name,
            "cover": {
                "palette": preset.cover_palette,
                "palette_name": COVER_PALETTES.get(preset.cover_palette, {}).get("name", preset.cover_palette),
                "rendering": preset.cover_rendering,
                "rendering_name": COVER_RENDERINGS.get(preset.cover_rendering, {}).get("name", preset.cover_rendering),
            },
            "infographic": {
                "layout": preset.infographic_layout,
                "layout_name": INFOGRAPHIC_LAYOUTS.get(preset.infographic_layout, {}).get("name", preset.infographic_layout),
                "style": preset.infographic_style,
                "style_name": INFOGRAPHIC_STYLES.get(preset.infographic_style, {}).get("name", preset.infographic_style),
            },
            "description": preset.description,
            "best_for": preset.best_for,
        }
    
    @staticmethod
    def format_style_recommendation(title: str, recommendations: List[StyleOption]) -> str:
        """格式化风格推荐文本"""
        lines = [
            f"基于对文章《{title}》的分析，我推荐以下配图风格：\n",
            "【推荐风格组合】\n",
        ]
        
        for i, style in enumerate(recommendations, 1):
            marker = "（推荐）" if i == 1 else ""
            lines.append(f"\n方案{i}：{style.name}{marker}")
            lines.append(f"- 封面图配色：{COVER_PALETTES.get(style.cover_palette, {}).get('name', style.cover_palette)} + 渲染：{COVER_RENDERINGS.get(style.cover_rendering, {}).get('name', style.cover_rendering)}")
            lines.append(f"- 信息图布局：{INFOGRAPHIC_LAYOUTS.get(style.infographic_layout, {}).get('name', style.infographic_layout)} + 风格：{INFOGRAPHIC_STYLES.get(style.infographic_style, {}).get('name', style.infographic_style)}")
            lines.append(f"- 适用理由：{style.description}")
            lines.append(f"- 最适合：{style.best_for}")
        
        lines.extend([
            "\n请选择您偏好的风格方案（1/2/3），或告诉我您有其他想法：",
            "\n⚠️ 注意：在您确认风格之前，我不会开始生成任何配图。",
        ])
        
        return "\n".join(lines)


def main():
    """测试风格选择器"""
    selector = StyleSelector()
    
    # 测试文章分析
    test_content = """
    # AI Agent架构设计指南
    
    本文将深入探讨AI Agent的系统架构设计，包括多Agent协作、A2A协议等核心技术。
    
    ## 什么是AI Agent
    AI Agent是一种能够自主决策和执行任务的智能系统...
    
    ## 架构设计原则
    1. 模块化设计
    2. 松耦合通信
    3. 可扩展性
    
    ## 对比分析
    单Agent vs 多Agent架构的优劣对比...
    """
    
    analysis = selector.analyze_article(test_content)
    print("文章分析结果：")
    print(f"  内容类型: {analysis['content_type']}")
    print(f"  情感基调: {analysis['emotion']}")
    print(f"  是否对比: {analysis['has_comparison']}")
    
    recommendations = selector.recommend_styles(analysis)
    print("\n" + selector.format_style_recommendation("AI Agent架构设计指南", recommendations))


if __name__ == "__main__":
    main()
