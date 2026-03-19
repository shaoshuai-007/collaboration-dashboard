#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 V6 - 真实LLM智能版
接入真实LLM，实现真正的探讨和辩论

Author: 南乔
Date: 2026-03-13
"""

from flask import Flask, render_template_string, jsonify, request
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import threading
import time
import random
import os
import json
import requests

app = Flask(__name__)

# ==================== LLM配置 ====================

# 百度千帆API配置（从环境变量读取，或使用默认值）
QIANFAN_API_KEY = os.environ.get('QIANFAN_API_KEY', '')
QIANFAN_SECRET_KEY = os.environ.get('QIANFAN_SECRET_KEY', '')

def call_llm(system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
    """调用LLM生成回复"""
    
    # 如果没有配置API，返回模拟回复
    if not QIANFAN_API_KEY or not QIANFAN_SECRET_KEY:
        return None
    
    try:
        # 获取access_token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={QIANFAN_API_KEY}&client_secret={QIANFAN_SECRET_KEY}"
        token_response = requests.post(token_url, timeout=10)
        access_token = token_response.json().get('access_token')
        
        if not access_token:
            return None
        
        # 调用ERNIE模型
        api_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
        
        payload = {
            "messages": [
                {"role": "user", "content": f"{system_prompt}\n\n---\n\n{user_message}"}
            ],
            "temperature": temperature,
            "top_p": 0.9
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        return result.get('result', None)
        
    except Exception as e:
        print(f"LLM调用失败: {e}")
        return None


# ==================== Agent角色定义 ====================

class Stance(Enum):
    COST_FIRST = "成本优先"
    QUALITY_FIRST = "质量优先"
    SCHEDULE_FIRST = "进度优先"
    BALANCED = "平衡折中"

@dataclass
class AgentPersona:
    agent_id: str
    name: str
    role: str
    emoji: str
    stance: Stance
    expertise: List[str]
    concern_points: List[str]
    
    def get_system_prompt(self) -> str:
        """生成Agent的系统提示词"""
        stance_desc = {
            Stance.COST_FIRST: "你非常关注成本控制，反对不必要的投入，倾向于选择性价比高的方案",
            Stance.QUALITY_FIRST: "你非常关注技术质量和用户体验，愿意为更好的方案投入更多资源",
            Stance.SCHEDULE_FIRST: "你非常关注项目进度和风险控制，反对可能导致延期的方案",
            Stance.BALANCED: "你综合考虑各方面因素，追求平衡的方案"
        }
        
        return f"""你是{self.name}，角色是{self.role}。

你的立场：{stance_desc[self.stance]}

你的专业领域：{', '.join(self.expertise)}
你最关注的问题：{', '.join(self.concern_points)}

发言规则：
1. 必须基于你的立场和专业领域发言
2. 如果看到其他人的方案与你的立场冲突，要明确提出质疑
3. 质疑时要具体指出问题，并提出你的替代建议
4. 回复要专业、简洁，控制在100字以内
5. 不要重复别人已经说过的内容
6. 如果同意某个方案，要说明理由

