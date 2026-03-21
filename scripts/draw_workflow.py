#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团工作流程图
"""

import sys
sys.path.insert(0, '/root/.openclaw/skills/svg-generator')
from caiwei_requirement_diagrams import draw_flowchart

# 定义流程步骤
steps = [
    {'text': '少帅下达任务', 'type': 'start'},
    {'text': '南乔接收并解析意图', 'type': 'process'},
    {'text': '南乔分配任务给对应Agent', 'type': 'process'},
    {'text': '需求分析阶段', 'type': 'io'},
    {'text': '采薇：需求文档（Word）', 'type': 'process'},
    {'text': '方案设计阶段', 'type': 'io'},
    {'text': '织锦：架构方案', 'type': 'process'},
    {'text': '筑台：售前方案', 'type': 'process'},
    {'text': '呈彩：方案PPT', 'type': 'process'},
    {'text': '详细设计阶段', 'type': 'io'},
    {'text': '工尺：系统设计文档', 'type': 'process'},
    {'text': '开发实现阶段', 'type': 'io'},
    {'text': '天工：代码实现', 'type': 'process'},
    {'text': '数据分析阶段', 'type': 'io'},
    {'text': '知微：数据分析报告', 'type': 'process'},
    {'text': '项目管理阶段', 'type': 'io'},
    {'text': '玉衡：项目计划（甘特图）', 'type': 'process'},
    {'text': '知识沉淀阶段', 'type': 'io'},
    {'text': '折桂：知识库归档', 'type': 'process'},
    {'text': '南乔汇总汇报', 'type': 'process'},
    {'text': '提交给少帅', 'type': 'end'}
]

# 绘制流程图
draw_flowchart(
    steps,
    "九星智囊团汇报方案编排流程",
    "/root/.openclaw/workspace/03_输出成果/九星智囊团工作流程图.png"
)

print("✅ 流程图已生成！")
