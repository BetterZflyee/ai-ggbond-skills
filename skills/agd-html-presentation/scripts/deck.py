#!/usr/bin/env python3
"""初始化可编辑工程，并将原生 ESM 运行时/场景合并为单文件 HTML。"""
import argparse
import html
import json
from pathlib import Path
import re
import shutil

SKILL = Path(__file__).resolve().parent.parent


def write_new(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(content)


def init_project(args):
    root = Path(args.project).expanduser().resolve()
    if args.engine in ('interactive', 'cinematic'):
        filename = 'presentation.html' if args.engine == 'interactive' else 'film.html'
        files = [filename, 'project.json']
        if args.engine == 'interactive':
            files.append('interactive-audio.js')
        collisions = [str(root / f) for f in files if (root / f).exists()]
        if collisions:
            raise SystemExit('已有工程文件，未覆盖：\n' + '\n'.join(collisions))
        template = SKILL / ('assets/interactive-starter.html' if args.engine == 'interactive' else 'assets/cinematic-starter.html')
        if not template.is_file():
            raise SystemExit('缺少对应的HTML起点：' + str(template))
        source = template.read_text(encoding='utf-8')
        if args.engine == 'interactive':
            audio = (SKILL / 'assets/interactive-audio.js').read_text(encoding='utf-8')
            source = source.replace('__AUDIO_RUNTIME__', inline_module(audio, 'interactive-audio'))
        source = source.replace('__TOPIC_HTML__', html.escape(args.topic, quote=True))
        source = re.sub(r'<title(?:\s[^>]*)?>.*?</title>', lambda _: '<title>' + html.escape(args.topic, quote=True) + '</title>', source, count=1, flags=re.S|re.I)
        root.mkdir(parents=True, exist_ok=True)
        if args.engine == 'interactive':
            write_new(root / 'interactive-audio.js', audio)
        write_new(root / filename, source)
        write_new(root / 'project.json', json.dumps({
            'topic': args.topic, 'title': args.topic, 'version': '1.0',
            'engine': args.engine, 'film': filename,
            **({'audioRuntime': 'interactive-audio.js'} if args.engine == 'interactive' else {}),
            'note': '交互音画起点；正式作品按主题重新设计世界、声景、对象、相机与节拍。' if args.engine == 'interactive' else '显式选用的音画时间线实验；正式作品按主题重新创作。'
        }, ensure_ascii=False, indent=2) + '\n')
        print(root)
        return
    files = ['runtime.js', 'deck.js', 'shell.html', 'project.json']
    collisions = [str(root / f) for f in files if (root / f).exists()]
    if collisions:
        raise SystemExit('已有工程文件，未覆盖：\n' + '\n'.join(collisions))
    root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILL / 'assets/runtime.js', root / 'runtime.js')
    shutil.copy2(SKILL / 'assets/shell.html', root / 'shell.html')
    topic_js = json.dumps(args.topic, ensure_ascii=False).replace('<', '\\u003c')
    starter = (SKILL / 'assets/scene-starter.js').read_text(encoding='utf-8')
    write_new(root / 'deck.js', starter.replace('__TOPIC_JSON__', topic_js))
    write_new(root / 'project.json', json.dumps({
        'topic': args.topic, 'title': args.topic, 'version': '1.0', 'engine': 'flat',
        'runtime': 'runtime.js', 'scenes': 'deck.js', 'shell': 'shell.html',
        'note': '示范场景用于验证运行接口；正式作品按主题重新创作。'
    }, ensure_ascii=False, indent=2) + '\n')
    print(root)


def inline_module(source, label):
    if re.search(r'^\s*(?:import\s|export\s+\*|export\s*\{)', source, re.M):
        raise SystemExit(f'{label} 含外部模块引用；先自行打包依赖，或改为无依赖场景模块。')
    source = re.sub(r'(^\s*)export\s+(?=(?:async\s+)?(?:function|class|const|let|var)\b)', r'\1', source, flags=re.M)
    if re.search(r'^\s*export\s', source, re.M):
        raise SystemExit(f'{label} 包含不支持的 export 形式。')
    return re.sub(r'</script', r'<\\/script', source, flags=re.I)


def build(args):
    root = Path(args.project).expanduser().resolve()
    config = json.loads((root / 'project.json').read_text(encoding='utf-8'))
    target = Path(args.output).expanduser().resolve() if args.output else root / f"presentation-V{config.get('version', '1.0')}.html"
    if target.exists():
        raise SystemExit(f'文件已存在，请递增版本或选择新的输出路径：{target}')
    if config.get('engine') in ('interactive', 'cinematic'):
        source = (root / config.get('film', 'film.html')).read_text(encoding='utf-8')
        if config.get('audioRuntime'):
            audio = inline_module((root / config['audioRuntime']).read_text(encoding='utf-8'), 'interactive-audio')
            source, count = re.subn(r'(<script id="agd-audio-runtime">).*?(</script>)', lambda m: m.group(1) + audio + m.group(2), source, count=1, flags=re.S)
            if count != 1:
                raise SystemExit('未找到内联声音模块位置 agd-audio-runtime。')
        result = re.sub(r'<title>.*?</title>', lambda _: '<title>' + html.escape(config.get('title', config['topic']), quote=True) + '</title>', source, count=1, flags=re.S|re.I)
        write_new(target, result)
        print(target)
        return
    runtime = inline_module((root / config.get('runtime', 'runtime.js')).read_text(encoding='utf-8'), 'runtime')
    scenes = inline_module((root / config.get('scenes', 'deck.js')).read_text(encoding='utf-8'), 'scenes')
    shell = (root / config.get('shell', 'shell.html')).read_text(encoding='utf-8')
    required = ['__TITLE__', '__RUNTIME__', '__SCENES__']
    if any(key not in shell for key in required):
        raise SystemExit('网页壳缺少 TITLE/RUNTIME/SCENES 插入位置。')
    result = shell.replace('__TITLE__', html.escape(config.get('title', config['topic']), quote=True))
    result = result.replace('__RUNTIME__', runtime).replace('__SCENES__', scenes)
    write_new(target, result)
    print(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='创建编辑工程，保留已有内容')
    init.add_argument('--topic', required=True)
    init.add_argument('--project', required=True)
    init.add_argument('--engine', choices=['interactive', 'cinematic', 'flat'], default='interactive')
    init.set_defaults(run=init_project)
    bundle = sub.add_parser('build', help='合并为独立 HTML')
    bundle.add_argument('--project', required=True)
    bundle.add_argument('--output')
    bundle.set_defaults(run=build)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
