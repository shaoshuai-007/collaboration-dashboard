#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能意图识别与Agent调度系统
- 四层意图识别架构
- RACI矩阵调度
- 三阶段协作流程

Author: 南乔
Date: 2026-03-14
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json

# ==================== 任务类型定义 ====================
class TaskCategory(Enum):
    """任务阶段分类"""
    REQUIREMENT = "需求阶段"
    DESIGN = "设计阶段"
    DEVELOPMENT = "开发阶段"
    TESTING = "测试阶段"
    DEPLOYMENT = "部署阶段"
    PROJECT_MANAGEMENT = "项目管理"


@dataclass
class TaskType:
    """任务类型定义"""
    code: str           # 任务代码，如 REQ-02
    name: str           # 任务名称
    category: TaskCategory
    description: str    # 任务描述
    keywords: List[str] # 触发关键词
    output_template: str  # 产出物模板
    confidence_base: float = 0.90  # 基础置信度


# ==================== 20个细粒度任务类型 ====================
TASK_TYPES = {
    # 需求阶段
    'REQ-01': TaskType(
        code='REQ-01', name='需求收集', category=TaskCategory.REQUIREMENT,
        description='收集、整理用户需求',
        keywords=['需求收集', '调研', '访谈', '收集需求', '需求调研', '客户访谈', '用户调研', '需求采集', '采集需求', '收集用户需求'],
        output_template='需求调研报告'
    ),
    'REQ-02': TaskType(
        code='REQ-02', name='需求分析', category=TaskCategory.REQUIREMENT,
        description='分析、拆解、规格化需求',
        keywords=['需求文档', 'SRS', '需求规格', '需求分析', '写需求', '需求文档生成', '分析需求', '需求设计', '整理需求', '梳理需求', 
                  '做需求', '需求梳理', '需求整理', '分析一下需求', '需求分析文档', '规格说明书', '需求规格说明书',
                  '需求方案', '方案需求', '需求方案文档', '输出需求', '需求输出', '做需求方案', '需求报告'],
        output_template='需求规格说明书(SRS)'
    ),
    'REQ-03': TaskType(
        code='REQ-03', name='需求评审', category=TaskCategory.REQUIREMENT,
        description='评审需求完整性、可行性',
        keywords=['需求评审', '评审需求', '评审一下', '看看需求', '检查需求', '需求检查', '评审一下需求'],
        output_template='需求评审报告'
    ),
    'REQ-04': TaskType(
        code='REQ-04', name='需求变更', category=TaskCategory.REQUIREMENT,
        description='分析需求变更影响',
        keywords=['需求变更', '变更分析', '需求修改', '变更影响', '需求变更分析', '变更影响分析'],
        output_template='变更影响分析报告'
    ),
    
    # 设计阶段
    'DES-01': TaskType(
        code='DES-01', name='概要设计', category=TaskCategory.DESIGN,
        description='设计系统整体架构',
        keywords=['架构设计', '概要设计', '系统设计', '系统架构', '整体设计', '技术架构', '总体设计', '方案设计',
                  '设计架构', '设计系统', '架构方案', '系统架构设计', '技术方案设计', '总体架构', '整体架构',
                  '功能设计', '功能架构', '功能模块设计', '系统功能设计', '功能方案'],
        output_template='系统架构设计文档(SAD)'
    ),
    'DES-02': TaskType(
        code='DES-02', name='详细设计', category=TaskCategory.DESIGN,
        description='设计模块细节、接口',
        keywords=['详细设计', '接口设计', '模块设计', '详细设计方案', '设计详细方案', '模块详细设计', '接口详细设计', '设计接口', '设计模块'],
        output_template='详细设计说明书(DDD)'
    ),
    'DES-03': TaskType(
        code='DES-03', name='数据库设计', category=TaskCategory.DESIGN,
        description='设计数据模型、表结构',
        keywords=['数据库设计', '表设计', 'ER图', '数据模型', '表结构', '设计数据库', '设计表结构', '数据表设计', '数据库建模'],
        output_template='数据库设计文档'
    ),
    'DES-04': TaskType(
        code='DES-04', name='UI/UX设计', category=TaskCategory.DESIGN,
        description='设计用户界面和交互',
        keywords=['UI设计', '界面设计', '原型设计', 'UX设计', '交互设计', '设计界面', '设计原型', '界面原型', '用户体验设计'],
        output_template='原型设计文档'
    ),
    
    # 开发阶段
    'DEV-01': TaskType(
        code='DEV-01', name='技术选型', category=TaskCategory.DEVELOPMENT,
        description='评估、选择技术方案',
        keywords=['技术选型', '技术方案', '技术栈', '技术选择', '方案对比', '技术评估', '选型评估', '技术方案评估'],
        output_template='技术选型报告'
    ),
    'DEV-02': TaskType(
        code='DEV-02', name='开发计划', category=TaskCategory.DEVELOPMENT,
        description='制定开发迭代计划',
        keywords=['开发计划', '迭代计划', 'WBS', '开发规划', '迭代规划', '制定开发计划', '开发排期', '迭代安排'],
        output_template='迭代计划'
    ),
    'DEV-03': TaskType(
        code='DEV-03', name='代码规范', category=TaskCategory.DEVELOPMENT,
        description='制定编码规范标准',
        keywords=['代码规范', '编码标准', '编码规范', '代码风格', '代码规范文档', '编码规范文档'],
        output_template='编码规范文档'
    ),
    
    # 测试阶段
    'TST-01': TaskType(
        code='TST-01', name='测试策略', category=TaskCategory.TESTING,
        description='制定测试策略和计划',
        keywords=['测试策略', '测试计划', '测试方案', '制定测试计划', '测试规划', '设计测试方案'],
        output_template='测试策略文档'
    ),
    'TST-02': TaskType(
        code='TST-02', name='测试用例', category=TaskCategory.TESTING,
        description='设计测试用例集',
        keywords=['测试用例', '用例设计', '测试用例设计', '设计测试用例', '编写测试用例', '用例编写'],
        output_template='测试用例集'
    ),
    'TST-03': TaskType(
        code='TST-03', name='质量评估', category=TaskCategory.TESTING,
        description='评估软件质量水平',
        keywords=['质量评估', '测试报告', '质量分析', '软件质量', '质量报告', '评估质量', '质量评测'],
        output_template='质量评估报告'
    ),
    
    # 部署阶段
    'DEP-01': TaskType(
        code='DEP-01', name='部署方案', category=TaskCategory.DEPLOYMENT,
        description='设计部署方案和环境',
        keywords=['部署方案', '环境规划', '部署设计', '上线方案', '设计部署', '部署计划', '上线规划', '环境部署'],
        output_template='部署方案文档'
    ),
    'DEP-02': TaskType(
        code='DEP-02', name='运维规划', category=TaskCategory.DEPLOYMENT,
        description='规划运维监控方案',
        keywords=['运维规划', '监控方案', '运维方案', '监控设计', '运维计划', '监控规划', '运维监控'],
        output_template='运维手册'
    ),
    
    # 项目管理
    'PM-01': TaskType(
        code='PM-01', name='项目计划', category=TaskCategory.PROJECT_MANAGEMENT,
        description='制定项目整体计划',
        keywords=['项目计划', '项目规划', '甘特图', '项目排期', '项目计划书', '项目管控', '项目管控计划', '制定计划', '项目进度', '进度计划',
                  '做项目计划', '制定项目计划', '项目计划书', '项目进度计划', '项目时间计划'],
        output_template='项目计划书'
    ),
    'PM-02': TaskType(
        code='PM-02', name='成本估算', category=TaskCategory.PROJECT_MANAGEMENT,
        description='估算项目成本和资源',
        keywords=['成本估算', '预算', '人天', '成本分析', '估算成本', '成本计划', '费用估算', '预算计划', '项目成本', '资源估算',
                  '评估成本', '预算评估', '项目预算', '成本预算', '算一下成本', '算成本', '报价', '项目报价'],
        output_template='成本估算表'
    ),
    'PM-03': TaskType(
        code='PM-03', name='风险管理', category=TaskCategory.PROJECT_MANAGEMENT,
        description='识别、评估、应对风险',
        keywords=['风险评估', '风险管理', '风险分析', '风险识别', '风险', '项目风险', '分析风险', '评估风险', '风险排查', '风险管控'],
        output_template='风险登记册'
    ),
    'PM-04': TaskType(
        code='PM-04', name='方案评估', category=TaskCategory.PROJECT_MANAGEMENT,
        description='评估对比多个方案',
        keywords=['方案对比', '方案评估', '方案选择', '方案比较', '方案分析', '对比方案', '评估方案', '选择方案', '方案评审'],
        output_template='方案评估报告'
    ),
}


