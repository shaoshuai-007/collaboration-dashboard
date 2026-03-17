#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多产出物工作流
- 自动识别产出物依赖关系
- 拓扑排序确定执行顺序
- 上下文传递保持一致性
- 生成统一会议纪要

Author: 南乔
Date: 2026-03-15
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# 导入模块
from nanqiao_intent_analyzer import NanqiaoIntentAnalyzer, StructuredIntent
from multi_round_discussion import MultiRoundDiscussion
from meeting_minutes_generator import MeetingMinutesGenerator


@dataclass
class OutputStep:
    """产出物执行步骤"""
    step_num: int           # 步骤编号
    output: dict            # 产出物信息
    dependencies: List[str] # 依赖的产出物代码
    status: str             # 状态: pending/running/completed


class MultiOutputWorkflow:
    """多产出物工作流"""
    
    # 产出物依赖关系定义
    OUTPUT_DEPENDENCIES = {
        'SRS': [],                    # 需求规格说明书 - 无依赖
        'SAD': ['SRS'],               # 系统架构设计 - 依赖需求
        'DDD': ['SRS', 'SAD'],        # 详细设计 - 依赖需求+架构
        'PP': ['SRS', 'SAD'],         # 项目计划 - 依赖需求+架构
        'CE': ['PP'],                 # 成本估算 - 依赖项目计划
        'RR': ['SRS', 'SAD'],         # 风险登记册 - 依赖需求+架构
        'MINDMAP': ['SRS'],           # 思维导图 - 依赖需求
        'PPT': ['SRS', 'SAD'],        # 方案PPT - 依赖需求+架构
    }
    
    # 产出物中文名
    OUTPUT_NAMES = {
        'SRS': '需求规格说明书',
        'SAD': '系统架构设计文档',
        'DDD': '详细设计说明书',
        'PP': '项目计划书',
        'CE': '成本估算表',
        'RR': '风险登记册',
        'MINDMAP': '思维导图',
        'PPT': '方案PPT',
    }
    
    # 产出物负责人
    OUTPUT_OWNERS = {
        'SRS': '采薇',
        'SAD': '织锦',
        'DDD': '工尺',
        'PP': '扶摇',
        'CE': '筑台',
        'RR': '玉衡',
        'MINDMAP': '织锦',
        'PPT': '呈彩',
    }
    
    def __init__(self):
        self.intent_analyzer = NanqiaoIntentAnalyzer()
        self.discussion = MultiRoundDiscussion()
        self.minutes_generator = MeetingMinutesGenerator()
        
        self.execution_results = {}
        self.all_rounds = []
    
    def execute(self, user_input: str) -> dict:
        """
        执行多产出物工作流
        
        Args:
            user_input: 用户输入
        
        Returns:
            {
                'intent': StructuredIntent,
                'steps': List[OutputStep],
                'results': dict,
                'meeting_minutes': str,
                'minutes_file': str
            }
        """
        print(f"[INFO] 开始执行多产出物工作流")
        print(f"[INFO] 用户输入: {user_input}")
        
        # 1. 意图分析
        intent = self.intent_analyzer.analyze(user_input)
        print(f"[INFO] 意图分析完成: {intent.structured_intent}")
        
        # 2. 拓扑排序
        steps = self._topological_sort(intent.outputs)
        print(f"[INFO] 拓扑排序完成: {len(steps)}个步骤")
        
        # 3. 分步执行
        self.execution_results = {}
        self.all_rounds = []
        
        for step in steps:
            print(f"[INFO] 执行步骤{step.step_num}: {step.output['name']}")
            
            # 获取依赖内容
            dependency_context = self._get_dependency_context(step.dependencies)
            
            # 执行讨论
            result = self._execute_step(step, intent, dependency_context)
            
            # 记录结果
            self.execution_results[step.output['code']] = result
            self.all_rounds.extend(result.get('rounds', []))
            
            step.status = 'completed'
            print(f"[INFO] 步骤{step.step_num}完成")
        
        # 4. 生成统一会议纪要
        meeting_minutes = self._generate_unified_minutes(intent)
        
        # 5. 导出到文件
        minutes_file = self.minutes_generator.export_to_file(meeting_minutes)
        
        print(f"[INFO] 工作流执行完成")
        
        return {
            'intent': intent,
            'steps': steps,
            'results': self.execution_results,
            'meeting_minutes': meeting_minutes,
            'minutes_file': minutes_file
        }
    
    def _topological_sort(self, outputs: List[dict]) -> List[OutputStep]:
        """
        拓扑排序
        
        Args:
            outputs: 产出物列表
        
        Returns:
            排序后的步骤列表
        """
        # 提取产出物代码
        output_codes = [o['code'] for o in outputs]
        
        # 拓扑排序
        sorted_codes = []
        added_codes = set()
        
        max_iterations = len(output_codes) * 2  # 防止死循环
        iterations = 0
        
        while len(sorted_codes) < len(output_codes) and iterations < max_iterations:
            iterations += 1
            
            for code in output_codes:
                if code in added_codes:
                    continue
                
                # 获取依赖
                deps = self.OUTPUT_DEPENDENCIES.get(code, [])
                
                # 过滤掉不在本次产出物列表中的依赖
                relevant_deps = [d for d in deps if d in output_codes]
                
                # 检查依赖是否已添加
                if all(d in added_codes for d in relevant_deps):
                    sorted_codes.append(code)
                    added_codes.add(code)
        
        # 创建步骤对象
        steps = []
        for i, code in enumerate(sorted_codes, 1):
            output = next((o for o in outputs if o['code'] == code), None)
            if output:
                deps = self.OUTPUT_DEPENDENCIES.get(code, [])
                relevant_deps = [d for d in deps if d in output_codes]
                
                steps.append(OutputStep(
                    step_num=i,
                    output=output,
                    dependencies=relevant_deps,
                    status='pending'
                ))
        
        return steps
    
    def _get_dependency_context(self, dependencies: List[str]) -> str:
        """获取依赖内容"""
        
        if not dependencies:
            return ""
        
        context_parts = []
        
        for dep_code in dependencies:
            if dep_code in self.execution_results:
                result = self.execution_results[dep_code]
                
                # 获取讨论结论
                if 'rounds' in result and result['rounds']:
                    last_round = result['rounds'][-1]
                    for msg in last_round.messages:
                        context_parts.append(f"【{msg.speaker_name}】{msg.content[:200]}")
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def _execute_step(self, step: OutputStep, intent: StructuredIntent, 
                       dependency_context: str) -> dict:
        """
        执行单个步骤
        
        Args:
            step: 步骤对象
            intent: 结构化意图
            dependency_context: 依赖内容
        
        Returns:
            讨论结果
        """
        step.status = 'running'
        
        # 构建增强的任务描述
        enhanced_task = intent.structured_intent
        
        if dependency_context:
            enhanced_task += f"\n\n已有前置产出物：\n{dependency_context}"
        
        # 确定参与角色
        output_code = step.output['code']
        participants = self._determine_participants(output_code)
        
        # 确定讨论轮次
        discussion_rounds = self._determine_rounds(output_code, intent.complexity)
        
        # 执行讨论
        result = self.discussion.run(
            task=enhanced_task,
            structured_intent={
                'structured_intent': enhanced_task,
                'project_name': intent.project_name,
                'task_name': step.output['name']
            },
            participants=participants,
            max_rounds=discussion_rounds
        )
        
        return result
    
    def _determine_participants(self, output_code: str) -> List[str]:
        """确定参与角色"""
        
        # 基于产出物类型确定参与者
        participant_map = {
            'SRS': ['caiwei', 'zhijin', 'yuheng'],           # 需求
            'SAD': ['zhijin', 'caiwei', 'gongchi', 'yuheng'], # 架构
            'DDD': ['gongchi', 'zhijin', 'yuheng'],           # 详细设计
            'PP': ['fuyao', 'yuheng', 'zhutai'],              # 项目计划
            'CE': ['zhutai', 'yuheng'],                       # 成本估算
            'RR': ['yuheng', 'caiwei', 'zhijin'],             # 风险登记
            'MINDMAP': ['zhijin', 'caiwei'],                  # 思维导图
            'PPT': ['chengcai', 'caiwei', 'zhijin'],          # PPT
        }
        
        return participant_map.get(output_code, ['caiwei', 'yuheng'])
    
    def _determine_rounds(self, output_code: str, complexity: str) -> int:
        """确定讨论轮次"""
        
        # 基础轮次
        base_rounds = {
            'low': 1,
            'medium': 2,
            'high': 2
        }
        
        return base_rounds.get(complexity, 2)
    
    def _generate_unified_minutes(self, intent: StructuredIntent) -> str:
        """生成统一会议纪要"""
        
        # 构建统一的讨论结果
        unified_result = {
            'rounds': self.all_rounds,
            'consensus_reached': True,
            'key_decisions': self._extract_all_decisions()
        }
        
        # 生成会议纪要
        return self.minutes_generator.generate(intent.__dict__, unified_result)
    
    def _extract_all_decisions(self) -> List[str]:
        """提取所有决策"""
        
        decisions = []
        
        for code, result in self.execution_results.items():
            output_name = self.OUTPUT_NAMES.get(code, code)
            key_decisions = result.get('key_decisions', [])
            
            for decision in key_decisions[:2]:  # 每个产出物最多2条
                decisions.append(f"[{output_name}] {decision}")
        
        return decisions


