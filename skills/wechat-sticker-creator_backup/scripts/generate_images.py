#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信贴图配图生成器
使用云雾API生成1:1正方形配图，适合小红书/朋友圈
"""

import os
import re
import logging
import requests
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_file():
    """加载环境变量"""
    script_dir = Path(__file__).parent
    env_file = script_dir.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


load_env_file()


@dataclass
class ImageResult:
    """图片生成结果"""
    url: str
    model: str = ""
    created: int = 0


class YunwuImageGenerator:
    """云雾API图像生成器 - 微信贴图专用版"""
    
    API_ENDPOINTS = [
        "https://yunwu.ai/v1/images/generations",
        "https://yunwu.zeabur.app/v1/images/generations",
        "https://api.apiplus.org/v1/images/generations"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("YUNWU_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 YUNWU_API_KEY 环境变量")
    
    def generate(
        self,
        prompt: str,
        model: str = "gemini-3.1-flash-image-preview",
        size: str = "1024x1024",
        quality: str = "hd",
        max_retries: int = 3,
        timeout: int = 180
    ) -> ImageResult:
        """
        生成图片
        
        Args:
            prompt: 提示词
            model: 模型名称
            size: 图片尺寸
            quality: 图片质量
            max_retries: 最大重试次数
            timeout: 超时时间
            
        Returns:
            图片生成结果
        """
        data = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        last_error = None
        for attempt in range(max_retries):
            for api_url in self.API_ENDPOINTS:
                try:
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=data,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "data" in result and len(result["data"]) > 0:
                            image_url = result["data"][0].get("url", "")
                            if image_url:
                                logger.info(f"✅ 图片生成成功！")
                                return ImageResult(url=image_url, model=model)
                    else:
                        last_error = f"HTTP {response.status_code}"
                        
                except Exception as e:
                    last_error = str(e)
                
                time.sleep(1)
            
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"图片生成失败: {last_error}")
    
    # 信息图风格定义
    INFOGRAPHIC_STYLES = {
        "高密度信息大图": {
            "description": "实验室精密手册感 + 波普实验风格",
            "colors": "蓝图网格(#F2F2F2) + 荧光粉(#E91E63) + 柠檬黄(#FFF200)",
            "features": "信息坐标化、超精细技术网格、6-7个高密度模块、坐标标签(R-20, G-02)",
            "density": "极高，留白≤5%",
            "modules": "6-7个模块"
        },
        "复古波普网格": {
            "description": "70年代复古波普艺术 + 瑞士网格系统",
            "colors": "奶油色(#F5F0E6) + 鲑鱼粉/天蓝/芥末黄",
            "features": "严格网格布局、粗黑线描边、2D扁平风格、反转对比",
            "density": "高，6-7个模块",
            "modules": "6-7个网格单元格"
        },
        "文件夹风格": {
            "description": "新拟物化文具风格、3D渲染感",
            "colors": "奶油色(#F5F5DC) + 克莱因蓝 + 活力橙",
            "features": "剪贴板框架、分层文件夹、3D鼠标光标、列表式文档",
            "density": "中高，5-6个模块",
            "modules": "5-6个文件夹模块"
        },
        "打印热敏纸": {
            "description": "现代票据/收据美学、3D图标",
            "colors": "亮青色/芥末黄边框 + 米白核心",
            "features": "穿孔边缘、3D拟物化头部、复古数字字体、粘土风图标",
            "density": "中等，4-5个模块",
            "modules": "4-5个票据模块"
        },
        "复古手帐": {
            "description": "复古剪贴簿 + 手绘日记美学",
            "colors": "牛皮纸棕 + 奶油白 + 大红/亮黄强调",
            "features": "撕裂纸边、网格纸、红色图钉、侦探证据板布局",
            "density": "中等，4-5个模块",
            "modules": "4-5个手帐模块"
        },
        "矢量插图": {
            "description": "扁平化矢量插画、统一黑色轮廓线",
            "colors": "米色/奶油色 + 珊瑚红/薄荷绿/芥末黄",
            "features": "统一黑色单线描边、几何化处理、2.5D视角",
            "density": "中等，4-5个模块",
            "modules": "4-5个矢量模块"
        }
    }

    def get_style_prompt(self, style_name: str) -> str:
        """获取指定风格的详细提示词描述"""
        style = self.INFOGRAPHIC_STYLES.get(style_name, self.INFOGRAPHIC_STYLES["复古波普网格"])
        return f"""
