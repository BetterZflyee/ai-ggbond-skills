#!/usr/bin/env python3
"""
Defuddle Skill Wrapper
Extract clean article content from web pages using defuddle CLI.
"""

import subprocess
import sys
import argparse
import json
import os
import shutil


def get_defuddle_command():
    """Find defuddle command, checking common npm global locations."""
    # First check if defuddle is in PATH
    defuddle_path = shutil.which("defuddle")
    if defuddle_path:
        return defuddle_path
    
    # Check common npm global locations on Windows
    npm_global_paths = [
        os.path.expanduser("~/AppData/Roaming/npm/defuddle.cmd"),
        os.path.expanduser("~/AppData/Roaming/npm/defuddle"),
        "C:/Program Files/nodejs/defuddle.cmd",
        "C:/Program Files/nodejs/defuddle",
    ]
    
    for path in npm_global_paths:
        if os.path.exists(path):
            return path
    
    return "defuddle"  # Fallback to just the command name


def run_defuddle(url: str, output_format: str = "markdown", property_name: str = None, output_file: str = None, debug: bool = False):
    """
    Run defuddle CLI to extract content from a URL.
    
    Args:
        url: The URL or file path to parse
        output_format: 'markdown' or 'json'
        property_name: Extract a single field (title, author, published, etc.)
        output_file: Save output to file
        debug: Enable verbose logging
    """
    # Build the command
    defuddle_cmd = get_defuddle_command()
    cmd = [defuddle_cmd, "parse", url]
    
    if output_format == "json":
        cmd.append("-j")
    else:
        cmd.append("-m")
    
    if property_name:
        cmd.extend(["-p", property_name])
    
    if output_file:
        cmd.extend(["-o", output_file])
    
    if debug:
        cmd.append("--debug")
    
    try:
        # Run defuddle command with UTF-8 encoding
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        
        return {
            "success": True,
            "output": result.stdout,
            "error": None
        }
    
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "output": e.stdout,
            "error": e.stderr
        }
    
    except FileNotFoundError:
        return {
            "success": False,
            "output": None,
            "error": "defuddle CLI not found. Please install it first: npm install -g defuddle"
        }


def main():
    parser = argparse.ArgumentParser(description="Defuddle Skill - Extract clean article content")
    parser.add_argument("url", help="URL or file path to parse")
    parser.add_argument("-m", "--markdown", action="store_true", help="Output as Markdown (default)")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON with metadata")
    parser.add_argument("-o", "--output", help="Save output to file")
    parser.add_argument("-p", "--property", help="Extract single field (title, author, published, etc.)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Determine output format
    output_format = "json" if args.json else "markdown"
    
    # Run defuddle
    result = run_defuddle(
        url=args.url,
        output_format=output_format,
        property_name=args.property,
        output_file=args.output,
        debug=args.debug
    )
    
    if result["success"]:
        print(result["output"])
        return 0
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        if result["output"]:
            print(result["output"])
        return 1


if __name__ == "__main__":
    sys.exit(main())
