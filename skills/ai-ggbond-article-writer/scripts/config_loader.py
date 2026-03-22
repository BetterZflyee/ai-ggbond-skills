#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器 - 支持用户级和项目级配置
类似 .ai-ggbond-skills 的配置结构

加载优先级（高优先级覆盖低优先级）：
1. 环境变量 (os.environ)
2. 项目级配置: ./.ai-ggbond-skills/.env
3. 用户级配置: ~/.ai-ggbond-skills/.env
4. 技能目录配置: {skill_dir}/.env (向后兼容)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional


def get_config_dir(level: str = "user") -> Path:
    """
    获取配置目录路径

    Args:
        level: "user" 或 "project"

    Returns:
        Path 对象
    """
    if level == "user":
        home = Path.home()
        return home / ".ai-ggbond-skills"
    else:
        return Path.cwd() / ".ai-ggbond-skills"


def get_env_file_path(level: str = "user") -> Path:
    """
    获取环境变量文件路径

    Args:
        level: "user" 或 "project"

    Returns:
        Path 对象
    """
    return get_config_dir(level) / ".env"


def get_skill_env_path() -> Path:
    """
    获取技能目录下的 .env 文件路径（向后兼容）

    Returns:
        Path 对象
    """
    script_dir = Path(__file__).parent
    return script_dir.parent / ".env"


def load_env_file(env_path: Path) -> Dict[str, str]:
    """
    加载单个 .env 文件

    Args:
        env_path: 文件路径

    Returns:
        环境变量字典
    """
    env: Dict[str, str] = {}

    if not env_path.exists():
        return env

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 去除引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    if key and value:
                        env[key] = value
    except Exception as e:
        print(f"⚠️  加载环境变量文件失败 {env_path}: {e}", file=sys.stderr)

    return env


def load_all_env() -> Dict[str, str]:
    """
    加载所有层级的环境变量（按优先级合并）

    优先级（高到低）：
    1. 系统环境变量 (os.environ)
    2. 项目级配置: ./.ai-ggbond-skills/.env
    3. 用户级配置: ~/.ai-ggbond-skills/.env
    4. 技能目录配置: {skill_dir}/.env (向后兼容)

    Returns:
        合并后的环境变量字典
    """
    # 从技能目录配置开始（最低优先级，向后兼容）
    merged_env = load_env_file(get_skill_env_path())

    # 加载用户级配置（覆盖技能目录配置）
    user_env = load_env_file(get_env_file_path("user"))
    merged_env.update(user_env)

    # 加载项目级配置（覆盖用户级）
    project_env = load_env_file(get_env_file_path("project"))
    merged_env.update(project_env)

    # 系统环境变量最高优先级
    for key, value in os.environ.items():
        if value:
            merged_env[key] = value

    return merged_env


def apply_env_to_os(env: Optional[Dict[str, str]] = None) -> None:
    """
    将环境变量应用到 os.environ

    Args:
        env: 环境变量字典，如果为 None 则调用 load_all_env()
    """
    if env is None:
        env = load_all_env()

    for key, value in env.items():
        if key not in os.environ:
            os.environ[key] = value


def check_config_exists(level: str = "user") -> bool:
    """
    检查指定级别的配置是否存在

    Args:
        level: "user" 或 "project"

    Returns:
        是否存在
    """
    return get_env_file_path(level).exists()


def get_config_status() -> Dict[str, bool]:
    """
    获取配置状态

    Returns:
        包含 user、project 和 skill 配置存在状态的字典
    """
    return {
        "user": check_config_exists("user"),
        "project": check_config_exists("project"),
        "skill": get_skill_env_path().exists()
    }


