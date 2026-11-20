"""Design decisions and measurable review signals; all heuristics are advisory."""
import math
import re
import struct
import unicodedata


def contrast(foreground, background):
    def luminance(value):
        rgb = [int(value[i:i+2],16)/255 for i in (1,3,5)]
        linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
        return sum(a*b for a,b in zip(linear,[0.2126,0.7152,0.0722]))
    a,b = sorted([luminance(foreground),luminance(background)])
    return (b+0.05)/(a+0.05)


def em_width(value):
    return sum(0 if unicodedata.combining(c) else 1 if unicodedata.east_asian_width(c) in {'W','F'} else 0.55 for c in value)


def image_dimensions(data):
    """Read raster headers, without resizing, decoding pixels or changing originals."""
    if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)>=24:
        return struct.unpack('>II',data[16:24])
    if data[:6] in {b'GIF87a',b'GIF89a'} and len(data)>=10:
        return struct.unpack('<HH',data[6:10])
    if data.startswith(b'\xff\xd8'):
        pos=2
        while pos+4<len(data):
            if data[pos]!=255:
                pos+=1; continue
            marker=data[pos+1];pos+=2
            if marker in {0xD8,0xD9,0x01} or 0xD0<=marker<=0xD7:
                continue
            size=int.from_bytes(data[pos:pos+2],'big')
            if size<2 or pos+size>len(data):
                break
            if marker in {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF} and size>=7:
                return int.from_bytes(data[pos+5:pos+7],'big'),int.from_bytes(data[pos+3:pos+5],'big')
            pos+=size
    if data[:4]==b'RIFF' and data[8:12]==b'WEBP' and len(data)>=30:
        kind=data[12:16]
        if kind==b'VP8X':
            return 1+int.from_bytes(data[24:27],'little'),1+int.from_bytes(data[27:30],'little')
        if kind==b'VP8 ' and data[23:26]==b'\x9d\x01\x2a':
            return int.from_bytes(data[26:28],'little')&0x3FFF,int.from_bytes(data[28:30],'little')&0x3FFF
        if kind==b'VP8L' and data[20]==0x2F:
            bits=int.from_bytes(data[21:25],'little')
            return (bits&0x3FFF)+1,((bits>>14)&0x3FFF)+1
    return None


NUMBER = re.compile(r'^[+−-]?[¥￥$€£]?\s*\d[\d,.]*(?:\s*(?:%|％|元|万|亿|次|天|年|月|分钟|小时|kg|ms|px|GB|MB|M|K|/kg))*$',re.I)


def numeric_column(values):
    nonempty=[v.strip() for v in values if v.strip()]
    return bool(nonempty) and all(NUMBER.fullmatch(v) for v in nonempty)


def table_plan(block, headers, rows, profile):
    count=len(headers)
    mode=block.get('layout','auto')
    intent=block.get('intent','comparison')
    if mode not in {'auto','table','records','split'} or intent not in {'comparison','records'}:
        raise ValueError('table.layout 应为 auto/table/records/split；intent 应为 comparison/records')
    key=block.get('key_column',0)
    if type(key) is not int or not 0<=key<count:
        raise ValueError('key_column 超出表头范围')
    minimum=320-2*profile['padding']
    requirements=[max(2,em_width(h),min(9,max(em_width(row[i]) for row in rows)))*profile['table_size']+12 for i,h in enumerate(headers)]
    reason='explicit'
    if mode=='auto':
        if count<=3 or count<=4 and sum(requirements)<=minimum:
            mode,reason='table','compact columns fit the 320px review target'
        elif intent=='records':
            mode,reason='records','record lookup prioritized over cross-column comparison'
        else:
            mode,reason='split','repeat the key column to preserve comparison relationships'
    if mode=='split' and count<3:
        mode='table'
    others=[i for i in range(count) if i!=key]
    groups=[[key,*others[i:i+2]] for i in range(0,len(others),2)] if mode=='split' else [list(range(count))]
    weights=block.get('column_widths',requirements)
    if not isinstance(weights,list) or len(weights)!=count or any(type(x) not in {int,float} or not 0<x<=10000 for x in weights):
        raise ValueError('column_widths 需要每列对应的正数权重')
    aligns=block.get('column_align')
    if aligns is None:
        aligns=['right' if i!=key and numeric_column([r[i] for r in rows]) else 'left' for i in range(count)]
    if not isinstance(aligns,list) or len(aligns)!=count or any(x not in {'left','right','center'} for x in aligns):
        raise ValueError('column_align 需要每列对应的 left/right/center')
    return {'layout':mode,'reason':reason,'groups':groups,'key_column':key,'column_weights':weights,'align':aligns,'estimated_required_px':round(sum(requirements),1),'available_px_at_320':minimum}