【视觉风格 - {style_name}】
- 风格描述：{style['description']}
- 配色方案：{style['colors']}
- 核心特征：{style['features']}
- 信息密度：{style['density']}
- 模块数量：{style['modules']}
"""

    def generate_sticker_image(
        self,
        title: str,
        content_points: List[str],
        image_type: str = "插图",
        style: str = "复古波普网格",
        ratio: str = "1:1",
        model: str = "gemini-3.1-flash-image-preview"
    ) -> ImageResult:
        """
        生成微信贴图配图
        
        Args:
            title: 图片标题
            content_points: 内容要点列表
            image_type: 图片类型（信息图/插图）
            style: 视觉风格（从INFOGRAPHIC_STYLES中选择）
            ratio: 图片比例（1:1/16:9/3:4）
            model: 模型名称
            
        Returns:
            图片生成结果
        """
        # 构建内容描述
        points_text = "\n".join([f"- {point}" for point in content_points[:5]])
        
        # 获取风格描述
        style_description = self.get_style_prompt(style)
        
        # 根据比例设置尺寸和布局
        if ratio == "16:9":
            size = "1792x1024"
            layout_desc = """
【布局结构】（16:9横版专用布局）
- 标题区（占12%）：左侧或顶部，醒目大标题
- 内容区（占78%）：横向展开，多列布局
  * 使用网格或分栏展示信息
  * 配4-6个相关插图均匀分布
  * 使用箭头、连接线引导视线
- 留白区：保持10%留白"""
        elif ratio == "3:4":
            size = "1024x1536"
            layout_desc = """
【布局结构】（3:4竖版专用布局）
- 标题区（占10%）：顶部，醒目大标题
- 内容区（占80%）：纵向展开，信息流布局
  * 使用卡片堆叠或时间轴展示
  * 配5-7个相关插图纵向排列
  * 使用引导线连接各模块
- 留白区：保持10%留白"""
        else:  # 1:1
            size = "1024x1024"
            layout_desc = """
【布局结构】（1:1正方形专用布局）
- 标题区（占15%）：顶部居中，手写字体，醒目突出
- 内容区（占70%）：信息密集排列，使用卡片、标签、气泡等形式
  * 核心内容居中展示
  * 配3-5个相关卡通插图穿插在内容中
  * 使用虚线、箭头连接各信息模块
- 留白区：保持15-20%留白，呼吸感"""
        
        prompt = f"""创建一张精美的{style}风格{image_type}。

【强制要求 - 必须遵守】
- 严格按比例{ratio}设计
- 必须使用【{style}】风格，确保视觉一致性
- 所有文字必须是简体中文，生成后检查是否有乱码或变形

【基本信息】
- 比例：{ratio}
- 分辨率：8K超高清
- 主题：{title}

【核心内容】
- 标题：{title}
- 核心要点：
{points_text}

{style_description}

{layout_desc}

【插图元素】
- 与主题相关的图标、符号、装饰元素
- 符合{style}风格的装饰线条和图形
- 与风格一致的效果（网格、标签、票据、手帐等）

【文字要求】
- 所有文字必须使用简体中文
- 确保中文文字清晰无乱码、无变形
- 标题字体大且醒目，正文字体清晰可读
- 字体风格符合{style}风格要求

OUTPUT: A beautiful {style} style {image_type} perfect for social media sharing."""

        return self.generate(prompt=prompt, model=model, size=size, quality="hd")
    
    def download_image(self, url: str, save_path: str) -> str:
        """
        下载图片
        
        Args:
            url: 图片URL
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"✅ 图片已下载: {save_path}")
        return str(save_path)


