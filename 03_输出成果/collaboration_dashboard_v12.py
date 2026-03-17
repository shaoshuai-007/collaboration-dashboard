#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 V12 - 导出增强版
- V11基础功能
- 新增Word/Excel导出功能
- 新增导出API接口

Author: 南乔
Date: 2026-03-14
"""

from flask import Flask, render_template_string, jsonify, request, send_file
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import threading
import time
import os
import requests
import json

# 导入导出模块
from export_module import ExportAPI, DiscussionTurn, DiscussionSummary

app = Flask(__name__)

# 导出API
export_api = ExportAPI()

# ==================== 百度千帆API配置 ====================
QIANFAN_API_KEY = os.environ.get('QIANFAN_API_KEY', 'bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19')

def call_qianfan(system_prompt: str, user_message: str, temperature: float = 0.7) -> Optional[str]:
    if not QIANFAN_API_KEY:
        return None
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
            "top_p": 0.9
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        if 'result' in result:
            return result['result']
        return None
    except Exception as e:
        print(f"千帆API调用失败: {e}")
        return None


# ==================== Agent角色定义（完整9个）====================
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
    color: str
    
    def get_system_prompt(self) -> str:
        stance_desc = {
            Stance.COST_FIRST: "你非常关注成本控制，反对不必要的投入，倾向于选择性价比高的方案。",
            Stance.QUALITY_FIRST: "你非常关注技术质量和用户体验，愿意为更好的方案投入更多资源。",
            Stance.SCHEDULE_FIRST: "你非常关注项目进度和风险控制，反对可能导致延期的方案。",
            Stance.BALANCED: "你综合考虑各方面因素，追求平衡的方案。"
        }
        return f"""你是{self.name}，角色是{self.role}。

你的立场：{stance_desc[self.stance]}

你的专业领域：{', '.join(self.expertise)}
你最关注的问题：{', '.join(self.concern_points)}

重要规则：
1. 必须基于你的立场和专业领域发言
2. 如果看到其他人的方案与你的立场冲突，要明确提出质疑
3. 回复要专业、简洁，控制在80字以内
4. 使用【角色名】开头"""


# 定义所有9个Agent
AGENTS = {
    'nanqiao': AgentPersona(
        agent_id='nanqiao', name='南乔', role='主控Agent', emoji='🌿',
        stance=Stance.BALANCED,
        expertise=['需求整理', '任务协调', '进度跟踪'],
        concern_points=['需求范围', '进度风险'],
        color='#9C27B0'
    ),
    'caiwei': AgentPersona(
        agent_id='caiwei', name='采薇', role='需求分析专家', emoji='🌸',
        stance=Stance.QUALITY_FIRST,
        expertise=['需求调研', '用户故事', '验收标准'],
        concern_points=['需求完整性', '用户体验'],
        color='#409EFF'
    ),
    'zhijin': AgentPersona(
        agent_id='zhijin', name='织锦', role='架构设计师', emoji='🧵',
        stance=Stance.QUALITY_FIRST,
        expertise=['架构设计', '技术选型', '系统设计'],
        concern_points=['技术可行性', '扩展性', '性能'],
        color='#67C23A'
    ),
    'zhutai': AgentPersona(
        agent_id='zhutai', name='筑台', role='售前工程师', emoji='🏗️',
        stance=Stance.COST_FIRST,
        expertise=['成本评估', '方案报价', 'ROI计算'],
        concern_points=['成本过高', '预算控制'],
        color='#E6A23C'
    ),
    'gongchi': AgentPersona(
        agent_id='gongchi', name='工尺', role='详细设计师', emoji='📐',
        stance=Stance.QUALITY_FIRST,
        expertise=['详细设计', '接口设计', '数据库设计'],
        concern_points=['实现难度', '代码质量'],
        color='#607D8B'
    ),
    'yuheng': AgentPersona(
        agent_id='yuheng', name='玉衡', role='项目经理', emoji='⚖️',
        stance=Stance.SCHEDULE_FIRST,
        expertise=['项目计划', '风险管理', '进度跟踪'],
        concern_points=['进度风险', '资源冲突'],
        color='#F56C6C'
    ),
    'fuyao': AgentPersona(
        agent_id='fuyao', name='扶摇', role='总指挥', emoji='🌀',
        stance=Stance.BALANCED,
        expertise=['决策判断', '资源调配', '团队协调'],
        concern_points=['决策风险', '团队共识'],
        color='#165DFF'
    ),
    'chengcai': AgentPersona(
        agent_id='chengcai', name='呈彩', role='方案设计师', emoji='🎨',
        stance=Stance.QUALITY_FIRST,
        expertise=['方案设计', 'PPT制作', '视觉呈现'],
        concern_points=['方案完整性', '展示效果'],
        color='#FF9800'
    ),
    'zhegui': AgentPersona(
        agent_id='zhegui', name='折桂', role='资源管家', emoji='📚',
        stance=Stance.BALANCED,
        expertise=['资源管理', '知识库维护', '文档归档'],
        concern_points=['资源不足', '知识沉淀'],
        color='#00BCD4'
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
    reply_to: str = ""

class ConversationMemory:
    def __init__(self):
        self.history: List[ConversationTurn] = []
        self.turn_count: int = 0
        self.current_task: str = ""
        self.start_time: datetime = None
    
    def add_turn(self, speaker: str, speaker_name: str, content: str, 
                 msg_type: str = "answer", is_challenging: bool = False, reply_to: str = ""):
        self.turn_count += 1
        turn = ConversationTurn(
            turn_id=self.turn_count,
            speaker=speaker,
            speaker_name=speaker_name,
            content=content,
            timestamp=datetime.now().isoformat(),
            msg_type=msg_type,
            is_challenging=is_challenging,
            reply_to=reply_to
        )
        self.history.append(turn)
        return turn
    
    def get_context(self, limit: int = 8) -> str:
        if not self.history:
            return ""
        parts = []
        for turn in self.history[-limit:]:
            prefix = "【质疑】" if turn.is_challenging else ""
            parts.append(f"{prefix}{turn.speaker_name}: {turn.content}")
        return "\n".join(parts)
    
    def get_consensus_level(self) -> int:
        if not self.history:
            return 0
        challenges = sum(1 for t in self.history if t.is_challenging)
        total = len([t for t in self.history if t.speaker != 'user' and t.speaker != 'nanqiao'])
        if total == 0:
            return 0
        consensus = max(0, 100 - (challenges * 15))
        return min(100, consensus)
    
    def clear(self):
        self.history.clear()
        self.turn_count = 0
        self.current_task = ""
        self.start_time = None


# ==================== 智能响应生成 ====================
class IntelligentResponder:
    def __init__(self):
        self.api_configured = bool(QIANFAN_API_KEY)
    
    def generate(self, agent: AgentPersona, task: str, memory: ConversationMemory) -> Tuple[str, bool, str]:
        context = memory.get_context()
        system_prompt = agent.get_system_prompt()
        
        if context:
            user_message = f"""当前任务：{task}

