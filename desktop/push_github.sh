#!/bin/bash
# 🐒 大肥猴 — 一键推送到 GitHub
# 前置：gh auth login 已完成
set -e

REPO="${1:-da-fei-hou}"
cd /Users/zmz/.openclaw/workspace/da-fei-hou

echo "🐒 准备推送大肥猴到 GitHub..."

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ 还没登录 GitHub，请先执行："
  echo "   gh auth login"
  echo "   （选 GitHub.com -> HTTPS -> 浏览器授权）"
  exit 1
fi

# 安全复核：确认没有凭据被提交
if git ls-files | grep -qi -E 'cookies/.*\.json|sessdata'; then
  echo "❌ 检测到凭据文件在仓库里，中止！"
  exit 1
fi
echo "✅ 安全检查通过：无凭据文件"

# 创建远端并推送
if gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  echo "仓库已存在，直接推送"
  git push -u origin HEAD
else
  echo "创建新仓库 $USER/$REPO"
  gh repo create "$REPO" --public --description "🐒 大肥猴 — macOS 原生桌宠 + B站自动冲浪（山寨喽喽形态）" --source=. --remote=origin --push
fi

echo ""
echo "✅ 推送完成！"
gh repo view "$USER/$REPO" --json url -q .url