现在请针对任务发表你的专业意见。"""


# 定义所有Agent
AGENTS = {
    'nanqiao': AgentPersona(
        agent_id='nanqiao', name='南乔', role='主控Agent', emoji='🌿',
        stance=Stance.BALANCED,
        expertise=['需求整理', '任务协调', '进度跟踪', '成果汇总'],
        concern_points=['需求范围', '进度风险', '团队协作']
    ),
    'caiwei': AgentPersona(
        agent_id='caiwei', name='采薇', role='需求分析专家', emoji='🌸',
        stance=Stance.QUALITY_FIRST,
        expertise=['需求调研', '用户故事', '验收标准', '业务流程'],
        concern_points=['需求完整性', '用户体验', '业务价值']
    ),
    'zhijin': AgentPersona(
        agent_id='zhijin', name='织锦', role='架构设计师', emoji='🧵',
        stance=Stance.QUALITY_FIRST,
        expertise=['架构设计', '技术选型', '系统设计', '性能优化'],
        concern_points=['技术可行性', '扩展性', '性能', '安全']
    ),
    'zhutai': AgentPersona(
        agent_id='zhutai', name='筑台', role='售前工程师', emoji='🏗️',
        stance=Stance.COST_FIRST,
        expertise=['成本评估', '方案报价', 'ROI计算', '竞品分析'],
        concern_points=['成本过高', '投入产出比', '预算控制']
    ),
    'gongchi': AgentPersona(
        agent_id='gongchi', name='工尺', role='详细设计师', emoji='📐',
        stance=Stance.QUALITY_FIRST,
        expertise=['详细设计', '接口设计', '数据库设计', '代码规范'],
        concern_points=['实现难度', '代码质量', '技术细节']
    ),
    'yuheng': AgentPersona(
        agent_id='yuheng', name='玉衡', role='项目经理', emoji='⚖️',
        stance=Stance.SCHEDULE_FIRST,
        expertise=['项目计划', '风险管理', '团队协调', '进度跟踪'],
        concern_points=['进度风险', '资源冲突', '需求变更']
    ),
    'fuyao': AgentPersona(
        agent_id='fuyao', name='扶摇', role='总指挥', emoji='🌀',
        stance=Stance.BALANCED,
        expertise=['决策判断', '资源调配', '风险仲裁', '团队协调'],
        concern_points=['决策风险', '目标达成', '团队共识']
    )
}


# ==================== 对话记忆 ====================

@dataclass
class ConversationTurn:
    turn_id: int
    speaker: str
    speaker_name: str
    content: str
    timestamp: str
    msg_type: str = "answer"
    is_challenging: bool = False

class ConversationMemory:
    def __init__(self):
        self.history: List[ConversationTurn] = []
        self.turn_count: int = 0
        self.current_task: str = ""
    
    def add_turn(self, speaker: str, speaker_name: str, content: str, 
                 msg_type: str = "answer", is_challenging: bool = False):
        self.turn_count += 1
        turn = ConversationTurn(
            turn_id=self.turn_count,
            speaker=speaker,
            speaker_name=speaker_name,
            content=content,
            timestamp=datetime.now().isoformat(),
            msg_type=msg_type,
            is_challenging=is_challenging
        )
        self.history.append(turn)
        return turn
    
    def get_context(self, limit: int = 8) -> str:
        """获取对话上下文"""
        if not self.history:
            return ""
        
        parts = []
        for turn in self.history[-limit:]:
            prefix = "【质疑】" if turn.is_challenging else ""
            parts.append(f"{prefix}{turn.speaker_name}: {turn.content}")
        
        return "\n".join(parts)
    
    def clear(self):
        self.history.clear()
        self.turn_count = 0
        self.current_task = ""


# ==================== 智能响应生成 ====================

class IntelligentResponder:
    """智能响应器 - 使用LLM生成真正的回复"""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
    
    def generate(self, agent: AgentPersona, task: str, memory: ConversationMemory) -> Tuple[str, bool]:
        """生成智能回复，返回 (内容, 是否质疑)"""
        
        # 构建上下文
        context = memory.get_context()
        system_prompt = agent.get_system_prompt()
        
        # 构建用户消息
        if context:
            user_message = f"""当前任务：{task}

已有讨论：
{context}

