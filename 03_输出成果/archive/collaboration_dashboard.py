#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 - Web界面集成版
Real-time Collaboration Dashboard

Author: 南乔
Date: 2026-03-13
"""

from flask import Flask, render_template_string, jsonify, request
from collaboration_framework import (
    CollaborationFramework, Message, MessageType, AgentRole, ReplyStyle
)
import threading
import time

app = Flask(__name__)

# 创建协作框架
framework = CollaborationFramework()

# 消息存储（用于前端展示）
messages_for_display = []
framework.bus.register_handler(
    lambda msg: messages_for_display.append(msg.to_dict())
)


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
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        
        .header {
            text-align: center;
            padding: 24px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            margin-bottom: 24px;
        }
        .header h1 { font-size: 28px; color: #C93832; margin-bottom: 8px; }
        .header p { color: #888; font-size: 14px; }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 24px;
        }
        
        .left-panel { display: flex; flex-direction: column; gap: 24px; }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }
        
        .agent-card {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 14px;
            border-left: 4px solid #595959;
            transition: all 0.3s;
            cursor: pointer;
        }
        .agent-card:hover { transform: translateY(-2px); }
        .agent-card.speaking { border-left-color: #C93832; background: rgba(201,56,50,0.2); animation: pulse 1.5s infinite; }
        .agent-card.active { border-left-color: #006EBD; background: rgba(0,110,189,0.15); }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .agent-name { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
        .agent-role { font-size: 11px; color: #888; margin-bottom: 6px; }
        .agent-status {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        .status-idle { background: #595959; }
        .status-speaking { background: #C93832; }
        .status-working { background: #006EBD; }
        
        .priority-badge {
            font-size: 10px;
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 3px;
            margin-left: 6px;
        }
        
        .chat-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 20px;
            flex: 1;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }
        .chat-header {
            font-size: 14px;
            color: #888;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding-right: 8px;
        }
        .chat-messages::-webkit-scrollbar { width: 6px; }
        .chat-messages::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        .chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }
        
        .message {
            margin-bottom: 12px;
            padding: 10px 14px;
            border-radius: 10px;
            background: rgba(0,110,189,0.2);
        }
        .message.broadcast { background: rgba(201,56,50,0.2); }
        .message .meta { font-size: 11px; color: #888; margin-bottom: 4px; display: flex; justify-content: space-between; }
        .message .content { font-size: 13px; line-height: 1.5; }
        
        .right-panel {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel-section h3 {
            font-size: 14px;
            color: #888;
            margin-bottom: 12px;
        }
        
        .speak-queue {
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 12px;
            min-height: 60px;
        }
        .queue-item {
            padding: 6px 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-bottom: 4px;
            font-size: 12px;
        }
        
        .control-btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
            margin-bottom: 8px;
            transition: all 0.2s;
        }
        .control-btn:hover { transform: scale(1.02); }
        .btn-primary { background: linear-gradient(135deg, #C93832, #006EBD); color: white; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: white; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .stat-box {
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .stat-value { font-size: 24px; font-weight: bold; color: #C93832; }
        .stat-label { font-size: 11px; color: #888; }
        
        .progress-bar {
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 12px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #C93832, #006EBD);
            transition: width 0.5s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧭 指南针工程 - 多Agent协作平台</h1>
            <p>实时协作调度 | 通信总线 | 冲突处理 | 任务分配</p>
        </div>
        
        <div class="main-grid">
            <div class="left-panel">
                <div class="agents-grid" id="agentsGrid">
                    <!-- Agent卡片由JS动态生成 -->
                </div>
                
                <div class="chat-panel">
                    <div class="chat-header">💬 实时对话流 (共 <span id="msgCount">0</span> 条消息)</div>
                    <div class="chat-messages" id="chatMessages">
                        <!-- 消息由JS动态生成 -->
                    </div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="panel-section">
                    <h3>📊 协作状态</h3>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-value" id="agentCount">9</div>
                            <div class="stat-label">活跃Agent</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" id="taskCount">0</div>
                            <div class="stat-label">进行中任务</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>🎤 发言队列</h3>
                    <div class="speak-queue" id="speakQueue">
                        <div style="color: #666; font-size: 12px;">当前空闲</div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>🎮 控制面板</h3>
                    <button class="control-btn btn-primary" onclick="sendBroadcast()">📢 广播通知</button>
                    <button class="control-btn btn-secondary" onclick="sendTask()">📋 分配任务</button>
                    <button class="control-btn btn-secondary" onclick="requestSpeak()">🎤 请求发言</button>
                    <button class="control-btn btn-secondary" onclick="refreshStatus()">🔄 刷新状态</button>
                </div>
                
                <div class="panel-section">
                    <h3>📜 最近事件</h3>
                    <div id="eventLog" style="font-size: 11px; color: #888; max-height: 150px; overflow-y: auto;">
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let agents = {};
        let messages = [];
        let currentSpeaker = null;
        
        // 初始化
        function init() {
            refreshStatus();
            setInterval(refreshStatus, 3000);  // 每3秒刷新
        }
        
        // 刷新状态
        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                agents = data.agents;
                messages = data.messages || [];
                currentSpeaker = data.current_speaker;
                
                renderAgents();
                renderMessages();
                updateStats(data);
            } catch (e) {
                console.error('刷新失败:', e);
            }
        }
        
        // 渲染Agent卡片
        function renderAgents() {
            const grid = document.getElementById('agentsGrid');
            grid.innerHTML = '';
            
            const sortedAgents = Object.values(agents).sort((a, b) => b.speak_priority - a.speak_priority);
            
            sortedAgents.forEach(agent => {
                const isSpeaking = currentSpeaker === agent.agent_id;
                const isActive = agent.current_task !== null;
                
                const card = document.createElement('div');
                card.className = `agent-card ${isSpeaking ? 'speaking' : ''} ${isActive ? 'active' : ''}`;
                card.innerHTML = `
                    <div class="agent-name">${agent.emoji} ${agent.name}
                        <span class="priority-badge">P${agent.speak_priority}</span>
                    </div>
                    <div class="agent-role">${agent.role}</div>
                    <span class="agent-status ${isSpeaking ? 'status-speaking' : isActive ? 'status-working' : 'status-idle'}">
                        ${isSpeaking ? '🎤 发言中' : isActive ? '💼 工作中' : '💤 空闲'}
                    </span>
                `;
                card.onclick = () => selectAgent(agent.agent_id);
                grid.appendChild(card);
            });
        }
        
        // 渲染消息
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            
            const recentMessages = messages.slice(-20);  // 最近20条
            recentMessages.forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.msg_type === 'broadcast' ? 'broadcast' : ''}`;
                div.innerHTML = `
                    <div class="meta">
                        <span>${msg.msg_type === 'broadcast' ? '📢 广播' : '💬 消息'}</span>
                        <span>${msg.timestamp.split('T')[1].split('.')[0]}</span>
                    </div>
                    <div class="content"><strong>${msg.from_agent}</strong> → ${msg.to_agents.join(', ')}: ${msg.content}</div>
                `;
                container.appendChild(div);
            });
            
            container.scrollTop = container.scrollHeight;
            document.getElementById('msgCount').textContent = messages.length;
        }
        
        // 更新统计
        function updateStats(data) {
            document.getElementById('agentCount').textContent = Object.keys(agents).length;
            document.getElementById('taskCount').textContent = Object.keys(data.active_tasks || {}).length;
            
            const progress = Math.min((messages.length / 20) * 100, 100);
            document.getElementById('progressFill').style.width = progress + '%';
            
            // 更新发言队列
            const queue = document.getElementById('speakQueue');
            if (data.speak_queue && data.speak_queue.length > 0) {
                queue.innerHTML = data.speak_queue.map(aid => 
                    `<div class="queue-item">${agents[aid]?.emoji || ''} ${agents[aid]?.name || aid}</div>`
                ).join('');
            } else {
                queue.innerHTML = '<div style="color: #666; font-size: 12px;">当前空闲</div>';
            }
        }
        
        // 选择Agent
        function selectAgent(agentId) {
            console.log('选中Agent:', agentId);
            // TODO: 显示Agent详情
        }
        
        // 广播消息
        async function sendBroadcast() {
            const content = prompt('请输入广播内容:');
            if (!content) return;
            
            await fetch('/api/broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({from: 'fuyao', content: content})
            });
            
            addEvent('广播: ' + content);
            refreshStatus();
        }
        
        // 分配任务
        async function sendTask() {
            const task = prompt('请输入任务描述:');
            if (!task) return;
            
            await fetch('/api/task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task: task})
            });
            
            addEvent('任务: ' + task);
            refreshStatus();
        }
        
        // 请求发言
        async function requestSpeak() {
            const agents = Object.keys(window.agents);
            const agent = prompt('请输入Agent ID:\\n' + agents.join(', '));
            if (!agent) return;
            
            await fetch('/api/speak', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({agent: agent})
            });
            
            refreshStatus();
        }
        
        // 添加事件日志
        function addEvent(text) {
            const log = document.getElementById('eventLog');
            const time = new Date().toLocaleTimeString();
            log.innerHTML = `<div>[${time}] ${text}</div>` + log.innerHTML;
        }
        
        // 启动
        init();
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status')
def api_status():
    status = framework.get_status()
    status['messages'] = messages_for_display[-50:]  # 最近50条
    return jsonify(status)


@app.route('/api/agents')
def api_agents():
    return jsonify({aid: agent.to_dict() for aid, agent in framework.scheduler.agents.items()})


@app.route('/api/broadcast', methods=['POST'])
def api_broadcast():
    data = request.json
    framework.broadcast(data.get('from', 'nanqiao'), data.get('content', ''))
    return jsonify({'status': 'ok'})


@app.route('/api/task', methods=['POST'])
def api_task():
    data = request.json
    tasks = framework.decompose_task(data.get('task', ''))
    framework.task_decomposer.assign_tasks(tasks)
    return jsonify({'status': 'ok', 'tasks': [{'id': t.id, 'desc': t.description, 'assignee': t.assignee} for t in tasks]})


@app.route('/api/speak', methods=['POST'])
def api_speak():
    data = request.json
    agent_id = data.get('agent')
    result = framework.scheduler.request_speak(agent_id)
    return jsonify({'status': 'ok' if result else 'queued', 'granted': result})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 多Agent协作框架 - Web界面")
    print("=" * 60)
    print("访问地址: http://localhost:5001")
    print("API接口:")
    print("  - GET  /api/status    获取状态")
    print("  - GET  /api/agents    获取Agent列表")
    print("  - POST /api/broadcast 广播消息")
    print("  - POST /api/task      分配任务")
    print("  - POST /api/speak     请求发言")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
