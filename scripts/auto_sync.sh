#!/bin/bash
# 自动同步代码到GitHub
# 使用方式: ./auto_sync.sh [commit_message]

REPO_DIR="/root/.openclaw/workspace"
GITHUB_USER="shaoshuai-007"
GITHUB_TOKEN="${GITHUB_TOKEN}"
REPO_NAME="collaboration-dashboard"

# 进入仓库目录
cd /tmp/github-push || exit 1

# 检查是否有变更
if git diff-index --quiet HEAD --; then
    echo "No changes to sync"
    exit 0
fi

# 生成提交信息
if [ -z "$1" ]; then
    COMMIT_MSG="auto: 自动同步代码 $(date '+%Y-%m-%d %H:%M')"
else
    COMMIT_MSG="$1"
fi

# 添加所有变更
git add -A

# 提交
git commit -m "$COMMIT_MSG"

# 推送（跳过SSL验证）
GIT_SSL_NO_VERIFY=1 git push origin main

echo "✅ Code synced to GitHub: $COMMIT_MSG"