# ==================== 测试用例 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("多产出物工作流测试")
    print("=" * 60)
    
    # 创建工作流
    workflow = MultiOutputWorkflow()
    
    # 测试用例1：单一产出物
    print("\n--- 测试1：单一产出物 ---")
    result1 = workflow.execute("做一个智能客服系统的需求分析")
    print(f"产出物数量：{len(result1['steps'])}")
    print(f"会议纪要文件：{result1['minutes_file']}")
    
    # 测试用例2：多产出物
    print("\n--- 测试2：多产出物 ---")
    result2 = workflow.execute("智能客服系统的需求文档和架构设计")
    print(f"产出物数量：{len(result2['steps'])}")
    
    print("\n执行顺序：")
    for step in result2['steps']:
        deps = f" (依赖: {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"  步骤{step.step_num}: {step.output['name']}{deps}")
    
    print(f"\n会议纪要文件：{result2['minutes_file']}")
    
    # 测试用例3：全流程
    print("\n--- 测试3：全流程 ---")
    result3 = workflow.execute("给出完整的可落地方案")
    print(f"产出物数量：{len(result3['steps'])}")
    
    print("\n执行顺序：")
    for step in result3['steps']:
        deps = f" (依赖: {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"  步骤{step.step_num}: {step.output['name']}{deps}")
    
    print("\n✅ 测试完成")