# ==================== 同义词词典 ====================
# 用户口语化表达 → 标准任务关键词
SYNONYM_DICT = {
    # 需求类
    '报价': '成本估算',
    '做个报价': '成本估算',
    '报价单': '成本估算',
    '多少钱': '成本估算',
    '花多少钱': '成本估算',
    '算一下钱': '成本估算',
    '算成本': '成本估算',
    
    '想法': '需求分析',
    '整理想法': '需求分析',
    '梳理想法': '需求分析',
    '把想法整理成需求': '需求分析',
    '用户的想法': '需求分析',
    
    '做需求': '需求分析',
    '写需求': '需求分析',
    '需求怎么写': '需求分析',
    '需求文档怎么写': '需求分析',
    
    '调研客户': '需求收集',
    '客户调研': '需求收集',
    '用户调研': '需求收集',
    '调研一下': '需求收集',
    
    # 设计类
    '画架构': '架构设计',
    '设计架构': '架构设计',
    '做个架构': '架构设计',
    '架构怎么设计': '架构设计',
    '系统怎么设计': '系统设计',
    '设计系统': '系统设计',
    
    '详细方案': '详细设计',
    '设计详细方案': '详细设计',
    '详细设计方案': '详细设计',
    '模块怎么设计': '模块设计',
    '接口怎么设计': '接口设计',
    
    '设计数据库': '数据库设计',
    '建表': '数据库设计',
    '表怎么设计': '表结构',
    '数据怎么存': '数据库设计',
    
    '画原型': '原型设计',
    '做个原型': '原型设计',
    '界面怎么设计': '界面设计',
    '设计界面': '界面设计',
    
    # 项目管理类
    '排期': '项目计划',
    '做个排期': '项目计划',
    '排一下期': '项目计划',
    '工期': '项目计划',
    '时间计划': '项目计划',
    '什么时候完成': '项目计划',
    
    '评估风险': '风险评估',
    '有什么风险': '风险评估',
    '风险有哪些': '风险识别',
    '分析风险': '风险分析',
    
    '对比方案': '方案对比',
    '比较方案': '方案对比',
    '选哪个方案': '方案选择',
    
    # 测试类
    '测一下': '测试策略',
    '怎么测': '测试策略',
    '测试怎么搞': '测试策略',
    '写测试用例': '测试用例',
    
    # 部署类
    '怎么部署': '部署方案',
    '上线方案': '部署方案',
    '怎么上线': '部署方案',
}

