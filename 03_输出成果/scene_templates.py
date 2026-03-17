#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景模板库
- 预设常见决策场景
- 参数化任务描述
- 一键启动讨论

Author: 南乔
Date: 2026-03-14
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class SceneTemplate:
    """场景模板"""
    id: str
    name: str
    description: str
    task_template: str  # 任务描述模板，{param}为占位符
    params: List[Dict]  # 参数定义
    recommended_agents: List[str]  # 推荐Agent
    knowledge_files: List[str]  # 关联知识库
    outputs: List[str]  # 产出物
    estimated_rounds: int  # 预计轮次


# ==================== 预设场景模板 ====================
SCENE_TEMPLATES = {
    # 智能客服系统
    'smart-customer-service': SceneTemplate(
        id='smart-customer-service',
        name='智能客服系统',
        description='智能客服系统全流程：需求分析→方案设计→成本估算',
        task_template='{enterprise}智能客服系统需求分析与方案设计',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['caiwei', 'zhutai', 'chengcai'],
        knowledge_files=[
            'industries/telecom/scenarios/scenarios-overview.md',
            'industries/telecom/ai-capabilities/ai-parameters.md'
        ],
        outputs=['需求文档.docx', '方案PPT.pptx'],
        estimated_rounds=10
    ),
    
    # 电渠智能化
    'digital-channel-ai': SceneTemplate(
        id='digital-channel-ai',
        name='电渠智能化转型',
        description='电子渠道智能化升级：AI配案+存量经营+营销自动化',
        task_template='{enterprise}电子渠道智能化转型项目需求分析',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['caiwei', 'zhijin', 'zhutai'],
        knowledge_files=[
            'industries/telecom/business/business-overview.md',
            'industries/telecom/scenarios/scenarios-overview.md'
        ],
        outputs=['需求文档.docx', '思维导图.html', '方案Excel.xlsx'],
        estimated_rounds=12
    ),
    
    # AI智能配案
    'ai-recommendation': SceneTemplate(
        id='ai-recommendation',
        name='AI智能配案系统',
        description='AI智能配案系统：需求→设计→成本',
        task_template='{enterprise}AI智能配案系统功能设计与成本估算',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['caiwei', 'gongchi', 'yuheng'],
        knowledge_files=[
            'industries/telecom/ai-capabilities/ai-parameters.md'
        ],
        outputs=['需求文档.docx', '详细设计.docx', '成本估算.xlsx'],
        estimated_rounds=8
    ),
    
    # 存量经营平台
    '存量经营': SceneTemplate(
        id='存量经营',
        name='存量经营平台',
        description='存量经营平台升级：需求→方案→项目计划',
        task_template='{enterprise}存量经营平台升级改造项目全流程',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['caiwei', 'zhutai', 'chengcai', 'yuheng'],
        knowledge_files=[
            'industries/telecom/business/business-rules.md'
        ],
        outputs=['全套文档'],
        estimated_rounds=15
    ),
    
    # 数据中台
    'data-platform': SceneTemplate(
        id='data-platform',
        name='数据中台建设',
        description='数据中台建设：架构设计→数据治理→安全规范',
        task_template='{enterprise}数据中台建设架构设计与数据治理方案',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['zhijin', 'gongchi', 'yuheng'],
        knowledge_files=[
            'industries/telecom/systems/systems-overview.md',
            'industries/telecom/standards/security-compliance.md'
        ],
        outputs=['架构图.png', '详细设计.docx', '项目计划.xlsx'],
        estimated_rounds=10
    ),
    
    # 智能营销话术
    'smart-script': SceneTemplate(
        id='smart-script',
        name='智能营销话术系统',
        description='智能营销话术推荐系统：需求→设计',
        task_template='{enterprise}智能营销话术推荐系统需求分析与功能设计',
        params=[
            {'name': 'enterprise', 'label': '企业名称', 'default': '湖北电信', 'type': 'text'}
        ],
        recommended_agents=['caiwei', 'zhutai'],
        knowledge_files=[
            'industries/telecom/scenarios/scenarios-overview.md'
        ],
        outputs=['需求文档.docx', '方案Excel.xlsx'],
        estimated_rounds=8
    )
}


class SceneTemplateAPI:
    """场景模板API"""
    
    def __init__(self):
        self.templates = SCENE_TEMPLATES
    
    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'params': t.params,
                'estimated_rounds': t.estimated_rounds
            }
            for t in self.templates.values()
        ]
    
    def get_template(self, template_id: str) -> Optional[SceneTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def fill_template(self, template_id: str, params: Dict) -> Dict:
        """填充模板参数，返回完整任务描述"""
        template = self.templates.get(template_id)
        if not template:
            return {'error': '模板不存在'}
        
        # 填充参数
        task = template.task_template
        for key, value in params.items():
            task = task.replace('{' + key + '}', value)
        
        return {
            'task': task,
            'recommended_agents': template.recommended_agents,
            'knowledge_files': template.knowledge_files,
            'outputs': template.outputs,
            'estimated_rounds': template.estimated_rounds
        }
    
    def to_dict(self, template: SceneTemplate) -> Dict:
        """转换为字典"""
        return {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'task_template': template.task_template,
            'params': template.params,
            'recommended_agents': template.recommended_agents,
            'knowledge_files': template.knowledge_files,
            'outputs': template.outputs,
            'estimated_rounds': template.estimated_rounds
        }


# 测试
if __name__ == '__main__':
    api = SceneTemplateAPI()
    
    print("=" * 60)
    print("📋 场景模板库")
    print("=" * 60)
    
    templates = api.list_templates()
    for t in templates:
        print(f"\n{t['id']}: {t['name']}")
        print(f"   {t['description']}")
        print(f"   预计轮次: {t['estimated_rounds']}")
    
    print("\n" + "=" * 60)
    print("测试填充模板")
    print("=" * 60)
    
    result = api.fill_template('smart-customer-service', {'enterprise': '湖北电信'})
    print(f"\n任务: {result['task']}")
    print(f"推荐Agent: {result['recommended_agents']}")
    print(f"产出物: {result['outputs']}")
