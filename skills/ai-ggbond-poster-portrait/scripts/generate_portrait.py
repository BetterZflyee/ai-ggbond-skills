#!/usr/bin/env python3
"""
GPT Image 2 女性肖像海报生成脚本
使用云雾API生成具有摄影感、电影感、情绪感的高质量女性肖像海报
"""

import os
import sys
import base64
import time
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any


def load_config() -> Dict[str, Any]:
    """加载云雾API配置"""
    config = {
        "api_key": os.environ.get("YUNWU_API_KEY", ""),
        "base_urls": os.environ.get(
            "YUNWU_BASE_URLS",
            "https://yunwu.ai,https://api.apiplus.org,https://api3.wlai.vip"
        ),
        "endpoint": os.environ.get("YUNWU_IMAGE_ENDPOINT", "/v1/images/generations"),
        "model": os.environ.get("YUNWU_DEFAULT_MODEL", "gpt-image-2"),
        "max_retries": int(os.environ.get("YUNWU_MAX_RETRIES", "3")),
        "retry_delay": int(os.environ.get("YUNWU_RETRY_DELAY", "8")),
        "timeout": int(os.environ.get("YUNWU_IMAGE_TIMEOUT", "300")),
    }
    
    # 从配置文件读取（如果环境变量为空）
    if not config["api_key"]:
        config_paths = [
            Path("./.ai-ggbond-skills/.env"),
            Path("~/.ai-ggbond-skills/.env").expanduser(),
        ]
        for config_path in config_paths:
            if config_path.exists():
                for line in config_path.read_text().splitlines():
                    if line.startswith("YUNWU_API_KEY="):
                        config["api_key"] = line.split("=", 1)[1].strip()
                        break
                if config["api_key"]:
                    break
    
    # 解析多链路
    config["base_url_list"] = [u.strip() for u in config["base_urls"].split(",") if u.strip()]
    
    return config


def get_size_from_ratio(ratio: str) -> str:
    """根据比例返回尺寸"""
    size_map = {
        "9:16": "1024x1792",
        "16:9": "1792x1024",
        "1:1": "1024x1024",
        "4:5": "1024x1280",
        "3:4": "1024x1365",
    }
    return size_map.get(ratio, "1024x1792")