# ==================== RACI矩阵 ====================
class RACIRole(Enum):
    """RACI角色"""
    R = "Responsible"    # 执行者
    A = "Accountable"    # 负责者
    C = "Consulted"      # 咨询者
    I = "Informed"       # 知情者


@dataclass
class AgentRole:
    """Agent角色定义"""
    agent_id: str
    name: str
    role: str
    color: str


# 9个Agent定义
AGENTS = {
    'BA': AgentRole(agent_id='BA', name='采薇', role='需求分析师', color='#409EFF'),
    'TA': AgentRole(agent_id='TA', name='织锦', role='技术架构师', color='#67C23A'),
    'UX': AgentRole(agent_id='UX', name='呈彩', role='用户体验师', color='#FF9800'),
    'RA': AgentRole(agent_id='RA', name='玉衡', role='风险评估师', color='#F56C6C'),
    'CA': AgentRole(agent_id='CA', name='筑台', role='成本分析师', color='#E6A23C'),
    'PM': AgentRole(agent_id='PM', name='扶摇', role='项目经理', color='#165DFF'),
    'PD': AgentRole(agent_id='PD', name='工尺', role='产品经理', color='#607D8B'),
    'SD': AgentRole(agent_id='SD', name='工尺', role='系统设计师', color='#607D8B'),
    'QA': AgentRole(agent_id='QA', name='折桂', role='测试工程师', color='#00BCD4'),
}

