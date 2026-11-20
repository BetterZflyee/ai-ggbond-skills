#!/usr/bin/env python3
"""Install only this layout skill and add a small routing block to existing skills."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import uuid

NAME = 'ai-ggbond-wechat-layout'
ROOT = Path(__file__).resolve().parents[1]
START = '<!-- BEGIN AI-GGBOND-WECHAT-LAYOUT -->'
END = '<!-- END AI-GGBOND-WECHAT-LAYOUT -->'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def package_hashes(path):
    return {str(p.relative_to(path)):sha(p.read_bytes()) for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def routing(text, target, publisher):
    content = (f'{START}\n## 公众号精细排版模块\n\n'
               f'涉及公众号精排、版式审查、图文组件、表格优化或手机预览时，先读取 `{target}/SKILL.md`。'
               '该模块沿用个人版式规则，生成可核查的正文、预览和草稿交接包。用户当前要求及稿件品牌规范优先。\n\n')
    if publisher:
        content += ('精排完成后使用交付包里的 `article.html` 和 `handoff.json`；不上传 `preview.html`、`reading-preview.html` 或 `review.html`，不把原 Markdown 再套主题转换。'
                    '实验 SVG 先单独验证平台保留。沿用户当前授权完成草稿操作并读回；仅排版请求完成本地交付即可。\n')
    else:
        content += ('在成稿后调用排版模块，保留原文、数据和引用。该模块的个人风格配置用于替代后文旧版排版模板的默认值；'
                    '写作、素材选择和事实核查仍遵从本技能。不要在排版阶段再次改写或缩短文章。\n')
    content += END + '\n'
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError('精排入口标记不完整或重复，请人工检查')
        return re.sub(re.escape(START)+r'[\s\S]*?'+re.escape(END)+r'\n?',lambda _:content,text,count=1)
    front = re.match(r'\A---\r?\n[\s\S]*?\r?\n---\r?\n',text)
    position = front.end() if front else 0
    return text[:position] + '\n' + content + '\n' + text[position:]


def install(home_root, backup_root, apply=False):
    source = ROOT.resolve()
    destinations = [home_root/'.hermes/skills/creative'/NAME,home_root/'.codex/skills'/NAME,home_root/'.agents/skills'/NAME]
    routes = [
        (home_root/'.hermes/skills/creative/ai-ggbond-article-writer/SKILL.md',destinations[0],False),
        (home_root/'.hermes/skills/productivity/ai-ggbond-post-to-wechat/SKILL.md',destinations[0],True),
        (home_root/'.codex/skills/ai-ggbond-artical-writer-codex/SKILL.md',destinations[1],False),
        (home_root/'.codex/skills/ai-ggbond-article-writer/SKILL.md',destinations[1],False),
        (home_root/'.codex/skills/ai-ggbond-post-to-wechat/SKILL.md',destinations[1],True),
        (home_root/'.agents/skills/ai-ggbond-artical-writer-codex/SKILL.md',destinations[2],False),
        (home_root/'.agents/skills/ai-ggbond-post-to-wechat/SKILL.md',destinations[2],True),
    ]
    hashes = package_hashes(source)
    planned_routes = []
    for path,target,publisher in routes:
        if not path.is_file():
            continue
        original = path.read_text(encoding='utf-8')
        updated = routing(original,target,publisher)
        planned_routes.append((path,original,updated))
    for dest in destinations:
        if dest.is_symlink():
            raise ValueError(f'安装目标是符号链接，需先核对真实位置：{dest}')
        if dest.exists() and not re.search(r'^name:\s*'+NAME+r'\s*$',(dest/'SKILL.md').read_text(),re.M):
            raise ValueError(f'安装目标不是本模块，拒绝替换：{dest}')
    plan = {'source':str(source),'files':len(hashes),'destinations':[str(p) for p in destinations],
            'routes':[{'path':str(p),'changed':a!=b,'before_sha256':sha(a.encode()),'after_sha256':sha(b.encode())} for p,a,b in planned_routes],
            'scope':'layout skill copies and marked routing blocks only; no models, credentials, gateways or publishing'}
    if not apply:
        return {'status':'plan',**plan}
    backup = backup_root / ('install-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])
    backup.mkdir(parents=True,exist_ok=False)
    records, touched_routes, touched_packages = [], [], []
    # Back up every mutable destination before installing anything.
    for i,(path,original,updated) in enumerate(planned_routes):
        saved = backup/f'route-{i}.md'
        saved.write_text(original,encoding='utf-8')
        records.append({'kind':'route','path':str(path),'backup':str(saved),'before_sha256':sha(original.encode())})
    for i,dest in enumerate(destinations):
        if dest.resolve() == source:
            continue
        saved = backup/f'package-{i}'
        if dest.exists():
            shutil.copytree(dest,saved)
        records.append({'kind':'package','path':str(dest),'backup':str(saved) if saved.exists() else None})
    (backup/'before.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    try:
        for dest in destinations:
            if dest.resolve() == source:
                continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.'+NAME+'-',dir=dest.parent))
            shutil.copytree(source,stage,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git'))
            if package_hashes(stage) != hashes:
                raise ValueError('安装前副本哈希校验失败')
            touched_packages.append(dest)
            if dest.exists():
                shutil.rmtree(dest)
            stage.rename(dest)
        for path,original,updated in planned_routes:
            if original == updated:
                continue
            if path.read_text(encoding='utf-8') != original:
                raise ValueError(f'入口在安装期间已变化，停止并回滚：{path}')
            touched_routes.append((path,original))
            path.write_text(updated,encoding='utf-8')
        for dest in destinations:
            if package_hashes(dest) != hashes:
                raise ValueError(f'安装后哈希不一致：{dest}')
        for path,original,updated in planned_routes:
            if path.read_text(encoding='utf-8') != updated:
                raise ValueError(f'入口读回不一致：{path}')
    except Exception:
        for path,original in reversed(touched_routes):
            path.write_text(original,encoding='utf-8')
        for dest in reversed(touched_packages):
            if dest.exists():
                shutil.rmtree(dest)
            record=next(x for x in records if x['kind']=='package' and x['path']==str(dest))
            if record['backup']:
                shutil.copytree(record['backup'],dest)
        raise
    result={'status':'installed','backup':str(backup),'package_hashes':hashes,**plan}
    (backup/'installed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,default=Path.home())
    parser.add_argument('--backup-dir',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    try:
        result=install(args.home.resolve(),args.backup_dir.resolve(),args.apply)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (OSError,ValueError) as error:
        parser.exit(2,str(error)+'\n')


if __name__=='__main__':
    main()
