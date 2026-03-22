# -*- coding: utf-8 -*-
"""
Agent Reach CLI — installer, doctor, and configuration tool.

Usage:
    agent-reach install --env=auto
    agent-reach doctor
    agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
    agent-reach setup
"""

import sys
import argparse
import json
import os

# Fix Windows console encoding — emoji/CJK characters crash on cp936/cp1252
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from agent_reach import __version__


def _configure_logging(verbose: bool = False):
    """Suppress loguru output unless --verbose is set."""
    from loguru import logger
    logger.remove()  # Remove default stderr handler
    if verbose:
        logger.add(sys.stderr, level="INFO")


def main():
    parser = argparse.ArgumentParser(
        prog="agent-reach",
        description="👁️ Give your AI Agent eyes to see the entire internet",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    parser.add_argument("--version", action="version", version=f"Agent Reach v{__version__}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── read ──
    # ── setup ──
    sub.add_parser("setup", help="Interactive configuration wizard")

    # ── install ──
    p_install = sub.add_parser("install", help="One-shot installer with flags")
    p_install.add_argument("--env", choices=["local", "server", "auto"], default="auto",
                           help="Environment: local, server, or auto-detect")
    p_install.add_argument("--proxy", default="",
                           help="Residential proxy for Reddit/Bilibili (http://user:pass@ip:port)")
    p_install.add_argument("--safe", action="store_true",
                           help="Safe mode: skip automatic system changes, show what's needed instead")
    p_install.add_argument("--dry-run", action="store_true",
                           help="Show what would be done without making any changes")

    # ── configure ──
    p_conf = sub.add_parser("configure", help="Set a config value or auto-extract from browser")
    p_conf.add_argument("key", nargs="?", default=None,
                        choices=["proxy", "github-token", "groq-key",
                                 "twitter-cookies", "youtube-cookies"],
                        help="What to configure (omit if using --from-browser)")
    p_conf.add_argument("value", nargs="*", help="The value(s) to set")
    p_conf.add_argument("--from-browser", metavar="BROWSER",
                        choices=["chrome", "firefox", "edge", "brave", "opera"],
                        help="Auto-extract ALL platform cookies from browser (chrome/firefox/edge/brave/opera)")

    # ── doctor ──
    sub.add_parser("doctor", help="Check platform availability")

    # ── check-update ──
    sub.add_parser("check-update", help="Check for new versions and changes")

    # ── watch ──
    sub.add_parser("watch", help="Quick health check + update check (for scheduled tasks)")

    # ── version ──
    sub.add_parser("version", help="Show version")

    args = parser.parse_args()

    # Suppress loguru noise unless --verbose
    _configure_logging(getattr(args, "verbose", False))

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "version":
        print(f"Agent Reach v{__version__}")
        sys.exit(0)

    if args.command == "doctor":
        _cmd_doctor()
    elif args.command == "check-update":
        _cmd_check_update()
    elif args.command == "watch":
        _cmd_watch()
    elif args.command == "setup":
        _cmd_setup()
    elif args.command == "install":
        _cmd_install(args)
    elif args.command == "configure":
        _cmd_configure(args)


# ── Command handlers ────────────────────────────────


def _cmd_install(args):
    """One-shot deterministic installer."""
    import os
    from agent_reach.config import Config
    from agent_reach.doctor import check_all, format_report

    safe_mode = args.safe
    dry_run = args.dry_run

    config = Config()
    print()
    print("👁️  Agent Reach Installer")
    print("=" * 40)

    if dry_run:
        print("🔍 DRY RUN — showing what would be done (no changes)")
        print()
    if safe_mode:
        print("🛡️  SAFE MODE — skipping automatic system changes")
        print()

    # Auto-detect environment
    env = args.env
    if env == "auto":
        env = _detect_environment()
    
    if env == "server":
        print(f"📡 Environment: Server/VPS (auto-detected)")
    else:
        print(f"💻 Environment: Local computer (auto-detected)")

    # Apply explicit flags
    if args.proxy:
        if dry_run:
            print(f"[dry-run] Would configure proxy for Reddit + Bilibili")
        else:
            config.set("reddit_proxy", args.proxy)
            config.set("bilibili_proxy", args.proxy)
            print(f"✅ Proxy configured for Reddit + Bilibili")

    # ── Install system dependencies ──
    print()
    if dry_run:
        _install_system_deps_dryrun()
    elif safe_mode:
        _install_system_deps_safe()
    else:
        _install_system_deps()

    # ── mcporter (for Exa search + XiaoHongShu) ──
    print()
    if dry_run:
        print("📦 [dry-run] Would install mcporter and configure Exa search")
    elif safe_mode:
        _install_mcporter_safe()
    else:
        _install_mcporter()

    # Auto-import cookies on local computers
    if env == "local" and not safe_mode and not dry_run:
        print()
        print("🍪 Trying to import cookies from browser...")
        try:
            from agent_reach.cookie_extract import configure_from_browser
            results = configure_from_browser("chrome", config)
            found = False
            for platform, success, message in results:
                if success:
                    print(f"  ✅ {platform}: {message}")
                    found = True
            if not found:
                # Try firefox
                results = configure_from_browser("firefox", config)
                for platform, success, message in results:
                    if success:
                        print(f"  ✅ {platform}: {message}")
                        found = True
            if not found:
                print("  ⬜ No cookies found (normal if you haven't logged into these sites)")
        except Exception:
            print("  ⬜ Could not read browser cookies (browser might be open)")
    elif env == "local" and safe_mode:
        print()
        print("🍪 Skipped auto cookie import (safe mode).")
        print("   To import manually: agent-reach configure --from-browser chrome")
    elif env == "local" and dry_run:
        print()
        print("🍪 [dry-run] Would try to import cookies from Chrome/Firefox")

    # Environment-specific advice
    if env == "server":
        print()
        print("💡 Tip: Reddit and Bilibili block server IPs.")
        print("   Reddit search still works via Exa (free).")
        print("   For full access: agent-reach configure proxy http://user:pass@ip:port")
        print("   Cheap option: https://www.webshare.io ($1/month)")

    # Test channels
    if not dry_run:
        print()
        print("Testing channels...")
        results = check_all(config)
        ok = sum(1 for r in results.values() if r["status"] == "ok")
        total = len(results)

        # Final status
        print()
        print(format_report(results))
        print()

        # ── Install agent skill ──
        _install_skill()

        print(f"✅ Installation complete! {ok}/{total} channels active.")

        if ok < total:
            print()
            print("🤖 Some channels are not active yet. If you're an AI Agent, try to fix them yourself — then run `agent-reach doctor` again.")
    else:
        print()
        print("🔍 Dry run complete. No changes were made.")


def _install_skill():
    """Install Agent Reach as an agent skill (OpenClaw / Claude Code)."""
    import os
    import importlib.resources

    # Determine skill install path
    skill_dirs = [
        os.path.expanduser("~/.openclaw/skills"),   # OpenClaw
        os.path.expanduser("~/.claude/skills"),      # Claude Code (if exists)
        os.path.expanduser("~/.agents/skills"),      # Generic agents
    ]

    installed = False
    for skill_dir in skill_dirs:
        if os.path.isdir(skill_dir):
            target = os.path.join(skill_dir, "agent-reach")
            try:
                os.makedirs(target, exist_ok=True)
                # Read SKILL.md from package data
                skill_md = importlib.resources.files("agent_reach").joinpath("skill", "SKILL.md").read_text()
                with open(os.path.join(target, "SKILL.md"), "w") as f:
                    f.write(skill_md)
                platform_name = "OpenClaw" if "openclaw" in skill_dir else "Claude Code" if "claude" in skill_dir else "Agent"
                print(f"🧩 Skill installed for {platform_name}: {target}")
                installed = True
            except Exception:
                pass

    if not installed:
        # No known skill directory found — create for OpenClaw by default
        target = os.path.expanduser("~/.openclaw/skills/agent-reach")
        try:
            os.makedirs(target, exist_ok=True)
            skill_md = importlib.resources.files("agent_reach").joinpath("skill", "SKILL.md").read_text()
            with open(os.path.join(target, "SKILL.md"), "w") as f:
                f.write(skill_md)
            print(f"🧩 Skill installed: {target}")
        except Exception:
            print("  ⬜ Could not install agent skill (optional)")


def _install_system_deps():
    """Install system-level dependencies: gh CLI, Node.js (for mcporter)."""
    import shutil
    import subprocess
    import platform

    print("🔧 Checking system dependencies...")

    # ── gh CLI ──
    if shutil.which("gh"):
        print("  ✅ gh CLI already installed")
    else:
        print("  📥 Installing gh CLI...")
        os_type = platform.system().lower()
        if os_type == "linux":
            try:
                # Official GitHub method for Linux
                cmds = [
                    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null",
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null',
                    "apt-get update -qq 2>/dev/null",
                    "apt-get install -y -qq gh 2>/dev/null",
                ]
                for cmd in cmds:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=60, encoding='utf-8', errors='replace')
                if shutil.which("gh"):
                    print("  ✅ gh CLI installed")
                else:
                    print("  ⚠️  gh CLI install failed. You can try: snap install gh, or download from https://github.com/cli/cli/releases")
            except Exception:
                print("  ⚠️  gh CLI install failed. You can try: snap install gh, or download from https://github.com/cli/cli/releases")
        elif os_type == "darwin":
            if shutil.which("brew"):
                try:
                    subprocess.run(["brew", "install", "gh"], capture_output=True, timeout=120, encoding='utf-8', errors='replace')
                    if shutil.which("gh"):
                        print("  ✅ gh CLI installed")
                    else:
                        print("  ⚠️  gh CLI install failed. Try: brew install gh")
                except Exception:
                    print("  ⚠️  gh CLI install failed. Try: brew install gh")
            else:
                print("  ⚠️  gh CLI not found. Install: https://cli.github.com")
        else:
            print("  ⚠️  gh CLI not found. Install: https://cli.github.com")

    # ── Node.js (needed for mcporter) ──
    if shutil.which("node") and shutil.which("npm"):
        print("  ✅ Node.js already installed")
    else:
        print("  📥 Installing Node.js...")
        try:
            # Use NodeSource for quick install
            subprocess.run(
                "curl -fsSL https://deb.nodesource.com/setup_22.x | bash - 2>/dev/null && apt-get install -y -qq nodejs 2>/dev/null",
                shell=True, capture_output=True, timeout=120, encoding='utf-8', errors='replace'
            )
            if shutil.which("node"):
                print("  ✅ Node.js installed")
            else:
                print("  ⚠️  Node.js install failed. Try: apt install nodejs npm, or nvm install 22, or download from https://nodejs.org")
        except Exception:
            print("  ⚠️  Node.js install failed. Try: apt install nodejs npm, or nvm install 22, or download from https://nodejs.org")

    # ── bird CLI (for Twitter search) ──
    if shutil.which("bird") or shutil.which("birdx"):
        print("  ✅ bird CLI already installed")
    else:
        if shutil.which("npm"):
            try:
                subprocess.run(
                    ["npm", "install", "-g", "@steipete/bird"],
                    capture_output=True, text=True, timeout=120,
                    shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace'
                )
                if shutil.which("bird"):
                    print("  ✅ bird CLI installed (Twitter search + timeline)")
                else:
                    print("  ⬜ bird CLI install failed (optional — Twitter reading still works via Jina)")
            except Exception:
                print("  ⬜ bird CLI install failed (optional — Twitter reading still works via Jina)")
        else:
            print("  ⬜ bird CLI requires Node.js (optional — Twitter reading still works via Jina)")

    # ── undici (proxy support for Node.js fetch) ──
    if shutil.which("npm"):
        try:
            npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=5, shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace').stdout.strip()
            undici_path = os.path.join(npm_root, "undici", "index.js") if npm_root else ""
            if os.path.exists(undici_path):
                print("  ✅ undici already installed (Node.js proxy support)")
            else:
                try:
                    subprocess.run(["npm", "install", "-g", "undici"], capture_output=True, text=True, timeout=60, shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace')
                    print("  ✅ undici installed (Node.js proxy support)")
                except Exception:
                    print("  ⬜ undici install failed (optional — bird may not work behind proxies)")
        except Exception as e:
            print(f"  ⚠️  Error checking npm root: {e}")


def _install_system_deps_safe():
    """Safe mode: check what's installed, print instructions for what's missing."""
    import shutil

    print("🔧 Checking system dependencies (safe mode — no auto-install)...")

    deps = [
        ("gh", ["gh"], "GitHub CLI", "https://cli.github.com — or: apt install gh / brew install gh"),
        ("node", ["node", "npm"], "Node.js", "https://nodejs.org — or: apt install nodejs npm"),
        ("bird", ["bird", "birdx"], "bird CLI (Twitter)", "npm install -g @steipete/bird"),
    ]

    missing = []
    for name, binaries, label, install_hint in deps:
        found = any(shutil.which(b) for b in binaries)
        if found:
            print(f"  ✅ {label} already installed")
        else:
            print(f"  ⬜ {label} not found")
            missing.append((label, install_hint))

    if missing:
        print()
        print("  To install missing dependencies manually:")
        for label, hint in missing:
            print(f"    {label}: {hint}")
    else:
        print("  All system dependencies are installed!")


def _install_system_deps_dryrun():
    """Dry-run: just show what would be checked/installed."""
    import shutil

    print("🔧 [dry-run] System dependency check:")

    checks = [
        ("gh CLI", ["gh"], "apt install gh / brew install gh"),
        ("Node.js", ["node"], "curl NodeSource setup | bash + apt install nodejs"),
        ("bird CLI", ["bird", "birdx"], "npm install -g @steipete/bird"),
    ]

    for label, binaries, method in checks:
        found = any(shutil.which(b) for b in binaries)
        if found:
            print(f"  ✅ {label}: already installed, skip")
        else:
            print(f"  📥 {label}: would install via: {method}")


def _install_mcporter():
    """Install mcporter and configure Exa + XiaoHongShu MCP servers."""
    import shutil
    import subprocess

    print("📦 Setting up mcporter (search + XiaoHongShu backend)...")

    if shutil.which("mcporter"):
        print("  ✅ mcporter already installed")
    else:
        # Check for npm/npx
        if not shutil.which("npm") and not shutil.which("npx"):
            print("  ⚠️  mcporter requires Node.js. Install Node.js first:")
            print("     https://nodejs.org/ or: curl -fsSL https://fnm.vercel.app/install | bash")
            return

        print("  📥 Installing mcporter...")
        try:
            subprocess.run(["npm", "install", "-g", "mcporter"], capture_output=True, text=True, timeout=60, shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace')
            if shutil.which("mcporter"):
                print("  ✅ mcporter installed")
            else:
                print("  ⚠️  mcporter install failed. Try: npm install -g mcporter")
                return
        except Exception:
            print("  ⚠️  mcporter install failed. Try: npm install -g mcporter")
            return

    # Configure Exa (free)
    try:
        r = subprocess.run(["mcporter", "list"], capture_output=True, text=True, timeout=5, shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace')
        if "exa" not in r.stdout.lower():
            print("  ⚙️  Configuring Exa search (free)...")
            subprocess.run(["mcporter", "config", "add", "exa", "https://mcp.exa.ai/mcp"],
                           capture_output=True, timeout=10, shell=platform.system().lower() == "windows", encoding='utf-8', errors='replace')
            print("  ✅ Exa search configured")
        else:
            print("  ✅ Exa search already configured")
    except Exception:
        print("  ⬜ Could not configure Exa search (optional)")


def _install_mcporter_safe():
    import shutil
    print("📦 Checking mcporter (safe mode)...")
    if shutil.which("mcporter"):
        print("  ✅ mcporter already installed")
    else:
        print("  ⬜ mcporter not found. Install: npm install -g mcporter")


def _detect_environment():
    """Detect if running on local computer or server."""
    # Heuristics:
    # 1. Has display? (Linux)
    # 2. Has known desktop paths? (Windows/Mac)
    # 3. User name is root/ubuntu/ec2-user?
    # Default to local unless strong evidence of server.
    
    if os.environ.get("DISPLAY"):
        return "local"
    
    user = os.environ.get("USER", "").lower()
    if user in ("root", "ubuntu", "ec2-user", "admin"):
        # Could be server, but also WSL.
        # Check for desktop directories
        home = os.path.expanduser("~")
        if os.path.isdir(os.path.join(home, "Desktop")) or os.path.isdir(os.path.join(home, "Downloads")):
            return "local"
        return "server"
        
    return "local"  # Default safe assumption


def _cmd_doctor():
    """Run diagnostics."""
    from agent_reach.doctor import check_all, format_report
    from agent_reach.config import Config

    config = Config()
    results = check_all(config)
    print(format_report(results))


def _cmd_check_update():
    """Check for new versions."""
    import requests
    print("Checking for updates...")
    try:
        r = requests.get("https://pypi.org/pypi/agent-reach/json", timeout=5)
        latest = r.json()["info"]["version"]
        if latest != __version__:
            print(f"🚀 New version available: {latest} (current: {__version__})")
            print("   Update: pip install -U agent-reach")
        else:
            print("✅ You are using the latest version.")
    except Exception:
        print("Could not check for updates.")


def _cmd_watch():
    """Quick check suitable for startup."""
    from agent_reach.doctor import check_all
    from agent_reach.config import Config
    
    config = Config()
    results = check_all(config)
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"Agent Reach: {ok}/{len(results)} channels active. (Run `agent-reach doctor` for details)")


def _cmd_setup():
    """Interactive setup wizard."""
    print("Interactive setup not fully implemented in CLI yet.")
    print("Please use `agent-reach install` for auto-setup.")
    print("Or `agent-reach configure` to set specific keys.")


def _cmd_configure(args):
    """Configure settings."""
    from agent_reach.config import Config
    config = Config()

    if args.from_browser:
        browser = args.from_browser
        print(f"Extracting cookies from {browser}...")
        try:
            from agent_reach.cookie_extract import configure_from_browser
            results = configure_from_browser(browser, config)
            for platform, success, message in results:
                if success:
                    print(f"✅ {platform}: {message}")
                else:
                    print(f"❌ {platform}: {message}")
        except Exception as e:
            print(f"Error: {e}")
        return

    if not args.key:
        print("Usage: agent-reach configure KEY VALUE")
        print("   or: agent-reach configure --from-browser chrome")
        return

    key = args.key
    val = " ".join(args.value)

    if key == "twitter-cookies":
        # Parse "auth_token=xxx; ct0=yyy"
        parts = val.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.strip().split("=", 1)
                if k == "auth_token":
                    config.set("twitter_auth_token", v)
                elif k == "ct0":
                    config.set("twitter_ct0", v)
        print("✅ Twitter cookies configured.")
        
    elif key == "proxy":
        config.set("reddit_proxy", val)
        config.set("bilibili_proxy", val)
        print("✅ Proxy configured for Reddit + Bilibili.")
        
    elif key == "github-token":
        config.set("github_token", val)
        print("✅ GitHub token configured.")
        
    else:
        config.set(key, val)
        print(f"✅ Configured {key}.")


if __name__ == "__main__":
    main()
