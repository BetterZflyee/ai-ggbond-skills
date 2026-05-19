#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章管理器
自动创建标准化的文件夹结构并保存文章，同时生成移动端优化的HTML版本。

功能：
1. 从Markdown文件中提取标题
2. 创建 YYYYMMDDHHMM-文章标题 格式的文件夹
3. 保存Markdown原文
4. 调用排版优化器生成HTML版本
5. 可选：调用云雾API生成配图
6. 记录创建日志
"""

import os
import re
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, List

# 配置 - 跨平台兼容
# 优先使用环境变量，否则使用脚本所在目录的父目录
_skill_dir = Path(__file__).parent.parent
ARTICLE_BASE_DIR = Path(os.environ.get("ARTICLE_BASE_DIR", str(_skill_dir / "Article")))
LOG_FILE = _skill_dir / "article_manager.log"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArticleManager:
    """文章管理器类"""

    def __init__(self, base_dir=None, yunwu_api_key: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else ARTICLE_BASE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.yunwu_api_key = yunwu_api_key or os.environ.get("YUNWU_API_KEY")
        logger.info(f"文章管理器初始化完成，基础目录: {self.base_dir}")
        if self.yunwu_api_key:
            logger.info("云雾API已配置，支持自动生图")

    def extract_title(self, markdown_content):
        """
        从Markdown内容中提取标题
        
        优先级：
        1. 第一个 # 标题
        2. 第一行非空内容
        3. 默认标题
        """
        lines = markdown_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配 # 标题
            if line.startswith('#'):
                title = re.sub(r'^#+\s*', '', line).strip()
                # 移除书名号（如果有）
                title = re.sub(r'^《(.+)》$', r'\1', title)
                if title:
                    return title
            
            # 如果没有 # 标题，使用第一个非空行
            return line[:50]  # 限制长度
        
        return "未命名文章"

    def sanitize_filename(self, title):
        """清理文件名，移除非法字符"""
        # 移除Windows文件名中的非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(illegal_chars, '', title)
        # 移除首尾空格和点
        sanitized = sanitized.strip('. ')
        # 限制长度
        return sanitized[:100] if sanitized else "未命名文章"

    def create_article_folder(self, title):
        """
        创建文章文件夹
        
        格式：YYYYMMDDHHMM-文章标题
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        sanitized_title = self.sanitize_filename(title)
        folder_name = f"{timestamp}-{sanitized_title}"
        folder_path = self.base_dir / folder_name
        
        # 如果文件夹已存在，添加序号
        counter = 1
        while folder_path.exists():
            folder_name = f"{timestamp}-{sanitized_title}-{counter}"
            folder_path = self.base_dir / folder_name
            counter += 1
        
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建文章文件夹: {folder_path}")
        
        return folder_path, sanitized_title

    def save_article(self, markdown_content, folder_path, title):
        """保存Markdown文章"""
        filename = f"{title}.md"
        file_path = folder_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"文章已保存: {file_path}")
        return file_path

    def generate_html(self, markdown_path, folder_path, title):
        """生成HTML版本（调用排版优化器，嵌入图片）"""
        try:
            import importlib.util
            script_dir = Path(__file__).parent
            formatter_path = script_dir / "format_article.py"
            
            if not formatter_path.exists():
                logger.warning(f"排版优化器不存在: {formatter_path}")
                return None
            
            spec = importlib.util.spec_from_file_location("format_article", formatter_path)
            format_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(format_module)
            
            formatter = format_module.ArticleFormatter()
            html_path = folder_path / f"{title}.html"
            
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 检查是否有图片目录
            images_dir = folder_path / "images"
            if images_dir.exists():
                logger.info(f"检测到图片目录，将嵌入图片到HTML中")
                html_content = formatter.format_article(markdown_content, title=title, images_dir=images_dir)
            else:
                html_content = formatter.format_article(markdown_content, title=title)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML排版优化完成: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"HTML生成失败: {e}")
            return None

    def extract_image_specs(self, markdown_content: str) -> List[Dict[str, str]]:
        """
        从Markdown内容中提取图片需求
        
        格式：[图片名称](图片内容详细提示词)
        
        Returns:
            图片规格列表
        """
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, markdown_content)
        
        image_specs = []
        for name, prompt in matches:
            if "图片" in name or len(prompt) > 20:
                if "封面" in name or "cover" in name.lower():
                    img_type = "cover"
                    size = "1792x1024"
                elif "信息图" in name or "infographic" in name.lower():
                    img_type = "infographic"
                    size = "1792x1024"
                else:
                    img_type = "concept"
                    size = "1024x1024"
                
                image_specs.append({
                    "name": name,
                    "prompt": prompt,
                    "type": img_type,
                    "size": size
                })
        
        return image_specs

    def generate_images(
        self,
        markdown_content: str,
        output_dir: Path,
        model: str = "gpt-image-2"
    ) -> Dict[str, str]:
        """
        为文章生成配图
        
        Args:
            markdown_content: Markdown内容
            output_dir: 输出目录
            model: 使用的模型
            
        Returns:
            {图片名称: 本地路径} 字典
        """
        if not self.yunwu_api_key:
            logger.warning("未配置云雾API Key，跳过图片生成")
            return {}
        
        try:
            import importlib.util
            script_dir = Path(__file__).parent
            generator_path = script_dir / "generate_images_v4.py"
            
            if not generator_path.exists():
                logger.warning(f"图片生成器不存在: {generator_path}")
                return {}
            
            spec = importlib.util.spec_from_file_location("generate_images_v4", generator_path)
            gen_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gen_module)
            
            generator = gen_module.YunwuImageGenerator(api_key=self.yunwu_api_key)
            
            image_specs = self.extract_image_specs(markdown_content)
            
            if not image_specs:
                logger.info("文章中没有找到图片标注，跳过图片生成")
                return {}
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = {}
            for i, spec in enumerate(image_specs, 1):
                name = spec["name"]
                prompt = spec["prompt"]
                img_type = spec["type"]
                size = spec["size"]
                
                logger.info(f"生成图片 [{i}/{len(image_specs)}]: {name}")
                
                try:
                    quality = "hd" if img_type == "cover" and model in ["gpt-image-2", "qwen-image-max", "dall-e-3", "gpt-image-1"] else "standard"
                    
                    result = generator.generate(
                        prompt=prompt,
                        model=model,
                        size=size,
                        quality=quality
                    )
                    
                    if result:
                        safe_name = re.sub(r'[<>:"/\\|?*]', '', name)
                        filename = f"{i:02d}-{safe_name}.png"
                        save_path = output_dir / filename
                        image_url = result[0].url if isinstance(result, list) else getattr(result, "url", "")
                        if image_url:
                            generator.download_image(image_url, str(save_path))
                            results[name] = str(save_path)
                        
                except Exception as e:
                    logger.error(f"生成图片 {name} 失败: {e}")
                    results[name] = ""
            
            return results
            
        except Exception as e:
            logger.error(f"图片生成模块加载失败: {e}")
            return {}

    def update_markdown_with_images(
        self,
        markdown_content: str,
        image_results: Dict[str, str]
    ) -> str:
        """
        更新Markdown内容，将图片标注替换为实际图片链接
        
        Args:
            markdown_content: 原始Markdown内容
            image_results: 图片生成结果
            
        Returns:
            更新后的Markdown内容
        """
        def replace_image(match):
            name = match.group(1)
            prompt = match.group(2)
            
            if name in image_results and image_results[name]:
                path = Path(image_results[name])
                relative_path = f"images/{path.name}"
                return f"![{name}]({relative_path})"
            
            return match.group(0)
        
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        return re.sub(pattern, replace_image, markdown_content)

    def process_file(self, input_path, generate_images: bool = False, image_model: str = "gpt-image-2"):
        """
        处理输入的Markdown文件
        
        Args:
            input_path: Markdown文件路径
            generate_images: 是否生成配图
            image_model: 图片生成模型
            
        Returns:
            (folder_path, md_path, html_path, image_results) 或 None
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            logger.error(f"输入文件不存在: {input_path}")
            return None
        
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        return self.process_content(markdown_content, generate_images, image_model)

    def process_content(self, markdown_content, generate_images: bool = False, image_model: str = "gpt-image-2"):
        """
        处理Markdown内容
        
        Args:
            markdown_content: Markdown文本内容
            generate_images: 是否生成配图
            image_model: 图片生成模型
            
        Returns:
            (folder_path, md_path, html_path, image_results) 或 None
        """
        try:
            title = self.extract_title(markdown_content)
            logger.info(f"提取到标题: {title}")
            
            folder_path, sanitized_title = self.create_article_folder(title)
            
            image_results = {}
            
            if generate_images and self.yunwu_api_key:
                images_dir = folder_path / "images"
                logger.info("开始生成文章配图...")
                image_results = self.generate_images(
                    markdown_content,
                    images_dir,
                    model=image_model
                )
                
                if image_results:
                    markdown_content = self.update_markdown_with_images(
                        markdown_content,
                        image_results
                    )
                    logger.info(f"已生成 {len([v for v in image_results.values() if v])} 张配图")
            
            md_path = self.save_article(markdown_content, folder_path, sanitized_title)
            
            html_path = self.generate_html(md_path, folder_path, sanitized_title)
            
            self._log_creation(title, str(folder_path))
            
            return folder_path, md_path, html_path, image_results
            
        except Exception as e:
            logger.error(f"处理文章失败: {e}")
            return None

    def _log_creation(self, title, folder_path):
        """记录文章创建日志"""
        log_entry = f"创建文章: {title} -> {folder_path}"
        logger.info(log_entry)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='文章管理器 - 创建标准化文件夹结构并保存文章',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python article_manager.py article.md
  python article_manager.py -i article.md --generate-images
  python article_manager.py -c "Markdown内容..." --generate-images --model flux-1.1-pro
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入的Markdown文件路径')
    parser.add_argument('-i', '--input-file', help='输入的Markdown文件路径')
    parser.add_argument('-c', '--content', help='直接输入Markdown内容')
    parser.add_argument('-d', '--dir', help='文章保存的基础目录')
    parser.add_argument('--generate-images', action='store_true',
                        help='使用云雾API生成配图')
    parser.add_argument('-m', '--model', default='gpt-image-2',
                        help='图片生成模型 (默认: gpt-image-2)')
    parser.add_argument('-k', '--api-key', help='云雾API密钥')
    
    args = parser.parse_args()
    
    manager = ArticleManager(
        base_dir=args.dir,
        yunwu_api_key=args.api_key
    )
    
    if args.content:
        result = manager.process_content(
            args.content,
            generate_images=args.generate_images,
            image_model=args.model
        )
    elif args.input or args.input_file:
        input_path = args.input or args.input_file
        result = manager.process_file(
            input_path,
            generate_images=args.generate_images,
            image_model=args.model
        )
    else:
        parser.print_help()
        sys.exit(1)
    
    if result:
        folder_path, md_path, html_path, image_results = result
        print(f"\n✅ 文章处理完成！")
        print(f"📁 文件夹: {folder_path}")
        print(f"📄 Markdown: {md_path}")
        if html_path:
            print(f"🌐 HTML: {html_path}")
        if image_results:
            print(f"\n📷 生成的配图 ({len([v for v in image_results.values() if v])} 张):")
            for name, path in image_results.items():
                if path:
                    print(f"   - {name}: {path}")
    else:
        print("❌ 文章处理失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
