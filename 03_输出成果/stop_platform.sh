#!/bin/bash
# 指南针工程智能协作平台 - 停止脚本

LOG_FILE="/root/.openclaw/workspace/03_输出成果/platform_access.log"

echo "════════════════════════════════════════"
echo "🧭 指南针工程智能协作平台 - 停止"
echo "════════════════════════════════════════"

# 检查是否运行
if ! netstat -tlnp 2>/dev/null | grep -q ":5001"; then
    echo "⚠️ 平台未运行"
    exit 0
fi

# 停止平台
pkill -f collaboration_dashboard_v11
sleep 1

if ! netstat -tlnp 2>/dev/null | grep -q ":5001"; then
    echo "✅ 平台已停止"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 平台已手动停止" >> "$LOG_FILE"
else
    echo "❌ 停止失败，请检查进程"
fi
