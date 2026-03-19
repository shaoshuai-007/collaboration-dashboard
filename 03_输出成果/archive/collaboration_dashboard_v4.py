#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 - Web界面 V4
支持对话记忆、自主调度、多轮对话

Author: 南乔
Date: 2026-03-13
"""

from flask import Flask, render_template_string, jsonify, request
from collaboration_framework import (
    CollaborationFramework, Message, MessageType, AgentRole, ReplyStyle
)
import threading
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

app = Flask(__name__)

# ==================== 对话记忆管理 ====================

@dataclass
class ConversationTurn:
    """对话轮次"""
    turn_id: int
    speaker: str
    speaker_name: str
    content: str
    timestamp: str
    msg_type: str = "answer"
    
class ConversationMemory:
    """对话记忆管理器"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: List[ConversationTurn] = []
        self.context_summary: str = ""
        self.current_topic: str = ""
        self.turn_count: int = 0
        self.participating_agents: set = set()
    
    def add_turn(self, speaker: str, speaker_name: str, content: str, msg_type: str = "answer"):
        """添加对话轮次"""
        self.turn_count += 1
        turn = ConversationTurn(
            turn_id=self.turn_count,
            speaker=speaker,
            speaker_name=speaker_name,
            content=content,
            timestamp=datetime.now().isoformat(),
            msg_type=msg_type
        )
        self.history.append(turn)
        self.participating_agents.add(speaker)
        
        # 限制历史长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return turn
    
    def get_recent_history(self, limit: int = 10) -> List[ConversationTurn]:
        """获取最近的对话历史"""
        return self.history[-limit:]
    
    def get_context_for_agent(self, agent_id: str) -> str:
        """为Agent生成上下文"""
        recent = self.get_recent_history(5)
        context_parts = []
        
        for turn in recent:
            context_parts.append(f"[{turn.speaker_name}]: {turn.content[:100]}")
        
        return "\n".join(context_parts)
    
    def get_last_speaker(self) -> Optional[str]:
        """获取上一个发言者"""
        if self.history:
            return self.history[-1].speaker
        return None
    
    def clear(self):
        """清空记忆"""
        self.history.clear()
        self.context_summary = ""
        self.current_topic = ""
        self.turn_count = 0
        self.participating_agents.clear()


# ==================== 自主调度器 ====================

class AutonomousScheduler:
    """自主调度器 - 决定下一个发言的Agent"""
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.speaking_sequence = []  # 当前发言序列
        self.current_index = 0
        
        # Agent专业领域映射
        self.agent_expertise = {
            'caiwei': ['需求', '分析', '用户故事', '验收'],
            'zhijin': ['架构', '设计', '技术', '系统'],
            'zhutai': ['成本', '预算', '报价', '投入'],
            'gongchi': ['详细设计', '接口', '数据库', '实现'],
            'yuheng': ['项目', '计划', '进度', '里程碑'],
            'chengcai': ['PPT', '汇报', '方案', '演示'],
            'zhegui': ['资源', '文档', '案例', '参考'],
            'fuyao': ['总结', '决策', '协调', '优先级'],
            'nanqiao': ['确认', '整理', '反馈', '收尾']
        }
        
        # 标准发言顺序（根据任务类型）
        self.standard_sequences = {
            '需求分析': ['nanqiao', 'caiwei', 'zhijin', 'yuheng', 'fuyao', 'nanqiao'],
            '架构设计': ['nanqiao', 'zhijin', 'gongchi', 'yuheng', 'fuyao', 'nanqiao'],
            '成本评估': ['nanqiao', 'zhutai', 'zhijin', 'yuheng', 'fuyao', 'nanqiao'],
            '项目计划': ['nanqiao', 'yuheng', 'caiwei', 'zhijin', 'fuyao', 'nanqiao'],
            'default': ['nanqiao', 'caiwei', 'zhijin', 'zhutai', 'yuheng', 'fuyao', 'nanqiao']
        }
    
    def decide_next_speaker(self, task_type: str = 'default', context: str = "") -> Optional[str]:
        """决定下一个发言的Agent"""
        
        # 获取发言序列
        if not self.speaking_sequence:
            self.speaking_sequence = self.standard_sequences.get(task_type, self.standard_sequences['default'])
            self.current_index = 0
        
        # 检查是否完成一轮
        if self.current_index >= len(self.speaking_sequence):
            return None  # 本轮结束
        
        next_speaker = self.speaking_sequence[self.current_index]
        self.current_index += 1
        
        return next_speaker
    
    def reset_sequence(self):
        """重置发言序列"""
        self.speaking_sequence = []
        self.current_index = 0
    
    def should_continue(self) -> bool:
        """是否应该继续对话"""
        return self.current_index < len(self.speaking_sequence)


