#!/bin/bash
# 自动Git提交推送脚本
# 使用方法: ./auto_git_push.sh "提交信息"

cd /root/.openclaw/workspace

# 获取提交信息
COMMIT_MSG="${1:-自动提交 $(date '+%Y-%m-%d %H:%M:%S')}"

# 添加所有修改
git add -A

# 提交
git commit -m "$COMMIT_MSG"

# 推送（如果配置了远程仓库）
if git remote | grep -q origin; then
    git push origin master
    echo "✅ 已推送到GitHub"
else
    echo "⚠️ 未配置远程仓库，仅本地提交"
    echo "配置方法: git remote add origin <仓库地址>"
fi

echo "✅ 提交完成: $COMMIT_MSG"