# RACI矩阵配置
# 格式: {任务代码: {AgentID: RACI角色}}
# 使用团队中文名称：采薇、织锦、筑台、呈彩、工尺、玉衡、扶摇
RACI_MATRIX = {
    # 需求阶段
    'REQ-01': {'caiwei': 'R', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'I', 'fuyao': 'I'},
    'REQ-02': {'caiwei': 'R', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'I', 'fuyao': 'C'},
    'REQ-03': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'R', 'gongchi': 'C', 'zhutai': 'I', 'fuyao': 'C'},
    'REQ-04': {'caiwei': 'R', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'I'},
    
    # 设计阶段
    'DES-01': {'caiwei': 'C', 'zhijin': 'R', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'I'},
    'DES-02': {'caiwei': 'C', 'zhijin': 'R', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'I', 'fuyao': 'C'},
    'DES-03': {'caiwei': 'I', 'zhijin': 'C', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'I', 'fuyao': 'I'},
    'DES-04': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'R', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'I', 'fuyao': 'C'},
    
    # 开发阶段
    'DEV-01': {'caiwei': 'C', 'zhijin': 'R', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'C'},
    'DEV-02': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'I', 'yuheng': 'R', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'C'},
    'DEV-03': {'caiwei': 'I', 'zhijin': 'R', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'I', 'fuyao': 'I'},
    
    # 测试阶段
    'TST-01': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'I', 'fuyao': 'I'},
    'TST-02': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'I', 'fuyao': 'I'},
    'TST-03': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'I', 'fuyao': 'I'},
    
    # 部署阶段
    'DEP-01': {'caiwei': 'I', 'zhijin': 'R', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'I'},
    'DEP-02': {'caiwei': 'I', 'zhijin': 'C', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'R', 'zhutai': 'C', 'fuyao': 'I'},
    
    # 项目管理
    'PM-01': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'I', 'yuheng': 'R', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'I'},
    'PM-02': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'I', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'R', 'fuyao': 'I'},
    'PM-03': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'A', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'R'},
    'PM-04': {'caiwei': 'C', 'zhijin': 'C', 'chengcai': 'C', 'yuheng': 'R', 'gongchi': 'C', 'zhutai': 'C', 'fuyao': 'C'},
}