# ==================== 响应生成器 ====================

class ResponseGenerator:
    """智能响应生成器"""
    
    def __init__(self):
        self.response_templates = {
            'caiwei': {
                '需求分析': [
                    "我已完成需求调研，识别出{count}个核心功能点。主要需求包括：{points}。建议下一步由织锦进行架构设计。",
                    "需求分析进展顺利。用户核心诉求是{summary}。我整理了用户故事地图，需要确认几个关键点：1.{q1} 2.{q2}",
                    "根据调研结果，{project}的核心需求已明确。预计需求文档30页，包含{modules}个模块的详细说明。"
                ]
            },
            'zhijin': {
                '架构设计': [
                    "基于采薇的需求分析，我设计了{layers}层架构。技术选型：前端{frontend}，后端{backend}，数据层{database}。",
                    "架构方案已完成。核心设计理念是{concept}。包含{count}个微服务，预计部署在{platform}平台。",
                    "技术架构图已输出。关键组件：API网关、服务注册中心、配置中心、消息队列。预计开发周期{weeks}周。"
                ]
            },
            'zhutai': {
                '成本评估': [
                    "根据架构方案，初步估算：开发投入{dev_cost}万，运维成本{ops_cost}万/年，基础设施{infra_cost}万。总计首年投入{total}万。",
                    "成本分析完成。推荐方案：{plan}。性价比最优，ROI预计{roi}个月回本。",
                    "预算明细已输出。人力成本占{hr_percent}%，基础设施占{infra_percent}%，第三方服务占{third_percent}%。"
                ]
            },
            'yuheng': {
                '项目计划': [
                    "项目计划已制定。关键里程碑：{m1}、{m2}、{m3}。总工期{duration}周，团队规模{team_size}人。",
                    "RACI矩阵已定义。风险清单识别出{risk_count}项风险，已制定应对措施。下周启动需求评审会。",
                    "甘特图已输出。关键路径：需求分析→架构设计→开发→测试→上线。预计{end_date}交付。"
                ]
            },
            'fuyao': {
                '总指挥': [
                    "综合各位的分析，{project}方案可行。建议按{approach}推进，优先完成{priority}模块。有问题及时上报。",
                    "任务分配确认。采薇负责需求、织锦负责架构、玉衡跟进进度。每周五汇报进展。",
                    "决策：{project}正式启动。A级优先级，调配资源{resources}。按标准流程执行。"
                ]
            },
            'nanqiao': {
                '主控': [
                    "收到您的需求。我将协调团队完成{project}的分析和方案设计。请各位Agent按专业分工协作。",
                    "感谢各位的分析。我已整理核心要点：{summary}。请确认是否有补充？",
                    "任务已完成。输出成果：需求文档、架构方案、成本预算、项目计划。请查阅并反馈。"
                ]
            }
        }
    
    def generate(self, agent_id: str, task_content: str, context: str) -> str:
        """生成响应"""
        import random
        
        # 提取项目名称
        project = "该项目"
        for kw in ['系统', '平台', '项目']:
            if kw in task_content:
                idx = task_content.find(kw)
                project = task_content[max(0, idx-8):idx+len(kw)]
                break
        
        # 获取模板
        templates = self.response_templates.get(agent_id, {})
        all_templates = []
        for t_list in templates.values():
            all_templates.extend(t_list)
        
        if not all_templates:
            return f"收到任务，正在处理{project}..."
        
        template = random.choice(all_templates)
        
        # 填充模板
        response = template.format(
            project=project,
            count=random.randint(5, 15),
            points="用户管理、权限控制、数据分析",
            summary=f"{project}的核心功能实现",
            q1="用户量级预估？",
            q2="是否需要移动端？",
            modules=random.randint(3, 8),
            layers=random.randint(4, 6),
            frontend="Vue3 + ElementPlus",
            backend="Spring Cloud微服务",
            database="PostgreSQL + Redis",
            concept="微服务 + 领域驱动设计",
            platform="Kubernetes",
            weeks=random.randint(8, 16),
            dev_cost=random.randint(80, 150),
            ops_cost=random.randint(30, 60),
            infra_cost=random.randint(20, 40),
            total=random.randint(130, 250),
            plan="中配方案",
            roi=random.randint(12, 24),
            hr_percent=60,
            infra_percent=25,
            third_percent=15,
            m1="需求评审(Week2)",
            m2="开发完成(Week10)",
            m3="上线(Week14)",
            duration=random.randint(10, 16),
            team_size=random.randint(6, 12),
            risk_count=random.randint(3, 6),
            end_date=f"{random.randint(2, 4)}个月后",
            approach="敏捷迭代，分阶段交付",
            priority="核心业务",
            resources="需求组2人、架构组1人、开发组5人"
        )
        
        return response