def add_watermark(
    image_path: str,
    watermark_text: str = "",
    position: str = "topright"
) -> str:
    """
    为图片添加水印
    
    Args:
        image_path: 图片路径
        watermark_text: 水印文字
        position: 水印位置
        
    Returns:
        处理后的图片路径
    """
    if not watermark_text:
        return image_path
    
    try:
        img = Image.open(image_path)
        
        # 转换模式
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # 计算字体大小
        img_width, img_height = img.size
        font_size = max(12, int(img_height * 0.02))
        
        # 加载字体
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
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # 获取文字边界框
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        margin = int(img_width * 0.02)
        if position == "topright":
            x = img_width - text_width - margin
            y = margin
        elif position == "topleft":
            x = margin
            y = margin
        elif position == "bottomright":
            x = img_width - text_width - margin
            y = img_height - text_height - margin
        else:  # bottomleft
            x = margin
            y = img_height - text_height - margin
        
        # 绘制半透明背景
        padding = int(font_size * 0.3)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
            fill=(255, 255, 255, 180)
        )
        
        # 合并背景
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        # 绘制文字
        draw = ImageDraw.Draw(img)
        text_color = (100, 100, 100, 200)
        draw.text((x, y), watermark_text, font=font, fill=text_color)
        
        # 保存
        img = img.convert('RGB')
        img.save(image_path, 'PNG', quality=95)
        
        logger.info(f"✅ 水印已添加: {watermark_text}")
        return image_path
        
    except Exception as e:
        logger.warning(f"⚠️ 添加水印失败: {e}")
        return image_path


