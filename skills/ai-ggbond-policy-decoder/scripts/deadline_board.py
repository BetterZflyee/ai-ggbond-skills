#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI GGbond 窗口清单（Deadline Board）：计算紧迫度、按元/小时排序、分区分级

用法：
  python3 deadline_board.py board.json              # 渲染 Markdown 清单
  python3 deadline_board.py board.json --review     # 只看数据体检（条数/时效/缺口）
  python3 deadline_board.py --selftest

排序原则：元/小时 = 典型可得金额 ÷ (操作分钟 / 60)
理由：普通人的真实约束是注意力，不是金额。
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

VERSION = "0.2.0"

REQUIRED = ["id", "name", "dept", "value_type", "minutes", "eligibility",
            "entry", "miss_cost", "verified_at"]
VALUE_TYPES = {"cash", "tax", "avoid_loss", "entitlement"}


def parse(d):
    return datetime.strptime(d, "%Y-%m-%d").date()


def compute(items, as_of):
    out = []
    for it in items:
        miss = [k for k in REQUIRED if it.get(k) in (None, "")]
        days = None
        if it.get("deadline"):
            days = (parse(it["deadline"]) - as_of).days
        ver = parse(it["verified_at"])
        stale = (as_of - ver).days
        v = it.get("value_typical")
        mins = it.get("minutes") or 0
        vph = round(v / (mins / 60), 0) if (v and mins) else None
        out.append(dict(it, days_left=days, stale_days=stale,
                        value_per_hour=vph, missing_fields=miss))
    return out


def bucket(it):
    d = it["days_left"]
    if it.get("reverse"):
        return "reverse"
    if d is None:
        return "nodl"
    if d < 0:
        return "expired"
    if d <= 7:
        return "urgent"
    if d <= 30:
        return "m30"
    if d <= 90:
        return "m90"
    return "later"


def render(items, meta, as_of):
    rows = compute(items, as_of)
    buckets = {k: [] for k in ("urgent", "m30", "m90", "later", "nodl", "expired", "reverse")}
    for it in rows:
        buckets[bucket(it)].append(it)

    def sort_key(it):
        # 待核验(>90天)沉底，其余按元/小时降序
        stale_penalty = 1 if it["stale_days"] > 90 else 0
        return (stale_penalty, -(it["value_per_hour"] or 0))

    for k in buckets:
        buckets[k].sort(key=sort_key)

    today = as_of
    active = [i for k in ("urgent", "m30", "m90", "later", "nodl")
              for i in buckets[k] if not i.get("done")]
    # 现金/抵税类才计入合计与加权时薪；避免损失类单列，防止尾部风险估值污染排序口径
    cash_items = [i for i in active if i["value_type"] in ("cash", "tax")]
    loss_items = [i for i in active if i["value_type"] == "avoid_loss"]
    total_value = sum(i["value_typical"] or 0 for i in cash_items)
    total_min = sum(i["minutes"] or 0 for i in active)
    weighted = round(total_value / (sum(i["minutes"] or 0 for i in cash_items) / 60), 0) \
        if cash_items else 0

    L = []
    L.append(f"# 窗口清单 · {meta.get('city','')} · {meta.get('period','')}")
    L.append("")
    L.append(f"**数据核验日** {as_of} ｜ **在办 {len(active)} 项** ｜ "
             f"**现金/抵税合计约 ¥{total_value:,.0f}** ｜ **全部耗时约 {total_min} 分钟**")
    L.append("")
    L.append(f"**现金/抵税类加权时薪 ¥{weighted:,.0f}/小时**"
             + (f"（另有 {len(loss_items)} 项为「避免损失」类，价值按尾部风险估，不计入合计）"
                if loss_items else ""))
    L.append("")

    bad = [i for i in rows if i["stale_days"] > 30 and not i.get("done")]
    if bad:
        L.append(f"> ⚠️ 有 {len(bad)} 项超过 30 天未核验："
                 + "、".join(i["name"] for i in bad)
                 + "。金额与门槛请以窗口答复为准。")
        L.append("")

    titles = {
        "urgent": "## 🔴 7 天内（今天办，或放弃）",
        "m30": "## 🟠 30 天内（本周动手）",
        "m90": "## 🟡 90 天内（排进日程）",
        "later": "## ⚪ 90 天以上",
        "nodl": "## ⚪ 无截止日 / 资格型（补漏用）",
        "expired": "## ⛔ 已过期（留着当警示）",
        "reverse": "## 🔄 反向项（要先花钱，默认不推荐）",
    }

    def line(it):
        check = "☑" if it.get("done") else "☐"
        d = it["days_left"]
        dl = "无截止日" if d is None else (f"剩 {d} 天" if d >= 0 else f"已过期 {abs(d)} 天")
        money = (f"约 ¥{it['value_typical']:,.0f}" if it.get("value_typical")
                 else "资格型")
        if it["value_type"] == "avoid_loss":
            hr = "**★避免损失·优先级最高**"
        elif it.get("value_per_hour"):
            hr = f"**¥{it['value_per_hour']:,.0f}/小时**"
        else:
            hr = "—"
        tags = []
        if it.get("quota_limited"):
            tags.append("⏳资金用完即止")
        if it.get("district"):
            tags.append(f"📍{it['district']}")
        if it["stale_days"] > 90:
            tags.append("❗待核验")
        tag_s = (" · " + " · ".join(tags)) if tags else ""
        out = [f"- {check} **{it['name']}** ｜ {dl} ｜ {money} ｜ {it['minutes']}分钟 ｜ {hr}{tag_s}"]
        out.append(f"  - 入口：{it['entry']}")
        out.append(f"  - 资格：{it['eligibility']}")
        if it.get("value_note"):
            out.append(f"  - 金额说明：{it['value_note']}")
        out.append(f"  - 错过代价：{it['miss_cost']}")
        if it.get("note"):
            out.append(f"  - 注意：{it['note']}")
        return "\n".join(out)

    for k in ("urgent", "m30", "m90", "later", "nodl", "reverse", "expired"):
        if not buckets[k]:
            continue
        L.append(titles[k])
        L.append("")
        for it in buckets[k]:
            L.append(line(it))
            L.append("")

    L.append("---")
    L.append("")
    L.append("**边界**：本清单只负责告诉你「去哪个门、大概多少钱、还剩几天」。"
             "金额、门槛、截止日一律以官方窗口答复为准。")
    return "\n".join(L)


