#!/usr/bin/env bash
# ai-ggbond-policy-decoder 安装脚本
# 用法：
#   bash install.sh                    # 装到 ~/.hermes/skills
#   bash install.sh --dir ~/.claude/skills
#   curl -fsSL https://raw.githubusercontent.com/BetterZflyee/ai-ggbond-skills/main/skills/ai-ggbond-policy-decoder/install.sh | bash
set -euo pipefail

REPO="BetterZflyee/ai-ggbond-skills"
BRANCH="main"
SKILL="ai-ggbond-policy-decoder"
TARGET="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) TARGET="$2"; shift 2 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "未知参数：$1"; exit 2 ;;
  esac
done

command -v curl >/dev/null || { echo "[ERROR] 需要 curl"; exit 1; }
command -v tar  >/dev/null || { echo "[ERROR] 需要 tar"; exit 1; }

echo "→ 下载 $REPO 的 $SKILL"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if ! curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" | tar -xz -C "$tmp"; then
  echo "[ERROR] 下载失败。国内网络请先设代理："
  echo "        export https_proxy=http://127.0.0.1:7897"
  exit 1
fi

src="$tmp/ai-ggbond-skills-$BRANCH/skills/$SKILL"
[ -f "$src/SKILL.md" ] || { echo "[ERROR] 包里没找到 $SKILL/SKILL.md"; exit 1; }

mkdir -p "$TARGET"
if [ -d "$TARGET/$SKILL" ]; then
  bak="$TARGET/$SKILL.bak.$(date +%Y%m%d-%H%M%S)"
  mv "$TARGET/$SKILL" "$bak"
  echo "→ 已存在的版本已备份到：$bak"
fi

cp -R "$src" "$TARGET/$SKILL"
echo "→ 已安装到：$TARGET/$SKILL"
echo "→ 版本：$(cat "$TARGET/$SKILL/VERSION" 2>/dev/null || echo unknown)"

if command -v python3 >/dev/null 2>&1; then
  echo "→ 自检："
  python3 "$TARGET/$SKILL/scripts/policy_card.py" --selftest
  python3 "$TARGET/$SKILL/scripts/deadline_board.py" --selftest
else
  echo "⚠ 未检测到 python3。两个脚本只用标准库，装个 python3 即可，无需 pip install。"
fi

cat <<EOF

✅ 安装完成。接下来：

1) 重启你的 agent 会话（技能列表在启动时加载）
2) 直接说人话触发，例如：
   - "深圳配售型保障房对我有什么用"
   - "这个月深圳还有哪些补贴没截止"
3) 换个城市/季度就改 boards/ 里的 json，格式见 templates/deadline-board.json

注意：技能不联网抓政策，数据要你自己核（每条都有 verified_at 字段）。
EOF
