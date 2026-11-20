#!/usr/bin/env python3
"""Plan/install sticker + layout packages and narrowly scoped publishing/routing updates."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
NAME = 'ai-ggbond-sticker-writer'
LAYOUT = 'ai-ggbond-wechat-layout'
START = '<!-- BEGIN AI-GGBOND-STICKER-INTEGRATION -->'
END = '<!-- END AI-GGBOND-STICKER-INTEGRATION -->'
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'node_modules')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hashes(root):
    if not root.exists():
        return None
    return {str(p.relative_to(root)): sha(p.read_bytes()) for p in sorted(root.rglob('*'))
            if p.is_file() and not any(x in p.parts for x in ['__pycache__', '.git', 'node_modules']) and p.suffix != '.pyc'}


def route(text, sticker, layout, kind):
    content = f'{START}\n## 公众号贴图与信息卡衔接\n\n'
    content += f'涉及短贴图、连续多图、证据卡或长文插图复用时，读取 `{sticker}/SKILL.md`；长文精排读取 `{layout}/SKILL.md`。当前用户要求及上述维护模块优先于后文历史模板。\n\n'
    if kind == 'publisher':
        content += ('原生贴图使用 `newspic-bundle.json --type newspic`：纯文本、第一张封面及有序图片独立交接；'
                    '先用 `--dry-run` 检查。未完成核对、图片哈希改变、数量缺失或任一上传失败时停止创建草稿。'
                    '长文章继续用精排 `article.html` 与 `handoff.json`，不将短正文套文章主题。'
                    '用户已有推送授权就继续相应操作并读回；历史接口/菜单失败不代表当前账号状态，不能称本地预检已发布。\n')
    elif kind == 'long-image':
        content += ('复用本技能的尺寸预设、纵向分组与接缝方法，将精确文字、来源和原图写入贴图计划。'
                    'Codex 用当前内置生图工具，Hermes 用当前 Profile 已配置且获授权的图像链路；用户已指定模型时遵从，'
                    '不因后文旧云雾模板自动换服务。实际生成与图片编辑遵从当前工具要求，拼接须有对应授权。'
                    '检查最终宽高、接缝、中文与手机可读性；分段计划和占位预览不能当成已完成长图。\n')
    else:
        content += ('复用本技能的选题研究、真实图片、人物叙事、去 AI 味、数据口径与个人品牌边界。'
                    '原生贴图另写短纯文本，长文保留完整正文；同一来源可复用到步骤、比较、时间线、数据和图片。'
                    '短贴图的 500 字是个人编辑预算，不套用于长文。已有标题、风格与生图授权直接沿用；'
                    '图片实际生成、中文核对和来源检查完成后再交接，封面不自动重复到长文正文。\n')
    content += END
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError('贴图入口标记不完整或重复')
        updated = re.sub(re.escape(START) + r'[\s\S]*?' + re.escape(END), lambda _: content, text, count=1)
        pattern = re.escape(START) + r'[\s\S]*?' + re.escape(END)
        assert re.sub(pattern, '', text) == re.sub(pattern, '', updated)
        return updated
    front = re.match(r'\A---\r?\n[\s\S]*?\r?\n---\r?\n', text)
    position = front.end() if front else 0
    insertion = '\n' + content + '\n\n'
    updated = text[:position] + insertion + text[position:]
    assert updated[:position] + updated[position + len(insertion):] == text
    return updated


def patched_api(original):
    spec = json.loads((ROOT / 'adapters/publisher-adapter.json').read_text())
    if sha(original) == spec['after_sha256']:
        return original
    if sha(original) != spec['before_sha256']:
        raise ValueError('发布器版本已变化；先重新核对适配补丁，拒绝覆盖现有实现')
    with tempfile.TemporaryDirectory(prefix='sticker-api-patch-') as tmp:
        file = Path(tmp) / 'wechat-api.ts'
        file.write_bytes(original)
        result = subprocess.run(['/usr/bin/patch', '-s', str(file), str(ROOT / 'adapters/wechat-api-sticker.patch')], capture_output=True, text=True)
        if result.returncode or sha(file.read_bytes()) != spec['after_sha256']:
            raise ValueError('发布器补丁校验失败，未修改安装目录')
        return file.read_bytes()


def protect(root):
    for p in [root, *root.rglob('*')]:
        if not p.is_symlink():
            p.chmod(0o700 if p.is_dir() else 0o600)


def atomic_write(path, data, mode=0o644):
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def install(home, layout_source, backup_root, apply=False, baseline=None):
    sticker_source = ROOT.resolve()
    layout_source = layout_source.resolve()
    if not (layout_source / 'SKILL.md').is_file():
        raise ValueError('必须提供已核对的公众号精排源码目录')
    if baseline:
        for item in json.loads(baseline.read_text()):
            if item['name'] == 'layout-source':
                continue
            if hashes(Path(item['path'])) != item['files']:
                raise ValueError('初始盘点后目录已变化，请保留变更并重新合并：' + item['path'])
    roots = [home / '.hermes/skills/creative', home / '.codex/skills', home / '.agents/skills']
    publishers = [home / '.hermes/skills/productivity/ai-ggbond-post-to-wechat', roots[1] / 'ai-ggbond-post-to-wechat', roots[2] / 'ai-ggbond-post-to-wechat']
    packages, files, skipped = [], [], []
    for root in roots:
        for source, name in [(sticker_source, NAME), (layout_source, LAYOUT)]:
            dest = root / name
            if dest.is_symlink():
                raise ValueError('安装目录为符号链接：' + str(dest))
            if dest.exists() and not re.search(r'^name:\s*' + name + r'\s*$', (dest / 'SKILL.md').read_text(), re.M):
                raise ValueError('目标不是指定 Skill：' + str(dest))
            if source != dest.resolve():
                packages.append({'source': source, 'path': dest, 'before': hashes(dest), 'after': hashes(source)})
    routes = []
    for i, root in enumerate(roots):
        writer_names = ['ai-ggbond-article-writer'] if i == 0 else ['ai-ggbond-artical-writer-codex']
        if i == 1:
            writer_names += ['ai-ggbond-article-writer']
        routes += [(root / name / 'SKILL.md', root, 'writer') for name in writer_names]
        routes += [(root / 'ai-ggbond-long-image-generator/SKILL.md', root, 'long-image')]
        routes += [(publishers[i] / 'SKILL.md', root, 'publisher')]
    for path, root, kind in routes:
        if not path.is_file():
            skipped.append(str(path)); continue
        before = path.read_bytes()
        after = route(before.decode('utf-8'), root / NAME, root / LAYOUT, kind).encode('utf-8')
        files.append({'path': path, 'before': before, 'after': after, 'kind': 'route', 'outside_marker_unchanged': True})
    helper = (ROOT / 'adapters/newspic-bundle.ts').read_bytes()
    for publisher in publishers:
        path = publisher / 'scripts/wechat-api.ts'
        if not path.is_file():
            skipped.append(str(path)); continue
        before = path.read_bytes()
        files.append({'path': path, 'before': before, 'after': patched_api(before), 'kind': 'publisher'})
        helper_path = publisher / 'scripts/newspic-bundle.ts'
        previous = helper_path.read_bytes() if helper_path.exists() else None
        if previous is not None and previous != helper:
            raise ValueError('发布器已有不同贴图适配器，请先合并：' + str(helper_path))
        files.append({'path': helper_path, 'before': previous, 'after': helper, 'kind': 'publisher'})
    legacy = json.loads((ROOT / 'adapters/legacy-hermes-entry.json').read_text())
    legacy_path = home / legacy['path']
    # A current repository checkout is a valid source, not a stale duplicate.
    # Identical SKILL.md entries are deduplicated by Hermes itself.
    if legacy_path.exists() and legacy_path.read_bytes() != (sticker_source / 'SKILL.md').read_bytes():
        before = legacy_path.read_bytes()
        if sha(before) != legacy['sha256']:
            raise ValueError('旧合集贴图入口已变化；先吸收新规则再处理同名冲突：' + str(legacy_path))
        retired = legacy_path.with_name(legacy['retired_name'])
        previous = retired.read_bytes() if retired.exists() else None
        if previous is not None and previous != before:
            raise ValueError('已存在不同历史入口存档，拒绝覆盖：' + str(retired))
        files.append({'path': retired, 'before': previous, 'after': before, 'kind': 'duplicate-entry', 'private': True})
        files.append({'path': legacy_path, 'before': before, 'after': None, 'kind': 'duplicate-entry'})
    if any(item['path'].is_symlink() for item in files):
        raise ValueError('文件目标为符号链接，请核对真实安装位置')
    summary = {'status': 'plan', 'packages': [{'source': str(p['source']), 'path': str(p['path']), 'files': len(p['after']), 'changed': p['before'] != p['after']} for p in packages],
               'files': [{'path': str(f['path']), 'kind': f['kind'], 'changed': f['before'] != f['after'], 'before_sha256': sha(f['before']) if f['before'] is not None else None, 'after_sha256': sha(f['after']) if f['after'] is not None else None, **({'outside_marker_unchanged': True} if f['kind'] == 'route' else {})} for f in files],
               'skipped': skipped, 'scope': 'six skill packages, marked routes, two publisher adapter files per environment and a hash-checked legacy entry rename; no credentials, model settings, gateways or remote writes'}
    if not apply:
        return summary
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = backup_root / ('install-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6])
    backup.mkdir(mode=0o700)
    for i, item in enumerate(packages):
        item['backup'] = backup / f'package-{i}'
        if item['path'].exists():
            shutil.copytree(item['path'], item['backup'], ignore=IGNORE)
    for i, item in enumerate(files):
        item['backup'] = backup / f'file-{i}'
        item['mode'] = stat.S_IMODE(item['path'].stat().st_mode) if item['path'].exists() else 0o644
        if item.get('private'):
            item['mode'] = 0o600
        if item['before'] is not None:
            item['backup'].write_bytes(item['before'])
    (backup / 'before.json').write_text(json.dumps({'packages': [{'path': str(p['path']), 'backup': str(p['backup']), 'files': p['before']} for p in packages], 'files': [{'path': str(f['path']), 'backup': str(f['backup']) if f['before'] is not None else None, 'mode': f['mode']} for f in files]}, ensure_ascii=False, indent=2))
    protect(backup)
    touched_packages, touched_files = [], []
    try:
        # Optimistic concurrency check after the backups, before any live edits.
        for item in packages:
            if hashes(item['path']) != item['before'] or hashes(item['source']) != item['after']:
                raise ValueError('安装期间包已变化：' + str(item['path']))
        for item in files:
            current = item['path'].read_bytes() if item['path'].exists() else None
            if current != item['before']:
                raise ValueError('安装期间文件已变化：' + str(item['path']))
        for item in packages:
            if item['before'] == item['after']:
                continue
            dest = item['path']; dest.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.' + dest.name + '-stage-', dir=dest.parent))
            try:
                shutil.copytree(item['source'], stage, dirs_exist_ok=True, ignore=IGNORE)
                if hashes(stage) != item['after']:
                    raise ValueError('暂存包哈希不一致')
                old = dest.with_name('.' + dest.name + '-old-' + uuid.uuid4().hex[:8]) if dest.exists() else None
                if old:
                    dest.rename(old)
                touched_packages.append((dest, old))
                stage.rename(dest)
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
        for item in files:
            if item['before'] == item['after']:
                continue
            touched_files.append(item)
            if item['after'] is None:
                item['path'].unlink()
            else:
                atomic_write(item['path'], item['after'], item['mode'])
        for item in packages:
            if hashes(item['path']) != item['after']:
                raise ValueError('安装后包读回失败：' + str(item['path']))
        for item in files:
            current = item['path'].read_bytes() if item['path'].exists() else None
            if current != item['after']:
                raise ValueError('安装后文件读回失败：' + str(item['path']))
    except Exception:
        for item in reversed(touched_files):
            if item['before'] is None:
                item['path'].unlink(missing_ok=True)
            else:
                atomic_write(item['path'], item['before'], item['mode'])
        for dest, old in reversed(touched_packages):
            if dest.exists():
                shutil.rmtree(dest)
            if old and old.exists():
                old.rename(dest)
        raise
    for dest, old in touched_packages:
        if old and old.exists():
            shutil.rmtree(old)
    result = {**summary, 'status': 'installed', 'backup': str(backup), 'readback_passed': True}
    (backup / 'installed.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    protect(backup)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--layout-source', type=Path, required=True)
    parser.add_argument('--backup-dir', type=Path, required=True)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.home.resolve(), args.layout_source, args.backup_dir.resolve(), args.apply, args.baseline), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
