#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南乔意图分析器
- 理解客户真正想要什么
- 识别产出物、复杂度、参与角色
- 生成结构化意图

Author: 南乔
Date: 2026-03-15
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

# 导入现有模块
from intent_scheduler import TASK_TYPES, RACI_MATRIX, AGENTS


@dataclass
class OutputItem:
    """产出物项"""
    name: str        # 产出物名称
    code: str        # 产出物代码
    owner: str       # 负责人


@dataclass
class StructuredIntent:
    """结构化意图"""
    project_name: str           # 项目名称
    task_type: str              # 任务类型
    task_name: str              # 任务名称
    outputs: List[Dict]         # 产出物清单
    complexity: str             # 复杂度
    participants: List[str]     # 参与角色
    discussion_rounds: int      # 讨论轮次
    structured_intent: str      # 结构化意图描述


class NanqiaoIntentAnalyzer:
    """南乔意图分析器"""
    
    # 产出物关键词映射
    OUTPUT_KEYWORDS = {
        # 需求类
        '需求': {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'},
        '需求文档': {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'},
        'SRS': {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'},
        '需求分析': {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'},
        
        # 设计类
        '架构': {'name': '系统架构设计文档', 'code': 'SAD', 'owner': '织锦'},
        '架构图': {'name': '系统架构设计文档', 'code': 'SAD', 'owner': '织锦'},
        '系统设计': {'name': '系统架构设计文档', 'code': 'SAD', 'owner': '织锦'},
        '架构设计': {'name': '系统架构设计文档', 'code': 'SAD', 'owner': '织锦'},
        '详细设计': {'name': '详细设计说明书', 'code': 'DDD', 'owner': '工尺'},
        '接口设计': {'name': '详细设计说明书', 'code': 'DDD', 'owner': '工尺'},
        
        # 项目管理类
        '项目计划': {'name': '项目计划书', 'code': 'PP', 'owner': '扶摇'},
        '排期': {'name': '项目计划书', 'code': 'PP', 'owner': '扶摇'},
        '甘特图': {'name': '项目计划书', 'code': 'PP', 'owner': '扶摇'},
        '项目管控': {'name': '项目计划书', 'code': 'PP', 'owner': '扶摇'},
        '成本': {'name': '成本估算表', 'code': 'CE', 'owner': '筑台'},
        '预算': {'name': '成本估算表', 'code': 'CE', 'owner': '筑台'},
        '报价': {'name': '成本估算表', 'code': 'CE', 'owner': '筑台'},
        '风险': {'name': '风险登记册', 'code': 'RR', 'owner': '玉衡'},
        '风险评估': {'name': '风险登记册', 'code': 'RR', 'owner': '玉衡'},
        
        # 思维导图
        '思维导图': {'name': '思维导图', 'code': 'MINDMAP', 'owner': '织锦'},
        '分析图': {'name': '思维导图', 'code': 'MINDMAP', 'owner': '织锦'},
        
        # 方案PPT
        'PPT': {'name': '方案PPT', 'code': 'PPT', 'owner': '呈彩'},
        '方案PPT': {'name': '方案PPT', 'code': 'PPT', 'owner': '呈彩'},
        '汇报PPT': {'name': '方案PPT', 'code': 'PPT', 'owner': '呈彩'},
    }
    
    # 全流程关键词
    FULL_FLOW_KEYWORDS = ['完整方案', '可落地', '全流程', '一站式', '完整']
    
    def analyze(self, user_input: str) -> StructuredIntent:
        """
        分析用户意图
        
        Args:
            user_input: 用户输入
        
        Returns:
            StructuredIntent: 结构化意图
        """
        # 1. 提取项目名称
        project_name = self._extract_project_name(user_input)
        
        # 2. 识别产出物
        outputs = self._identify_outputs(user_input)
        
        # 3. 映射任务类型
        task_type = self._map_to_task_type(outputs, user_input)
        
        # 4. 判断复杂度
        complexity = self._assess_complexity(outputs)
        
        # 5. 确定参与角色
        participants = self._determine_participants(task_type, complexity)
        
        # 6. 计算讨论轮次
        discussion_rounds = self._calculate_rounds(complexity, len(participants))
        
        # 7. 生成结构化意图描述
        structured_intent = self._generate_structured_intent(
            project_name, task_type, outputs
        )
        
        return StructuredIntent(
            project_name=project_name,
            task_type=task_type,
            task_name=TASK_TYPES.get(task_type, TASK_TYPES['REQ-02']).name,
            outputs=outputs,
            complexity=complexity,
            participants=participants,
            discussion_rounds=discussion_rounds,
            structured_intent=structured_intent
        )
    
    def _extract_project_name(self, user_input: str) -> str:
        """提取项目名称"""
        
        # 规则1：XX系统的"系统"前的内容
        patterns = [
            r'(.+?)系统',        # 智能客服系统 → 智能客服
            r'(.+?)平台',        # 营销平台 → 营销
            r'(.+?)项目',        # AI项目 → AI
            r'关于(.+?)的',      # 关于智能客服的需求 → 智能客服
            r'为(.+?)做',        # 为智能客服做需求 → 智能客服
            r'帮(.+?)做',        # 帮智能客服做需求 → 智能客服
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                name = match.group(1).strip()
                # 过滤掉常见的无意义词
                if name not in ['一个', '这个', '那个', '某', '做一个', '做']:
                    # 清理前面的动词
                    for prefix in ['做一个', '做', '做一个', '帮我做', '帮我', '请做', '请']:
                        if name.startswith(prefix):
                            name = name[len(prefix):]
                    return name
        
        # 如果没有明确的项目名，返回"待定"
        return "待定"
    
    def _identify_outputs(self, user_input: str) -> List[Dict]:
        """识别产出物"""
        
        outputs = []
        
        # 检查是否全流程
        for keyword in self.FULL_FLOW_KEYWORDS:
            if keyword in user_input:
                return [
                    {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'},
                    {'name': '系统架构设计文档', 'code': 'SAD', 'owner': '织锦'},
                    {'name': '详细设计说明书', 'code': 'DDD', 'owner': '工尺'},
                    {'name': '项目计划书', 'code': 'PP', 'owner': '扶摇'},
                    {'name': '成本估算表', 'code': 'CE', 'owner': '筑台'},
                ]
        
        # 匹配关键词
        for keyword, output_info in self.OUTPUT_KEYWORDS.items():
            if keyword in user_input:
                outputs.append(output_info.copy())
        
        # 去重（按code）
        seen = set()
        unique_outputs = []
        for o in outputs:
            if o['code'] not in seen:
                seen.add(o['code'])
                unique_outputs.append(o)
        
        # 默认：需求文档
        return unique_outputs if unique_outputs else [
            {'name': '需求规格说明书', 'code': 'SRS', 'owner': '采薇'}
        ]
    
    def _map_to_task_type(self, outputs: List[Dict], user_input: str) -> str:
        """映射到任务类型"""
        
        # 基于产出物映射
        output_codes = [o['code'] for o in outputs]
        
        # 单产出物映射
        if len(outputs) == 1:
            code = outputs[0]['code']
            mapping = {
                'SRS': 'REQ-02',      # 需求分析
                'SAD': 'DES-01',      # 架构设计
                'DDD': 'DES-02',      # 详细设计
                'PP': 'PM-01',        # 项目计划
                'CE': 'PM-02',        # 成本估算
                'RR': 'PM-03',        # 风险管理
                'MINDMAP': 'DES-01',  # 思维导图归入架构设计
                'PPT': 'DES-04',      # PPT归入UI设计
            }
            return mapping.get(code, 'REQ-02')
        
        # 多产出物：取第一个任务的类型
        if outputs:
            return self._map_to_task_type([outputs[0]], user_input)
        
        return 'REQ-02'
    
    def _assess_complexity(self, outputs: List[Dict]) -> str:
        """判断复杂度"""
        
        output_count = len(outputs)
        
        if output_count == 1:
            return 'low'
        elif output_count <= 3:
            return 'medium'
        else:
            return 'high'
    
    def _determine_participants(self, task_type: str, complexity: str) -> List[str]:
        """确定参与角色"""
        
        # 基于RACI矩阵
        raci = RACI_MATRIX.get(task_type, {})
        
        if not raci:
            # 默认参与者
            return ['caiwei', 'zhijin', 'yuheng']
        
        # 必选：R和A角色
        participants = []
        for agent_id, role in raci.items():
            if role in ['R', 'A']:
                participants.append(agent_id)
        
        # 根据复杂度添加C角色
        if complexity in ['medium', 'high']:
            for agent_id, role in raci.items():
                if role == 'C' and agent_id not in participants:
                    participants.append(agent_id)
        
        return participants if participants else ['caiwei', 'zhijin', 'yuheng']
    
    def _calculate_rounds(self, complexity: str, participant_count: int) -> int:
        """计算讨论轮次"""
        
        base_rounds = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        return base_rounds.get(complexity, 2)
    
    def _generate_structured_intent(self, project_name: str, task_type: str, 
                                     outputs: List[Dict]) -> str:
        """生成结构化意图描述"""
        
        task_name = TASK_TYPES.get(task_type, TASK_TYPES['REQ-02']).name
        output_names = '、'.join([o['name'] for o in outputs])
        
        return f"为「{project_name}」进行{task_name}，输出{output_names}"


# ==================== 测试用例 ====================
if __name__ == '__main__':
    analyzer = NanqiaoIntentAnalyzer()
    
    # 测试用例
    test_cases = [
        "做一个智能客服系统的需求分析",
        "画个架构图",
        "需求文档和架构设计",
        "给出完整的可落地方案",
        "做个成本估算",
        "湖北电信营销平台的项目计划",
    ]
    
    print("=" * 60)
    print("南乔意图分析器测试")
    print("=" * 60)
    
    for test_input in test_cases:
        result = analyzer.analyze(test_input)
        
        print(f"\n输入: {test_input}")
        print(f"项目名称: {result.project_name}")
        print(f"任务类型: {result.task_type} - {result.task_name}")
        print(f"产出物: {[o['name'] for o in result.outputs]}")
        print(f"复杂度: {result.complexity}")
        print(f"参与角色: {result.participants}")
        print(f"讨论轮次: {result.discussion_rounds}")
        print(f"结构化意图: {result.structured_intent}")
        print("-" * 60)