def generate_portrait(
    prompt: str,
    output_path: str,
    ratio: str = "9:16",
    model: Optional[str] = None,
    verbose: bool = True
) -> bool:
    """
    生成肖像海报
    
    Args:
        prompt: 完整的提示词
        output_path: 输出图片路径
        ratio: 画幅比例 (9:16, 16:9, 1:1, 4:5, 3:4)
        model: 模型名称（可选，默认使用配置）
        verbose: 是否显示详细信息
    
    Returns:
        bool: 是否成功
    """
    config = load_config()
    
    if not config["api_key"]:
        print("❌ 错误：未配置YUNWU_API_KEY")
        print("请创建配置文件 ~/.ai-ggbond-skills/.env 并添加：")
        print("YUNWU_API_KEY=your_api_key_here")
        return False
    
    size = get_size_from_ratio(ratio)
    use_model = model or config["model"]
    
    data = {
        "model": use_model,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    
    if verbose:
        print(f"🎨 模型: {use_model}")
        print(f"📐 比例: {ratio} ({size})")
        print(f"📁 输出: {output_path}")
        print()
    
    # 尝试所有链路
    for base_url in config["base_url_list"]:
        endpoint = f"{base_url}{config['endpoint']}"
        if verbose:
            print(f"🔄 尝试链路: {base_url}")
        
        for attempt in range(config["max_retries"]):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=data,
                    timeout=config["timeout"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    img_data = result["data"][0]
                    
                    # 确保输出目录存在
                    output_dir = Path(output_path).parent
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 保存图片
                    if "b64_json" in img_data:
                        img_bytes = base64.b64decode(img_data["b64_json"])
                        with open(output_path, "wb") as f:
                            f.write(img_bytes)
                    elif "url" in img_data:
                        img_response = requests.get(img_data["url"], timeout=60)
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                    else:
                        print("❌ 响应中没有图片数据")
                        return False
                    
                    if verbose:
                        print(f"✅ 图片已保存: {output_path}")
                    return True
                    
                elif response.status_code == 429:
                    wait_time = config["retry_delay"] * (attempt + 1)
                    if verbose:
                        print(f"⚠️  链路负载饱和 (429)，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    error_msg = response.text[:200] if response.text else "Unknown error"
                    if verbose:
                        print(f"❌ 请求失败: {response.status_code} - {error_msg}")
                    break
                    
            except requests.exceptions.Timeout:
                if verbose:
                    print(f"⏰ 请求超时，重试 {attempt + 1}/{config['max_retries']}")
                time.sleep(config["retry_delay"])
                continue
                
            except Exception as e:
                if verbose:
                    print(f"❌ 请求异常: {e}")
                break
    
    if verbose:
        print("❌ 所有链路均失败")
    return False


def build_prompt_from_params(params: Dict[str, str]) -> str:
    """
    从参数字典构建完整的英文提示词
    
    Args:
        params: 参数字典，包含摄影风格、场景、服装等
    
    Returns:
        str: 完整的英文提示词
    """
    # 基础提示词模板
    prompt_parts = []
    
    # 主体描述
    temperament = params.get("气质标签", "gentle, sweet")
    body_type = params.get("身形方向", "petite and slender")
    facial = params.get("五官方向", "soft and delicate")
    
    prompt_parts.append(
        f"A 22-year-old adult female character with a {body_type} build, "
        f"youthful appearance, and {temperament} temperament."
    )
    
    # 场景描述
    scene = params.get("场景方向", "indoor setting")
    prompt_parts.append(f"She is in {scene}.")
    
    # 姿态动作
    pose = params.get("姿态动作", "sitting naturally")
    prompt_parts.append(f"Pose: {pose}")
    
    # 服装描述
    clothing = params.get("服装方向", "casual clothing")
    prompt_parts.append(f"Clothing: {clothing}")
    
    # 摄影风格
    photo_style = params.get("摄影风格", "soft aesthetic")
    prompt_parts.append(f"Photography style: {photo_style}")
    
    # 光线氛围
    lighting = params.get("光线氛围", "soft natural light")
    prompt_parts.append(f"Lighting: {lighting}")
    
    # 滤镜效果
    filter_effect = params.get("滤镜效果", "soft colors, gentle tones")
    prompt_parts.append(f"Filter effect: {filter_effect}")
    
    # 镜头方向
    camera = params.get("镜头方向", "half-body shot")
    prompt_parts.append(f"Camera angle: {camera}")
    
    # 补充要求
    extra = params.get("补充要求", "")
    if extra:
        prompt_parts.append(f"Additional: {extra}")
    
    # 安全审核要求
    prompt_parts.append(
        "The image should be tasteful, elegant, and suitable for social media. "
        "Avoid any vulgar or inappropriate content."
    )
    
    return "\n\n".join(prompt_parts)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GPT Image 2 女性肖像海报生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用提示词文件生成
  python generate_portrait.py --prompt prompt.txt --output portrait.png
  
  # 使用参数生成
  python generate_portrait.py \\
    --scene "客厅沙发" \\
    --style "柔光CCD风" \\
    --clothing "奶油色针织衫" \\
    --output portrait.png
  
  # 指定模型和比例
  python generate_portrait.py \\
    --prompt prompt.txt \\
    --model gpt-image-2 \\
    --ratio 16:9 \\
    --output portrait_wide.png
        """
    )
    
    # 提示词输入
    parser.add_argument("--prompt", "-p", help="提示词文件路径")
    parser.add_argument("--prompt-text", help="直接输入提示词文本")
    
    # 参数化输入
    parser.add_argument("--scene", help="场景方向")
    parser.add_argument("--style", help="摄影风格")
    parser.add_argument("--clothing", help="服装方向")
    parser.add_argument("--temperament", help="气质标签")
    parser.add_argument("--body-type", help="身形方向")
    parser.add_argument("--facial", help="五官方向")
    parser.add_argument("--pose", help="姿态动作")
    parser.add_argument("--lighting", help="光线氛围")
    parser.add_argument("--filter", help="滤镜效果")
    parser.add_argument("--camera", help="镜头方向")
    parser.add_argument("--extra", help="补充要求")
    
    # 输出配置
    parser.add_argument("--output", "-o", required=True, help="输出图片路径")
    parser.add_argument("--ratio", "-r", default="9:16", 
                       choices=["9:16", "16:9", "1:1", "4:5", "3:4"],
                       help="画幅比例 (默认: 9:16)")
    parser.add_argument("--model", "-m", help="模型名称 (默认: gpt-image-2)")
    
    # 其他选项
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    parser.add_argument("--list-models", action="store_true", help="列出可用模型")
    
    args = parser.parse_args()
    
    # 列出可用模型
    if args.list_models:
        print("可用模型:")
        print("  - gpt-image-2 (默认推荐)")
        print("  - gpt-image-1 (上一代，更稳定)")
        print("  - gemini-2.5-flash-image (快速)")
        print("  - dall-e-3 (英文渲染好)")
        print("  - qwen-image-edit-2509 (中文优化)")
        return
    
    # 构建提示词
    prompt = None
    
    if args.prompt:
        # 从文件读取提示词
        prompt_path = Path(args.prompt)
        if not prompt_path.exists():
            print(f"❌ 提示词文件不存在: {args.prompt}")
            sys.exit(1)
        prompt = prompt_path.read_text()
        
    elif args.prompt_text:
        # 直接使用提示词文本
        prompt = args.prompt_text
        
    elif args.scene or args.style:
        # 使用参数化输入
        params = {}
        if args.scene: params["场景方向"] = args.scene
        if args.style: params["摄影风格"] = args.style
        if args.clothing: params["服装方向"] = args.clothing
        if args.temperament: params["气质标签"] = args.temperament
        if args.body_type: params["身形方向"] = args.body_type
        if args.facial: params["五官方向"] = args.facial
        if args.pose: params["姿态动作"] = args.pose
        if args.lighting: params["光线氛围"] = args.lighting
        if args.filter: params["滤镜效果"] = args.filter
        if args.camera: params["镜头方向"] = args.camera
        if args.extra: params["补充要求"] = args.extra
        
        prompt = build_prompt_from_params(params)
        
    else:
        print("❌ 请提供提示词 (--prompt, --prompt-text 或参数化输入)")
        parser.print_help()
        sys.exit(1)
    
    if not args.quiet:
        print("=" * 50)
        print("🎨 GPT Image 2 女性肖像海报生成器")
        print("=" * 50)
        print()
        print("📝 提示词预览:")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
        print()
    
    # 生成图片
    success = generate_portrait(
        prompt=prompt,
        output_path=args.output,
        ratio=args.ratio,
        model=args.model,
        verbose=not args.quiet
    )
    
    if success:
        if not args.quiet:
            print()
            print("🎉 生成完成！")
        sys.exit(0)
    else:
        if not args.quiet:
            print()
            print("💥 生成失败，请检查配置和网络")
        sys.exit(1)


if __name__ == "__main__":
    main()
