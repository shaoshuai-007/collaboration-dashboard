#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程 - 智能协作平台 V15
- 首页展示
- 单智能体工作区
- 多智能体工作区

Author: 南乔
Date: 2026-03-15
"""

from flask import Flask, render_template_string, jsonify, request, send_file, Response
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import threading
import time
import os
import requests
import json
import glob

# 导入导出模块
from export_module import ExportAPI, DiscussionTurn, DiscussionSummary

# 导入智能调度模块
from intent_scheduler import IntelligentScheduler, TASK_TYPES

# V15模块延迟导入
V15_MODULES_LOADED = False
MultiRoundDiscussion = None
NanqiaoIntentAnalyzer = None
MeetingMinutesGenerator = None

def load_v15_modules():
    """延迟加载V15模块"""
    global V15_MODULES_LOADED, NanqiaoIntentAnalyzer, MeetingMinutesGenerator, MultiRoundDiscussion
    if V15_MODULES_LOADED:
        return True
    try:
        from nanqiao_intent_analyzer import NanqiaoIntentAnalyzer as NIA
        from meeting_minutes_generator import MeetingMinutesGenerator as MMG
        from multi_round_discussion import MultiRoundDiscussion as MRD
        NanqiaoIntentAnalyzer = NIA
        MeetingMinutesGenerator = MMG
        MultiRoundDiscussion = MRD
        V15_MODULES_LOADED = True
        print("[V15] 模块加载成功：意图分析、多轮讨论、会议纪要")
        return True
    except ImportError as e:
        print(f"[WARN] V15模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== 知识库加载 ====================
class KnowledgeBase:
    """知识库管理器"""
    def __init__(self):
        self.base_path = '/root/.openclaw/skills/compass-shared/knowledge'
        self.cache = {}

    def load_file(self, relative_path: str) -> str:
        if relative_path in self.cache:
            return self.cache[relative_path]
        try:
            with open(os.path.join(self.base_path, relative_path), 'r', encoding='utf-8') as f:
                content = f.read()
            self.cache[relative_path] = content
            return content
        except:
            return ""

    def list_files(self) -> List[Dict]:
        files = []
        for root, dirs, filenames in os.walk(self.base_path):
            for filename in filenames:
                if filename.endswith('.md'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.base_path)
                    files.append({'path': rel_path, 'name': filename})
        return files

knowledge_base = KnowledgeBase()

# ==================== Agent定义 ====================
@dataclass
class AgentPersona:
    agent_id: str
    name: str
    role: str
    system_prompt: str
    color: str
    emoji: str
    stance: str

AGENTS = {
    'caiwei': AgentPersona('caiwei', '采薇', '需求分析专家', 
        '你是采薇，电信行业资深需求分析专家。擅长业务流程分析、用户故事编写、验收标准定义。你的分析严谨细致，注重可追溯性。', 
        '#409EFF', '🌸', '质量优先'),
    'zhijin': AgentPersona('zhijin', '织锦', '架构设计师', 
        '你是织锦，资深技术架构师。擅长系统架构设计、技术选型、性能优化。你的设计注重扩展性、可维护性和技术前瞻性。', 
        '#67C23A', '🧵', '质量优先'),
    'zhutai': AgentPersona('zhutai', '筑台', '售前工程师', 
        '你是筑台，资深售前工程师。擅长方案报价、成本估算、客户沟通。你的方案注重商业价值和客户满意度。', 
        '#E6A23C', '🏗️', '成本优先'),
    'chengcai': AgentPersona('chengcai', '呈彩', '方案设计师', 
        '你是呈彩，资深方案设计师。擅长PPT设计、方案呈现、用户体验设计。你的方案美观专业，注重打动客户。', 
        '#FF9800', '🎨', '质量优先'),
    'gongchi': AgentPersona('gongchi', '工尺', '系统设计师', 
        '你是工尺，资深系统设计师。擅长详细设计、接口设计、数据库设计。你的设计规范严谨，注重实现细节。', 
        '#607D8B', '📐', '质量优先'),
    'yuheng': AgentPersona('yuheng', '玉衡', '项目经理', 
        '你是玉衡，资深项目经理。擅长进度管理、风险管控、资源协调。你的管理注重可执行性和风险预防。', 
        '#F56C6C', '⚖️', '进度优先'),
    'zhegui': AgentPersona('zhegui', '折桂', '资源管家', 
        '你是折桂，资深资源管家。擅长知识管理、资源调配、文档管理。你的工作注重知识沉淀和资源优化。', 
        '#00BCD4', '📚', '平衡'),
    'fuyao': AgentPersona('fuyao', '扶摇', '总指挥', 
        '你是扶摇，项目总指挥。擅长全局把控、决策协调、战略规划。你的决策注重平衡各方利益，追求最优解。', 
        '#165DFF', '🌀', '平衡'),
    'nanqiao': AgentPersona('nanqiao', '南乔', '主控Agent', 
        '你是南乔，用户的主控Agent。负责理解用户意图、协调其他Agent、总结输出。你的回复温暖贴心，有点俏皮。', 
        '#9C27B0', '🌿', '平衡'),
}

# Agent详细介绍（用于单智能体工作区）
AGENT_DETAILS = {
    'caiwei': {
        'name': '采薇',
        'role': '需求分析专家',
        'emoji': '🌸',
        'color': '#409EFF',
        'introduction': '我是采薇，电信行业资深需求分析专家，深耕业务流程分析、用户故事编写及验收标准定义领域超十年。',
        'expertise': ['业务流程分析', '用户故事编写', '验收标准定义', '需求追溯矩阵'],
        'scenarios': ['需求文档编写', '业务痛点梳理', '验收标准制定', '需求变更分析'],
        'guidance': '您可以问我：\n• 请帮我梳理XX系统的需求\n• 如何编写验收标准\n• 业务流程有哪些痛点'
    },
    'zhijin': {
        'name': '织锦',
        'role': '架构设计师',
        'emoji': '🧵',
        'color': '#67C23A',
        'introduction': '我是织锦，资深技术架构师，专注于系统架构设计、技术选型与性能优化，注重系统的扩展性与可维护性。',
        'expertise': ['系统架构设计', '技术选型评估', '性能优化方案', '微服务架构'],
        'scenarios': ['技术架构设计', '技术选型建议', '性能优化方案', '系统重构规划'],
        'guidance': '您可以问我：\n• 请帮我设计XX系统的技术架构\n• XX技术选型有什么建议\n• 如何优化系统性能'
    },
    'zhutai': {
        'name': '筑台',
        'role': '售前工程师',
        'emoji': '🏗️',
        'color': '#E6A23C',
        'introduction': '我是筑台，资深售前工程师，擅长方案报价、成本估算与客户沟通，我的方案注重商业价值和客户满意度。',
        'expertise': ['方案报价', '成本估算', '客户沟通', '竞标策略'],
        'scenarios': ['方案报价编制', '成本预算分析', '客户需求对接', '竞标方案设计'],
        'guidance': '您可以问我：\n• 请帮我估算XX项目的成本\n• 如何编制有竞争力的报价\n• 方案如何打动客户'
    },
    'chengcai': {
        'name': '呈彩',
        'role': '方案设计师',
        'emoji': '🎨',
        'color': '#FF9800',
        'introduction': '我是呈彩，资深方案设计师，擅长PPT设计、方案呈现与用户体验设计，我的方案美观专业，注重打动客户。',
        'expertise': ['PPT设计', '方案呈现', '用户体验设计', '视觉设计'],
        'scenarios': ['方案PPT制作', '用户体验设计', '方案呈现优化', '视觉设计指导'],
        'guidance': '您可以问我：\n• 请帮我设计XX方案的PPT\n• 如何提升用户体验\n• 方案呈现有哪些技巧'
    },
    'gongchi': {
        'name': '工尺',
        'role': '系统设计师',
        'emoji': '📐',
        'color': '#607D8B',
        'introduction': '我是工尺，资深系统设计师，擅长详细设计、接口设计与数据库设计，我的设计规范严谨，注重实现细节。',
        'expertise': ['详细设计', '接口设计', '数据库设计', '技术规范制定'],
        'scenarios': ['详细设计文档', '接口规范定义', '数据库设计', '技术方案细化'],
        'guidance': '您可以问我：\n• 请帮我设计XX系统的接口\n• 数据库如何设计\n• 详细设计文档怎么写'
    },
    'yuheng': {
        'name': '玉衡',
        'role': '项目经理',
        'emoji': '⚖️',
        'color': '#F56C6C',
        'introduction': '我是玉衡，资深项目经理，擅长进度管理、风险管控与资源协调，我的管理注重可执行性和风险预防。',
        'expertise': ['进度管理', '风险管控', '资源协调', '项目规划'],
        'scenarios': ['项目进度规划', '风险识别管控', '资源调配优化', '里程碑管理'],
        'guidance': '您可以问我：\n• 请帮我制定项目计划\n• 如何识别和管理风险\n• 资源如何合理分配'
    },
    'zhegui': {
        'name': '折桂',
        'role': '资源管家',
        'emoji': '📚',
        'color': '#00BCD4',
        'introduction': '我是折桂，资深资源管家，擅长知识管理、资源调配与文档管理，我的工作注重知识沉淀和资源优化。',
        'expertise': ['知识管理', '资源调配', '文档管理', '知识库建设'],
        'scenarios': ['知识库建设', '资源管理优化', '文档规范制定', '知识传承体系'],
        'guidance': '您可以问我：\n• 如何建设知识库\n• 资源管理最佳实践\n• 文档规范如何制定'
    },
    'fuyao': {
        'name': '扶摇',
        'role': '总指挥',
        'emoji': '🌀',
        'color': '#165DFF',
        'introduction': '我是扶摇，项目总指挥，擅长全局把控、决策协调与战略规划，我的决策注重平衡各方利益，追求最优解。',
        'expertise': ['全局把控', '决策协调', '战略规划', '资源整合'],
        'scenarios': ['项目全局规划', '决策协调支持', '战略方案制定', '跨部门协调'],
        'guidance': '您可以问我：\n• 请帮我规划项目全局\n• 如何协调各方利益\n• 战略方案如何制定'
    },
    'nanqiao': {
        'name': '南乔',
        'role': '智能助手',
        'emoji': '🌿',
        'color': '#9C27B0',
        'introduction': '我是南乔，您的智能助手，负责理解您的意图、协调其他专家、为您总结输出。我的回复温暖贴心，有点俏皮。',
        'expertise': ['意图理解', '专家协调', '信息总结', '用户服务'],
        'scenarios': ['意图识别', '专家推荐', '信息汇总', '问题解答'],
        'guidance': '您可以问我：\n• 我应该找哪位专家\n• 请帮我总结XX内容\n• 这个问题如何解决'
    }
}

AGENT_NAMES = {aid: agent.name for aid, agent in AGENTS.items()}

# ==================== 千帆API调用 ====================
QIANFAN_API_KEY = os.environ.get('QIANFAN_API_KEY', 'bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19')

def call_qianfan(system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
    """调用千帆API"""
    if not QIANFAN_API_KEY:
        return "[错误: API Key未配置]"
    
    try:
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro"
        headers = {
            "Authorization": f"Bearer {QIANFAN_API_KEY}",
            "Content-Type": "application/json"
        }
        combined_message = f"{system_prompt}\n\n---\n\n{user_message}"
        payload = {
            "messages": [{"role": "user", "content": combined_message}],
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()
        
        if 'result' in result:
            return result['result']
        return f"[API返回错误: {response.status_code}]"
    except Exception as e:
        return f"[调用失败: {str(e)}]"

# ==================== 首页模板 ====================
HOME_PAGE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>指南针工程 - 智能协作平台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        /* 导航栏 */
        .navbar {
            background: rgba(255,255,255,0.95);
            padding: 16px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: bold;
            color: #C93832;
        }
        
        .logo-icon {
            font-size: 28px;
        }
        
        .nav-links {
            display: flex;
            gap: 30px;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #595959;
            font-size: 15px;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #C93832;
        }
        
        /* Hero区域 */
        .hero {
            text-align: center;
            padding: 80px 40px;
            color: white;
        }
        
        .hero h1 {
            font-size: 48px;
            margin-bottom: 20px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .hero .slogan {
            font-size: 24px;
            margin-bottom: 40px;
            opacity: 0.95;
        }
        
        .hero .subtitle {
            font-size: 18px;
            opacity: 0.85;
            margin-bottom: 40px;
        }
        
        .hero-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #C93832, #A02820);
            color: white;
            padding: 14px 40px;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            text-decoration: none;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(201, 56, 50, 0.4);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 14px 40px;
            border: 2px solid white;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }
        
        .btn-secondary:hover {
            background: white;
            color: #C93832;
        }
        
        /* 内容区域 */
        .content {
            background: #f8f9fa;
            padding: 60px 40px;
        }
        
        .section {
            max-width: 1200px;
            margin: 0 auto 60px;
        }
        
        .section-title {
            text-align: center;
            font-size: 28px;
            color: #333;
            margin-bottom: 40px;
            position: relative;
        }
        
        .section-title::after {
            content: '';
            display: block;
            width: 60px;
            height: 3px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            margin: 15px auto 0;
            border-radius: 2px;
        }
        
        /* 核心能力卡片 */
        .capabilities {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
        }
        
        .capability-card {
            background: white;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .capability-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }
        
        .capability-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .capability-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
        }
        
        .capability-desc {
            font-size: 14px;
            color: #666;
            line-height: 1.6;
        }
        
        .capability-stat {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #eee;
            font-size: 13px;
            color: #C93832;
            font-weight: 500;
        }
        
        /* 理念愿景 */
        .vision-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
        }
        
        .vision-card {
            background: linear-gradient(135deg, #006EBD, #005a9e);
            color: white;
            padding: 40px;
            border-radius: 16px;
            text-align: center;
        }
        
        .vision-card:nth-child(2) {
            background: linear-gradient(135deg, #C93832, #A02820);
        }
        
        .vision-card:nth-child(3) {
            background: linear-gradient(135deg, #595959, #3d3d3d);
        }
        
        .vision-icon {
            font-size: 40px;
            margin-bottom: 16px;
        }
        
        .vision-title {
            font-size: 16px;
            margin-bottom: 12px;
            opacity: 0.9;
        }
        
        .vision-text {
            font-size: 18px;
            font-weight: bold;
            line-height: 1.5;
        }
        
        /* 团队介绍 */
        .team-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
        }
        
        .team-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 15px rgba(0,0,0,0.06);
            transition: transform 0.3s;
            border-left: 4px solid #006EBD;
        }
        
        .team-card:hover {
            transform: translateY(-3px);
        }
        
        .team-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin: 0 auto 12px;
        }
        
        .team-name {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 4px;
        }
        
        .team-role {
            font-size: 13px;
            color: #666;
        }
        
        /* 模式选择 */
        .mode-section {
            background: white;
            border-radius: 20px;
            padding: 50px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.1);
        }
        
        .mode-cards {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 40px;
            margin-top: 40px;
        }
        
        .mode-card {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            border: 2px solid transparent;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .mode-card:hover {
            border-color: #C93832;
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(201, 56, 50, 0.15);
        }
        
        .mode-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        .mode-title {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
        }
        
        .mode-desc {
            font-size: 15px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        
        .mode-btn {
            display: inline-block;
            background: linear-gradient(135deg, #006EBD, #005a9e);
            color: white;
            padding: 12px 32px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 15px;
            transition: all 0.3s;
        }
        
        .mode-btn:hover {
            background: linear-gradient(135deg, #C93832, #A02820);
            transform: scale(1.05);
        }
        
        /* 页脚 */
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 14px;
        }
        
        .footer a {
            color: #C93832;
            text-decoration: none;
        }
        
        /* 响应式 */
        @media (max-width: 1024px) {
            .capabilities { grid-template-columns: repeat(2, 1fr); }
            .team-grid { grid-template-columns: repeat(3, 1fr); }
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 32px; }
            .capabilities { grid-template-columns: 1fr; }
            .vision-cards { grid-template-columns: 1fr; }
            .team-grid { grid-template-columns: repeat(2, 1fr); }
            .mode-cards { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="logo">
            <span class="logo-icon">🧭</span>
            <span>指南针工程</span>
        </div>
        <div class="nav-links">
            <a href="/">首页</a>
            <a href="/multi">工作区</a>
            <a href="#team">团队</a>
            <a href="#about">关于</a>
        </div>
    </nav>
    
    <!-- Hero区域 -->
    <div class="hero">
        <h1>🌟 九星汇聚，智胜千里</h1>
        <p class="slogan">智能协作平台 - 让AI团队为您解决复杂问题</p>
        <p class="subtitle">意图识别 × RACI调度 × 多轮讨论 × 会议纪要</p>
        <div class="hero-buttons">
            <a href="#modes" class="btn-primary">立即体验</a>
            <a href="#capabilities" class="btn-secondary">了解更多</a>
        </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="content">
        <!-- 核心能力 -->
        <div class="section" id="capabilities">
            <h2 class="section-title">核心能力</h2>
            <div class="capabilities">
                <div class="capability-card">
                    <div class="capability-icon">🎯</div>
                    <div class="capability-title">意图识别</div>
                    <div class="capability-desc">四层意图识别架构，精准理解用户需求，支持多任务并行识别</div>
                    <div class="capability-stat">准确率 95%+</div>
                </div>
                <div class="capability-card">
                    <div class="capability-icon">📊</div>
                    <div class="capability-title">RACI调度</div>
                    <div class="capability-desc">基于RACI矩阵的智能调度，自动匹配主导Agent和参与团队</div>
                    <div class="capability-stat">9大专家协同</div>
                </div>
                <div class="capability-card">
                    <div class="capability-icon">💬</div>
                    <div class="capability-title">多轮讨论</div>
                    <div class="capability-desc">支持多轮循环讨论，Agent互相质疑、补充、达成共识</div>
                    <div class="capability-stat">降低决策风险</div>
                </div>
                <div class="capability-card">
                    <div class="capability-icon">📝</div>
                    <div class="capability-title">会议纪要</div>
                    <div class="capability-desc">自动生成结构化会议纪要，支持Word/Excel/Markdown导出</div>
                    <div class="capability-stat">一键导出</div>
                </div>
            </div>
        </div>
        
        <!-- 理念愿景 -->
        <div class="section">
            <h2 class="section-title">理念愿景</h2>
            <div class="vision-cards">
                <div class="vision-card">
                    <div class="vision-icon">💡</div>
                    <div class="vision-title">理念</div>
                    <div class="vision-text">以智为针，以信为盘</div>
                </div>
                <div class="vision-card">
                    <div class="vision-icon">🌟</div>
                    <div class="vision-title">愿景</div>
                    <div class="vision-text">成为电信行业AI转型的领航者</div>
                </div>
                <div class="vision-card">
                    <div class="vision-icon">🎯</div>
                    <div class="vision-title">使命</div>
                    <div class="vision-text">让每一个决策都有智慧支撑</div>
                </div>
            </div>
        </div>
        
        <!-- 团队介绍 -->
        <div class="section" id="team">
            <h2 class="section-title">九星智囊团</h2>
            <div class="team-grid">
                <div class="team-card" style="border-left-color: #165DFF;">
                    <div class="team-avatar" style="background: #165DFF;">🌀</div>
                    <div class="team-name">扶摇</div>
                    <div class="team-role">总指挥</div>
                </div>
                <div class="team-card" style="border-left-color: #409EFF;">
                    <div class="team-avatar" style="background: #409EFF;">🌸</div>
                    <div class="team-name">采薇</div>
                    <div class="team-role">需求分析专家</div>
                </div>
                <div class="team-card" style="border-left-color: #67C23A;">
                    <div class="team-avatar" style="background: #67C23A;">🧵</div>
                    <div class="team-name">织锦</div>
                    <div class="team-role">架构设计师</div>
                </div>
                <div class="team-card" style="border-left-color: #E6A23C;">
                    <div class="team-avatar" style="background: #E6A23C;">🏗️</div>
                    <div class="team-name">筑台</div>
                    <div class="team-role">售前工程师</div>
                </div>
                <div class="team-card" style="border-left-color: #F56C6C;">
                    <div class="team-avatar" style="background: #F56C6C;">⚖️</div>
                    <div class="team-name">玉衡</div>
                    <div class="team-role">项目经理</div>
                </div>
                <div class="team-card" style="border-left-color: #FF9800;">
                    <div class="team-avatar" style="background: #FF9800;">🎨</div>
                    <div class="team-name">呈彩</div>
                    <div class="team-role">方案设计师</div>
                </div>
                <div class="team-card" style="border-left-color: #607D8B;">
                    <div class="team-avatar" style="background: #607D8B;">📐</div>
                    <div class="team-name">工尺</div>
                    <div class="team-role">系统设计师</div>
                </div>
                <div class="team-card" style="border-left-color: #00BCD4;">
                    <div class="team-avatar" style="background: #00BCD4;">📚</div>
                    <div class="team-name">折桂</div>
                    <div class="team-role">资源管家</div>
                </div>
                <div class="team-card" style="border-left-color: #9C27B0;">
                    <div class="team-avatar" style="background: #9C27B0;">🌿</div>
                    <div class="team-name">南乔</div>
                    <div class="team-role">智能助手</div>
                </div>
            </div>
        </div>
        
        <!-- 模式选择 -->
        <div class="section" id="modes">
            <div class="mode-section">
                <h2 class="section-title">选择工作模式</h2>
                <div class="mode-cards">
                    <div class="mode-card">
                        <div class="mode-icon">👤</div>
                        <div class="mode-title">单智能体模式</div>
                        <div class="mode-desc">
                            与专家一对一深度咨询<br>
                            专注于某一领域的专业建议<br>
                            快速响应，精准解答
                        </div>
                        <a href="/single" class="mode-btn">进入工作区 →</a>
                    </div>
                    <div class="mode-card">
                        <div class="mode-icon">🤝</div>
                        <div class="mode-title">多智能体模式</div>
                        <div class="mode-desc">
                            九星团队协作决策<br>
                            多维论证，降低风险<br>
                            共识输出，结构化文档
                        </div>
                        <a href="/multi" class="mode-btn">进入工作区 →</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 页脚 -->
    <div class="footer" id="about">
        <p>© 2026 指南针工程 | 九星智囊团 | <a href="#">南乔技术支持</a></p>
        <p style="margin-top: 10px; opacity: 0.7;">南有乔木，不可休思</p>
    </div>
</body>
</html>
'''

# ==================== 单智能体工作区模板 ====================
SINGLE_AGENT_PAGE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>单智能体工作区 V3.1 - 指南针工程</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #C93832;
            --secondary: #006EBD;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: #f5f7fa;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* 顶部导航 */
        .header {
            background: linear-gradient(135deg, #C93832, #A02820);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header a {
            color: white;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 6px;
            background: rgba(255,255,255,0.15);
            font-size: 13px;
            margin-left: 8px;
        }
        
        .header a:hover { background: rgba(255,255,255,0.25); }
        
        /* 主内容区 */
        .main-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* 左侧专家选择 */
        .sidebar {
            width: 260px;
            background: white;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
            font-weight: bold;
            font-size: 14px;
            color: #666;
        }
        
        .agent-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }
        
        /* 专家卡片 */
        .agent-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 4px;
            border: 2px solid transparent;
            background: white;
            transition: all 0.2s;
            pointer-events: auto;
            position: relative;
            z-index: 1;
        }
        
        .agent-item:hover {
            background: #f0f2f5;
        }
        
        .agent-item.active {
            background: #e8f4ff;
            border-color: #006EBD;
        }
        
        .agent-avatar {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
            flex-shrink: 0;
        }
        
        .agent-info {
            flex: 1;
            min-width: 0;
        }
        
        .agent-name {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .agent-role {
            font-size: 11px;
            color: #666;
            margin-top: 2px;
        }
        
        /* 右侧对话区 */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            min-width: 0;
        }
        
        /* 专家信息区 */
        .agent-info-panel {
            padding: 16px 20px;
            border-bottom: 1px solid #e0e0e0;
            display: block;
            min-height: 150px;
            background: linear-gradient(135deg, #f5f7fa, #e4e7eb);
            border-left: 4px solid #409EFF;
        }
        
        .agent-info-panel.show {
            display: block;
        }
        
        .agent-intro {
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }
        
        .agent-intro-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            color: white;
            flex-shrink: 0;
        }
        
        .agent-intro-content {
            flex: 1;
        }
        
        .agent-intro-name {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 4px;
        }
        
        .agent-intro-role {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .agent-intro-desc {
            font-size: 13px;
            color: #888;
            line-height: 1.6;
        }
        
        .agent-expertise {
            margin-top: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .expertise-tag {
            background: #e8f4ff;
            color: #006EBD;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }
        
        .agent-intro {
            display: flex;
            gap: 16px;
        }
        
        .agent-intro-avatar {
            width: 56px;
            height: 56px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            color: white;
            flex-shrink: 0;
        }
        
        .agent-intro-content {
            flex: 1;
        }
        
        .agent-intro-name {
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
        }
        
        .agent-intro-role {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .agent-intro-desc {
            font-size: 13px;
            color: #1a1a1a;
            line-height: 1.6;
            margin-bottom: 12px;
        }
        
        .agent-expertise {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
        }
        
        .expertise-tag {
            background: #f0f2f5;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            color: #666;
        }
        
        .agent-guidance {
            background: #fff8e6;
            border-left: 3px solid #ffc107;
            padding: 10px 14px;
            font-size: 12px;
            color: #856404;
            line-height: 1.6;
            white-space: pre-line;
        }
        
        /* 消息区 */
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .message {
            display: flex;
            gap: 10px;
            max-width: 85%;
        }
        
        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            flex-shrink: 0;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.6;
            font-size: 14px;
        }
        
        .message.user .message-content {
            background: #006EBD;
            color: white;
        }
        
        .message.agent .message-content {
            background: #f0f2f5;
            color: #1a1a1a;
        }
        
        /* 输入区 - 固定底部 */
        .input-area {
            padding: 12px 16px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            background: white;
        }
        
        .input-area textarea {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            resize: none;
            font-family: inherit;
            min-height: 42px;
            max-height: 120px;
        }
        
        .input-area textarea:focus {
            outline: none;
            border-color: #006EBD;
        }
        
        .send-btn {
            padding: 10px 24px;
            background: linear-gradient(135deg, #006EBD, #005a9e);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* 欢迎提示 */
        .welcome-tip {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #666;
            text-align: center;
            padding: 40px;
        }
        
        .welcome-tip .icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .welcome-tip h3 {
            font-size: 18px;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        
        /* 打字动画 */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 6px 10px;
        }
        
        .typing-indicator span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
    </style>
</head>
<body>
    <header class="header">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 18px; font-weight: bold;">🧭 指南针工程</div>
            <div style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 16px; font-size: 12px;">👤 单智能体模式</div>
        </div>
        <div>
            <a href="/">返回首页</a>
            <a href="/multi">切换多智能体</a>
        </div>
    </header>
    
    <div class="main-container">
        <div class="sidebar">
            <div class="sidebar-header">⭐ 选择专家顾问 <span style="font-size:10px;color:#999;margin-left:8px;">V3.1</span></div>
            <div class="agent-list" id="agentList">
                <div class="agent-item" onclick="selectAgent('caiwei')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#409EFF">🌸</div>
                    <div class="agent-info"><div class="agent-name">采薇</div><div class="agent-role">需求分析专家</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('zhijin')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#67C23A">🧵</div>
                    <div class="agent-info"><div class="agent-name">织锦</div><div class="agent-role">架构设计师</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('zhutai')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#E6A23C">🏗️</div>
                    <div class="agent-info"><div class="agent-name">筑台</div><div class="agent-role">售前工程师</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('chengcai')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#FF9800">🎨</div>
                    <div class="agent-info"><div class="agent-name">呈彩</div><div class="agent-role">方案设计师</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('yuheng')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#F56C6C">⚖️</div>
                    <div class="agent-info"><div class="agent-name">玉衡</div><div class="agent-role">项目经理</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('gongchi')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#607D8B">📐</div>
                    <div class="agent-info"><div class="agent-name">工尺</div><div class="agent-role">系统设计师</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('zhegui')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#00BCD4">📚</div>
                    <div class="agent-info"><div class="agent-name">折桂</div><div class="agent-role">资源管家</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('fuyao')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#165DFF">🌀</div>
                    <div class="agent-info"><div class="agent-name">扶摇</div><div class="agent-role">总指挥</div></div>
                </div>
                <div class="agent-item" onclick="selectAgent('nanqiao')" style="cursor:pointer">
                    <div class="agent-avatar" style="background:#9C27B0">🌿</div>
                    <div class="agent-info"><div class="agent-name">南乔</div><div class="agent-role">智能助手</div></div>
                </div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="agent-info-panel" id="agentInfoPanel"></div>
            
            <div class="messages-area" id="messagesArea">
                <div class="welcome-tip" id="welcomeTip">
                    <div class="icon">👈</div>
                    <h3>请选择一位专家开始对话</h3>
                    <p>点击左侧专家卡片即可开始一对一咨询</p>
                </div>
            </div>
            
            <div class="input-area">
                <textarea id="messageInput" placeholder="输入您的问题..." rows="1" disabled></textarea>
                <button class="send-btn" id="sendBtn" disabled>发送</button>
            </div>
        </div>
    </div>
    
    <script>
        // Agent数据
        var AGENTS = {
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸', color: '#409EFF' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵', color: '#67C23A' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️', color: '#E6A23C' },
            'chengcai': { name: '呈彩', role: '方案设计师', emoji: '🎨', color: '#FF9800' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️', color: '#F56C6C' },
            'gongchi': { name: '工尺', role: '系统设计师', emoji: '📐', color: '#607D8B' },
            'zhegui': { name: '折桂', role: '资源管家', emoji: '📚', color: '#00BCD4' },
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀', color: '#165DFF' },
            'nanqiao': { name: '南乔', role: '智能助手', emoji: '🌿', color: '#9C27B0' }
        };
        
        // 状态变量
        var currentAgent = null;
        var conversations = {};
        var isProcessing = false;
        
        // 页面加载后绑定发送按钮
        document.addEventListener('DOMContentLoaded', function() {
            console.log('页面加载完成');
            
            // 绑定发送按钮事件
            var sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.addEventListener('click', sendMessage);
            }
            
            // 绑定回车发送
            var input = document.getElementById('messageInput');
            if (input) {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
            }
            
            // 默认选中第一个专家
            window.selectAgent('caiwei');
        });
        
        // 渲染专家列表
        function renderAgentList() {
            var container = document.getElementById('agentList');
            container.innerHTML = '';
            
            var order = ['caiwei', 'zhijin', 'zhutai', 'chengcai', 'yuheng', 'gongchi', 'zhegui', 'fuyao', 'nanqiao'];
            
            for (var i = 0; i < order.length; i++) {
                var id = order[i];
                var agent = AGENTS[id];
                
                // 创建元素
                var item = document.createElement('div');
                item.className = 'agent-item' + (currentAgent === id ? ' active' : '');
                item.setAttribute('data-agent-id', id);
                item.style.cursor = 'pointer';
                item.style.pointerEvents = 'auto';
                item.style.position = 'relative';
                
                // 使用闭包正确捕获 id
                var clickHandler = (function(agentId) {
                    return function(e) {
                        if (e) {
                            e.preventDefault();
                            e.stopPropagation();
                        }
                        console.log('点击专家: ' + agentId);
                        window.selectAgent(agentId);
                    };
                })(id);
                
                // 直接绑定 onclick
                item.onclick = clickHandler;
                
                // 添加键盘支持
                item.setAttribute('tabindex', '0');
                item.setAttribute('role', 'button');
                item.onkeydown = function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        var aid = this.getAttribute('data-agent-id');
                        console.log('键盘选择专家: ' + aid);
                        window.selectAgent(aid);
                    }
                };
                
                // 创建内部元素
                var avatar = document.createElement('div');
                avatar.className = 'agent-avatar';
                avatar.style.background = agent.color;
                avatar.style.pointerEvents = 'none';
                avatar.textContent = agent.emoji;
                
                var info = document.createElement('div');
                info.className = 'agent-info';
                info.style.pointerEvents = 'none';
                
                var name = document.createElement('div');
                name.className = 'agent-name';
                name.textContent = agent.name;
                
                var role = document.createElement('div');
                role.className = 'agent-role';
                role.textContent = agent.role;
                
                info.appendChild(name);
                info.appendChild(role);
                item.appendChild(avatar);
                item.appendChild(info);
                container.appendChild(item);
            }
            
            console.log('专家列表渲染完成，共 ' + order.length + ' 位专家');
        }
        
        // 选择专家 - 暴露到 window 以确保全局可访问
        window.selectAgent = function(agentId) {
            console.log('selectAgent called: ' + agentId);
            
            try {
                // 强制重置状态
                isProcessing = false;
                var sendBtn = document.getElementById('sendBtn');
                if (sendBtn) sendBtn.disabled = false;
                
                currentAgent = agentId;
                
                // 更新左侧列表active状态
                var agentItems = document.querySelectorAll('.agent-item');
                agentItems.forEach(function(item) {
                    var onclickAttr = item.getAttribute('onclick');
                    if (onclickAttr && onclickAttr.indexOf("'" + agentId + "'") > -1) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
                
                // 初始化对话
                if (!conversations[agentId]) {
                    conversations[agentId] = [];
                }
                
                // 隐藏欢迎提示
                var tip = document.getElementById('welcomeTip');
                if (tip) tip.style.display = 'none';
                
                var input = document.getElementById('messageInput');
                if (input) input.disabled = false;
                if (sendBtn) sendBtn.disabled = false;
                
                // 显示专家信息
                var panel = document.getElementById('agentInfoPanel');
                if (!panel) return;
                
                var agents = {
                    'caiwei': {name:'采薇',role:'需求分析专家',emoji:'🌸',color:'#409EFF',intro:'电信行业资深需求分析专家，深耕业务流程分析、用户故事编写及验收标准定义领域超十年。',expertise:['业务流程分析','用户故事编写','验收标准定义','需求追踪矩阵'],guidance:'您可以问我：<br>• 请帮我梳理XX业务的需求<br>• 请帮我编写用户故事<br>• 请帮我制定验收标准'},
                    'zhijin': {name:'织锦',role:'架构设计师',emoji:'🧵',color:'#67C23A',intro:'系统架构设计专家，擅长复杂业务系统架构、微服务设计和技术选型。',expertise:['系统架构设计','微服务设计','技术选型','性能优化'],guidance:'您可以问我：<br>• 请帮我设计XX系统的技术架构<br>• XX技术选型有什么建议<br>• 如何优化系统性能'},
                    'zhutai': {name:'筑台',role:'售前工程师',emoji:'🏗️',color:'#E6A23C',intro:'资深售前顾问，擅长需求分析、方案演讲和客户沟通。',expertise:['需求分析','方案演讲','客户沟通','报价估算'],guidance:'您可以问我：<br>• 请帮我准备售前咨询方案<br>• 如何进行方案演示<br>• 请帮我分析客户需求'},
                    'chengcai': {name:'呈彩',role:'方案设计师',emoji:'🎨',color:'#FF9800',intro:'方案设计专家，擅长PPT制作、方案呈现和演示demo。',expertise:['PPT制作','方案呈现','演示demo','视觉设计'],guidance:'您可以问我：<br>• 请帮我制作方案PPT<br>• 如何设计演示Demo<br>• 请帮我优化方案呈现'},
                    'yuheng': {name:'玉衡',role:'项目经理',emoji:'⚖️',color:'#F56C6C',intro:'项目管理专家，擅长项目计划、进度控制和风险管理。',expertise:['项目计划','进度控制','风险管理','团队协调'],guidance:'您可以问我：<br>• 请帮我制定项目计划<br>• 如何控制项目进度<br>• 请帮我识别项目风险'},
                    'gongchi': {name:'工尺',role:'系统设计师',emoji:'📐',color:'#607D8B',intro:'系统设计专家，擅长接口设计、数据库设计和详细设计。',expertise:['接口设计','数据库设计','详细设计','API规范'],guidance:'您可以问我：<br>• 请帮我设计接口<br>• 请帮我设计数据库<br>• 请帮我编写详细设计文档'},
                    'zhegui': {name:'折桂',role:'资源管家',emoji:'📚',color:'#00BCD4',intro:'知识管理专家，擅长知识整理、知识分类和知识图谱构建。',expertise:['知识整理','知识分类','知识图谱','智能搜索'],guidance:'您可以问我：<br>• 请帮我整理知识库<br>• 如何构建知识图谱<br>• 请帮我分类知识文档'},
                    'fuyao': {name:'扶摇',role:'总指挥',emoji:'🌀',color:'#165DFF',intro:'团队协调专家，擅长任务调度、团队协作和进度监控。',expertise:['任务调度','团队协作','进度监控','资源协调'],guidance:'您可以问我：<br>• 请帮我分配任务<br>• 如何协调团队进度<br>• 请帮我监控项目进展'},
                    'nanqiao': {name:'南乔',role:'智能助手',emoji:'🌿',color:'#9C27B0',intro:'您的智能助手，擅长问题解答、任务协调和知识服务。',expertise:['问题解答','任务协调','知识服务','决策建议'],guidance:'您可以问我：<br>• 请帮我解答问题<br>• 请帮我协调任务<br>• 请帮我查找知识'}
                };
                
                var a = agents[agentId];
                if (!a) return;
                
                panel.style.display = 'block';
                panel.innerHTML = '<div style="display:flex;align-items:flex-start;gap:16px;padding:16px;background:linear-gradient(135deg,#f5f7fa,#e4e7eb);border-radius:8px;border-left:4px solid ' + a.color + '">' +
                    '<div style="width:60px;height:60px;border-radius:50%;background:' + a.color + ';display:flex;align-items:center;justify-content:center;font-size:28px;color:white;flex-shrink:0">' + a.emoji + '</div>' +
                    '<div style="flex:1"><div style="font-size:20px;font-weight:bold;color:#333;margin-bottom:4px">' + a.name + '</div>' +
                    '<div style="font-size:14px;color:#666;margin-bottom:8px">' + a.role + '</div>' +
                    '<div style="font-size:13px;color:#888;line-height:1.6;margin-bottom:12px">' + a.intro + '</div>' +
                    '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">' + a.expertise.map(function(e){return'<span style="background:#e8f4ff;color:#006EBD;padding:4px 12px;border-radius:12px;font-size:12px">'+e+'</span>'}).join('') + '</div>' +
                    '<div style="font-size:12px;color:#666;background:#fff;padding:12px;border-radius:8px;line-height:1.8">' + a.guidance + '</div></div></div>';
                
                document.title = a.name + ' - 指南针工程';
                
            } catch (e) {
                console.error('selectAgent错误:', e);
            }
        };
        
        // 加载专家详细信息
        function loadAgentInfo(agentId) {
            fetch('/api/agent/info/' + agentId)
                .then(function(response) { return response.json(); })
                .then(function(result) {
                    if (result.status === 'ok') {
                        var agent = result.agent;
                        var panel = document.getElementById('agentInfoPanel');
                        panel.className = 'agent-info-panel show';
                        panel.innerHTML = 
                            '<div class="agent-intro">' +
                            '<div class="agent-intro-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div>' +
                            '<div class="agent-intro-content">' +
                            '<div class="agent-intro-name">' + agent.name + '</div>' +
                            '<div class="agent-intro-role">' + agent.role + '</div>' +
                            '<div class="agent-intro-desc">' + agent.introduction + '</div>' +
                            '<div class="agent-expertise">' + agent.expertise.map(function(e) { return '<span class="expertise-tag">' + e + '</span>'; }).join('') + '</div>' +
                            '<div class="agent-guidance">' + agent.guidance + '</div>' +
                            '</div></div>';
                    }
                })
                .catch(function(e) {
                    console.error('加载专家信息失败', e);
                });
        }
        
        // 渲染消息
        function renderMessages() {
            var area = document.getElementById('messagesArea');
            if (!area) return;
            
            var msgs = conversations[currentAgent] || [];
            
            area.innerHTML = '';
            
            for (var i = 0; i < msgs.length; i++) {
                var msg = msgs[i];
                var msgDiv = document.createElement('div');
                msgDiv.className = 'message ' + msg.type;
                
                var agent = AGENTS[currentAgent] || {color:'#409EFF', emoji:'🌿'};
                
                if (msg.type === 'user') {
                    msgDiv.innerHTML = '<div class="message-avatar" style="background: #595959;">👤</div><div class="message-content">' + escapeHtml(msg.content) + '</div>';
                } else if (msg.type === 'agent') {
                    msgDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content">' + escapeHtml(msg.content) + '</div>';
                }
                
                area.appendChild(msgDiv);
            }
            
            area.scrollTop = area.scrollHeight;
        }
        
        // 发送消息
        function sendMessage() {
            var input = document.getElementById('messageInput');
            var message = input.value.trim();
            
            if (!message || !currentAgent || isProcessing) return;
            
            // 添加用户消息
            conversations[currentAgent].push({ type: 'user', content: message });
            renderMessages();
            input.value = '';
            
            // 显示加载状态
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            showTyping();
            
            // 发送请求
            fetch('/api/agent/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: currentAgent,
                    message: message,
                    history: conversations[currentAgent].slice(-10).map(function(m) {
                        return { speaker: m.type === 'user' ? 'user' : 'agent', content: m.content };
                    })
                })
            })
            .then(function(response) {
                var reader = response.body.getReader();
                var decoder = new TextDecoder();
                var fullResponse = '';
                
                hideTyping();
                
                var area = document.getElementById('messagesArea');
                var agent = AGENTS[currentAgent];
                var msgDiv = document.createElement('div');
                msgDiv.className = 'message agent';
                msgDiv.id = 'current-response';
                msgDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content"></div>';
                area.appendChild(msgDiv);
                
                function readChunk() {
                    reader.read().then(function(result) {
                        if (result.done) {
                            conversations[currentAgent].push({ type: 'agent', content: fullResponse });
                            isProcessing = false;
                            document.getElementById('sendBtn').disabled = false;
                            document.getElementById('current-response').removeAttribute('id');
                            return;
                        }
                        
                        var chunk = decoder.decode(result.value);
                        var lines = chunk.split('\\n');
                        
                        for (var i = 0; i < lines.length; i++) {
                            var line = lines[i];
                            if (line.indexOf('data: ') === 0) {
                                var data = line.substring(6);
                                if (data === '[DONE]') break;
                                try {
                                    var json = JSON.parse(data);
                                    if (json.text) {
                                        fullResponse += json.text;
                                        document.querySelector('#current-response .message-content').textContent = fullResponse;
                                        area.scrollTop = area.scrollHeight;
                                    }
                                } catch (e) {}
                            }
                        }
                        
                        readChunk();
                    }).catch(function(e) {
                        console.error('流式读取错误:', e);
                        isProcessing = false;
                        document.getElementById('sendBtn').disabled = false;
                        var currentResp = document.getElementById('current-response');
                        if (currentResp) currentResp.removeAttribute('id');
                    });
                }
                
                readChunk();
            })
            .catch(function(e) {
                hideTyping();
                alert('网络错误，请重试');
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            });
        }
        
        // 显示/隐藏打字指示器
        function showTyping() {
            var area = document.getElementById('messagesArea');
            var agent = AGENTS[currentAgent];
            var typingDiv = document.createElement('div');
            typingDiv.className = 'message agent';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<div class="message-avatar" style="background: ' + agent.color + '">' + agent.emoji + '</div><div class="message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
            area.appendChild(typingDiv);
            area.scrollTop = area.scrollHeight;
        }
        
        function hideTyping() {
            var typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }
        
        // HTML转义
        function escapeHtml(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\\n/g, '<br>');
        }
    </script>
</body>
</html>
'''



# ==================== Flask应用 ====================
app = Flask(__name__)

@app.route('/')
def index():
    """首页"""
    return render_template_string(HOME_PAGE)

@app.route('/single')
def single_agent():
    """单智能体工作区"""
    return render_template_string(SINGLE_AGENT_PAGE)

# 导入多智能体平台（从V14）
# 这里需要将V14的MULTI_AGENT_PAGE导入
# 为了简化，我们直接重定向到V14
@app.route('/multi')
def multi_agent():
    """多智能体工作区 - 重定向到V14平台"""
    return '''
    <script>
        // 自动跳转到V14平台
        window.location.href = 'http://120.48.169.242:5001/';
    </script>
    <p>正在跳转到多智能体工作区...</p>
    <p>如果没有自动跳转，请<a href="http://120.48.169.242:5001/">点击这里</a></p>
    '''

# ==================== 单Agent对话API ====================
@app.route('/api/agent/info/<agent_id>')
def api_agent_info(agent_id):
    """获取专家详细信息"""
    if agent_id not in AGENT_DETAILS:
        return jsonify({'status': 'error', 'message': '未知专家'})
    return jsonify({
        'status': 'ok',
        'agent': AGENT_DETAILS[agent_id]
    })

@app.route('/api/agent/chat', methods=['POST'])
def api_agent_chat():
    """单Agent对话API"""
    data = request.json
    agent_id = data.get('agent_id')
    message = data.get('message')
    history = data.get('history', [])
    
    if agent_id not in AGENTS:
        return jsonify({'status': 'error', 'message': '未知Agent'})
    
    agent = AGENTS[agent_id]
    
    # 构建对话历史
    history_text = ""
    if history:
        history_text = "\\n\\n【对话历史】\\n"
        for h in history[-6:]:
            speaker = "用户" if h['speaker'] == 'user' else agent.name
            history_text += f"{speaker}: {h['content'][:200]}\\n"
    
    # 构建Prompt
    prompt = f"""{agent.system_prompt}

