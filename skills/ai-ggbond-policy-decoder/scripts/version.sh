#!/usr/bin/env bash
# AI GGbond 政策解码器 · 版本与回滚工具
# 用法：
#   ./scripts/version.sh ship "改了啥"        # 校验VERSION+CHANGELOG → commit → tag
#   ./scripts/version.sh list                # 列出所有版本
#   ./scripts/version.sh rollback v0.1.0     # 回滚到指定版本（自动打保险标签）
#   ./scripts/version.sh status              # 当前版本与工作区状态

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 回滚范围：只恢复技能本体，不动 ledger（预测台账是历史事实）
RESTORE_PATHS=(SKILL.md VERSION CHANGELOG.md ROLLBACK.md references templates examples scripts boards)

die() { echo "[ERROR] $*" >&2; exit 1; }

current_version() { tr -d '[:space:]' < VERSION; }

cmd_ship() {
  local msg="${1:-}"
  [ -n "$msg" ] || die "请提供提交说明：./scripts/version.sh ship \"说明\""

  [ -d .git ] || die "当前目录不是 git 仓库，先执行 git init"

  local ver; ver="$(current_version)"
  [ -n "$ver" ] || die "VERSION 文件为空"
  grep -q "^## \[$ver\]" CHANGELOG.md \
    || die "CHANGELOG.md 里没有 [${ver}] 条目 —— 先补变更记录再 ship"

  if git rev-parse -q --verify "refs/tags/v${ver}" >/dev/null; then
    die "标签 v${ver} 已存在 —— 改了内容就必须升版本号（0.x 升 MINOR）"
  fi

  git add -A
  git commit -m "v${ver}: ${msg}" >/dev/null
  git tag -a "v${ver}" -m "v${ver} ${msg}"
  echo "[OK] 已提交并打标签 v${ver}"
  echo "     回滚命令：./scripts/version.sh rollback v${ver}"
}

cmd_list() {
  echo "当前版本：$(current_version)"
  echo
  echo "全部标签（新→旧）："
  git tag -l 'v*' --sort=-v:refname | head -30
  echo
  echo "最近提交："
  git log --oneline -10
}

cmd_status() {
  echo "当前版本：$(current_version)"
  echo "分支：$(git rev-parse --abbrev-ref HEAD)"
  echo "标签数：$(git tag -l 'v*' | wc -l | tr -d ' ')"
  echo
  git status --short || true
}

cmd_rollback() {
  local target="${1:-}"
  [ -n "$target" ] || die "请指定目标版本，例如：./scripts/version.sh rollback v0.1.0"
  git rev-parse -q --verify "refs/tags/${target}" >/dev/null \
    || die "标签 ${target} 不存在，用 list 查看可用版本"

  local safe="pre-rollback-$(date +%Y%m%d-%H%M%S)"
  git tag -a "$safe" -m "回滚到 ${target} 之前的安全点"
  echo "[OK] 已打保险标签 ${safe}（后悔时可以回到这里）"

  for p in "${RESTORE_PATHS[@]}"; do
    if git cat-file -e "${target}:${p}" 2>/dev/null; then
      git checkout "${target}" -- "$p"
      echo "  restored: $p"
    fi
  done

  echo
  echo "[DONE] 文件已恢复到 ${target}，但**尚未提交**。"
  echo "      确认无误后：git commit -m \"rollback to ${target}\""
  echo "      想放弃回滚：git checkout -- . "
}

case "${1:-}" in
  ship)     shift; cmd_ship "${1:-}" ;;
  list)     cmd_list ;;
  rollback) shift; cmd_rollback "${1:-}" ;;
  status)   cmd_status ;;
  *)        sed -n '2,10p' "$0" ;;
esac
