#!/usr/bin/env python3
"""
批量压缩图片到微信公众号要求的尺寸和大小。
用法：python3 compress_images.py <图片目录> [输出目录] [最大宽度] [质量]
默认：输出到 /tmp/compressed_images，最大宽度 1200px，JPEG 质量 75

微信 API 限制：
- 正文图 >1MB 会触发 ECONNRESET
- 推荐压缩到 50-100KB
"""
import os
import sys
import glob
from PIL import Image

def compress_images(image_dir, output_dir="/tmp/compressed_images", max_width=1200, quality=75):
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有图片文件
    image_files = glob.glob(os.path.join(image_dir, "*.png")) + \
                  glob.glob(os.path.join(image_dir, "*.jpg")) + \
                  glob.glob(os.path.join(image_dir, "*.jpeg"))
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    results = []
    for img_file in image_files:
        try:
            img = Image.open(img_file)
            
            # 转换 RGBA 为 RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 调整大小
            w, h = img.size
            if w > max_width:
                ratio = max_width / w
                new_size = (max_width, int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # 保存为 JPEG
            filename = os.path.splitext(os.path.basename(img_file))[0] + '.jpg'
            output_path = os.path.join(output_dir, filename)
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ {filename}: {file_size/1024:.1f} KB")
            results.append(output_path)
            
        except Exception as e:
            print(f"❌ {img_file}: {e}")
    
    print(f"\n压缩完成！输出目录: {output_dir}")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 compress_images.py <图片目录> [输出目录] [最大宽度] [质量]")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/compressed_images"
    max_width = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 75
    
    compress_images(image_dir, output_dir, max_width, quality)