{history_text}

【用户问题】
{message}

请以{agent.name}的身份，从{agent.role}的专业角度回答用户的问题。要求：
1. 回答专业、准确、有深度
2. 体现你的专业视角和经验
3. 如果涉及具体方案，给出可执行的建议
4. 回答简洁有力，不超过300字"""

    # 调用千帆API
    response = call_qianfan(agent.system_prompt, prompt)
    
    return jsonify({
        'status': 'ok',
        'agent_id': agent_id,
        'agent_name': agent.name,
        'response': response
    })

@app.route('/api/agent/stream', methods=['POST'])
def api_agent_stream():
    """流式输出API - SSE"""
    data = request.json
    agent_id = data.get('agent_id')
    message = data.get('message')
    history = data.get('history', [])
    
    if agent_id not in AGENTS:
        return jsonify({'status': 'error', 'message': '未知专家'})
    
    agent = AGENTS[agent_id]
    
    def generate():
        # 构建对话历史
        history_text = ""
        if history:
            history_text = "\\n\\n【对话历史】\\n"
            for h in history[-6:]:
                speaker = "用户" if h['speaker'] == 'user' else agent.name
                history_text += f"{speaker}: {h['content'][:200]}\\n"
        
        # 构建Prompt
        prompt = f"""{agent.system_prompt}
{history_text}

【用户问题】
{message}

请以{agent.name}的身份，从{agent.role}的专业角度回答。要求专业、准确、简洁（不超过300字）。"""
        
        # 调用千帆流式API
        try:
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro"
            headers = {
                "Authorization": f"Bearer {QIANFAN_API_KEY}",
                "Content-Type": "application/json"
            }
            combined_message = f"{agent.system_prompt}\\n\\n---\\n\\n{prompt}"
            payload = {
                "messages": [{"role": "user", "content": combined_message}],
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": True
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]
                        if data_str.strip():
                            try:
                                d = json.loads(data_str)
                                if 'result' in d:
                                    yield f"data: {json.dumps({'text': d['result']})}\\n\\n"
                            except:
                                continue
            
            yield "data: [DONE]\\n\\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
    
    return Response(generate(), mimetype='text/event-stream')

# ==================== 启动 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🧭 指南针工程 - 智能协作平台 V15")
    print("=" * 60)
    print("首页: http://120.48.169.242:5002/")
    print("单智能体: http://120.48.169.242:5002/single")
    print("多智能体: http://120.48.169.242:5001/ (V14平台)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=False)
