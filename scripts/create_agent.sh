#!/bin/bash
# 技能转智能体一键命令
# 用法：./create_agent.sh <id> <name> <skill> [vibe] [emoji]
#
# 示例：
#   ./create_agent.sh tiangong 天工 compass-dev "代码如诗，追求极致" 💻
#   ./create_agent.sh zhiwei 知微 compass-analysis "数据说话，洞察为先" 📊

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/skill_to_agent.py"

if [ $# -lt 3 ]; then
    echo "用法：$0 <id> <name> <skill> [vibe] [emoji]"
    echo ""
    echo "示例："
    echo "  $0 tiangong 天工 compass-dev \"代码如诗，追求极致\" 💻"
    echo "  $0 zhiwei 知微 compass-analysis \"数据说话，洞察为先\" 📊"
    exit 1
fi

ID="$1"
NAME="$2"
SKILL="$3"
VIBE="${4:-专业、高效、贴心}"
EMOJI="${5:-🤖}"

python3 "$PYTHON_SCRIPT" \
    --id "$ID" \
    --name "$NAME" \
    --skill "$SKILL" \
    --vibe "$VIBE" \
    --emoji "$EMOJI"

echo ""
echo "✅ Agent配置完成！"
echo "⚠️  请执行以下命令重启Gateway："
echo "   openclaw gateway restart --force"
