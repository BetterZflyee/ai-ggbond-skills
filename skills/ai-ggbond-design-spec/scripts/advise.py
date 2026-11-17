#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-ggbond-design-spec · 设计风格推荐引擎

只读取 design-kb，不写任何文件，不联网，不调用生图 API。

用法：
  python3 advise.py "做一张电商主图"
  python3 advise.py --json "给 B 端产品做个设置页"
  python3 advise.py --style clean-app          # 直接查某风格的完整规格
  python3 advise.py --list                     # 列出 16 风格 + 13 路由
  python3 advise.py --doctor                   # 知识库体检

退出码：
  0 = 命中路由或查询成功
  1 = 未命中路由（需人工判断，不算错误，但要显式告知）
  2 = 知识库缺失或数据损坏
"""

import argparse
import json
import os
import sys

KB = "/Users/zhufei/.dsh/bot/workspace/design-kb"

RED_LINES = [
    "永不推荐「米白底 #F5EFE6 + 陶土色 #C67B5C + 无衬线大标题」（飞哥明确否决，AI 味识别符）",
    "科技暗色必须附风险提示，默认降级为去特效版（无发光边框/光束/粒子星空）",
    "提示词必须含具体数值（色值/字号/行高/间距/圆角），禁止「高级一点」「大气一些」",
]

NEGATIVE_PROMPT = (
    "【禁止】米白底 #F5EFE6 + 陶土色 #C67B5C 的组合；深色底 + 发光边框 + 光束特效；"
    "卡片内再套卡片；「01 / 02 / 03」式编号小标题；斜体衬线大标题配细字重；"
    "提示框左侧一根彩色竖条；无来源的环境光与发光；过度圆角（>16px）配大阴影；"
    "彩虹式多色数据图；居中对称却无层级的标题堆叠；纯装饰性图标（不带信息量）。"
)

# 这 6 种风格在 top10.json 里没有现成 prompt，必须按 styles.json 特征拼装
NO_PROMPT_STYLES = ["minimal", "glass", "y2k", "motion3d", "collage", "retro-print"]


def load(name):
    path = os.path.join(KB, "data", name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"知识库数据缺失: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all():
    return {
        "route": load("route.json"),
        "styles": load("styles.json"),
        "top10": load("top10.json"),
        "combos": load("combos.json"),
        "sites": load("sites.json"),
        "audience": load("audience.json"),
    }


def doctor():
    """知识库体检：文件齐全性、引用完整性、覆盖缺口"""
    print("=" * 66)
    print("design-kb 体检")
    print("=" * 66)
    print(f"路径: {KB}")

    if not os.path.isdir(KB):
        print("❌ 知识库目录不存在")
        return 2

    required = ["route.json", "styles.json", "top10.json", "combos.json",
                "sites.json", "audience.json", "site-style-map.json"]
    missing = [f for f in required if not os.path.exists(os.path.join(KB, "data", f))]
    print(f"\n[1] 必需数据文件: {len(required) - len(missing)}/{len(required)} 就绪")
    if missing:
        print(f"    ❌ 缺失: {missing}")
        return 2

    d = load_all()
    keys = {s["key"] for s in d["styles"]}
    print(f"\n[2] 规模")
    print(f"    风格 {len(d['styles'])} 种 / 场景路由 {len(d['route'])} 条 / "
          f"现成提示词 {len(d['top10'])} 条 / 组合 {len(d['combos'])} 组 / "
          f"参考站 {len(d['sites'])} 个")

    print(f"\n[3] 引用完整性")
    bad = []
    for r in d["route"]:
        for k in [r["primary"]] + r["alt"]:
            if k not in keys:
                bad.append(f"路由「{r['trigger'][0]}」引用了不存在的风格 {k}")
    t10 = {t["key"] for t in d["top10"]}
    for k in t10:
        if k not in keys:
            bad.append(f"top10 含 styles 中没有的风格 {k}")
    if bad:
        print("    ❌ 发现问题:")
        for b in bad:
            print(f"       {b}")
        return 2
    print("    ✅ 路由与 top10 引用的风格全部存在")

    print(f"\n[4] 覆盖缺口（技能已做兜底）")
    no_prompt = sorted(keys - t10)
    print(f"    无现成 prompt 的风格: {no_prompt}")
    print(f"    ⚠️ 这 {len(no_prompt)} 种须按 styles.json 特征拼装，不许说「没有模板」")
    rt = {r["primary"] for r in d["route"]} | {x for r in d["route"] for x in r["alt"]}
    orphan = sorted(keys - rt)
    print(f"    未进任何路由的风格: {orphan}")
    print(f"    只在用户点名或按风格族反查时用到")

    print(f"\n[5] 站点核验状态")
    lv = {}
    for s in d["sites"]:
        lv[s.get("verify_level", "?")] = lv.get(s.get("verify_level", "?"), 0) + 1
    print(f"    verify_level 分布: {lv}")
    warn = sum(1 for s in d["sites"] if "已修正" in s.get("verify", "") or "失效" in s.get("verify", ""))
    print(f"    含失效/已修正说明的: {warn} 个 —— 引用时必须一并告知状态")

    print(f"\n[6] 硬性红线: {len(RED_LINES)} 条")
    for i, r in enumerate(RED_LINES, 1):
        print(f"    {i}. {r}")

    print("\n✅ 体检通过")
    return 0


def match_route(text, route):
    """按命中词数取最优路由。返回 (route_obj, hit_terms)"""
    best, best_hits = None, []
    for r in route:
        hits = [t for t in r["trigger"] if t in text]
        if len(hits) > len(best_hits):
            best, best_hits = r, hits
    return best, best_hits


def guess_by_family(text, styles):
    """未命中路由时，按情绪关键词反查风格族"""
    mood_map = {
        "理性": ["克制型", "秩序型"], "专业": ["克制型", "秩序型"],
        "可信": ["克制型", "秩序型"], "严肃": ["克制型", "秩序型"],
        "高级": ["克制型"], "极简": ["克制型"], "干净": ["克制型"],
        "冲击": ["反叛型"], "吸睛": ["反叛型"], "潮": ["反叛型"],
        "年轻": ["反叛型", "复古型"], "醒目": ["反叛型"],
        "温暖": ["亲和型"], "亲切": ["亲和型"], "可爱": ["亲和型"],
        "家庭": ["亲和型"], "健康": ["亲和型"],
        "情绪": ["氛围型"], "沉浸": ["氛围型"], "酷": ["氛围型"],
        "科技": ["氛围型"], "电影": ["氛围型"],
        "复古": ["复古型"], "怀旧": ["复古型"],
        "阅读": ["叙事型"], "长文": ["叙事型"], "故事": ["叙事型"],
        "信息": ["秩序型"], "数据": ["秩序型"], "清晰": ["秩序型"],
    }
    fams = []
    for k, v in mood_map.items():
        if k in text:
            fams.extend(v)
    if not fams:
        return []
    seen, out = set(), []
    for f in fams:
        for s in styles:
            if s["family"] == f and s["key"] not in seen:
                seen.add(s["key"])
                out.append(s)
    return out[:3]


def style_card(s, prompt_entry=None):
    """输出单个风格的完整规格"""
    lines = [
        f"风格：{s['name']}（{s['family']}）",
        f"  视觉：{s['visual']}",
        f"  配色：{s['palette']}",
        f"  字体：{s['typo']}",
        f"  情绪：{s['mood']}",
        f"  受众：{s['audience']}",
        f"  适用：{s['scenes']}",
        f"  ⚠️ 已知风险：{s['caution']}",
        f"  参考站：{', '.join(s['sites'][:4])}",
    ]
    if prompt_entry:
        lines.append(f"  现成提示词：有（top10 rank {prompt_entry['rank']}）")
    elif s["key"] in NO_PROMPT_STYLES:
        lines.append(f"  现成提示词：❌ 无 —— 须按上面 visual/palette/typo 拼装")
    return "\n".join(lines)


def advise(text, as_json=False):
    d = load_all()
    styles = {s["key"]: s for s in d["styles"]}
    prompts = {t["key"]: t for t in d["top10"]}

    r, hits = match_route(text, d["route"])
    source = "route.json 命中"

    if r is None:
        # 未命中：按风格族反查
        cands = guess_by_family(text, d["styles"])
        if not cands:
            msg = "未命中任何场景路由，且情绪关键词不足以反查风格族。请人工判断场景，或补充：交付物类型 / 渠道尺寸 / 受众 / 情绪。"
            if as_json:
                print(json.dumps({"hit": False, "reason": msg}, ensure_ascii=False, indent=2))
            else:
                print(f"⚠️ {msg}")
            return 1
        primary = cands[0]
        alts = cands[1:]
        question = "未命中路由（按风格族反查）——请先确认交付物类型、渠道尺寸、受众与目标情绪，再定稿。"
        note = "按情绪关键词反查风格族得出，非标准路由"
        source = "按风格族反查"
    else:
        primary = styles[r["primary"]]
        alts = [styles[k] for k in r["alt"] if k in styles]
        question = r["question"]
        note = r["note"]

    p_key = primary["key"]
    prompt_entry = prompts.get(p_key)

    if as_json:
        out = {
            "hit": True,
            "source": source,
            "matched_terms": hits,
            "primary": {
                "key": p_key, "name": primary["name"], "family": primary["family"],
                "palette": primary["palette"], "typo": primary["typo"],
                "visual": primary["visual"], "caution": primary["caution"],
                "sites": primary["sites"], "audience": primary["audience"],
                "has_prompt": bool(prompt_entry),
                "prompt": prompt_entry["prompt"] if prompt_entry else None,
            },
            "alternatives": [
                {"key": a["key"], "name": a["name"], "family": a["family"],
                 "caution": a["caution"], "has_prompt": a["key"] in prompts}
                for a in alts
            ],
            "question": question,
            "note": note,
            "negative_prompt": NEGATIVE_PROMPT,
            "red_lines": RED_LINES,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    # 文本输出：固定四段
    print("=" * 66)
    print(f"需求：{text}")
    print(f"来源：{source}" + (f"（命中词：{', '.join(hits)}）" if hits else ""))
    print("=" * 66)

    print(f"\n✅ 首选：{primary['name']}（{primary['family']}）")
    print(f"   配色：{primary['palette']}")
    print(f"   字体：{primary['typo']}")
    print(f"   视觉：{primary['visual']}")
    print(f"   ⚠️ 已知风险：{primary['caution']}")
    print(f"   参考站：{', '.join(primary['sites'][:3])}")

    if alts:
        print(f"\n◻ 备选：")
        for a in alts:
            tag = "有现成提示词" if a["key"] in prompts else "需拼装"
            print(f"   · {a['name']}（{a['family']}，{tag}）")
            print(f"     风险：{a['caution'][:60]}")

    print(f"\n❓ 反问：{question}")
    if note:
        print(f"   补充：{note}")

    print(f"\n🎯 提示词：")
    if prompt_entry:
        print(f"   [{primary['name']}] top10 rank {prompt_entry['rank']}")
        print(f"   核心要点：{prompt_entry['core']}")
        print(f"\n{prompt_entry['prompt']}")
    else:
        print(f"   ⚠️ {primary['name']} 在 top10.json 里没有现成 prompt，"
              f"须按 styles.json 特征拼装（visual/palette/typo 三项照抄，补具体数值）")
        print(f"\n【任务】为 {{对象}} 设计 {{交付物类型}}")
        print(f"【风格】{primary['name']}（{primary['family']}）")
        print(f"【配色】{primary['palette']}")
        print(f"【字体】{primary['typo']}")
        print(f"【版式】栅格 {{列数}} 列；外边距 {{数值}}px；模块间距 {{数值}}px；圆角 {{数值}}px")
        print(f"【内容】{{具体要放什么}}")

    print(f"\n{NEGATIVE_PROMPT}")

    print(f"\n⚠️ 硬性红线：")
    for i, line in enumerate(RED_LINES, 1):
        print(f"   {i}. {line}")
    return 0


def show_style(key, as_json=False):
    d = load_all()
    styles = {s["key"]: s for s in d["styles"]}
    prompts = {t["key"]: t for t in d["top10"]}
    if key not in styles:
        print(f"未知风格 {key}。可选: {', '.join(sorted(styles))}")
        return 1
    s = styles[key]
    if as_json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0
    print("=" * 66)
    print(style_card(s, prompts.get(key)))
    if key in prompts:
        print(f"\n🎯 现成提示词：\n{prompts[key]['prompt']}")
    print(f"\n{NEGATIVE_PROMPT}")
    return 0


def list_all():
    d = load_all()
    print("=" * 66)
    print(f"design-kb：{len(d['styles'])} 风格 / {len(d['route'])} 路由 / "
          f"{len(d['top10'])} 提示词 / {len(d['combos'])} 组合")
    print("=" * 66)

    print("\n【16 种风格】")
    t10 = {t["key"] for t in d["top10"]}
    for s in d["styles"]:
        flag = "✓prompt" if s["key"] in t10 else "需拼装"
        print(f"  {s['key']:14} {s['family']:6} {s['name']:32} {flag}")

    print("\n【13 条场景路由】")
    for r in d["route"]:
        print(f"  {r['trigger'][0]:10} → {r['primary']:13} 备选: {', '.join(r['alt'])}")

    print("\n【6 组混搭方案】")
    for c in d["combos"]:
        print(f"  · {c['name']}")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="ai-ggbond-design-spec 风格推荐引擎（只读 design-kb）")
    ap.add_argument("demand", nargs="?", default=None, help="需求描述，如「做一张电商主图」")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--style", default=None, help="直接查某风格的完整规格")
    ap.add_argument("--list", action="store_true", help="列出全部风格/路由/组合")
    ap.add_argument("--doctor", action="store_true", help="知识库体检")
    args = ap.parse_args()

    try:
        if args.doctor:
            return doctor()
        if args.list:
            return list_all()
        if args.style:
            return show_style(args.style, args.json)
        if not args.demand:
            ap.print_help()
            return 1
        return advise(args.demand, args.json)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("   技能不会用记忆编造风格特征。请确认 design-kb 路径后重试。")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ 知识库 JSON 损坏: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