def ensure_config_dir(level: str = "user") -> Path:
    """
    确保配置目录存在，如果不存在则创建

    Args:
        level: "user" 或 "project"

    Returns:
        Path 对象
    """
    config_dir = get_config_dir(level)
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def create_default_env(level: str = "user", api_key: Optional[str] = None) -> Path:
    """
    创建默认的 .env 文件

    Args:
        level: "user" 或 "project"
        api_key: API密钥（可选）

    Returns:
        创建的文件路径
    """
    config_dir = ensure_config_dir(level)
    env_file = config_dir / ".env"

    default_content = f"""# AI GGBond Skills - 文章撰写助手环境变量配置
# 配置级别: {level}
# 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# ============================================
# 云雾 API 配置（用于图片生成）
# ============================================
YUNWU_API_KEY={api_key or 'your-api-key-here'}
YUNWU_BASE_URL=https://yunwu.ai

# 默认模型配置
# 支持: gemini-3.1-flash-image-preview, qwen-image-max, dall-e-3, flux-1.1-pro, gpt-image-1, ideogram-3.0
YUNWU_DEFAULT_MODEL=gemini-3.1-flash-image-preview

# ============================================
# 可选配置
# ============================================
# 输出目录（覆盖默认路径）
# ARTICLE_OUTPUT_DIR=./articles

# 章节图片输出目录
# SECTION_IMAGE_OUTPUT_DIR=./outputs/section-images

# 默认图片尺寸
# SECTION_IMAGE_SIZE=1792x1024
"""

    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(default_content)

    return env_file


def print_config_guide() -> None:
    """打印配置指南"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🔧 配置指南                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  配置加载优先级（高优先级覆盖低优先级）：                    ║
║                                                              ║
║    1. 系统环境变量 (os.environ)                              ║
║    2. 项目级配置: ./.ai-ggbond-skills/.env                   ║
║    3. 用户级配置: ~/.ai-ggbond-skills/.env                   ║
║    4. 技能目录配置: {skill_dir}/.env (向后兼容)              ║
║                                                              ║
║  推荐配置方式：                                              ║
║                                                              ║
║    • 用户级配置 (~/.ai-ggbond-skills/.env)                   ║
║      适合个人使用，所有项目共享                              ║
║                                                              ║
║    • 项目级配置 (./.ai-ggbond-skills/.env)                   ║
║      适合团队协作，配置随项目走                              ║
║      建议添加到 .gitignore                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def interactive_setup() -> None:
    """交互式配置向导"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🚀 AI GGBond Article Writer - 首次使用配置               ║
╠══════════════════════════════════════════════════════════════╣
""")

    # 检查现有配置
    status = get_config_status()

    if any(status.values()):
        print("✅ 检测到已有配置：")
        if status["user"]:
            print(f"   • 用户级配置: {get_env_file_path('user')}")
        if status["project"]:
            print(f"   • 项目级配置: {get_env_file_path('project')}")
        if status["skill"]:
            print(f"   • 技能目录配置: {get_skill_env_path()}")
        print()

        choice = input("是否重新配置? (y/N): ").strip().lower()
        if choice != 'y':
            print("\n保持现有配置，退出配置向导。")
            return

    print("\n请选择配置级别：")
    print("  1. 用户级配置 (~/.ai-ggbond-skills/.env) - 推荐")
    print("     适合个人使用，所有项目共享配置")
    print()
    print("  2. 项目级配置 (./.ai-ggbond-skills/.env)")
    print("     适合团队协作，配置随项目走")
    print()

    while True:
        choice = input("请输入选项 (1/2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ 无效选项，请重新输入")

    level = "user" if choice == '1' else "project"

    print(f"\n📝 创建{level}级配置...")

    # 获取 API Key
    api_key = input("\n请输入云雾 API Key (直接回车跳过): ").strip()

    # 创建配置文件
    env_file = create_default_env(level, api_key if api_key else None)

    print(f"\n✅ 配置文件已创建: {env_file}")

    if level == "project":
        print("\n💡 提示: 建议将配置目录添加到 .gitignore")
        print("   echo '.ai-ggbond-skills/' >> .gitignore")

    print("\n🎉 配置完成！你可以编辑配置文件添加更多选项：")
    print(f"   {env_file}")


if __name__ == "__main__":
    # 如果直接运行此脚本，启动交互式配置向导
    interactive_setup()