def review(items, as_of):
    rows = compute(items, as_of)
    print(f"条数：{len(rows)}")
    for it in rows:
        flags = []
        if it["missing_fields"]:
            flags.append("缺字段:" + ",".join(it["missing_fields"]))
        if it["stale_days"] > 90:
            flags.append(f"待核验({it['stale_days']}天)")
        elif it["stale_days"] > 30:
            flags.append(f"超30天({it['stale_days']}天)")
        if it["value_per_hour"] is None and it["value_type"] != "entitlement":
            flags.append("无法算元/小时")
        print(f"  - {it['name']:<16} {bucket(it):<8} 元/小时={it['value_per_hour']} "
              f"{' | '.join(flags)}")
    return 0


def selftest():
    as_of = date(2026, 11, 2)
    items = [
        {"id": "a", "name": "养老金", "dept": "税务", "value_type": "tax",
         "value_typical": 2040, "minutes": 20, "eligibility": "e", "entry": "手机银行",
         "miss_cost": "当年额度不结转", "verified_at": "2026-11-01",
         "deadline": "2026-12-31"},
        {"id": "b", "name": "购车补贴", "dept": "商务", "value_type": "cash",
         "value_typical": 15000, "minutes": 600, "eligibility": "e", "entry": "懂车帝",
         "miss_cost": "拿不到", "verified_at": "2026-11-01",
         "deadline": "2026-12-31", "reverse": True, "quota_limited": True},
        {"id": "c", "name": "在园补贴", "dept": "教育", "value_type": "cash",
         "value_typical": 1500, "minutes": 30, "eligibility": "e", "entry": "i深圳",
         "miss_cost": "本学年作废", "verified_at": "2026-10-01",
         "deadline": "2026-10-27", "district": "光明区"},
    ]
    rows = compute(items, as_of)
    assert rows[0]["days_left"] == 59 and rows[0]["value_per_hour"] == 6120
    assert bucket(rows[0]) == "m90"
    assert bucket(rows[1]) == "reverse"
    assert bucket(rows[2]) == "expired"
    out = render(items, {"city": "X市", "period": "2026Q4"}, as_of)
    assert "反向项" in out and "已过期" in out and "☐ **养老金**" in out
    print("selftest OK：元/小时、分区、反向项、过期项、渲染全部符合预期")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--selftest" in flags:
        selftest()
        return 0
    if not args:
        print(__doc__)
        return 2
    data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    as_of = parse(data["meta"].get("as_of") or date.today().isoformat())
    items = data.get("items") or []
    if not items:
        print("[ERROR] items 为空", file=sys.stderr)
        return 1
    if "--review" in flags:
        return review(items, as_of)
    print(render(items, data["meta"], as_of))
    return 0


if __name__ == "__main__":
    sys.exit(main())