已有讨论：
{context}

请基于你的角色立场，针对任务发表专业意见。如果有不同意见请明确提出质疑。"""
        else:
            user_message = f"请针对以下任务发表你的专业意见：{task}"
        
        response = call_qianfan(system_prompt, user_message)
        
        if response:
            is_challenge = any(kw in response for kw in ['质疑', '反对', '不同意', '但是', '有问题', '不可行', '建议修改', '成本过高', '周期太长', '风险'])
            reply_to = ""
            if is_challenge and memory.history:
                for t in reversed(memory.history):
                    if t.speaker != agent.agent_id:
                        reply_to = t.speaker_name
                        break
            return response.strip(), is_challenge, reply_to
        
        return self._fallback(agent, task, context)
    
    def _fallback(self, agent: AgentPersona, task: str, context: str) -> Tuple[str, bool, str]:
        responses = {
            'caiwei': ("【需求分析】我梳理了核心需求。主要功能点已识别，建议进行技术可行性评估。", False, ""),
            'zhijin': ("【架构设计】基于需求，推荐微服务架构。技术栈：Spring Cloud + K8s + PostgreSQL。", False, ""),
            'zhutai': ("【成本质疑】微服务架构成本较高，建议评估必要性。可采用单体架构降低初期投入。", True, "织锦"),
            'yuheng': ("【进度提醒】复杂方案会增加开发周期。建议敏捷迭代，首期交付核心功能。", True, "织锦"),
            'gongchi': ("【详细设计】数据库设计约30张表，核心接口50个。开发工时评估完成。", False, ""),
            'fuyao': ("【决策】综合讨论，采纳分阶段方案。平衡成本、质量和进度。", False, ""),
            'nanqiao': ("【主控】收到任务，协调团队分析中。", False, ""),
            'chengcai': ("【方案设计】建议采用分层架构展示，突出核心价值点。", False, ""),
            'zhegui': ("【资源管理】已整理相关技术文档和案例库，可随时调用。", False, "")
        }
        return responses.get(agent.agent_id, ("处理中...", False, ""))


# ==================== 全局状态 ====================
memory = ConversationMemory()
responder = IntelligentResponder()
agent_status: Dict[str, str] = {}
is_processing = False


# ==================== HTML模板 ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 智能协作平台 V11</title>
    <style>
        :root {
            --primary: #165DFF;
            --primary-light: #E8F3FF;
            --bg-main: #F5F7FA;
            --bg-card: #FFFFFF;
            --text-primary: #303133;
            --text-secondary: #606266;
            --text-muted: #909399;
            --border: #E4E7ED;
            --success: #67C23A;
            --warning: #E6A23C;
            --danger: #F56C6C;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: var(--bg-main);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            font-size: 14px;
        }
        
        /* ========== 顶部导航 ========== */
        .header {
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 0 24px;
            height: 56px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo {
            font-size: 20px;
            font-weight: 600;
            color: var(--primary);
        }
        .logo-sub {
            font-size: 12px;
            color: var(--text-muted);
            padding: 2px 8px;
            background: var(--primary-light);
            border-radius: 4px;
        }
        .header-right {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--success);
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
        }
        
        /* ========== 主区域 ========== */
        .main {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* ========== 左侧边栏 ========== */
        .sidebar {
            width: 300px;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }
        
        /* Agent卡片 */
        .agent-card {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            margin-bottom: 6px;
            background: var(--bg-main);
            border-radius: 8px;
            border-left: 3px solid transparent;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .agent-card:hover {
            background: var(--primary-light);
        }
        .agent-card.active {
            border-left-color: var(--agent-color, var(--primary));
            background: var(--primary-light);
        }
        .agent-card.speaking {
            border-left-color: var(--agent-color, var(--primary));
            box-shadow: 0 2px 8px rgba(22, 93, 255, 0.15);
        }
        .agent-card.challenge {
            border-left-color: var(--warning);
            background: #FFF7E6;
        }
        
        .agent-avatar {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            margin-right: 10px;
            color: white;
        }
        .agent-info {
            flex: 1;
        }
        .agent-name {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
        }
        .agent-role {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 1px;
        }
        .agent-stance {
            display: inline-block;
            font-size: 9px;
            padding: 1px 5px;
            border-radius: 3px;
            margin-top: 3px;
            background: var(--primary-light);
            color: var(--primary);
        }
        
        /* ========== 对话区域 ========== */
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }
        
        /* 筛选栏 */
        .filter-bar {
            padding: 10px 16px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .filter-btn {
            padding: 5px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-card);
            font-size: 12px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-btn:hover, .filter-btn.active {
            border-color: var(--primary);
            color: var(--primary);
            background: var(--primary-light);
        }
        
        /* 消息区 */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: var(--bg-main);
        }
        
        /* 消息气泡 */
        .message {
            margin-bottom: 16px;
            position: relative;
            padding-left: 48px;
        }
        
        .message.user {
            text-align: right;
            padding-left: 0;
            padding-right: 0;
        }
        
        .message-avatar {
            position: absolute;
            left: 0;
            top: 0;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
            z-index: 1;
        }
        
        .message-content {
            display: inline-block;
            max-width: 75%;
            background: var(--bg-card);
            border-radius: 10px;
            padding: 12px 14px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            position: relative;
        }
        .message.user .message-content {
            background: var(--primary);
            color: white;
        }
        
        .message-header {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 6px;
        }
        .message-speaker {
            font-size: 12px;
            font-weight: 600;
        }
        .message-time {
            font-size: 10px;
            color: var(--text-muted);
        }
        .message-badge {
            font-size: 9px;
            padding: 2px 6px;
            border-radius: 4px;
            background: #FFF7E6;
            color: var(--warning);
            font-weight: 500;
        }
        .message-text {
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .message-footer {
            display: flex;
            gap: 10px;
            margin-top: 6px;
        }
        .message-action {
            font-size: 10px;
            color: var(--text-muted);
            cursor: pointer;
        }
        .message-action:hover {
            color: var(--primary);
        }
        
        /* 回复箭头 */
        .reply-arrow {
            font-size: 11px;
            color: var(--text-muted);
            margin: 6px 0;
            padding-left: 20px;
        }
        
        /* 输入区 */
        .input-area {
            padding: 14px 16px;
            background: var(--bg-card);
            border-top: 1px solid var(--border);
        }
        .input-row {
            display: flex;
            gap: 10px;
        }
        .input-field {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-field:focus {
            border-color: var(--primary);
        }
        .send-btn {
            padding: 10px 24px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .send-btn:hover:not(:disabled) {
            background: #0D47A1;
        }
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .quick-actions {
            display: flex;
            gap: 6px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        .quick-btn {
            padding: 5px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-card);
            font-size: 11px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        /* ========== 右侧数据面板 ========== */
        .data-panel {
            width: 280px;
            background: var(--bg-card);
            border-left: 1px solid var(--border);
            padding: 16px;
            overflow-y: auto;
        }
        .panel-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
        }
        
        /* 共识度 */
        .consensus-card {
            background: var(--bg-main);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 16px;
        }
        .consensus-label {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
        .consensus-bar {
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
        }
        .consensus-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s ease, background 0.5s ease;
        }
        .consensus-value {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 6px;
        }
        
        /* 统计卡片 */
        .stats-card {
            background: var(--bg-main);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid var(--border);
        }
        .stat-item:last-child {
            border-bottom: none;
        }
        .stat-label {
            font-size: 11px;
            color: var(--text-secondary);
        }
        .stat-value {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        /* 发言统计图 */
        .speaker-stats {
            margin-top: 12px;
        }
        .speaker-bar {
            display: flex;
            align-items: center;
            margin-bottom: 6px;
        }
        .speaker-name {
            width: 50px;
            font-size: 10px;
            color: var(--text-secondary);
        }
        .speaker-progress {
            flex: 1;
            height: 5px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
            margin: 0 6px;
        }
        .speaker-fill {
            height: 100%;
            border-radius: 3px;
        }
        .speaker-count {
            width: 24px;
            font-size: 10px;
            color: var(--text-muted);
            text-align: right;
        }
        
        /* ========== 空状态 ========== */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }
        .empty-icon {
            font-size: 56px;
            margin-bottom: 12px;
            opacity: 0.5;
        }
        .empty-title {
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
        .empty-desc {
            font-size: 12px;
        }
        
        /* ========== 响应式 ========== */
        @media (max-width: 1024px) {
            .data-panel { display: none; }
        }
        @media (max-width: 768px) {
            .sidebar { 
                position: absolute;
                left: -300px;
                z-index: 100;
                height: 100%;
            }
            .sidebar.open { left: 0; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="logo">🧭 指南针工程</div>
            <div class="logo-sub">智能协作平台 V11</div>
        </div>
        <div class="header-right">
            <div class="status-badge">
                <div class="status-dot"></div>
                <span id="apiStatus">千帆API已连接</span>
            </div>
            <button class="filter-btn" onclick="exportWord()">📥 Word</button>
            <button class="filter-btn" onclick="exportExcel()">📊 Excel</button>
            <button class="filter-btn" onclick="exportMarkdown()">📝 MD</button>
        </div>
    </div>
    
    <div class="main">
        <!-- 左侧Agent面板 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <span>👥 协作团队</span>
                <span id="agentCount">9人在线</span>
            </div>
            <div class="sidebar-content" id="agentList"></div>
        </div>
        
        <!-- 中间对话区 -->
        <div class="chat-area">
            <div class="filter-bar">
                <button class="filter-btn active" onclick="filterMessages('all')">全部</button>
                <button class="filter-btn" onclick="filterMessages('challenge')">质疑</button>
                <button class="filter-btn" onclick="filterMessages('support')">支持</button>
                <button class="filter-btn" onclick="filterMessages('decision')">决策</button>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <div class="empty-icon">💬</div>
                    <div class="empty-title">开始智能协作</div>
                    <div class="empty-desc">输入任务主题，Agent团队将进行专业讨论和辩论</div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-row">
                    <input type="text" class="input-field" id="taskInput" 
                           placeholder="输入任务主题，按 Enter 发送..." 
                           onkeypress="handleKeyPress(event)">
                    <button class="send-btn" id="sendBtn" onclick="submitTask()">发送</button>
                </div>
                <div class="quick-actions">
                    <button class="quick-btn" onclick="quickTask('湖北电信电渠智能化转型项目需求分析')">📋 电渠智能化</button>
                    <button class="quick-btn" onclick="quickTask('AI智能配案系统功能设计')">🤖 AI配案系统</button>
                    <button class="quick-btn" onclick="quickTask('存量经营平台升级改造')">📊 存量经营平台</button>
                    <button class="quick-btn" onclick="quickTask('智能营销话术推荐系统')">🎯 智能话术</button>
                    <button class="quick-btn" onclick="clearChat()">🗑️ 清空</button>
                </div>
            </div>
        </div>
        
        <!-- 右侧数据面板 -->
        <div class="data-panel">
            <div class="panel-title">📊 协作数据</div>
            
            <div class="consensus-card">
                <div class="consensus-label">共识达成度</div>
                <div class="consensus-bar">
                    <div class="consensus-fill" id="consensusFill" style="width: 0%; background: #F56C6C;"></div>
                </div>
                <div class="consensus-value" id="consensusValue">0%</div>
            </div>
            
            <div class="stats-card">
                <div class="stat-item">
                    <span class="stat-label">当前轮次</span>
                    <span class="stat-value" id="roundCount">0 / 10</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">辩论耗时</span>
                    <span class="stat-value" id="elapsedTime">00:00</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">质疑次数</span>
                    <span class="stat-value" id="challengeCount">0</span>
                </div>
            </div>
            
            <div class="panel-title" style="margin-top: 16px;">🎤 发言统计</div>
            <div class="speaker-stats" id="speakerStats"></div>
        </div>
    </div>
    
    <script>
        // 完整9个Agent配置
        const AGENTS = {
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀', stance: '平衡', color: '#165DFF' },
            'nanqiao': { name: '南乔', role: '主控Agent', emoji: '🌿', stance: '平衡', color: '#9C27B0' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️', stance: '进度优先', color: '#F56C6C' },
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸', stance: '质量优先', color: '#409EFF' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵', stance: '质量优先', color: '#67C23A' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️', stance: '成本优先', color: '#E6A23C' },
            'gongchi': { name: '工尺', role: '详细设计师', emoji: '📐', stance: '质量优先', color: '#607D8B' },
            'chengcai': { name: '呈彩', role: '方案设计师', emoji: '🎨', stance: '质量优先', color: '#FF9800' },
            'zhegui': { name: '折桂', role: '资源管家', emoji: '📚', stance: '平衡', color: '#00BCD4' }
        };
        
        let conversations = [];
        let agentStatus = {};
        let isProcessing = false;
        let startTime = null;
        let timerInterval = null;
        let currentFilter = 'all';
        
        // 初始化
        function init() {
            renderAgentList();
            fetchStatus();
            setInterval(fetchStatus, 800);
        }
        
        // 渲染Agent列表（完整9个）
        function renderAgentList() {
            const container = document.getElementById('agentList');
            container.innerHTML = '';
            
            const order = ['fuyao', 'nanqiao', 'yuheng', 'caiwei', 'zhijin', 'zhutai', 'gongchi', 'chengcai', 'zhegui'];
            
            order.forEach(id => {
                const agent = AGENTS[id];
                if (!agent) return;
                
                const status = agentStatus[id] || 'idle';
                
                const card = document.createElement('div');
                card.className = `agent-card ${status === 'speaking' ? 'speaking' : ''} ${status === 'challenge' ? 'challenge' : ''}`;
                card.style.setProperty('--agent-color', agent.color);
                card.id = `agent-${id}`;
                card.onclick = () => filterByAgent(id);
                
                card.innerHTML = `
                    <div class="agent-avatar" style="background: ${agent.color}">${agent.emoji}</div>
                    <div class="agent-info">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-role">${agent.role}</div>
                        <div class="agent-stance">${agent.stance}</div>
                    </div>
                `;
                container.appendChild(card);
            });
        }
        
        // 获取状态
        async function fetchStatus() {
            try {
                const response = await fetch('/api/conversation');
                const data = await response.json();
                conversations = data.conversations || [];
                agentStatus = data.agentStatus || {};
                
                renderMessages();
                updateAgentCards();
                updateDataPanel();
            } catch (e) { console.error('fetchStatus error:', e); }
        }
        
        // 渲染消息
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            
            if (conversations.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">💬</div>
                        <div class="empty-title">开始智能协作</div>
                        <div class="empty-desc">输入任务主题，Agent团队将进行专业讨论和辩论</div>
                    </div>
                `;
                return;
            }
            
            let html = '';
            
            conversations.forEach((conv, idx) => {
                const agent = AGENTS[conv.speaker] || { name: conv.speaker, emoji: '🤖', color: '#909399' };
                const isUser = conv.speaker === 'user';
                const time = conv.timestamp.split('T')[1].split('.')[0].substring(0, 5);
                
                // 筛选
                if (currentFilter !== 'all') {
                    if (currentFilter === 'challenge' && !conv.is_challenging) return;
                    if (currentFilter === 'support' && conv.is_challenging) return;
                    if (currentFilter === 'decision' && conv.msg_type !== 'conclusion') return;
                }
                
                // 回复箭头
                if (conv.reply_to && idx > 0) {
                    html += `<div class="reply-arrow">↳ 回复 ${conv.reply_to}</div>`;
                }
                
                html += `
                    <div class="message ${isUser ? 'user' : ''}" data-speaker="${conv.speaker}" data-type="${conv.is_challenging ? 'challenge' : 'support'}">
                        ${!isUser ? `<div class="message-avatar" style="background: ${agent.color}">${agent.emoji}</div>` : ''}
                        <div class="message-content">
                            <div class="message-header">
                                <span class="message-speaker" style="color: ${isUser ? 'white' : agent.color}">${agent.emoji} ${agent.name}</span>
                                ${conv.is_challenging ? '<span class="message-badge">⚠️ 质疑</span>' : ''}
                                ${conv.msg_type === 'conclusion' ? '<span class="message-badge" style="background:#E8F5E9;color:#67C23A">✓ 决策</span>' : ''}
                                <span class="message-time">${time}</span>
                            </div>
                            <div class="message-text">${conv.content}</div>
                            <div class="message-footer">
                                <span class="message-action" onclick="copyMessage(this)" data-text="${encodeURIComponent(conv.content)}">📋 复制</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
        }
        
        // 更新Agent卡片
        function updateAgentCards() {
            Object.keys(agentStatus).forEach(id => {
                const card = document.getElementById(`agent-${id}`);
                if (card) {
                    card.className = `agent-card ${agentStatus[id] === 'speaking' ? 'speaking' : ''} ${agentStatus[id] === 'challenge' ? 'challenge' : ''}`;
                }
            });
        }
        
        // 更新数据面板
        function updateDataPanel() {
            const challengeCount = conversations.filter(c => c.is_challenging).length;
            const totalAgentMsgs = conversations.filter(c => c.speaker !== 'user').length;
            let consensus = 0;
            if (totalAgentMsgs > 0) {
                consensus = Math.max(0, 100 - (challengeCount * 15));
                if (conversations.some(c => c.msg_type === 'conclusion')) {
                    consensus = 100;
                }
            }
            
            const fill = document.getElementById('consensusFill');
            const value = document.getElementById('consensusValue');
            fill.style.width = consensus + '%';
            if (consensus < 30) fill.style.background = '#F56C6C';
            else if (consensus < 70) fill.style.background = '#E6A23C';
            else fill.style.background = '#67C23A';
            value.textContent = consensus + '%';
            
            document.getElementById('roundCount').textContent = `${Math.ceil(totalAgentMsgs / 2)} / 10`;
            document.getElementById('challengeCount').textContent = challengeCount;
            
            // 发言统计
            const stats = {};
            conversations.forEach(c => {
                if (c.speaker !== 'user') {
                    if (!stats[c.speaker]) stats[c.speaker] = 0;
                    stats[c.speaker]++;
                }
            });
            
            let statsHtml = '';
            const maxCount = Math.max(...Object.values(stats), 1);
            Object.entries(stats).forEach(([id, count]) => {
                const agent = AGENTS[id];
                if (agent) {
                    const percent = (count / maxCount) * 100;
                    statsHtml += `
                        <div class="speaker-bar">
                            <span class="speaker-name">${agent.name}</span>
                            <div class="speaker-progress">
                                <div class="speaker-fill" style="width: ${percent}%; background: ${agent.color}"></div>
                            </div>
                            <span class="speaker-count">${count}</span>
                        </div>
                    `;
                }
            });
            document.getElementById('speakerStats').innerHTML = statsHtml;
        }
        
        // 处理键盘事件
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                submitTask();
            }
        }
        
        // 发送任务（修复版）
        async function submitTask() {
            if (isProcessing) {
                console.log('正在处理中，请稍候...');
                return;
            }
            
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) {
                console.log('任务内容为空');
                return;
            }
            
            console.log('提交任务:', content);
            isProcessing = true;
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            input.value = '';
            
            // 开始计时
            startTime = Date.now();
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(updateTimer, 1000);
            
            try {
                const response = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
                const result = await response.json();
                console.log('任务提交结果:', result);
            } catch (e) {
                console.error('提交失败:', e);
            }
            
            // 60秒后自动解除锁定
            setTimeout(() => {
                isProcessing = false;
                sendBtn.disabled = false;
                console.log('处理完成，解锁');
            }, 60000);
        }
        
        // 更新计时器
        function updateTimer() {
            if (!startTime) return;
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const secs = (elapsed % 60).toString().padStart(2, '0');
            document.getElementById('elapsedTime').textContent = `${mins}:${secs}`;
        }
        
        // 快捷任务
        function quickTask(task) {
            document.getElementById('taskInput').value = task;
            submitTask();
        }
        
        // 清空
        async function clearChat() {
            await fetch('/api/clear', {method: 'POST'});
            if (timerInterval) clearInterval(timerInterval);
            document.getElementById('elapsedTime').textContent = '00:00';
            startTime = null;
        }
        
        // 筛选
        function filterMessages(type) {
            currentFilter = type;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            renderMessages();
        }
        
        function filterByAgent(agentId) {
            currentFilter = 'all';
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector('.filter-btn').classList.add('active');
            renderMessages();
            
            const msgs = document.querySelectorAll(`[data-speaker="${agentId}"]`);
            if (msgs.length > 0) {
                msgs[0].scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        }
        
        // 复制消息
        function copyMessage(element) {
            const text = decodeURIComponent(element.getAttribute('data-text'));
            navigator.clipboard.writeText(text).then(() => {
                element.textContent = '✓ 已复制';
                setTimeout(() => {
                    element.textContent = '📋 复制';
                }, 1500);
            });
        }
        
        // 导出Word
        async function exportWord() {
            if (conversations.length === 0) {
                alert('暂无对话可导出');
                return;
            }
            
            try {
                const response = await fetch('/api/export/word', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `讨论报告_${new Date().toISOString().slice(0,10)}.docx`;
                    a.click();
                    URL.revokeObjectURL(url);
                } else {
                    alert('导出失败，请稍后重试');
                }
            } catch (e) {
                console.error('导出Word失败:', e);
                alert('导出失败：' + e.message);
            }
        }
        
        // 导出Excel
        async function exportExcel() {
            if (conversations.length === 0) {
                alert('暂无对话可导出');
                return;
            }
            
            try {
                const response = await fetch('/api/export/excel', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `讨论报告_${new Date().toISOString().slice(0,10)}.xlsx`;
                    a.click();
                    URL.revokeObjectURL(url);
                } else {
                    alert('导出失败，请稍后重试');
                }
            } catch (e) {
                console.error('导出Excel失败:', e);
                alert('导出失败：' + e.message);
            }
        }
        
        // 导出Markdown
        async function exportMarkdown() {
            if (conversations.length === 0) {
                alert('暂无对话可导出');
                return;
            }
            
            try {
                const response = await fetch('/api/export/markdown', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                
                if (result.status === 'ok') {
                    const blob = new Blob([result.content], {type: 'text/markdown'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `讨论报告_${new Date().toISOString().slice(0,10)}.md`;
                    a.click();
                    URL.revokeObjectURL(url);
                } else {
                    alert('导出失败：' + result.message);
                }
            } catch (e) {
                console.error('导出Markdown失败:', e);
                alert('导出失败：' + e.message);
            }
        }
        
        // 原有的导出函数保留（向后兼容）
        function exportChat() {
            exportMarkdown();
        }
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                exportChat();
            }
        });
        
        // 启动
        init();
    </script>
</body>
</html>
'''


# ==================== API路由 ====================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status')
def api_status():
    return jsonify({'api_connected': bool(QIANFAN_API_KEY)})


@app.route('/api/conversation')
def api_conversation():
    return jsonify({
        'conversations': [
            {'turn_id': t.turn_id, 'speaker': t.speaker, 'speaker_name': t.speaker_name,
             'content': t.content, 'timestamp': t.timestamp, 'msg_type': t.msg_type,
             'is_challenging': t.is_challenging, 'reply_to': t.reply_to}
            for t in memory.history
        ],
        'agentStatus': agent_status
    })


@app.route('/api/task', methods=['POST'])
def api_task():
    global agent_status
    
    data = request.json
    task = data.get('task', '')
    
    agent_status = {aid: 'idle' for aid in AGENTS.keys()}
    memory.clear()
    memory.current_task = task
    memory.start_time = datetime.now()
    memory.add_turn('user', '用户', task)
    
    def run_discussion():
        global agent_status
        
        # 1. 南乔开场
        time.sleep(0.5)
        agent_status['nanqiao'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['nanqiao'], task, memory)
        memory.add_turn('nanqiao', '南乔', response)
        time.sleep(1)
        agent_status['nanqiao'] = 'idle'
        
        # 2. 采薇需求分析
        time.sleep(0.8)
        agent_status['caiwei'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['caiwei'], task, memory)
        memory.add_turn('caiwei', '采薇', response)
        time.sleep(3)
        agent_status['caiwei'] = 'idle'
        
        # 3. 织锦架构设计
        time.sleep(0.8)
        agent_status['zhijin'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['zhijin'], task, memory)
        memory.add_turn('zhijin', '织锦', response)
        time.sleep(3)
        agent_status['zhijin'] = 'idle'
        
        # 4. 筑台成本评估
        time.sleep(0.8)
        response, is_challenge, reply_to = responder.generate(AGENTS['zhutai'], task, memory)
        agent_status['zhutai'] = 'challenge' if is_challenge else 'speaking'
        memory.add_turn('zhutai', '筑台', response, is_challenging=is_challenge, reply_to=reply_to)
        time.sleep(3)
        agent_status['zhutai'] = 'idle'
        
        # 5. 玉衡项目管理
        time.sleep(0.8)
        response, is_challenge, reply_to = responder.generate(AGENTS['yuheng'], task, memory)
        agent_status['yuheng'] = 'challenge' if is_challenge else 'speaking'
        memory.add_turn('yuheng', '玉衡', response, is_challenging=is_challenge, reply_to=reply_to)
        time.sleep(3)
        agent_status['yuheng'] = 'idle'
        
        # 6. 工尺详细设计
        time.sleep(0.8)
        agent_status['gongchi'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['gongchi'], task, memory)
        memory.add_turn('gongchi', '工尺', response)
        time.sleep(2)
        agent_status['gongchi'] = 'idle'
        
        # 7. 呈彩方案设计
        time.sleep(0.8)
        agent_status['chengcai'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['chengcai'], task, memory)
        memory.add_turn('chengcai', '呈彩', response)
        time.sleep(2)
        agent_status['chengcai'] = 'idle'
        
        # 8. 折桂资源管理
        time.sleep(0.8)
        agent_status['zhegui'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['zhegui'], task, memory)
        memory.add_turn('zhegui', '折桂', response)
        time.sleep(2)
        agent_status['zhegui'] = 'idle'
        
        # 9. 扶摇总结决策
        time.sleep(0.8)
        agent_status['fuyao'] = 'speaking'
        response, _, _ = responder.generate(AGENTS['fuyao'], task, memory)
        memory.add_turn('fuyao', '扶摇', response, msg_type='conclusion')
        time.sleep(1)
        agent_status['fuyao'] = 'idle'
        
        # 10. 南乔收尾
        time.sleep(0.5)
        agent_status['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', '【主控】讨论完成。团队已形成共识方案。', msg_type='conclusion')
        time.sleep(0.3)
        agent_status['nanqiao'] = 'idle'
    
    thread = threading.Thread(target=run_discussion)
    thread.start()
    
    return jsonify({'status': 'ok'})


@app.route('/api/clear', methods=['POST'])
def api_clear():
    global agent_status
    memory.clear()
    agent_status = {aid: 'idle' for aid in AGENTS.keys()}
    return jsonify({'status': 'ok'})


@app.route('/api/export/word', methods=['POST'])
def api_export_word():
    """导出Word文档"""
    try:
        # 转换对话历史
        turns = []
        for t in memory.history:
            turn = DiscussionTurn(
                turn_id=t.turn_id,
                speaker=t.speaker,
                speaker_name=t.speaker_name,
                speaker_role=AGENTS.get(t.speaker, AGENTS['nanqiao']).role if t.speaker in AGENTS else '用户',
                content=t.content,
                timestamp=t.timestamp,
                is_challenging=t.is_challenging,
                reply_to=t.reply_to
            )
            turns.append(turn)
        
        # 创建摘要
        participants = list(set([t.speaker_name for t in memory.history if t.speaker != 'user']))
        summary = DiscussionSummary(
            task=memory.current_task or '未命名任务',
            start_time=memory.start_time.isoformat() if memory.start_time else '',
            end_time=datetime.now().isoformat(),
            total_turns=memory.turn_count,
            consensus_level=memory.get_consensus_level(),
            participants=participants,
            key_points=[],  # 可以从讨论中提取
            risks=[],
            decisions=[]
        )
        
        # 导出
        word_path = export_api.export_word(turns, summary)
        return send_file(word_path, as_attachment=True, download_name=f'讨论报告_{datetime.now().strftime("%Y%m%d")}.docx')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/export/excel', methods=['POST'])
def api_export_excel():
    """导出Excel表格"""
    try:
        # 转换对话历史
        turns = []
        for t in memory.history:
            turn = DiscussionTurn(
                turn_id=t.turn_id,
                speaker=t.speaker,
                speaker_name=t.speaker_name,
                speaker_role=AGENTS.get(t.speaker, AGENTS['nanqiao']).role if t.speaker in AGENTS else '用户',
                content=t.content,
                timestamp=t.timestamp,
                is_challenging=t.is_challenging,
                reply_to=t.reply_to
            )
            turns.append(turn)
        
        # 创建摘要
        participants = list(set([t.speaker_name for t in memory.history if t.speaker != 'user']))
        summary = DiscussionSummary(
            task=memory.current_task or '未命名任务',
            start_time=memory.start_time.isoformat() if memory.start_time else '',
            end_time=datetime.now().isoformat(),
            total_turns=memory.turn_count,
            consensus_level=memory.get_consensus_level(),
            participants=participants,
            key_points=[],
            risks=[],
            decisions=[]
        )
        
        # 导出
        excel_path = export_api.export_excel(turns, summary)
        return send_file(excel_path, as_attachment=True, download_name=f'讨论报告_{datetime.now().strftime("%Y%m%d")}.xlsx')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/export/markdown', methods=['POST'])
def api_export_markdown():
    """导出Markdown文档"""
    try:
        # 转换对话历史
        turns = []
        for t in memory.history:
            turn = DiscussionTurn(
                turn_id=t.turn_id,
                speaker=t.speaker,
                speaker_name=t.speaker_name,
                speaker_role=AGENTS.get(t.speaker, AGENTS['nanqiao']).role if t.speaker in AGENTS else '用户',
                content=t.content,
                timestamp=t.timestamp,
                is_challenging=t.is_challenging,
                reply_to=t.reply_to
            )
            turns.append(turn)
        
        # 创建摘要
        participants = list(set([t.speaker_name for t in memory.history if t.speaker != 'user']))
        summary = DiscussionSummary(
            task=memory.current_task or '未命名任务',
            start_time=memory.start_time.isoformat() if memory.start_time else '',
            end_time=datetime.now().isoformat(),
            total_turns=memory.turn_count,
            consensus_level=memory.get_consensus_level(),
            participants=participants,
            key_points=[],
            risks=[],
            decisions=[]
        )
        
        # 导出
        md_content = export_api.export_markdown(turns, summary)
        return jsonify({'status': 'ok', 'content': md_content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 指南针工程 - 智能协作平台 V12 (导出增强版)")
    print("=" * 60)
    print("新增功能：Word导出 | Excel导出 | Markdown导出")
    print("访问地址：http://120.48.169.242:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