def generate_sticker_images(
    prompts_file: str,
    output_dir: str,
    api_key: Optional[str] = None,
    model: str = "gemini-3.1-flash-image-preview",
    watermark: str = ""
) -> Dict[str, str]:
    """
    从提示词文件生成贴图配图
    
    Args:
        prompts_file: 提示词文件路径
        output_dir: 输出目录
        api_key: API密钥
        model: 模型名称
        watermark: 水印文字
        
    Returns:
        生成的图片路径字典
    """
    prompts_path = Path(prompts_file)
    if not prompts_path.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompts_file}")
    
    # 读取提示词
    with open(prompts_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析提示词
    image_prompts = []
    current_prompt = {}
    in_prompt_block = False
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('## 图片'):
            if current_prompt and current_prompt.get('prompt'):
                image_prompts.append(current_prompt)
            current_prompt = {
                'title': line.split('：', 1)[-1].strip(),
                'prompt': '',
                'type': '插图',
                'ratio': '1:1'
            }
            in_prompt_block = False
        elif line.startswith('**类型**：'):
            current_prompt['type'] = line.replace('**类型**：', '').strip()
        elif line.startswith('**比例**：'):
            ratio_text = line.replace('**比例**：', '').strip()
            if '16:9' in ratio_text:
                current_prompt['ratio'] = '16:9'
            else:
                current_prompt['ratio'] = '1:1'
        elif line.startswith('```') and current_prompt:
            in_prompt_block = not in_prompt_block
        elif in_prompt_block and current_prompt:
            current_prompt['prompt'] += (line + '\n')
    
    if current_prompt and current_prompt.get('prompt'):
        image_prompts.append(current_prompt)
    
    logger.info(f"✅ 解析到 {len(image_prompts)} 张图片的提示词")
    
    # 生成图片
    generator = YunwuImageGenerator(api_key=api_key)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for i, prompt_data in enumerate(image_prompts, 1):
        logger.info(f"\n生成图片 {i}/{len(image_prompts)}: {prompt_data.get('title', f'图片{i}')}")
        
        try:
            prompt_text = prompt_data.get('prompt', '')
            ratio = prompt_data.get('ratio', '1:1')
            
            # 根据比例设置尺寸
            if ratio == '16:9':
                size = "1792x1024"
                logger.info(f"📐 使用16:9比例，尺寸: {size}")
            else:
                size = "1024x1024"
                logger.info(f"📐 使用1:1比例，尺寸: {size}")
            
            # 直接使用详细提示词生成，不使用模板
            result = generator.generate(
                prompt=prompt_text,
                model=model,
                size=size,
                quality="hd"
            )
            
            # 下载图片
            save_path = output_path / f"{i:02d}-{prompt_data.get('title', 'image')[:20]}.png"
            generator.download_image(result.url, str(save_path))
            
            # 添加水印
            if watermark:
                add_watermark(str(save_path), watermark)
            
            results[f'图片{i}'] = str(save_path)
            logger.info(f"✅ 图片已保存: {save_path}")
            
        except Exception as e:
            logger.error(f"❌ 图片{i}生成失败: {e}")
            results[f'图片{i}'] = ""
        
        time.sleep(3)
    
    success_count = len([v for v in results.values() if v])
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ 配图生成完成！成功: {success_count}/{len(results)}")
    logger.info(f"{'='*60}\n")
    
    return results


def generate_single_image(
    title: str,
    content_points: List[str],
    output_path: str,
    image_type: str = "插图",
    style: str = "复古波普网格",
    ratio: str = "1:1",
    api_key: Optional[str] = None,
    model: str = "gemini-3.1-flash-image-preview",
    watermark: str = ""
) -> str:
    """
    生成单张贴图配图
    
    Args:
        title: 图片标题
        content_points: 内容要点
        output_path: 保存路径
        image_type: 图片类型
        style: 视觉风格（高密度信息大图/复古波普网格/文件夹风格/打印热敏纸/复古手帐/矢量插图）
        ratio: 图片比例（1:1/16:9/3:4）
        api_key: API密钥
        model: 模型名称
        watermark: 水印文字
        
    Returns:
        保存的图片路径
    """
    generator = YunwuImageGenerator(api_key=api_key)
    
    result = generator.generate_sticker_image(
        title=title,
        content_points=content_points,
        image_type=image_type,
        style=style,
        ratio=ratio,
        model=model
    )
    
    # 下载图片
    generator.download_image(result.url, output_path)
    
    # 添加水印
    if watermark:
        add_watermark(output_path, watermark)
    
    return output_path


def main():
    """命令行入口"""
    import argparse
    
    # 可用风格列表
    available_styles = [
        "高密度信息大图",
        "复古波普网格", 
        "文件夹风格",
        "打印热敏纸",
        "复古手帐",
        "矢量插图"
    ]
    
    parser = argparse.ArgumentParser(description='微信贴图配图生成器')
    parser.add_argument('--prompts', help='提示词文件路径')
    parser.add_argument('--output-dir', default='./images', help='输出目录')
    parser.add_argument('--title', help='单图模式：图片标题')
    parser.add_argument('--points', nargs='+', help='单图模式：内容要点')
    parser.add_argument('--type', default='插图', help='图片类型（信息图/插图）')
    parser.add_argument('--style', default='复古波普网格', 
                       help=f'视觉风格（可选：{", ".join(available_styles)}）')
    parser.add_argument('--ratio', default='1:1', choices=['1:1', '16:9', '3:4'],
                       help='图片比例（1:1/16:9/3:4）')
    parser.add_argument('--list-styles', action='store_true',
                       help='列出所有可用风格')
    parser.add_argument('-k', '--api-key', help='云雾API密钥')
    parser.add_argument('-m', '--model', default='gemini-3.1-flash-image-preview', help='模型名称')
    parser.add_argument('-w', '--watermark', default='', help='水印文字')
    
    args = parser.parse_args()
    
    # 列出可用风格
    if args.list_styles:
        print("\n📚 可用信息图风格：")
        print("=" * 60)
        generator = YunwuImageGenerator()
        for i, (style_name, style_info) in enumerate(generator.INFOGRAPHIC_STYLES.items(), 1):
            print(f"\n{i}. {style_name}")
            print(f"   描述：{style_info['description']}")
            print(f"   配色：{style_info['colors']}")
            print(f"   密度：{style_info['density']}")
        print("\n" + "=" * 60)
        return
    
    # 验证风格
    if args.style not in available_styles:
        print(f"\n⚠️ 警告：未知的风格 '{args.style}'")
        print(f"可用风格：{', '.join(available_styles)}")
        print(f"使用默认风格：复古波普网格")
        args.style = '复古波普网格'
    
    if args.prompts:
        # 批量模式
        try:
            results = generate_sticker_images(
                prompts_file=args.prompts,
                output_dir=args.output_dir,
                api_key=args.api_key,
                model=args.model,
                watermark=args.watermark
            )
            print(f"\n生成结果:")
            for name, path in results.items():
                status = "✅" if path else "❌"
                print(f"  {status} {name}: {path or '失败'}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
    elif args.title and args.points:
        # 单图模式
        try:
            output_path = Path(args.output_dir) / f"{args.title[:20]}.png"
            print(f"\n🎨 生成配置：")
            print(f"   风格：{args.style}")
            print(f"   比例：{args.ratio}")
            print(f"   类型：{args.type}")
            print(f"   标题：{args.title}")
            
            result = generate_single_image(
                title=args.title,
                content_points=args.points,
                output_path=str(output_path),
                image_type=args.type,
                style=args.style,
                ratio=args.ratio,
                api_key=args.api_key,
                model=args.model,
                watermark=args.watermark
            )
            print(f"\n✅ 图片已生成: {result}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