# ==================== 全局状态 ====================

framework = CollaborationFramework()
memory = ConversationMemory()
scheduler = AutonomousScheduler(memory)
response_gen = ResponseGenerator()

# Agent信息
AGENT_INFO = {
    'nanqiao': {'name': '南乔', 'role': '主控Agent', 'emoji': '🌿'},
    'caiwei': {'name': '采薇', 'role': '需求分析专家', 'emoji': '🌸'},
    'zhijin': {'name': '织锦', 'role': '架构设计师', 'emoji': '🧵'},
    'zhutai': {'name': '筑台', 'role': '售前工程师', 'emoji': '🏗️'},
    'gongchi': {'name': '工尺', 'role': '详细设计师', 'emoji': '📐'},
    'yuheng': {'name': '玉衡', 'role': '项目经理', 'emoji': '⚖️'},
    'chengcai': {'name': '呈彩', 'role': 'PPT设计师', 'emoji': '🎨'},
    'zhegui': {'name': '折桂', 'role': '资源管家', 'emoji': '📚'},
    'fuyao': {'name': '扶摇', 'role': '总指挥', 'emoji': '🌀'}
}

# 当前处理状态
is_processing = False


# ==================== HTML模板 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 多Agent协作平台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: #f5f5f5;
            color: #333;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* 顶部 */
        .header {
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .header h1 { font-size: 18px; font-weight: 600; }
        .header .subtitle { font-size: 12px; opacity: 0.9; }
        .status-dot { 
            display: inline-block; 
            width: 8px; height: 8px; 
            background: #4CAF50; 
            border-radius: 50%; 
            margin-right: 6px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        /* 主体 */
        .main {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* 左侧Agent列表 */
        .sidebar {
            width: 240px;
            background: white;
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
            padding: 12px;
        }
        .sidebar h3 {
            font-size: 12px;
            color: #888;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 8px;
        }
        .agent-card {
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 6px;
            background: #fafafa;
            border-radius: 8px;
            border-left: 3px solid #e0e0e0;
            transition: all 0.2s;
        }
        .agent-card:hover { background: #f0f0f0; }
        .agent-card.active { border-left-color: #C93832; background: #fff5f5; }
        .agent-card.speaking { 
            border-left-color: #006EBD; 
            background: #f0f7ff;
            animation: speaking-pulse 1s infinite;
        }
        @keyframes speaking-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(0,110,189,0.3); } 50% { box-shadow: 0 0 0 4px rgba(0,110,189,0.1); } }
        
        .agent-avatar {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 16px;
            margin-right: 10px;
        }
        .agent-info { flex: 1; }
        .agent-name { font-size: 13px; font-weight: 600; color: #333; }
        .agent-role { font-size: 11px; color: #888; }
        .agent-status {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: #e0e0e0;
        }
        .agent-status.working { background: #e3f2fd; color: #1976d2; }
        
        /* 对话区 */
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #fafafa;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        
        .message {
            margin-bottom: 16px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } }
        
        .message.user { justify-content: flex-end; }
        
        .message-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            background: white;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .message.user .message-bubble {
            background: #C93832;
            color: white;
        }
        
        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 6px;
        }
        .message-emoji { margin-right: 6px; }
        .message-name { font-size: 12px; font-weight: 600; color: #C93832; }
        .message.user .message-name { color: rgba(255,255,255,0.9); }
        .message-time { font-size: 10px; color: #aaa; margin-left: auto; }
        
        .message-content { font-size: 13px; line-height: 1.6; }
        
        /* 输入区 */
        .input-area {
            background: white;
            border-top: 1px solid #e0e0e0;
            padding: 12px 16px;
        }
        .input-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .input-row input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }
        .input-row input:focus { border-color: #006EBD; }
        .input-row button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .input-row button:hover { transform: scale(1.02); }
        .input-row button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .quick-actions {
            margin-top: 8px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .quick-btn {
            padding: 6px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: white;
            color: #666;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { background: #f5f5f5; border-color: #006EBD; color: #006EBD; }
        
        /* 空状态 */
        .empty-state {
            text-align: center;
            padding: 60px;
            color: #999;
        }
        .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
        
        /* 打字指示器 */
        .typing-indicator {
            display: none;
            align-items: center;
            padding: 12px 16px;
            color: #888;
            font-size: 12px;
        }
        .typing-indicator.show { display: flex; }
        .typing-dots { margin-right: 8px; }
        .typing-dots span {
            display: inline-block;
            width: 6px; height: 6px;
            background: #888;
            border-radius: 50%;
            margin: 0 2px;
            animation: typing 1s infinite;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
    </style>
</head>
<body>
    <!-- 顶部 -->
    <div class="header">
        <div>
            <h1>🧭 指南针工程 - 多Agent协作平台</h1>
            <div class="subtitle">对话记忆 · 自主调度 · 多轮协作</div>
        </div>
        <div id="statusBadge"><span class="status-dot"></span>系统就绪</div>
    </div>
    
    <!-- 主体 -->
    <div class="main">
        <!-- 左侧Agent列表 -->
        <div class="sidebar">
            <h3>👥 协作团队 (9人)</h3>
            <div id="agentList"></div>
        </div>
        
        <!-- 对话区 -->
        <div class="chat-area">
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <div>输入需求，Agent团队将自主协作完成分析</div>
                </div>
            </div>
            
            <!-- 打字指示器 -->
            <div class="typing-indicator" id="typingIndicator">
                <div class="typing-dots"><span></span><span></span><span></span></div>
                <span id="typingText">采薇正在输入...</span>
            </div>
            
            <!-- 输入区 -->
            <div class="input-area">
                <div class="input-row">
                    <input type="text" id="taskInput" placeholder="输入需求，如：需要开发一个用户数据管理系统">
                    <button id="sendBtn" onclick="submitTask()">发送</button>
                </div>
                <div class="quick-actions">
                    <button class="quick-btn" onclick="quickTask('需求分析')">📋 需求分析</button>
                    <button class="quick-btn" onclick="quickTask('架构设计')">🏗️ 架构设计</button>
                    <button class="quick-btn" onclick="quickTask('成本评估')">💰 成本评估</button>
                    <button class="quick-btn" onclick="quickTask('项目计划')">📅 项目计划</button>
                    <button class="quick-btn" onclick="clearChat()">🗑️ 清空</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let conversations = [];
        let agentStatus = {};
        let isProcessing = false;
        
        const AGENT_INFO = {
            'nanqiao': { name: '南乔', role: '主控Agent', emoji: '🌿' },
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️' },
            'gongchi': { name: '工尺', role: '详细设计师', emoji: '📐' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️' },
            'chengcai': { name: '呈彩', role: 'PPT设计师', emoji: '🎨' },
            'zhegui': { name: '折桂', role: '资源管家', emoji: '📚' },
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀' }
        };
        
        function init() {
            renderAgentList();
            fetchStatus();
            setInterval(fetchStatus, 1500);
        }
        
        function renderAgentList() {
            const container = document.getElementById('agentList');
            container.innerHTML = '';
            
            const order = ['fuyao', 'nanqiao', 'yuheng', 'caiwei', 'zhijin', 'zhutai', 'gongchi', 'chengcai', 'zhegui'];
            
            order.forEach(id => {
                const info = AGENT_INFO[id];
                const status = agentStatus[id] || 'idle';
                
                const card = document.createElement('div');
                card.className = `agent-card ${status === 'working' ? 'active' : ''} ${status === 'speaking' ? 'speaking' : ''}`;
                card.id = `agent-${id}`;
                card.innerHTML = `
                    <div class="agent-avatar">${info.emoji}</div>
                    <div class="agent-info">
                        <div class="agent-name">${info.name}</div>
                        <div class="agent-role">${info.role}</div>
                    </div>
                    <span class="agent-status ${status === 'working' ? 'working' : ''}">${status === 'working' ? '处理中' : '空闲'}</span>
                `;
                container.appendChild(card);
            });
        }
        
        async function fetchStatus() {
            try {
                const response = await fetch('/api/conversation');
                const data = await response.json();
                conversations = data.conversations || [];
                agentStatus = data.agentStatus || {};
                
                renderMessages();
                updateAgentStatus();
            } catch (e) { console.error(e); }
        }
        
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            
            if (conversations.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">💬</div>
                        <div>输入需求，Agent团队将自主协作完成分析</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '';
            
            conversations.forEach(conv => {
                const info = AGENT_INFO[conv.speaker] || { name: conv.speaker, emoji: '🤖' };
                const isUser = conv.speaker === 'user';
                
                const msg = document.createElement('div');
                msg.className = `message ${isUser ? 'user' : ''}`;
                msg.innerHTML = `
                    <div class="message-bubble">
                        <div class="message-header">
                            <span class="message-emoji">${info.emoji}</span>
                            <span class="message-name">${info.name}</span>
                            <span class="message-time">${conv.timestamp.split('T')[1].split('.')[0]}</span>
                        </div>
                        <div class="message-content">${conv.content}</div>
                    </div>
                `;
                container.appendChild(msg);
            });
            
            container.scrollTop = container.scrollHeight;
        }
        
        function updateAgentStatus() {
            Object.keys(agentStatus).forEach(id => {
                const card = document.getElementById(`agent-${id}`);
                if (card) {
                    const status = agentStatus[id];
                    card.className = `agent-card ${status === 'working' ? 'active' : ''} ${status === 'speaking' ? 'speaking' : ''}`;
                    card.querySelector('.agent-status').textContent = status === 'working' ? '处理中' : '空闲';
                    card.querySelector('.agent-status').className = `agent-status ${status === 'working' ? 'working' : ''}`;
                }
            });
        }
        
        function showTyping(agentId) {
            const info = AGENT_INFO[agentId];
            const indicator = document.getElementById('typingIndicator');
            const text = document.getElementById('typingText');
            text.textContent = `${info.name}正在输入...`;
            indicator.classList.add('show');
        }
        
        function hideTyping() {
            document.getElementById('typingIndicator').classList.remove('show');
        }
        
        async function submitTask() {
            if (isProcessing) return;
            
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) { alert('请输入需求'); return; }
            
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            input.value = '';
            
            try {
                await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
            } catch (e) { alert('提交失败'); }
            
            setTimeout(() => {
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            }, 10000);
        }
        
        function quickTask(type) {
            const tasks = {
                '需求分析': '请完成需求分析',
                '架构设计': '请设计系统架构',
                '成本评估': '请评估项目成本',
                '项目计划': '请制定项目计划'
            };
            document.getElementById('taskInput').value = tasks[type];
            submitTask();
        }
        
        async function clearChat() {
            await fetch('/api/clear', {method: 'POST'});
        }
        
        document.getElementById('taskInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') submitTask();
        });
        
        init();
    </script>
</body>
</html>
'''


# ==================== API路由 ====================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/conversation')
def api_conversation():
    """获取对话状态"""
    return jsonify({
        'conversations': [{'turn_id': t.turn_id, 'speaker': t.speaker, 'speaker_name': t.speaker_name, 
                          'content': t.content, 'timestamp': t.timestamp, 'msg_type': t.msg_type} 
                         for t in memory.history],
        'agentStatus': agentStatus
    })


@app.route('/api/task', methods=['POST'])
def api_task():
    """接收任务并启动多轮对话"""
    global agentStatus, is_processing
    
    data = request.json
    task_desc = data.get('task', '')
    
    # 重置状态
    agentStatus = {aid: 'idle' for aid in AGENT_INFO.keys()}
    scheduler.reset_sequence()
    
    # 添加用户消息
    memory.add_turn('user', '用户', task_desc, 'user')
    
    # 启动多轮对话线程
    def run_multi_turn_conversation():
        global agentStatus
        
        # 1. 南乔广播接收任务
        time.sleep(0.5)
        agentStatus['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', f'收到您的需求：{task_desc[:50]}...我将协调团队完成分析。', 'broadcast')
        time.sleep(1)
        agentStatus['nanqiao'] = 'idle'
        
        # 2. 采薇需求分析
        time.sleep(1.5)
        agentStatus['caiwei'] = 'speaking'
        context = memory.get_context_for_agent('caiwei')
        response = response_gen.generate('caiwei', task_desc, context)
        memory.add_turn('caiwei', '采薇', response, 'answer')
        time.sleep(1)
        agentStatus['caiwei'] = 'idle'
        
        # 3. 织锦架构设计
        time.sleep(1.5)
        agentStatus['zhijin'] = 'speaking'
        context = memory.get_context_for_agent('zhijin')
        response = response_gen.generate('zhijin', task_desc, context)
        memory.add_turn('zhijin', '织锦', response, 'answer')
        time.sleep(1)
        agentStatus['zhijin'] = 'idle'
        
        # 4. 筑台成本评估
        time.sleep(1.5)
        agentStatus['zhutai'] = 'speaking'
        context = memory.get_context_for_agent('zhutai')
        response = response_gen.generate('zhutai', task_desc, context)
        memory.add_turn('zhutai', '筑台', response, 'answer')
        time.sleep(1)
        agentStatus['zhutai'] = 'idle'
        
        # 5. 玉衡项目计划
        time.sleep(1.5)
        agentStatus['yuheng'] = 'speaking'
        context = memory.get_context_for_agent('yuheng')
        response = response_gen.generate('yuheng', task_desc, context)
        memory.add_turn('yuheng', '玉衡', response, 'answer')
        time.sleep(1)
        agentStatus['yuheng'] = 'idle'
        
        # 6. 扶摇总结
        time.sleep(1.5)
        agentStatus['fuyao'] = 'speaking'
        context = memory.get_context_for_agent('fuyao')
        response = response_gen.generate('fuyao', task_desc, context)
        memory.add_turn('fuyao', '扶摇', response, 'answer')
        time.sleep(1)
        agentStatus['fuyao'] = 'idle'
        
        # 7. 南乔收尾
        time.sleep(1)
        agentStatus['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', '任务分析完成。核心成果：需求文档、架构方案、成本预算、项目计划。请查阅并反馈。', 'answer')
        time.sleep(0.5)
        agentStatus['nanqiao'] = 'idle'
    
    thread = threading.Thread(target=run_multi_turn_conversation)
    thread.start()
    
    return jsonify({'status': 'ok'})


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """清空对话"""
    global agentStatus
    memory.clear()
    agentStatus = {aid: 'idle' for aid in AGENT_INFO.keys()}
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 多Agent协作平台 V4")
    print("=" * 60)
    print("功能: 对话记忆 · 自主调度 · 多轮协作")
    print("访问: http://120.48.169.242:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