def design_report(data, profile, renderer, plain):
    findings=[]
    def add(code,block,message,priority='review'):
        findings.append({'code':code,'block':block,'priority':priority,'message':message})
    pairs=[]
    for role,fg,bg in [('body',profile['text'],'#FFFFFF'),('secondary',profile['muted'],'#FFFFFF'),('link',profile['link_color'],'#FFFFFF'),('quote',profile['text'],profile['quote_bg'])]:
        ratio=contrast(fg,bg)
        pairs.append({'role':role,'foreground':fg,'background':bg,'ratio':round(ratio,3),'reference_minimum':4.5,'passed':ratio>=4.5})
        if ratio<4.5:
            add('LOW_CONTRAST',None,f'{role} 文字对比度 {ratio:.2f}:1，低于本模块采用的 4.5:1 参考值','high')
    if profile['heading_follow_gap']>=profile['section_gap']:
        add('HEADING_GROUPING',None,'标题后距不小于章节前距，所属关系可能不清楚')
    headings_seen=set()
    heavy_run=[]
    for i,b in enumerate(data['blocks']):
        identifier=b.get('id',f'b{i+1:03}')
        kind=b['type']
        if kind=='heading':
            level=b.get('level',2)
            if level==3 and 2 not in headings_seen:
                add('HEADING_LEVEL',identifier,'首个章节从 h3 开始，请检查是否缺少上一级标题')
            headings_seen.add(level)
        if kind=='paragraph':
            text=plain(b['text'])
            lines=math.ceil(em_width(text)/((375-2*profile['padding'])/profile['font_size']))
            if lines>10:
                add('LONG_PARAGRAPH',identifier,f'按 375px 粗估约 {lines} 行；结合语义判断是否需要分段，未自动改写')
            emphasized=sum(len(plain(value)) for pair in re.findall(r'\*\*(.+?)\*\*|__(.+?)__',b['text']) for value in pair if value)
            if len(text)>=60 and emphasized/len(text)>0.35:
                add('EMPHASIS_DENSITY',identifier,'该段超过约三分之一文字被加粗，请检查强调是否失去区分度')
        if kind in {'image','quote','chart','callout','metrics'}:
            heavy_run.append(identifier)
        elif kind!='heading':
            heavy_run=[]
        if len(heavy_run)==3 and data['meta'].get('intent')!='component-demo':
            add('COMPONENT_CLUSTER',identifier,'连续出现三个视觉重组件，请确认它们各自的信息作用；不是强制插入段落')
    for item in renderer.image_reviews:
        if item['role'] in {'diagram','screenshot'} and item['source_min_text_px'] is None:
            add('IMAGE_TEXT_UNMEASURED',item['block'],'图中文字的最小字号未记录，需在手机尺寸人工查看')
        if item['estimated_min_text_px_at_320'] is not None and item['estimated_min_text_px_at_320']<12:
            add('IMAGE_TEXT_TOO_SMALL',item['block'],f"图中文字在 320px 下估计仅 {item['estimated_min_text_px_at_320']:.1f}px，建议拆图或重新绘制",'high')
        if not item['alt'] and item['role']!='decorative':
            add('MISSING_ALT',item['block'],'图片缺少辅助描述，勿用可见图注代替 alt')
    for item in renderer.table_reviews:
        if item['layout']=='records' and item['intent']=='comparison':
            add('TABLE_COMPARISON_LOSS',item['block'],'已明确选择逐条记录，但此表标为比较用途，请复核横向比较是否受损')
        if item['layout']=='table' and item['estimated_required_px']>item['available_px_at_320']*1.5:
            add('DENSE_TABLE',item['block'],'列内文本较密，请查看实际换行或显式选择 split')
    return {'status':'review_required' if findings else 'no_automatic_findings','scope':'advisory design review; not WCAG certification or WeChat verification','contrast':pairs,'tables':renderer.table_reviews,'images':renderer.image_reviews,'findings':findings,'manual_checks':['Chinese punctuation and line endings','heading grouping','source and caption necessity','image text at reading size','mobile WeChat and dark mode'],'threshold_basis':'4.5:1 uses WCAG contrast guidance; 12px image text, paragraph and density limits are local review heuristics'}
