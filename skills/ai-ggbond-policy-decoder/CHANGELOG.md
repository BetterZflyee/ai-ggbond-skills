# CHANGELOG

格式参考 Keep a Changelog，版本号遵循语义化。

## [0.3.0] - 2026-11-02

### 新增 · 分发能力
- `install.sh`：一条命令安装本技能。从 GitHub 拉 tarball → 自动备份旧版本（`<skill>.bak.<时间戳>`）→ 安装 → 跑两个 selftest 自检。
- 支持 `--dir` 指定目标目录（Hermes / Claude Code / Codex / OpenClaw / 任意 SKILL.md 兼容 agent）。
- 零依赖：只用 `python3` 标准库，不需要 `pip install`，不需要任何 API Key。
- 失败时提示国内代理设置（`export https_proxy=...`）。

### 已知问题（0.4 待解）
- 安装脚本不校验下载包的完整性（无 checksum），只依赖 HTTPS。
- 未提供 `uninstall`。
- 无版本锁定安装（总是装 main 分支最新）。

## [0.2.2] - 2026-11-02

### 修正
- 清单渲染中「避免损失」类（医保等）仍显示 `¥240,000/小时` 这类失真数字，会误导读者以为它可以被比较。改为显示「★避免损失·优先级最高」，不参与元/小时的横向比较。

## [0.2.1] - 2026-11-02

### 修正
- `version.sh` 回滚范围漏了 `boards/`：回滚到含清单的版本时，清单目录不会被恢复。已补入 `RESTORE_PATHS`（`ledger/` 仍排除，历史事实不随代码回滚）。

## [0.2.0] - 2026-11-02

### 新增 · 模式 B：窗口清单（Deadline Board）
- `references/deadline-board.md`：清单模式方法论。核心是**按「元/小时」排序而非按金额**（普通人约束是注意力不是钱），四种价值类型（cash/tax/avoid_loss/entitlement）不混算，三类标记（REVERSED 反向项 / QUOTA 资金用完即止 / LOCAL 区级差异），数据时效三档（30 天警告、90 天降级）。
- `scripts/deadline_board.py`：输入 JSON → 自动算剩余天数、元/小时、分六区（7天/30天/90天/更远/无截止日/已过期）+ 反向项独立成区；`--review` 做数据体检。
- `templates/deadline-board.json`：数据模板。
- `boards/shenzhen-2026Q4.json`：首份真实清单（深圳 2026Q4，8 项，含 1 项已过期、1 项反向）。
- SKILL.md 增加「两种模式，先选后做」：A 单政策深挖（研究），B 窗口清单（执行）。

### 修正
- 加权时薪只计 cash + tax，`avoid_loss` 单列不计入合计——避免尾部风险估值（如医保按 2 万损失估）把整个清单的时薪口径拉到失真（首版曾算出 ¥240,000/小时）。
- `templates/deadline-board.json` 与真实清单分离：模板只留骨架，真实数据进 `boards/`。

### 已知问题（0.3 待解）
- 仍无自动抓取：清单靠人工检索+核验，`verified_at` 靠手填。
- 区级差异只能靠人肉逐区查，未做并行扫描。
- 无「已完成」状态回写机制，`done` 字段要手改。
- 单政策卡片（模式 A）仍是手工拼 JSON，未做从政策原文半自动提取。

## [0.1.0] - 2026-11-02

### 新增
- 首个可用骨架。七阶段工作流：触发识别 → 文本解剖 → 双层定位 → 人群锚定★ → 五路径传导 → 三时间线推演 → 双重安全检查★ → 输出登记。
- 双层分类法 `references/taxonomy.md`：
  - Layer A 存量层（五端：门票 / 收入 / 支出[住房·教育育儿·医养] / 资产负债 / 兜底）
  - Layer B 增量层（城市增长信用 / 行业增长信号 / 资本政策三层）
  - 可操作性 L1–L4 分级
- `references/persona-schema.md`：七参数画像 + 三类预设人群 + 数据缺口降级规则。
- `references/transmission-paths.md`：五路径传导（现金流/资产价格/流动性/选择权/时间成本）+ 传导衰减系数。
- `references/horizons.md`：3年算账（区间）/ 5年判结构（方向）/ 10年给分叉（情景树）；双曲贴现提示。
- `references/irreversibility.md`：不可逆五类决策、决策三分级、逃生资金四条、中间态设计。
- `references/anti-narrative.md`：古德哈特定律、已被定价、扶持≠回报、反身性拥挤度、执行摩擦折扣表。
- `references/text-anatomy.md`：六要素解剖 + 埋坑位置 + A/B/C/D 信源分级。
- `references/source-map.md`：层级规律（钱在区县）+ 检索路径 + Layer B 硬指标出处 + 刚性/预期性之辨。
- `references/prediction-ledger.md`：预测台账与打脸率三种口径（方向错/幅度错/时点错）。
- `templates/policy-card.md` 输出模板；`templates/ledger-entry.json` 台账样例。
- `scripts/policy_card.py`：字段校验 + Markdown 渲染。强制两条硬纪律（不可逆清单为空拒收、证伪条件<2 拒收），含 selftest。
- `scripts/version.sh`：ship / list / rollback 三个动作，回滚前自动打保险标签。

### 已知问题（0.2 待解）
- **无真实案例验证**。所有规则均由推演得出，尚未跑过一条真实政策。
- Layer B 的三个硬指标（土地财政依赖度、城投利差、小学生入学人数）只给了出处，**没有取数脚本**，全靠手工查。
- `scripts/policy_card.py` 只做字段完整性校验，**不做逻辑一致性校验**（例如"置信度=高"但同时缺 3 项画像，目前只报 warning）。
- 领域 playbook（住房/教育/医养/就业/落户）**尚未编写**，目前只有通用流程。
- 没有 persona 自动匹配：每次都要手填七参数，暂无"给定一句自述→自动补全画像"的能力。
- 打脸率统计无自动化，`ledger/` 目录尚未建立。

### 设计决策记录
- 不按政府部门分类，改按**普通人决策节点**分类（理由见 taxonomy.md 首节）。
- Layer A 与 Layer B 使用**两种输出语法**，禁止混用：A 给二元动作，B 只给概率+证伪。
- 城市增长采用"市场定价指标"而非"政府目标值"，因古德哈特定律污染。
- 时间越长越不给确定结论，10 年线强制情景树（脚本级强制）。
