#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能调度执行器
- 意图识别 → 技能组合选择 → 自动执行
- 端到端自动化

Author: 南乔
Date: 2026-03-14
"""

from typing import Dict, List, Tuple
from datetime import datetime
import json

# 导入意图调度器
from intent_scheduler import IntelligentScheduler
# 导入指南针对接器
from compass_connector import CompassConnector


# ==================== 任务类型 → 技能组合映射 ====================
TASK_SKILL_MAPPING = {
    # 需求阶段 → 采薇
    'REQ-01': {'skills': ['caiwei'], 'description': '需求调研 → 需求文档'},
    'REQ-02': {'skills': ['caiwei'], 'description': '需求分析 → 需求文档'},
    'REQ-03': {'skills': ['caiwei', 'zhijin'], 'description': '需求评审 → 需求文档 + 思维导图'},
    'REQ-04': {'skills': ['caiwei'], 'description': '需求变更 → 需求文档'},
    
    # 设计阶段 → 织锦 + 筑台 + 呈彩
    'DES-01': {'skills': ['zhijin', 'chengcai'], 'description': '架构设计 → 思维导图 + PPT'},
    'DES-02': {'skills': ['zhijin', 'zhutai', 'chengcai'], 'description': '方案设计 → 思维导图 + 方案举措 + PPT'},
    'DES-03': {'skills': ['zhijin'], 'description': '技术选型 → 思维导图'},
    'DES-04': {'skills': ['zhijin', 'chengcai'], 'description': '原型设计 → 思维导图 + PPT'},
    
    # 开发阶段 → 工尺
    'DEV-01': {'skills': ['gongchi'], 'description': '技术选型 → 详细设计'},
    'DEV-02': {'skills': ['gongchi'], 'description': '代码开发 → 详细设计'},
    'DEV-03': {'skills': ['gongchi'], 'description': '代码审查 → 详细设计'},
    
    # 测试阶段 → 工尺
    'TST-01': {'skills': ['gongchi'], 'description': '测试用例 → 详细设计'},
    'TST-02': {'skills': ['gongchi'], 'description': '测试执行 → 详细设计'},
    'TST-03': {'skills': ['gongchi'], 'description': '缺陷管理 → 详细设计'},
    
    # 部署阶段 → 工尺 + 玉衡
    'DEP-01': {'skills': ['gongchi', 'yuheng'], 'description': '部署规划 → 详细设计 + 项目管控'},
    'DEP-02': {'skills': ['gongchi', 'yuheng'], 'description': '上线发布 → 详细设计 + 项目管控'},
    
    # 项目管理 → 玉衡
    'PM-01': {'skills': ['yuheng'], 'description': '项目计划 → 项目管控'},
    'PM-02': {'skills': ['yuheng'], 'description': '成本估算 → 项目管控'},
    'PM-03': {'skills': ['yuheng'], 'description': '风险评估 → 项目管控'},
    'PM-04': {'skills': ['yuheng'], 'description': '项目汇报 → 项目管控'},
}


# ==================== 智能调度执行器 ====================
class SmartScheduler:
    """智能调度执行器"""
    
    def __init__(self):
        self.scheduler = IntelligentScheduler()
        self.connector = CompassConnector()
    
    def execute(self, task_input: str, discussion_data: Dict = None) -> Dict:
        """
        智能调度执行
        
        Args:
            task_input: 任务输入（自然语言）
            discussion_data: 讨论数据（可选）
        
        Returns:
            {
                'task_code': str,
                'task_name': str,
                'confidence': float,
                'skills': list,
                'results': dict,
                'outputs': list
            }
        """
        # 1. 意图识别
        schedule_result = self.scheduler.process(task_input)
        
        task_code = schedule_result['task_code']
        task_name = schedule_result['task_name']
        confidence = schedule_result['confidence']
        complexity = schedule_result.get('complexity', 'medium')
        
        # 2. 获取技能组合
        skill_config = TASK_SKILL_MAPPING.get(task_code, {'skills': ['caiwei'], 'description': '默认需求文档'})
        skills = skill_config['skills']
        
        # 3. 准备执行数据
        if discussion_data is None:
            discussion_data = {
                'task': task_input,
                'turns': [],
                'key_points': [task_input],
                'risks': [],
                'consensus_level': 80
            }
        
        # 4. 执行技能组合
        results = self.connector.execute_workflow(discussion_data, skills=skills)
        
        # 5. 整理输出
        outputs = []
        for skill_id, result in results.items():
            if result['success']:
                outputs.append({
                    'skill': skill_id,
                    'file': result['output_path'].split('/')[-1],
                    'path': result['output_path']
                })
        
        return {
            'task_code': task_code,
            'task_name': task_name,
            'confidence': confidence,
            'complexity': complexity,
            'skills': skills,
            'skill_description': skill_config['description'],
            'results': results,
            'outputs': outputs,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_full_workflow(self, task_input: str, discussion_data: Dict = None) -> Dict:
        """
        执行完整工作流（所有6个技能）
        
        Args:
            task_input: 任务输入
            discussion_data: 讨论数据
        
        Returns:
            执行结果
        """
        if discussion_data is None:
            discussion_data = {
                'task': task_input,
                'turns': [],
                'key_points': [task_input],
                'risks': [],
                'consensus_level': 80
            }
        
        # 执行所有技能
        results = self.connector.execute_workflow(discussion_data)
        
        outputs = []
        for skill_id, result in results.items():
            if result['success']:
                outputs.append({
                    'skill': skill_id,
                    'file': result['output_path'].split('/')[-1],
                    'path': result['output_path']
                })
        
        return {
            'task': task_input,
            'mode': 'full_workflow',
            'skills': list(results.keys()),
            'outputs': outputs,
            'timestamp': datetime.now().isoformat()
        }


# ==================== API接口 ====================
def smart_execute(task_input: str, discussion_data: Dict = None, full_workflow: bool = False) -> Dict:
    """
    智能执行入口函数
    
    Args:
        task_input: 任务输入
        discussion_data: 讨论数据
        full_workflow: 是否执行全流程
    
    Returns:
        执行结果
    """
    scheduler = SmartScheduler()
    
    if full_workflow:
        return scheduler.execute_full_workflow(task_input, discussion_data)
    else:
        return scheduler.execute(task_input, discussion_data)


# ==================== 测试 ====================
if __name__ == '__main__':
    print("=" * 70)
    print("智能调度执行器测试")
    print("=" * 70)
    
    test_tasks = [
        "我需要做需求分析",
        "请帮我设计方案架构",
        "项目风险评估",
        "技术选型评估",
        "帮我生成项目计划",
        "完整工作流：智能客服系统"
    ]
    
    for task in test_tasks:
        print(f"\n【任务】{task}")
        print("-" * 70)
        
        if "完整工作流" in task:
            result = smart_execute(task, full_workflow=True)
            print(f"  模式：完整工作流")
            print(f"  技能：{' → '.join(result['skills'])}")
        else:
            result = smart_execute(task)
            print(f"  识别：{result['task_code']} - {result['task_name']}")
            print(f"  置信度：{result['confidence']:.0%}")
            print(f"  复杂度：{result['complexity']}")
            print(f"  调度：{result['skill_description']}")
            print(f"  技能：{' → '.join(result['skills'])}")
        
        print(f"  输出：{len(result['outputs'])}个文档")
        for output in result['outputs']:
            print(f"    ✅ {output['file']}")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
