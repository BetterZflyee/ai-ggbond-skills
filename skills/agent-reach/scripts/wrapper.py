import sys
import os
import subprocess
import shutil

# Add parent directory to sys.path to allow importing agent_reach
current_dir = os.path.dirname(os.path.abspath(__file__))
skill_root = os.path.dirname(current_dir)
sys.path.insert(0, skill_root)

REQUIRED_PACKAGES = [
    "requests",
    "feedparser",
    "python-dotenv",
    "loguru",
    "pyyaml",
    "rich",
    "yt-dlp",
    "browser-cookie3"
]

def install_dependencies():
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def main():
    # Check dependencies
    try:
        import requests
        import feedparser
        import dotenv
        import loguru
        import yaml
        import rich
        import yt_dlp
        import browser_cookie3
    except ImportError:
        install_dependencies()

    # Import CLI main
    try:
        from agent_reach.cli import main as cli_main
    except ImportError as e:
        print(f"Failed to import agent_reach: {e}")
        print(f"sys.path: {sys.path}")
        sys.exit(1)
    
    # Run CLI
    if len(sys.argv) == 1:
        # If no args, show help
        sys.argv.append("--help")
        
    cli_main()

if __name__ == "__main__":
    main()