# ==================== 意图识别器 ====================
class IntentRecognizer:
    """意图识别器 - 四层架构"""
    
    def __init__(self):
        self.task_types = TASK_TYPES
        self.raci_matrix = RACI_MATRIX
        self.synonym_dict = SYNONYM_DICT
    
    def recognize(self, user_input: str, context: str = "") -> Tuple[str, float, str]:
        """
        识别用户意图
        
        Returns:
            task_code: 任务代码
            confidence: 置信度
            method: 识别方法
        """
        # 第一层：精准关键词匹配
        task_code, confidence = self._keyword_match(user_input)
        if confidence >= 0.90:
            return task_code, confidence, "keyword_match"
        
        # 第二层：同义词匹配
        task_code, confidence = self._synonym_match(user_input)
        if confidence >= 0.80:
            return task_code, confidence, "synonym_match"
        
        # 第三层：语义规则分析
        task_code, confidence = self._semantic_analysis(user_input)
        if confidence >= 0.75:
            return task_code, confidence, "semantic_analysis"
        
        # 第四层：上下文推理
        if context:
            task_code, confidence = self._context_inference(user_input, context)
            if confidence >= 0.70:
                return task_code, confidence, "context_inference"
        
        # 默认：需求分析
        return 'REQ-02', 0.60, "default"
    
    def _keyword_match(self, user_input: str) -> Tuple[str, float]:
        """第一层：关键词精准匹配"""
        best_match = None
        best_score = 0
        
        user_input_lower = user_input.lower()
        
        for code, task in self.task_types.items():
            for keyword in task.keywords:
                if keyword in user_input_lower:
                    # 计算匹配分数
                    score = task.confidence_base
                    # 如果是完整匹配，提高置信度
                    if keyword == user_input_lower:
                        score = 0.98
                    if score > best_score:
                        best_score = score
                        best_match = code
        
        return best_match or 'REQ-02', best_score
    
    def _synonym_match(self, user_input: str) -> Tuple[str, float]:
        """第二层：同义词匹配"""
        user_input_lower = user_input.lower()
        
        for synonym, task_keyword in self.synonym_dict.items():
            if synonym in user_input_lower:
                # 找到同义词对应的任务
                for task_code, task in self.task_types.items():
                    if task_keyword in task.keywords:
                        return task_code, 0.85
        
        return None, 0.0
    
    def _semantic_analysis(self, user_input: str) -> Tuple[str, float]:
        """第二层：语义分析"""
        # 语义规则
        semantic_rules = [
            # 需求类
            (r'帮我.*需求|分析.*需求|需求.*文档', 'REQ-02', 0.85),
            (r'评审|检查|看看.*需求', 'REQ-03', 0.80),
            (r'收集|调研|访谈', 'REQ-01', 0.75),
            
            # 设计类
            (r'架构|系统设计|概要设计', 'DES-01', 0.85),
            (r'详细设计|接口设计|模块设计', 'DES-02', 0.80),
            (r'数据库|表结构|ER图', 'DES-03', 0.80),
            
            # 开发类
            (r'技术选型|技术方案|技术栈', 'DEV-01', 0.85),
            (r'开发计划|迭代|WBS', 'DEV-02', 0.80),
            
            # 项目管理类
            (r'项目计划|项目规划|甘特图', 'PM-01', 0.85),
            (r'成本|预算|人天', 'PM-02', 0.80),
            (r'风险|风险分析|风险评估', 'PM-03', 0.85),
            (r'方案对比|方案评估|方案选择', 'PM-04', 0.80),
        ]
        
        for pattern, code, confidence in semantic_rules:
            if re.search(pattern, user_input):
                return code, confidence
        
        return 'REQ-02', 0.50
    
    def _context_inference(self, user_input: str, context: str) -> Tuple[str, float]:
        """第三层：上下文推理"""
        # 简单的上下文推理规则
        context_lower = context.lower()
        
        # 如果前文提到需求，可能是在做需求相关任务
        if '需求' in context_lower:
            if '分析' in user_input or '文档' in user_input:
                return 'REQ-02', 0.75
            if '评审' in user_input:
                return 'REQ-03', 0.70
        
        # 如果前文提到架构，可能是在做设计任务
        if '架构' in context_lower or '设计' in context_lower:
            if '详细' in user_input:
                return 'DES-02', 0.70
        
        return 'REQ-02', 0.50


