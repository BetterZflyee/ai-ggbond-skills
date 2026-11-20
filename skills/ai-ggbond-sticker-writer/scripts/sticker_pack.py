#!/usr/bin/env python3
"""Build an offline, ordered sticker delivery pack. Never generates or publishes images."""
import argparse
import copy
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'ai-ggbond-sticker-writer'
VERSION = '3.0.0'
SCENES = {'newspic', 'article-cards', 'long-image'}
ROLES = {'cover', 'overview', 'steps', 'comparison', 'timeline', 'data', 'person', 'concept', 'quote', 'summary', 'case'}
ROLE_NAMES = dict(zip(['cover','overview','steps','comparison','timeline','data','person','concept','quote','summary','case'], ['封面','概览','步骤','对比','时间线','数据','人物','概念','引语','总结','案例']))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def text(value, field, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f'{field} 需要文字')
    return value


def identifier(value, field):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
        raise ValueError(f'{field} 需要字母、数字、短横线或下划线')
    return value


def ratio(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9]\d{0,3}:[1-9]\d{0,3}', value):
        raise ValueError('ratio 需要形如 16:9 的比例')
    a,b = map(int, value.split(':'))
    return a/b


def image_reader(layout_skill=None):
    skill = Path(layout_skill).expanduser() if layout_skill else ROOT.parent/'ai-ggbond-wechat-layout'
    file = skill/'scripts/layout_design.py'
    if not file.is_file():
        raise ValueError('需要已安装的公众号精排模块，或用 --layout-skill 指定其目录')
    spec = importlib.util.spec_from_file_location('sticker_layout_design', file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.image_dimensions


def validate(plan):
    if not isinstance(plan, dict) or plan.get('schema_version') != 1:
        raise ValueError('需要 schema_version:1 的计划对象')
    if plan.get('scene', 'newspic') not in SCENES:
        raise ValueError('scene 应为 newspic/article-cards/long-image')
    meta = plan.get('meta')
    if not isinstance(meta, dict):
        raise ValueError('需要 meta 对象')
    text(meta.get('title'), 'meta.title')
    caption = text(plan.get('caption', ''), 'caption', empty=True)
    if re.search(r'(?m)^\s*#{1,6}\s|\*\*|!\[[^\]]*\]\(|</?[A-Za-z][^>]*>', caption):
        raise ValueError('caption 应为可直接粘贴的纯文本；编辑标记另存原稿')
    tags = plan.get('tags', [])
    if not isinstance(tags, list) or any(not isinstance(t,str) or not re.fullmatch(r'[^\s#]+', t) for t in tags):
        raise ValueError('tags 需要不含空格或 # 的标签文字数组')
    style = plan.get('style', {})
    if not isinstance(style, dict):
        raise ValueError('style 需要对象')
    sources = plan.get('sources', [])
    if not isinstance(sources, list) or any(not isinstance(s,dict) for s in sources):
        raise ValueError('sources 需要来源对象数组')
    source_ids = [identifier(s.get('id'), 'source.id') for s in sources]
    if any(s.get('status','provided') not in {'provided','verified','unverified','archive'} for s in sources):
        raise ValueError('source.status 应为 provided/verified/unverified/archive')
    if len(source_ids) != len(set(source_ids)):
        raise ValueError('source.id 不可重复')
    images = plan.get('images')
    if not isinstance(images, list) or not images:
        raise ValueError('images 需要明确且有顺序的图片计划')
    ids = []
    for image in images:
        if not isinstance(image, dict):
            raise ValueError('每张图片需要对象')
        ids.append(identifier(image.get('id'), 'image.id'))
        if image.get('role') not in ROLES:
            raise ValueError('图片 role 不在支持的内容任务中')
        text(image.get('heading'), 'image.heading')
        lines = image.get('text', [])
        if not isinstance(lines, list) or any(not isinstance(s,str) or not s.strip() for s in lines):
            raise ValueError('image.text 需要精确上图文字数组')
        for s in [image['heading'], *lines, image.get('prompt', '')]:
            if not isinstance(s,str) or re.search(r'(?<![0-9A-Za-z])#[\w\u3400-\u9fff]+', re.sub(r'#[0-9A-Fa-f]{6}(?![A-Za-z0-9])','',s)):
                raise ValueError('图片文字和提示词不能包含正文标签')
        ratio(image.get('ratio', '16:9'))
        refs = image.get('source_ids', [])
        if not isinstance(refs,list) or any(s not in source_ids for s in refs):
            raise ValueError('image.source_ids 必须对应 sources 中的来源')
    if len(ids) != len(set(ids)):
        raise ValueError('image.id 不可重复')
    count = plan.get('expected_image_count', len(images))
    if type(count) is not int or count != len(images):
        raise ValueError('图片计划数量与 expected_image_count 不一致；不可静默截取或增加')
    if plan.get('scene', 'newspic')=='newspic' and any(i['role']=='cover' for i in images[1:]):
        raise ValueError('原生贴图的封面页应放第一张')
    budget = meta.get('caption_budget', 500 if plan.get('scene','newspic')=='newspic' else None)
    if budget is not None and (type(budget) is not int or not 1<=budget<=100000):
        raise ValueError('caption_budget 应为正整数或 null')


def prompt_for(image, style):
    if image.get('prompt'):
        return image['prompt']
    visual = style.get('description', '商业杂志编辑风，米白纸感、黑字、单一墨绿强调，清楚的字阶与大留白，不堆叠卡片或霓虹光')
    layout = image.get('layout', '按信息的阅读顺序组织，突出主信息，保持图内文字在手机上可读')
    character = style.get('character', '')
    return (f'制作一张 {image.get("ratio","16:9")} 的中文内容信息图，用于{ROLE_NAMES[image["role"]]}。'
            f'{visual}。{layout}。'+(f'角色：{character}，服务于主题，不遮挡信息。' if character else '')+
            '\n精确上图文字：\n'+'\n'.join('「'+v+'」' for v in [image['heading'],*image.get('text',[])])+
            '\n品牌名按给定文字保留；不自行增加数字或标签。重点内容避开裁切边缘。')


def doc(title, body):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title></head><body style="margin:0;font:15px/1.8 -apple-system,BlinkMacSystemFont,\'PingFang SC\',sans-serif;color:#2B2B2B;background:white">'+body+'</body></html>'


def post_preview(plan, content, assets):
    cards=[]
    for i,item in enumerate(assets):
        visual=('<img src="'+html.escape(item['path'],quote=True)+'" alt="'+html.escape(item['alt'],quote=True)+'" style="display:block;width:100%;max-width:'+str(item['dimensions'][0])+'px;height:auto;margin:auto">') if item.get('path') else '<p style="padding:50px 20px;background:#F2F4F7">第 '+str(i+1)+' 张图片待生成</p>'
        cards.append('<figure style="flex:0 0 100%;margin:0;scroll-snap-align:start">'+visual+'<figcaption style="padding:6px 16px;font-size:13px;color:#606B7B">'+str(i+1)+' / '+str(len(assets))+'</figcaption></figure>')
    return doc(plan['meta']['title'], '<main style="max-width:680px;margin:auto"><div id="slides" style="display:flex;overflow-x:auto;scroll-snap-type:x mandatory">'+''.join(cards)+'</div><section style="padding:16px"><h1 style="font-size:20px;line-height:1.5;margin:0 0 14px">'+html.escape(plan['meta']['title'])+'</h1><p style="margin:0;white-space:pre-wrap;overflow-wrap:anywhere">'+html.escape(content)+'</p></section></main>')


def preview_page(plan, report):
    buttons=''.join(f'<button type="button" data-width="{w}" aria-pressed="{str(w==375).lower()}">{w}px</button>' for w in [320,375,390,430])
    issues=''.join('<li>'+html.escape(x['message'])+'</li>' for x in report['findings']) or '<li>自动检查未发现提示项；仍需按实际发布环境复核。</li>'
    return doc('贴图交付预览', '<style>*{box-sizing:border-box}body{background:#F2F4F7}header,footer{max-width:1000px;margin:auto;padding:20px 16px}h1{font-size:24px;margin:0 0 12px}nav{display:flex;flex-wrap:wrap;gap:8px}button,a{font:inherit;font-size:13px;padding:8px 12px;border:1px solid #B9C3D2;border-radius:4px;color:#255BB0;background:white;text-decoration:none}button[aria-pressed=true]{background:#255BB0;color:white}button:focus-visible,a:focus-visible{outline:3px solid #255BB0;outline-offset:3px}.frame{overflow-x:auto;padding:0 16px}iframe{display:block;box-sizing:content-box;width:375px;max-width:none;height:760px;margin:auto;border:1px solid #D3DAE5;background:white}footer{font-size:13px}li{margin:6px 0}</style><header><h1>'+html.escape(plan['meta']['title'])+'</h1><p>贴图阅读模拟 · '+str(len(plan['images']))+' 张 · 标题与正文合计 '+str(report['caption']['total_codepoints'])+' 字符。按图片顺序横向查看。</p><nav>'+buttons+'<button type="button" id="prev">上一张</button><button type="button" id="next">下一张</button><a href="caption.txt">纯文本正文</a></nav></header><div class="frame"><iframe src="post-preview.html" title="贴图阅读视口"></iframe></div><footer><p>这是本地阅读模拟，不是微信后台或真机截图。图片原文件保持不变；窗口窄时横向查看画框。</p><ul>'+issues+'</ul></footer><script>const frame=document.querySelector("iframe");document.querySelectorAll("[data-width]").forEach(b=>b.onclick=()=>{frame.style.width=b.dataset.width+"px";document.querySelectorAll("[data-width]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)))});for(const [id,direction] of [["prev",-1],["next",1]])document.getElementById(id).onclick=()=>frame.contentWindow.postMessage({type:"sticker-scroll",direction},"*");</script>')


def article_input(plan, assets, output):
    article=plan.get('article_reuse')
    if article is None:
        return None
    if not isinstance(article,dict) or not isinstance(article.get('blocks'),list) or not article['blocks']:
        raise ValueError('article_reuse 需要完整的 blocks，不能靠图片自动编写正文')
    by_id={a['id']:a for a in assets}
    meta=copy.deepcopy(article.get('meta', {'title':plan['meta']['title']}))
    cover=article.get('cover_image_id')
    if cover:
        if cover not in by_id or not by_id[cover].get('path'):
            raise ValueError('article_reuse 的封面图片不可用')
        meta['cover']=str(output/by_id[cover]['path'])
    blocks=[]
    for block in article['blocks']:
        item=copy.deepcopy(block)
        if item.get('type')=='image' and 'image_id' in item:
            key=item.pop('image_id')
            if key not in by_id or not by_id[key].get('path'):
                raise ValueError('article_reuse 的正文图片不可用')
            if key==cover and not meta.get('allow_cover_in_body'):
                raise ValueError('长文封面不可自动重复进正文，请明确调整复用计划')
            asset=by_id[key]
            item.update(src=str(output/asset['path']),alt=asset['alt'])
            item.setdefault('role','diagram')
            if asset['source_min_text_px'] is not None:
                item['source_min_text_px']=asset['source_min_text_px']
        blocks.append(item)
    return {'schema_version':1,'meta':meta,'blocks':blocks}


def build(source, output, layout_skill=None):
    source=Path(source).expanduser().resolve();output=Path(output).expanduser().absolute()
    if output.is_symlink() or output.exists():
        raise ValueError('输出目录已存在或为符号链接，请使用新的版本目录')
    output=output.resolve()
    if output==source.parent or output in source.parents or output==ROOT or output in ROOT.parents:
        raise ValueError('输出不能覆盖源稿或 Skill 目录')
    raw=source.read_bytes();plan=json.loads(raw.decode('utf-8-sig'));validate(plan)
    dimensions=image_reader(layout_skill)
    output.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.'+output.name+'-',dir=output.parent))
    try:
        (stage/'assets').mkdir();(stage/'prompts').mkdir()
        findings=[];assets=[]
        def add(code,message,priority='review',image_id=None):
            findings.append({'code':code,'message':message,'priority':priority,'image_id':image_id})
        content=plan.get('caption','')
        if plan.get('tags'):
            content+= ('\n\n' if content else '')+' '.join('#'+s for s in plan['tags'])
        total=plan['meta']['title']+'\n\n'+content
        budget=plan['meta'].get('caption_budget',500 if plan.get('scene','newspic')=='newspic' else None)
        counts={'title_codepoints':len(plan['meta']['title']),'body_codepoints':len(content),'total_codepoints':len(total),'body_utf16_units':len(content.encode('utf-16-le'))//2,'budget':budget,'basis':'personal editorial budget, not a verified platform limit'}
        if budget and len(total)>budget:
            add('CAPTION_BUDGET',f'标题、正文及标签共 {len(total)} 字符，超过本次编辑预算 {budget}；未截断文字','high')
        if plan.get('scene','newspic')=='newspic' and not 3<=len(plan.get('tags',[]))<=5:
            add('TAG_COUNT','检查是否需要 3–5 个正文标签；按本次内容决定')
        for record in plan.get('sources',[]):
            if record.get('status') in {'unverified','archive'}:
                add('SOURCE_REVIEW_PENDING',f'来源 {record["id"]} 尚未完成当前内容核实；历史材料不能自动视为可发布依据','high')
        for order,item in enumerate(plan['images'],1):
            prompt=prompt_for(item,plan.get('style',{}))
            (stage/'prompts'/f'{order:02d}-{item["id"]}.md').write_text(prompt+'\n',encoding='utf-8')
            asset={'id':item['id'],'order':order,'role':item['role'],'heading':item['heading'],'text':item.get('text',[]),'alt':item.get('alt',item['heading']),'requested_ratio':item.get('ratio','16:9'),'source_min_text_px':item.get('source_min_text_px'),'source_ids':item.get('source_ids',[]),'path':None,'review_status':'pending'}
            minimum=asset['source_min_text_px']
            if minimum is not None and (type(minimum) not in {int,float} or not 1<=minimum<=1000):
                raise ValueError('source_min_text_px 需要 1–1000 的原图字号，未知时省略')
            if not item.get('asset'):
                add('MISSING_IMAGE',f'第 {order} 张图片待生成，提示词不等于成图','high',item['id'])
            else:
                path=Path(text(item['asset'],'image.asset')).expanduser()
                path=(source.parent/path).resolve() if not path.is_absolute() else path.resolve()
                if not path.is_file() or path.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.gif'}:
                    raise ValueError(f'图片不存在或格式不支持：{item["id"]}')
                data=path.read_bytes();size=dimensions(data)
                if not size or min(size)<=0:
                    raise ValueError(f'无法读取图片尺寸：{item["id"]}')
                digest=sha(data);relative=f'assets/{order:02d}-{item["id"]}{path.suffix.lower()}'
                (stage/relative).write_bytes(data)
                actual=size[0]/size[1];error=abs(actual/ratio(asset['requested_ratio'])-1)
                asset.update(path=relative,original=str(path),sha256=digest,dimensions=list(size),bytes=len(data),actual_ratio=actual,ratio_error=error,estimated_text_at_320=minimum*min(320,size[0])/size[0] if minimum else None)
                if error>0.015:
                    add('ASPECT_MISMATCH',f'第 {order} 张实测 {size[0]}×{size[1]}，与 {asset["requested_ratio"]} 有差异；未拉伸或裁图','high',item['id'])
                if minimum is None:
                    add('IMAGE_TEXT_UNMEASURED',f'第 {order} 张图内字号未知，需在手机尺寸人工查看',image_id=item['id'])
                elif asset['estimated_text_at_320']<12:
                    add('IMAGE_TEXT_SMALL',f'第 {order} 张在 320px 下最小字估计 {asset["estimated_text_at_320"]:.1f}px，建议拆分或重新绘制','high',item['id'])
                review=item.get('review',{})
                if not isinstance(review,dict):
                    raise ValueError('image.review 需要对象')
                if review.get('status')=='passed' and review.get('sha256')==digest and review.get('method') in {'visual','ocr+visual'}:
                    asset['review_status']='passed';asset['review']=review
                else:
                    add('IMAGE_REVIEW_PENDING',f'第 {order} 张尚未完成绑定当前文件的图文核对',image_id=item['id'])
            assets.append(asset)
        ready=not any(f['priority']=='high' for f in findings) and all(a['review_status']=='passed' for a in assets)
        report={'version':VERSION,'status':'ready_for_handoff' if ready else 'review_required','caption':counts,'images':assets,'findings':findings,'scope':'local pack checks; image text size is an estimate; no factual, OCR, platform or phone verification is inferred','external_validation':{'image_generation':'not_run','wechat_draft':'not_tested','phone_wechat':'not_tested'}}
        (stage/'source.json').write_bytes(raw);write_json(stage/'plan.json',plan)
        (stage/'caption.txt').write_text(content,encoding='utf-8')
        (stage/'content.md').write_text('# '+plan['meta']['title']+'\n\n'+content+'\n',encoding='utf-8')
        write_json(stage/'sources.json',plan.get('sources',[]));write_json(stage/'design-review.json',report)
        handoff={'owner':OWNER,'schema_version':1,'article_type':'newspic','status':'ready' if ready else 'review_required','title':plan['meta']['title'],'author':plan['meta'].get('author',''),'content':content,'images':[{k:a.get(k) for k in ['id','order','path','sha256','alt']} for a in assets],'draft_target':plan.get('draft_target',{'account':None,'existing_media_id':None}),'quality_report':'design-review.json'}
        if plan.get('scene','newspic')=='newspic':
            write_json(stage/'newspic-bundle.json',handoff)
        if plan.get('article_reuse'):
            if all(a.get('path') for a in assets):
                write_json(stage/'layout-input.json',article_input(plan,assets,output))
            else:
                write_json(stage/'article-reuse-pending.json',plan['article_reuse'])
        reading=post_preview(plan,content,assets)
        reading=reading.replace('</body>','<script>window.addEventListener("message",e=>{if(e.source!==parent||e.data?.type!=="sticker-scroll"||![1,-1].includes(e.data.direction))return;const s=document.getElementById("slides");s.scrollBy({left:s.clientWidth*e.data.direction,behavior:"smooth"})});</script></body>')
        (stage/'post-preview.html').write_text(reading,encoding='utf-8')
        (stage/'preview.html').write_text(preview_page(plan,report),encoding='utf-8')
        manifest={'owner':OWNER,'version':VERSION,'source':{'path':str(source),'sha256':sha(raw)},'files':{str(p.relative_to(stage)):sha(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()}}
        write_json(stage/'manifest.json',manifest);stage.rename(output)
        return {'status':'built','output':str(output),'images_planned':len(assets),'images_available':sum(bool(a['path']) for a in assets),'quality':report['status'],'caption':counts}
    except Exception:
        shutil.rmtree(stage,ignore_errors=True);raise


def audit(output):
    output=Path(output).resolve();manifest=json.loads((output/'manifest.json').read_text())
    if manifest.get('owner')!=OWNER:
        raise ValueError('不是本模块的交付包')
    changed=[]
    for name,digest in manifest['files'].items():
        path=(output/name).resolve()
        if output not in path.parents or not path.is_file() or sha(path.read_bytes())!=digest:
            changed.append(name)
    return {'status':'failed' if changed else 'passed','changed_or_missing':changed,'scope':'file integrity only, not publishing approval'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('build');p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--layout-skill',type=Path)
    p=sub.add_parser('audit');p.add_argument('bundle',type=Path)
    args=parser.parse_args()
    try:
        result=build(args.input,args.out,args.layout_skill) if args.command=='build' else audit(args.bundle)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result['status']=='failed':parser.exit(1)
    except (ValueError,OSError,TypeError,KeyError) as error:
        parser.exit(2,str(error)+'\n')


if __name__=='__main__':
    main()
