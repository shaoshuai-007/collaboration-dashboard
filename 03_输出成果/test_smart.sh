#!/bin/bash
# 智能调度测试脚本

echo "========================================================================"
echo "智能调度测试"
echo "========================================================================"

echo ""
echo "【测试1】需求分析"
echo "------------------------------------------------------------------------"
python3 -c "
from smart_scheduler import smart_execute
result = smart_execute('我需要做需求分析')
print(f'任务识别：{result[\"task_code\"]} - {result[\"task_name\"]}')
print(f'置信度：{result[\"confidence\"]:.0%}')
print(f'调度技能：{\" → \".join(result[\"skills\"])}')
print(f'输出文档：')
for o in result['outputs']:
    print(f'  ✅ {o[\"file\"]}')
"

echo ""
echo "【测试2】方案设计"
echo "------------------------------------------------------------------------"
python3 -c "
from smart_scheduler import smart_execute
result = smart_execute('请帮我设计方案架构')
print(f'任务识别：{result[\"task_code\"]} - {result[\"task_name\"]}')
print(f'置信度：{result[\"confidence\"]:.0%}')
print(f'调度技能：{\" → \".join(result[\"skills\"])}')
print(f'输出文档：')
for o in result['outputs']:
    print(f'  ✅ {o[\"file\"]}')
"

echo ""
echo "【测试3】风险评估"
echo "------------------------------------------------------------------------"
python3 -c "
from smart_scheduler import smart_execute
result = smart_execute('项目风险评估')
print(f'任务识别：{result[\"task_code\"]} - {result[\"task_name\"]}')
print(f'置信度：{result[\"confidence\"]:.0%}')
print(f'调度技能：{\" → \".join(result[\"skills\"])}')
print(f'输出文档：')
for o in result['outputs']:
    print(f'  ✅ {o[\"file\"]}')
"

echo ""
echo "【测试4】完整工作流"
echo "------------------------------------------------------------------------"
python3 -c "
from smart_scheduler import smart_execute
result = smart_execute('智能客服系统建设', full_workflow=True)
print(f'执行模式：完整工作流')
print(f'技能链：{\" → \".join(result[\"skills\"])}')
print(f'输出文档：')
for o in result['outputs']:
    print(f'  ✅ {o[\"file\"]}')
"

echo ""
echo "========================================================================"
echo "测试完成！输出目录：/root/.openclaw/workspace/03_输出成果/指南针输出/"
echo "========================================================================"