# ==================== Agent调度器 ====================
class AgentScheduler:
    """Agent调度器 - 基于RACI矩阵"""
    
    def __init__(self):
        self.raci_matrix = RACI_MATRIX
        self.agents = AGENTS
    
    def schedule(self, task_code: str, complexity: str = 'medium') -> Dict:
        """
        调度Agent
        
        Args:
            task_code: 任务代码
            complexity: 复杂度 (low/medium/high)
        
        Returns:
            调度结果
        """
        if task_code not in self.raci_matrix:
            return self._default_schedule()
        
        raci = self.raci_matrix[task_code]
        
        # 必选：R和A
        lead_agent = None
        accountable_agent = None
        participants = []
        consultants = []
        
        for agent_id, role in raci.items():
            if role == 'R':
                lead_agent = agent_id
                participants.append(agent_id)
            elif role == 'A':
                accountable_agent = agent_id
                participants.append(agent_id)
            elif role == 'C':
                consultants.append(agent_id)
        
        # 根据复杂度添加C角色（完全基于RACI规则）
        if complexity == 'high':
            participants.extend(consultants)  # 高复杂度：所有C角色参与
        elif complexity == 'medium':
            participants.extend(consultants)  # 中复杂度：所有C角色参与
        # low复杂度：只有R和A参与，不添加C角色
        
        # 去重
        participants = list(set(participants))
        
        return {
            'task_code': task_code,
            'lead_agent': lead_agent,
            'accountable_agent': accountable_agent,
            'participants': participants,
            'consultants': consultants,
            'complexity': complexity,
            'discussion_flow': self._create_flow(task_code, participants)
        }
    
    def _default_schedule(self):
        """默认调度"""
        return {
            'task_code': 'REQ-02',
            'lead_agent': '采薇',
            'accountable_agent': '玉衡',
            'participants': ['采薇', '织锦', '玉衡'],
            'consultants': ['呈彩', '工尺'],
            'complexity': 'medium',
            'discussion_flow': ['caiwei', 'zhijin', 'yuheng']
        }
    
    def _create_flow(self, task_code: str, participants: List[str]) -> List[str]:
        """创建讨论流程"""
        # R角色先发言
        flow = []
        raci = self.raci_matrix.get(task_code, {})
        
        # R角色优先
        for agent_id in participants:
            if raci.get(agent_id) == 'R':
                flow.append(agent_id)
        
        # 其他角色按顺序
        for agent_id in participants:
            if agent_id not in flow:
                flow.append(agent_id)
        
        return flow


# ==================== 复杂度评估器 ====================
class ComplexityEvaluator:
    """复杂度评估器"""
    
    @staticmethod
    def evaluate(user_input: str, context: str = "") -> str:
        """
        评估任务复杂度
        
        Returns:
            'low' | 'medium' | 'high'
        """
        score = 0
        
        # 输入长度
        if len(user_input) > 50:
            score += 1
        if len(user_input) > 100:
            score += 1
        if len(user_input) > 200:
            score += 1
        
        # 多任务关键词（和、与、同时、也）
        multi_task_keywords = ['和', '与', '同时', '以及', '还有', '也']
        for kw in multi_task_keywords:
            if kw in user_input:
                score += 2  # 多任务默认复杂度高
                break
        
        # 关键词复杂度
        complex_keywords = [
            '系统', '平台', '架构', '微服务', '分布式',
            '高并发', '大数据', 'AI', '智能化',
            '多模块', '集成', '迁移', '重构'
        ]
        for kw in complex_keywords:
            if kw in user_input:
                score += 1
        
        # 上下文复杂度
        if context and len(context) > 500:
            score += 1
        
        # 判断等级
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'


