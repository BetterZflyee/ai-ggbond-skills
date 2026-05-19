#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信贴图管理器
处理贴图文案的保存、文件夹创建和文件管理
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StickerManager:
    """微信贴图管理器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化管理器
        
        Args:
            base_dir: 基础输出目录，默认为当前工作目录下的 wechat_stickers/
        """
        if base_dir:
            self.base_dir = Path(base_dir).expanduser()
        else:
            self.base_dir = Path(os.environ.get("WECHAT_STICKER_OUTPUT_DIR", "/Users/admin/SuperIp/stickers")).expanduser()
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"贴图输出目录: {self.base_dir}")
    
    def sanitize_filename(self, title: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            title: 原始标题
            
        Returns:
            清理后的文件名
        """
        # 移除emoji（不要使用 \U000024C2-\U0001F251 这种超宽范围，
        # 它会误删 CJK 中文字符，导致中文标题目录名只剩英文片段）
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002600-\U000026FF"  # misc symbols
            u"\U00002700-\U000027BF"  # dingbats
            "]+", flags=re.UNICODE)
        variation_selector_pattern = re.compile(r"[\uFE0E\uFE0F]")
        
        clean_title = variation_selector_pattern.sub('', emoji_pattern.sub('', title))
        
        # 移除非法字符
        clean_title = re.sub(r'[\\/*?:"<>|]', '', clean_title)
        
        # 移除多余空格
        clean_title = clean_title.strip()
        
        # 限制长度
        if len(clean_title) > 50:
            clean_title = clean_title[:50]
        
        return clean_title
    
    def create_sticker_folder(self, title: str) -> Path:
        """
        创建贴图文件夹
        
        Args:
            title: 贴图标题
            
        Returns:
            创建的文件夹路径
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        clean_title = self.sanitize_filename(title)
        
        folder_name = f"{timestamp}-{clean_title}"
        folder_path = self.base_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # 创建images子文件夹
        images_dir = folder_path / "images"
        images_dir.mkdir(exist_ok=True)
        
        logger.info(f"创建贴图文件夹: {folder_path}")
        return folder_path
    
    def save_sticker_content(self, folder_path: Path, title: str, content: str) -> Path:
        """
        保存贴图文案
        
        Args:
            folder_path: 贴图文件夹路径
            title: 标题
            content: 文案内容
            
        Returns:
            保存的文件路径
        """
        file_path = folder_path / f"{folder_path.name}.md"
        
        # 构建完整的Markdown内容
        full_content = f"# {title}\n\n{content}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logger.info(f"贴图文案已保存: {file_path}")
        return file_path
    
    def save_image_prompts(self, folder_path: Path, prompts: Dict[str, Any], ratio: str = "16:9") -> Path:
        """
        保存配图提示词
        
        Args:
            folder_path: 贴图文件夹路径
            prompts: 提示词字典
            
        Returns:
            保存的文件路径
        """
        images_dir = folder_path / "images"
        prompt_file = images_dir / "prompt.md"
        
        content = "# 配图提示词\n\n"
        
        for i, (key, prompt_data) in enumerate(prompts.items(), 1):
            content += f"## 图片{i}：{prompt_data.get('title', key)}\n\n"
            content += f"**类型**：{prompt_data.get('type', '插图')}\n\n"
            content += f"**比例**：{ratio}\n\n"
            content += "**提示词**：\n```\n"
            content += prompt_data.get('prompt', '')
            content += "\n```\n\n"
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"配图提示词已保存: {prompt_file}")
        return prompt_file
    
    def generate_sticker(
        self,
        title: str,
        content: str,
        image_prompts: Optional[Dict[str, Any]] = None,
        ratio: str = "16:9"
    ) -> Dict[str, Path]:
        """
        一键生成完整贴图
        
        Args:
            title: 贴图标题
            content: 贴图文案内容
            image_prompts: 配图提示词（可选）
            
        Returns:
            包含所有文件路径的字典
        """
        # 创建文件夹
        folder_path = self.create_sticker_folder(title)
        
        # 保存文案
        content_file = self.save_sticker_content(folder_path, title, content)
        
        result = {
            'folder': folder_path,
            'content': content_file
        }
        
        # 保存配图提示词
        if image_prompts:
            prompt_file = self.save_image_prompts(folder_path, image_prompts, ratio=ratio)
            result['prompts'] = prompt_file
        
        logger.info(f"✅ 贴图生成完成！文件夹: {folder_path}")
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='微信贴图管理器')
    parser.add_argument('--title', required=True, help='贴图标题')
    parser.add_argument('--content', required=True, help='贴图文案内容')
    parser.add_argument('--output-dir', help='输出目录')
    parser.add_argument('--ratio', default='16:9', choices=['1:1', '16:9', '3:4'], help='配图比例')
    
    args = parser.parse_args()
    
    manager = StickerManager(base_dir=args.output_dir)
    result = manager.generate_sticker(
        title=args.title,
        content=args.content,
        ratio=args.ratio
    )
    
    print(f"\n✅ 贴图生成完成！")
    print(f"📁 文件夹: {result['folder']}")
    print(f"📄 文案: {result['content']}")


if __name__ == '__main__':
    main()
