#!/bin/bash
# 九星智囊团新增成员快速脚本
# 用法：./add_member.sh <角色类型> <名字> <emoji> <技能>

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 帮助信息
show_help() {
    echo -e "${RED}九星智囊团新增成员快速脚本${NC}"
    echo ""
    echo "用法："
    echo "  $0 <角色类型> <名字> <emoji> <核心技能>"
    echo ""
    echo "示例："
    echo "  $0 '测试工程师' '试剑' '⚔️' 'coding-agent'"
    echo "  $0 '运维工程师' '运维' '🔧' 'github'"
    echo ""
    echo "预设角色类型："
    echo "  需求分析、架构设计、售前支持、方案设计"
    echo "  系统设计、项目管理、知识管理、协调调度"
    echo "  开发实现、数据分析"
    echo ""
    echo "核心技能："
    echo "  summarize    - 文本摘要"
    echo "  coding-agent - AI编程"
    echo "  github       - 版本管理"
    echo "  coordinator  - 协调调度"
}

# 检查参数
if [ $# -lt 4 ]; then
    show_help
    exit 1
fi

ROLE_TYPE="$1"
NAME="$2"
EMOJI="$3"
SKILL="$4"

# 自动生成技能名称
SKILL_NAME="compass-$(echo "$NAME" | tr '[:upper:]' '[:lower:]')"
SKILL_PATH="/root/.openclaw/skills/$SKILL_NAME"

echo -e "${RED}========================================${NC}"
echo -e "${RED}🌿 九星智囊团新增成员${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "角色类型：${GREEN}$ROLE_TYPE${NC}"
echo -e "成员名字：${GREEN}$NAME${NC}"
echo -e "角色Emoji：${GREEN}$EMOJI${NC}"
echo -e "核心技能：${GREEN}$SKILL${NC}"
echo -e "技能名称：${GREEN}$SKILL_NAME${NC}"
echo ""

# 调用Python脚本
python3 /root/.openclaw/workspace/scripts/add_new_member.py \
    --role "$ROLE_TYPE" \
    --name "$NAME" \
    --emoji "$EMOJI" \
    --skill "$SKILL" \
    --skill-name "$SKILL_NAME"

echo ""
echo -e "${GREEN}✅ 新成员创建完成！${NC}"
echo -e "技能路径：${BLUE}$SKILL_PATH${NC}"