# ==================== 智能调度系统 ====================
class IntelligentScheduler:
    """智能调度系统 - 总控"""
    
    def __init__(self):
        self.recognizer = IntentRecognizer()
        self.scheduler = AgentScheduler()
        self.evaluator = ComplexityEvaluator()
    
    def process(self, user_input: str, context: str = "") -> Dict:
        """
        处理用户输入，返回调度结果
        
        Returns:
            {
                'task_code': 任务代码,
                'task_name': 任务名称,
                'category': 任务阶段,
                'confidence': 置信度,
                'recognition_method': 识别方法,
                'complexity': 复杂度,
                'schedule': 调度结果,
                'need_confirm': 是否需要确认
            }
        """
        # 1. 意图识别
        task_code, confidence, method = self.recognizer.recognize(user_input, context)
        
        # 2. 复杂度评估
        complexity = self.evaluator.evaluate(user_input, context)
        
        # 3. Agent调度
        schedule = self.scheduler.schedule(task_code, complexity)
        
        # 4. 是否需要确认
        need_confirm = confidence < 0.80
        
        # 5. 获取任务信息
        task = TASK_TYPES.get(task_code)
        
        return {
            'task_code': task_code,
            'task_name': task.name if task else '未知任务',
            'category': task.category.value if task else '未知',
            'description': task.description if task else '',
            'output_template': task.output_template if task else '',
            'confidence': confidence,
            'recognition_method': method,
            'complexity': complexity,
            'schedule': schedule,
            'need_confirm': need_confirm
        }
    
    def get_confirmation_prompt(self, result: Dict) -> str:
        """生成确认提示"""
        if not result['need_confirm']:
            return ""
        
        return f"""检测到您的任务类型为：{result['task_name']}（置信度：{result['confidence']:.0%}）

请确认或选择其他任务类型：
1. ✅ 确认：{result['task_name']}
2. 📋 需求分析（REQ-02）
3. 🏗️ 架构设计（DES-01）
4. 💰 成本估算（PM-02）
5. ⚠️ 风险评估（PM-03）
6. 📊 方案对比（PM-04）

请回复数字或任务名称。"""
    
    def process_multi(self, user_input: str, context: str = "") -> List[Dict]:
        """
        处理用户输入，支持多任务识别
        
        核心逻辑：
        基于TASK_TYPES的keywords动态生成识别规则，不硬编码
        """
        results = []
        detected_tasks = []  # (task_code, task_name, matched_keyword)
        
        # 动态生成识别规则：基于TASK_TYPES的keywords
        for task_code, task in TASK_TYPES.items():
            for keyword in task.keywords:
                if keyword in user_input:
                    detected_tasks.append((task_code, task.name, keyword))
                    break  # 每个任务类型只匹配一次
        
        # 去重（同一task_code只保留一个）
        seen_codes = set()
        unique_tasks = []
        for task_code, task_name, keyword in detected_tasks:
            if task_code not in seen_codes:
                seen_codes.add(task_code)
                unique_tasks.append((task_code, task_name))
        
        # 如果检测到多个任务
        if len(unique_tasks) > 1:
            for task_code, task_name in unique_tasks:
                result = self._process_task(task_code, task_name, user_input, context)
                results.append(result)
            return results
        
        # 如果只有一个或没有，使用常规识别
        result = self.process(user_input, context)
        return [result]
    
    def _process_task(self, task_code: str, task_name: str, user_input: str, context: str) -> Dict:
        """处理单个任务"""
        complexity = self.evaluator.evaluate(user_input, context)
        schedule = self.scheduler.schedule(task_code, complexity)
        task = TASK_TYPES.get(task_code)
        
        return {
            'task_code': task_code,
            'task_name': task_name,  # 使用传入的task_name，确保一致性
            'category': task.category.value if task else '未知',
            'description': task.description if task else '',
            'output_template': task.output_template if task else '',
            'confidence': 0.90,
            'recognition_method': 'multi-pattern',
            'complexity': complexity,
            'schedule': schedule,
            'need_confirm': False,
            'estimated_time': self._estimate_time(task_code, complexity)
        }
    
    def _estimate_time(self, task_code: str, complexity: str) -> str:
        """估算任务完成时间"""
        base_times = {
            'REQ-01': '2-3天',
            'REQ-02': '3-5天',
            'DES-01': '5-7天',
            'DES-02': '3-5天',
            'SOL-01': '3-5天',
            'SOL-02': '2-3天',
            'PM-01': '2-3天',
            'PM-02': '1-2天',
            'PM-03': '1-2天',
            'DEV-01': '5-10天',
        }
        base = base_times.get(task_code, '3-5天')
        if complexity == 'high':
            return f"{base}（复杂度较高，可能延长）"
        return base


# ==================== 测试 ====================
if __name__ == '__main__':
    scheduler = IntelligentScheduler()
    
    # 测试用例
    test_cases = [
        "帮我写需求文档",
        "客户需要一个智能客服系统，帮我分析需求",
        "技术选型，评估技术方案",
        "成本估算，预算分析",
        "风险评估，分析项目风险",
        "架构设计，系统整体设计",
    ]
    
    print("=" * 60)
    print("智能意图识别与Agent调度系统测试")
    print("=" * 60)
    
    for user_input in test_cases:
        print(f"\n用户输入：{user_input}")
        result = scheduler.process(user_input)
        print(f"任务类型：{result['task_code']} - {result['task_name']}")
        print(f"置信度：{result['confidence']:.0%}（{result['recognition_method']}）")
        print(f"复杂度：{result['complexity']}")
        print(f"主导Agent：{result['schedule']['lead_agent']}")
        print(f"参与Agent：{', '.join(result['schedule']['participants'])}")
        print(f"需要确认：{'是' if result['need_confirm'] else '否'}")
