#!/bin/bash
# 指南针工程智能协作平台 - 启动授权脚本
# 
# 使用方法：
#   bash start_platform.sh [授权码]
#
# 授权码获取：向南乔申请临时授权码
#
# 注意：未经授权启动平台将被记录

# 配置
PLATFORM_DIR="/root/.openclaw/workspace/03_输出成果"
PLATFORM_SCRIPT="collaboration_dashboard_v11.py"
LOG_FILE="/root/.openclaw/workspace/03_输出成果/platform_access.log"
AUTH_FILE="/root/.openclaw/workspace/03_输出成果/.platform_auth"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 记录日志
log_access() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查是否已运行
check_running() {
    if netstat -tlnp 2>/dev/null | grep -q ":5001"; then
        echo -e "${YELLOW}⚠️ 平台已在运行中${NC}"
        echo "访问地址: http://120.48.169.242:5001"
        exit 0
    fi
}

# 验证授权
verify_auth() {
    local code="$1"
    
    # 检查授权文件是否存在
    if [ ! -f "$AUTH_FILE" ]; then
        echo -e "${RED}❌ 未找到授权文件${NC}"
        echo "请联系南乔获取授权"
        log_access "未授权启动尝试 (无授权文件)"
        exit 1
    fi
    
    # 读取授权信息
    AUTH_CODE=$(grep "auth_code" "$AUTH_FILE" 2>/dev/null | cut -d'=' -f2)
    AUTH_EXPIRE=$(grep "expire_time" "$AUTH_FILE" 2>/dev/null | cut -d'=' -f2)
    
    # 检查授权码
    if [ -z "$AUTH_CODE" ]; then
        echo -e "${RED}❌ 授权码无效${NC}"
        log_access "未授权启动尝试 (无效授权码)"
        exit 1
    fi
    
    # 检查是否需要授权码
    if [ "$AUTH_CODE" = "DISABLED" ]; then
        echo -e "${RED}❌ 平台已禁用${NC}"
        echo "请联系少帅启用手动授权"
        log_access "启动尝试 (平台已禁用)"
        exit 1
    fi
    
    # 如果提供了授权码，验证
    if [ -n "$code" ]; then
        if [ "$code" != "$AUTH_CODE" ]; then
            echo -e "${RED}❌ 授权码错误${NC}"
            log_access "授权码错误: $code"
            exit 1
        fi
    fi
    
    # 检查过期时间
    if [ -n "$AUTH_EXPIRE" ] && [ "$AUTH_EXPIRE" != "NEVER" ]; then
        CURRENT=$(date +%s)
        if [ "$CURRENT" -gt "$AUTH_EXPIRE" ]; then
            echo -e "${RED}❌ 授权已过期${NC}"
            log_access "启动尝试 (授权过期)"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ 授权验证通过${NC}"
}

# 启动平台
start_platform() {
    cd "$PLATFORM_DIR"
    nohup python3 "$PLATFORM_SCRIPT" > /tmp/collab_platform.log 2>&1 &
    sleep 2
    
    if netstat -tlnp 2>/dev/null | grep -q ":5001"; then
        echo -e "${GREEN}✅ 指南针工程智能协作平台启动成功${NC}"
        echo "访问地址: http://120.48.169.242:5001"
        log_access "平台启动成功"
    else
        echo -e "${RED}❌ 启动失败${NC}"
        log_access "平台启动失败"
        exit 1
    fi
}

# 主流程
main() {
    echo "════════════════════════════════════════"
    echo "🧭 指南针工程智能协作平台"
    echo "════════════════════════════════════════"
    
    check_running
    verify_auth "$1"
    start_platform
}

main "$@"
