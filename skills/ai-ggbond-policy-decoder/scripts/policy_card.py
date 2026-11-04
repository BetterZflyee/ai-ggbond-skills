#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI GGbond 政策卡片：校验 + 渲染

两条硬纪律在这里被强制执行：
  1. 不可逆清单为空 -> 拒收
  2. 证伪条件 < 2 条 -> 拒收

用法：
  python3 policy_card.py card.json            # 校验并渲染 Markdown
  python3 policy_card.py card.json --check    # 只校验，输出 JSON
  python3 policy_card.py --selftest           # 自检
"""

import json
import sys
from pathlib import Path

VERSION = "0.1.0"

REQUIRED_TOP = [
    "meta", "layer_a", "persona", "paths",
    "horizons", "scenarios", "irreversible", "falsifiers",
]
META_KEYS = [
    "id", "date", "city", "policy_title", "policy_level",
    "stage", "source_url",
]
PERSONA_KEYS = [
    "age_family", "hukou_social", "income",
    "assets", "debt", "skill", "mobility",
]
PATH_KEYS = ["cashflow", "asset", "liquidity", "option", "time_cost"]
HORIZON_KEYS = ["y3", "y5", "y10"]
SCENARIO_KEYS = ["name", "prob", "condition", "action", "falsifier"]

UNKNOWN_MARKS = ("", "unknown", "[未知]", "未知", "n/a", "NA")


def _missing(d, keys):
    return [k for k in keys if k not in d or d[k] in (None, "")]


def validate(data):
    """返回 (errors, warnings)。errors 非空则拒绝输出。"""
    errors, warnings = [], []

    miss = _missing(data, REQUIRED_TOP)
    if miss:
        errors.append(f"缺少顶层字段：{', '.join(miss)}")

    meta = data.get("meta") or {}
    miss = _missing(meta, META_KEYS)
    if miss:
        errors.append(f"meta 缺少：{', '.join(miss)}")

    persona = data.get("persona") or {}
    miss = _missing(persona, PERSONA_KEYS)
    if miss:
        errors.append(f"人群未锚定（persona 缺少）：{', '.join(miss)} —— 七参数不全不许推演")
    unknown = [k for k in PERSONA_KEYS if str(persona.get(k, "")).strip() in UNKNOWN_MARKS]
    if unknown and not miss:
        warnings.append(f"画像有 {len(unknown)} 项未知（{', '.join(unknown)}），置信度降为低")

    paths = data.get("paths") or {}
    miss = _missing(paths, PATH_KEYS)
    if miss:
        errors.append(f"五路径不完整，缺少：{', '.join(miss)} —— 五行缺一行即分析不完整")

    horizons = data.get("horizons") or {}
    miss = _missing(horizons, HORIZON_KEYS)
    if miss:
        errors.append(f"三时间线缺失：{', '.join(miss)}")
    y3 = str(horizons.get("y3", ""))
    if y3 and not any(m in y3 for m in ("~", "-", "—", "至", "区间")):
        warnings.append("3 年线未给区间（应给区间不给点值）")

    scenarios = data.get("scenarios") or []
    if len(scenarios) < 3:
        errors.append(f"10 年线必须给至少三个情景，当前 {len(scenarios)} 个")
    for i, s in enumerate(scenarios, 1):
        miss = _missing(s, SCENARIO_KEYS)
        if miss:
            errors.append(f"情景 {i} 缺少：{', '.join(miss)}")
        if not str(s.get("falsifier", "")).strip():
            errors.append(f"情景 {i} 没有证伪信号 —— 是许愿不是推演")
    probs = [float(s.get("prob", 0)) for s in scenarios if s.get("prob") is not None]
    if probs and not (0.90 <= sum(probs) <= 1.10):
        warnings.append(f"情景概率合计 {sum(probs):.2f}，应≈1.00")

    irreversible = data.get("irreversible") or []
    if not irreversible:
        errors.append("不可逆清单为空 —— 未完成不可逆检查，拒绝输出")

    falsifiers = data.get("falsifiers") or []
    if len(falsifiers) < 2:
        errors.append(f"证伪条件需 ≥2 条，当前 {len(falsifiers)} 条")

    return errors, warnings


def _table(rows, header):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def render(data):
    m = data["meta"]
    p = data["persona"]
    pa = data["paths"]
    h = data["horizons"]
    la = data["layer_a"]

    lines = []
    lines.append(f"# 【政策卡片】{m['city']} · {m['policy_title']}")
    lines.append("")
    lines.append(f"**版本** {VERSION} ｜ **推演日期** {m['date']} ｜ **台账编号** {m['id']}")
    lines.append("")
    lines.append("## 一、这份政策是什么")
    lines.append("")
    lines.append(f"- **层级**：{m['policy_level']}")
    lines.append(f"- **阶段**：{m['stage']}")
    if m.get("effective_from") or m.get("effective_to"):
        lines.append(f"- **生效与期限**：{m.get('effective_from','?')} 至 {m.get('effective_to','?')}")
    if m.get("is_trial"):
        lines.append("- **注意**：本政策为**试行**，到期可能不再延续")
    lines.append(f"- **原文**：{m['source_url']}")
    lines.append("")
    lines.append("## 二、三十秒结论")
    lines.append("")
    lines.append(f"> {data.get('bottom_line', '（未填写）')}")
    lines.append("")
    lines.append(f"**动作：{data.get('action', '等')}**")
    lines.append("")
    lines.append("## 三、对谁（画像）")
    lines.append("")
    lines.append(_table(
        [[k, p.get(k, "")] for k in PERSONA_KEYS],
        ["参数", "值"],
    ))
    lines.append("")
    conf = data.get("confidence", "中")
    lines.append(f"**置信度**：{conf}")
    lines.append("")
    lines.append("## 四、五条传导路径")
    lines.append("")
    lines.append(_table(
        [[k, pa.get(k, "")] for k in PATH_KEYS],
        ["路径", "变化"],
    ))
    lines.append("")
    lines.append("## 五、三时间线")
    lines.append("")
    lines.append(f"### 3 年 · 现金流（给区间）\n\n{h['y3']}\n")
    lines.append(f"### 5 年 · 资产结构（给方向）\n\n{h['y5']}\n")
    lines.append(f"### 10 年 · 选择权（给分叉）\n\n{h['y10']}\n")
    lines.append(_table(
        [[s["name"], f"{float(s['prob']):.0%}", s["condition"], s["action"]]
         for s in data["scenarios"]],
        ["情景", "概率", "成立条件", "我的动作"],
    ))
    lines.append("")
    lines.append("## 六、不可逆清单")
    lines.append("")
    for i, item in enumerate(data["irreversible"], 1):
        lines.append(f"{i}. {item}")
    lines.append("")
    lines.append("## 七、证伪条件")
    lines.append("")
    for i, f in enumerate(data["falsifiers"], 1):
        lines.append(f"{i}. {f}")
    lines.append("")
    lines.append(f"## 八、分类定位\n\n- Layer A：{la.get('endpoint','')}\n- 可操作性：{la.get('operability','')}")
    if data.get("layer_b"):
        lines.append(f"- Layer B：{data['layer_b']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**边界声明**：本卡片是基于公开文本的情景推演，不构成投资建议、法律意见或办理承诺。实际执行以窗口答复为准。")
    return "\n".join(lines)


def selftest():
    base = {
        "meta": {"id": "t1", "date": "2026-11-02", "city": "X市",
                 "policy_title": "测试政策", "policy_level": "市级",
                 "stage": "已生效", "source_url": "https://e.g"},
        "layer_a": {"endpoint": "支出-住房", "operability": "L2"},
        "persona": {k: "v" for k in PERSONA_KEYS},
        "paths": {k: "v" for k in PATH_KEYS},
        "horizons": {"y3": "+8000~+15000", "y5": "结构恶化", "y10": "三分支"},
        "scenarios": [
            {"name": "基准", "prob": 0.6, "condition": "c", "action": "a", "falsifier": "f"},
            {"name": "乐观", "prob": 0.2, "condition": "c", "action": "a", "falsifier": "f"},
            {"name": "悲观", "prob": 0.2, "condition": "c", "action": "a", "falsifier": "f"},
        ],
        "irreversible": ["买房首付+限售3年"],
        "falsifiers": ["小学入学人数连降两年", "城投利差>150bp"],
    }
    e, w = validate(base)
    assert e == [], f"valid card rejected: {e}"
    assert "政策卡片" in render(base)

    bad = json.loads(json.dumps(base))
    bad["irreversible"] = []
    e, _ = validate(bad)
    assert any("不可逆" in x for x in e), "empty irreversible not caught"

    bad2 = json.loads(json.dumps(base))
    bad2["falsifiers"] = ["only one"]
    e, _ = validate(bad2)
    assert any("证伪" in x for x in e), "falsifier count not caught"

    bad3 = json.loads(json.dumps(base))
    del bad3["persona"]["debt"]
    e, _ = validate(bad3)
    assert any("人群未锚定" in x for x in e), "persona gap not caught"

    print("selftest OK: 3 个拒收场景 + 1 个放行场景全部符合预期")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}

    if "--selftest" in flags:
        selftest()
        return 0

    if not args:
        print(__doc__)
        return 2

    path = Path(args[0])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] 无法读取 JSON：{e}")
        return 2

    errors, warnings = validate(data)
    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    if errors:
        print("[REJECT] 校验未通过，拒绝输出：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if "--check" in flags:
        print(json.dumps({"ok": True, "warnings": warnings}, ensure_ascii=False))
        return 0

    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