请基于你的角色立场，针对任务发表专业意见。如果有不同意见请明确提出。"""
        else:
            user_message = f"请针对以下任务发表你的专业意见：{task}"
        
        # 尝试调用LLM
        if self.use_llm:
            llm_response = call_llm(system_prompt, user_message)
            if llm_response:
                # 判断是否是质疑
                is_challenge = any(kw in llm_response for kw in ['质疑', '反对', '不同意', '但是', '有问题', '不可行', '建议修改'])
                return llm_response.strip(), is_challenge
        
        # LLM失败时使用智能模板
        return self._generate_fallback(agent, task, memory)
    
    def _generate_fallback(self, agent: AgentPersona, task: str, memory: ConversationMemory) -> Tuple[str, bool]:
        """LLM不可用时的智能降级回复"""
        
        context = memory.get_context()
        
        # 分析最近的讨论内容
        is_challenge = False
        response = ""
        
        # 根据Agent立场和上下文生成
        if agent.agent_id == 'caiwei':
            if '需求' not in context or len(memory.history) < 2:
                response = f"【需求分析】我梳理了任务核心需求。主要功能点已识别，建议下一步进行技术可行性评估。需要关注：用户规模、性能要求、集成接口。"
            else:
                response = f"【需求补充】从用户角度看，还需要考虑易用性和培训成本。需求边界建议明确，避免后期范围蔓延。"
        
        elif agent.agent_id == 'zhijin':
            if '架构' not in context:
                response = f"【架构设计】基于需求，推荐云原生架构：微服务 + K8s + PostgreSQL。优势是高可用和易扩展，但初期投入会大一些。"
            elif '成本' in context or '预算' in context:
                response = f"【架构调整】理解成本顾虑。可以采用单体架构起步，后期演进。技术栈建议：Spring Boot + MySQL + Redis，开发成本降低40%。"
                is_challenge = True
            else:
                response = f"【技术方案】核心组件已设计完成。建议采用前后端分离，支持水平扩展。"
        
        elif agent.agent_id == 'zhutai':
            if '成本' not in context and '预算' not in context:
                response = f"【成本评估】根据方案规模，初步估算首年投入约150万，运维成本30万/年。ROI需要评估业务收益。"
            elif '微服务' in context or '云原生' in context:
                response = f"【成本质疑】微服务架构初期成本较高，包括基础设施、运维人员、技术培训。建议先评估必要性，或采用简化方案降低成本。"
                is_challenge = True
            else:
                response = f"【预算建议】建议分阶段投入，首期控制在100万以内，验证效果后再追加。"
        
        elif agent.agent_id == 'yuheng':
            if '进度' not in context and '周期' not in context:
                response = f"【项目计划】根据方案复杂度，开发周期预计12-16周。关键里程碑：需求评审W2、设计评审W4、开发完成W12。"
            elif '微服务' in context or len(context) > 200:
                response = f"【进度提醒】复杂方案会增加开发周期和风险。建议采用敏捷迭代，首期交付核心功能，控制风险。"
                is_challenge = random.random() > 0.5
            else:
                response = f"【风险提示】需要关注：需求变更、技术难点、资源可用性。建议预留20%缓冲时间。"
        
        elif agent.agent_id == 'gongchi':
            response = f"【详细设计】基于架构方案，数据库设计约30张表，核心接口50个。开发工时评估：后端60人天，前端40人天。"
        
        elif agent.agent_id == 'fuyao':
            if len(memory.history) > 6:
                response = f"【决策】综合讨论，团队意见已统一。采纳分阶段方案，平衡成本、质量和进度。首期聚焦核心功能，预算控制在合理范围。"
            else:
                response = f"【协调】各位的分析都很专业。建议继续讨论，找出最优方案。"
        
        else:  # nanqiao
            if len(memory.history) < 2:
                response = f"收到任务。我将协调团队进行分析，请各位基于专业立场发表意见。"
            else:
                response = f"讨论进展顺利。核心问题已明确，等待决策后我将汇总成果。"
        
        return response, is_challenge


# ==================== 全局状态 ====================

memory = ConversationMemory()
responder = IntelligentResponder(use_llm=True)
agent_status: Dict[str, str] = {}
is_processing = False


# ==================== HTML模板 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 智能协作平台</title>
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
        
        .header {
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 18px; }
        .header .info { font-size: 12px; opacity: 0.9; }
        
        .main { flex: 1; display: flex; overflow: hidden; }
        
        .sidebar {
            width: 260px;
            background: white;
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
            padding: 12px;
        }
        .sidebar h3 {
            font-size: 12px;
            color: #888;
            padding: 10px 4px;
            border-bottom: 1px solid #eee;
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
        .agent-card.speaking {
            border-left-color: #006EBD;
            background: #e3f2fd;
        }
        .agent-card.challenge {
            border-left-color: #ff9800;
            background: #fff3e0;
        }
        
        .agent-avatar {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 16px;
            margin-right: 10px;
        }
        .agent-info { flex: 1; }
        .agent-name { font-size: 13px; font-weight: 600; }
        .agent-role { font-size: 11px; color: #888; }
        .agent-stance { font-size: 10px; color: #C93832; margin-top: 2px; }
        
        .chat-area { flex: 1; display: flex; flex-direction: column; }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        
        .message { margin-bottom: 14px; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } }
        
        .message.user { text-align: right; }
        
        .msg-bubble {
            display: inline-block;
            max-width: 75%;
            padding: 12px 16px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: left;
        }
        .message.user .msg-bubble {
            background: #C93832;
            color: white;
        }
        
        .msg-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .msg-speaker { font-size: 12px; font-weight: 600; color: #C93832; }
        .message.user .msg-speaker { color: rgba(255,255,255,0.9); }
        .msg-time { font-size: 10px; color: #aaa; }
        .msg-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: #fff3e0;
            color: #f57c00;
            margin-left: 6px;
        }
        
        .msg-content { font-size: 13px; line-height: 1.6; white-space: pre-wrap; }
        
        .input-area {
            background: white;
            border-top: 1px solid #e0e0e0;
            padding: 16px;
        }
        .input-row { display: flex; gap: 10px; }
        .input-row input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
        }
        .input-row input:focus { border-color: #006EBD; }
        .input-row button {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        }
        .input-row button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .quick-actions { margin-top: 10px; display: flex; gap: 8px; }
        .quick-btn {
            padding: 6px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: white;
            color: #666;
            font-size: 12px;
            cursor: pointer;
        }
        .quick-btn:hover { border-color: #006EBD; color: #006EBD; }
        
        .empty-state { text-align: center; padding: 60px; color: #999; }
        .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
        
        .llm-status {
            padding: 8px 12px;
            background: #f5f5f5;
            border-radius: 6px;
            font-size: 11px;
            color: #666;
            margin-bottom: 12px;
        }
        .llm-status.connected { background: #e8f5e9; color: #2e7d32; }
        .llm-status.offline { background: #fff3e0; color: #f57c00; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🧭 指南针工程 - 智能协作平台</h1>
            <div class="info">真实LLM驱动 · 角色立场辩论 · 智能决策</div>
        </div>
        <div id="statusText">● 系统就绪</div>
    </div>
    
    <div class="main">
        <div class="sidebar">
            <div class="llm-status" id="llmStatus">检查LLM状态...</div>
            <h3>👥 协作团队</h3>
            <div id="agentList"></div>
        </div>
        
        <div class="chat-area">
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <div>输入需求，Agent将进行真实的讨论和辩论</div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-row">
                    <input type="text" id="taskInput" placeholder="输入任务，如：需要开发一个用户数据管理系统，预算100万">
                    <button id="sendBtn" onclick="submitTask()">发送</button>
                </div>
                <div class="quick-actions">
                    <button class="quick-btn" onclick="quickTask('开发CRM客户管理系统')">📋 CRM系统</button>
                    <button class="quick-btn" onclick="quickTask('搭建数据分析平台')">📊 数据平台</button>
                    <button class="quick-btn" onclick="quickTask('建设AI智能客服')">🤖 AI客服</button>
                    <button class="quick-btn" onclick="clearChat()">🗑️ 清空</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let conversations = [];
        let agentStatus = {};
        let isProcessing = false;
        
        const AGENTS = {
            'nanqiao': { name: '南乔', role: '主控Agent', emoji: '🌿', stance: '平衡' },
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸', stance: '质量优先' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵', stance: '质量优先' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️', stance: '成本优先' },
            'gongchi': { name: '工尺', role: '详细设计师', emoji: '📐', stance: '质量优先' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️', stance: '进度优先' },
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀', stance: '平衡' }
        };
        
        function init() {
            renderAgentList();
            checkLLMStatus();
            fetchStatus();
            setInterval(fetchStatus, 1000);
        }
        
        async function checkLLMStatus() {
            try {
                const response = await fetch('/api/llm-status');
                const data = await response.json();
                const statusDiv = document.getElementById('llmStatus');
                
                if (data.connected) {
                    statusDiv.className = 'llm-status connected';
                    statusDiv.textContent = '✓ LLM已连接';
                } else {
                    statusDiv.className = 'llm-status offline';
                    statusDiv.textContent = '○ LLM未配置（使用智能模板）';
                }
            } catch (e) {
                document.getElementById('llmStatus').textContent = '○ 检查失败';
            }
        }
        
        function renderAgentList() {
            const container = document.getElementById('agentList');
            container.innerHTML = '';
            
            ['fuyao', 'nanqiao', 'yuheng', 'caiwei', 'zhijin', 'zhutai', 'gongchi'].forEach(id => {
                const agent = AGENTS[id];
                const status = agentStatus[id] || 'idle';
                
                const card = document.createElement('div');
                card.className = `agent-card ${status === 'speaking' ? 'speaking' : ''} ${status === 'challenge' ? 'challenge' : ''}`;
                card.id = `agent-${id}`;
                card.innerHTML = `
                    <div class="agent-avatar">${agent.emoji}</div>
                    <div class="agent-info">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-role">${agent.role}</div>
                        <div class="agent-stance">${agent.stance}</div>
                    </div>
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
                updateAgentCards();
            } catch (e) { }
        }
        
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            
            if (conversations.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="icon">💬</div><div>输入需求，Agent将进行真实的讨论和辩论</div></div>';
                return;
            }
            
            container.innerHTML = '';
            
            conversations.forEach(conv => {
                const agent = AGENTS[conv.speaker] || { name: conv.speaker, emoji: '🤖' };
                const isUser = conv.speaker === 'user';
                
                const msg = document.createElement('div');
                msg.className = `message ${isUser ? 'user' : ''}`;
                msg.innerHTML = `
                    <div class="msg-bubble">
                        <div class="msg-header">
                            <span class="msg-speaker">${agent.emoji} ${agent.name}</span>
                            ${conv.is_challenging ? '<span class="msg-badge">质疑</span>' : ''}
                            <span class="msg-time">${conv.timestamp.split('T')[1].split('.')[0]}</span>
                        </div>
                        <div class="msg-content">${conv.content}</div>
                    </div>
                `;
                container.appendChild(msg);
            });
            
            container.scrollTop = container.scrollHeight;
        }
        
        function updateAgentCards() {
            Object.keys(agentStatus).forEach(id => {
                const card = document.getElementById(`agent-${id}`);
                if (card) {
                    card.className = `agent-card ${agentStatus[id] === 'speaking' ? 'speaking' : ''} ${agentStatus[id] === 'challenge' ? 'challenge' : ''}`;
                }
            });
        }
        
        async function submitTask() {
            if (isProcessing) return;
            
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) return;
            
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            input.value = '';
            
            try {
                await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
            } catch (e) { }
            
            setTimeout(() => {
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            }, 25000);
        }
        
        function quickTask(task) {
            document.getElementById('taskInput').value = task;
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


@app.route('/api/llm-status')
def api_llm_status():
    """检查LLM状态"""
    connected = bool(QIANFAN_API_KEY and QIANFAN_SECRET_KEY)
    return jsonify({'connected': connected})


@app.route('/api/conversation')
def api_conversation():
    return jsonify({
        'conversations': [
            {'turn_id': t.turn_id, 'speaker': t.speaker, 'speaker_name': t.speaker_name,
             'content': t.content, 'timestamp': t.timestamp, 'msg_type': t.msg_type,
             'is_challenging': t.is_challenging}
            for t in memory.history
        ],
        'agentStatus': agent_status
    })


@app.route('/api/task', methods=['POST'])
def api_task():
    """接收任务并启动真实讨论"""
    global agent_status
    
    data = request.json
    task = data.get('task', '')
    
    # 重置
    agent_status = {aid: 'idle' for aid in AGENTS.keys()}
    memory.clear()
    memory.current_task = task
    
    # 用户消息
    memory.add_turn('user', '用户', task)
    
    def run_real_discussion():
        global agent_status
        
        # 1. 南乔开场
        time.sleep(0.5)
        agent_status['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', f'收到任务：「{task[:50]}」我将协调团队进行分析讨论。请各位基于专业立场发表意见。')
        time.sleep(1)
        agent_status['nanqiao'] = 'idle'
        
        # 2. 采薇需求分析
        time.sleep(0.8)
        agent_status['caiwei'] = 'speaking'
        response, _ = responder.generate(AGENTS['caiwei'], task, memory)
        memory.add_turn('caiwei', '采薇', response)
        time.sleep(1.2)
        agent_status['caiwei'] = 'idle'
        
        # 3. 织锦架构设计
        time.sleep(0.8)
        agent_status['zhijin'] = 'speaking'
        response, _ = responder.generate(AGENTS['zhijin'], task, memory)
        memory.add_turn('zhijin', '织锦', response)
        time.sleep(1.2)
        agent_status['zhijin'] = 'idle'
        
        # 4. 筑台成本评估（可能质疑）
        time.sleep(0.8)
        response, is_challenge = responder.generate(AGENTS['zhutai'], task, memory)
        agent_status['zhutai'] = 'challenge' if is_challenge else 'speaking'
        memory.add_turn('zhutai', '筑台', response, is_challenging=is_challenge)
        time.sleep(1.2)
        agent_status['zhutai'] = 'idle'
        
        # 5. 玉衡项目管理
        time.sleep(0.8)
        response, is_challenge = responder.generate(AGENTS['yuheng'], task, memory)
        agent_status['yuheng'] = 'challenge' if is_challenge else 'speaking'
        memory.add_turn('yuheng', '玉衡', response, is_challenging=is_challenge)
        time.sleep(1.2)
        agent_status['yuheng'] = 'idle'
        
        # 6. 工尺详细设计（如果有必要）
        if len(memory.history) < 8:
            time.sleep(0.8)
            agent_status['gongchi'] = 'speaking'
            response, _ = responder.generate(AGENTS['gongchi'], task, memory)
            memory.add_turn('gongchi', '工尺', response)
            time.sleep(1)
            agent_status['gongchi'] = 'idle'
        
        # 7. 扶摇总结决策
        time.sleep(0.8)
        agent_status['fuyao'] = 'speaking'
        response, _ = responder.generate(AGENTS['fuyao'], task, memory)
        memory.add_turn('fuyao', '扶摇', response, msg_type='conclusion')
        time.sleep(1)
        agent_status['fuyao'] = 'idle'
        
        # 8. 南乔收尾
        time.sleep(0.5)
        agent_status['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', '讨论完成。团队已形成共识方案，请查阅决策结果。', msg_type='conclusion')
        time.sleep(0.3)
        agent_status['nanqiao'] = 'idle'
    
    thread = threading.Thread(target=run_real_discussion)
    thread.start()
    
    return jsonify({'status': 'ok'})


@app.route('/api/clear', methods=['POST'])
def api_clear():
    global agent_status
    memory.clear()
    agent_status = {aid: 'idle' for aid in AGENTS.keys()}
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 指南针工程 - 智能协作平台 V6")
    print("=" * 60)
    print("LLM状态:", "已连接" if QIANFAN_API_KEY else "未配置（使用智能模板）")
    print("访问地址: http://120.48.169.242:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
