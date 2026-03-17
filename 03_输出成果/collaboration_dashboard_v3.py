#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 - Web界面集成版 V3
支持进度条、异步处理、实时反馈

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

app = Flask(__name__)

# 创建协作框架
framework = CollaborationFramework()

# 消息存储
messages_for_display = []
framework.bus.register_handler(
    lambda msg: messages_for_display.append(msg.to_dict())
)

# Agent处理状态
agent_progress = {}


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 多Agent协作平台 V3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        
        /* 顶部标题栏 */
        .header {
            background: linear-gradient(90deg, #C93832, #006EBD);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 20px; font-weight: 600; }
        .header .subtitle { font-size: 12px; opacity: 0.9; }
        .header .status-badge {
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
        }
        
        .main-container {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 60px);
        }
        
        /* 对话展示区 */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: rgba(0,0,0,0.2);
        }
        .chat-messages {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 14px 16px;
            border-radius: 10px;
            background: rgba(255,255,255,0.08);
            border-left: 3px solid #595959;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .message.broadcast { border-left-color: #C93832; background: rgba(201,56,50,0.15); }
        .message.answer { border-left-color: #006EBD; background: rgba(0,110,189,0.15); }
        .message.user { border-left-color: #2d5a27; background: rgba(45,90,39,0.15); }
        
        .message .meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 11px;
            color: #888;
        }
        .message .agent-name {
            font-size: 13px;
            font-weight: 600;
            color: #C93832;
        }
        .message .agent-role {
            font-size: 11px;
            color: #006EBD;
            margin-left: 8px;
        }
        .message .content {
            font-size: 13px;
            line-height: 1.6;
            color: #e0e0e0;
        }
        
        /* Agent状态进度条 */
        .progress-container {
            background: rgba(0,0,0,0.4);
            padding: 12px 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .progress-title {
            font-size: 12px;
            color: #888;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }
        .progress-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .progress-item {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.05);
            padding: 8px 12px;
            border-radius: 8px;
        }
        .progress-item .emoji { font-size: 16px; }
        .progress-item .info { flex: 1; }
        .progress-item .name { font-size: 11px; font-weight: 600; }
        .progress-item .role { font-size: 9px; color: #888; }
        .progress-item .bar {
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 4px;
        }
        .progress-item .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #C93832, #006EBD);
            transition: width 0.5s;
        }
        .progress-item .percent { font-size: 10px; color: #006EBD; min-width: 30px; text-align: right; }
        .progress-item.active .bar-fill { animation: pulse-bar 1s infinite; }
        @keyframes pulse-bar { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
        
        /* 底部输入区 */
        .input-container {
            background: rgba(0,0,0,0.5);
            padding: 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .input-wrapper {
            max-width: 1000px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
        }
        .input-wrapper input {
            flex: 1;
            padding: 14px 18px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 14px;
        }
        .input-wrapper input::placeholder { color: #888; }
        .input-wrapper input:focus { outline: none; background: rgba(255,255,255,0.15); }
        
        .input-wrapper button {
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .input-wrapper button:hover { transform: scale(1.02); }
        .input-wrapper button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .quick-actions {
            max-width: 1000px;
            margin: 10px auto 0;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .quick-btn {
            padding: 6px 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            background: transparent;
            color: #aaa;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { background: rgba(255,255,255,0.1); color: white; }
        
        /* 空状态 */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
        .empty-state .text { font-size: 14px; }
        
        /* 滚动条 */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }
    </style>
</head>
<body>
    <!-- 顶部标题栏 -->
    <div class="header">
        <div>
            <h1>🧭 指南针工程 - 多Agent协作平台</h1>
            <div class="subtitle">需求输入 → 自动分配 → 协作处理 → 实时反馈</div>
        </div>
        <div class="status-badge" id="statusBadge">● 系统就绪</div>
    </div>
    
    <div class="main-container">
        <!-- 对话展示区 -->
        <div class="chat-container" id="chatContainer">
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <div class="text">输入您的需求，Agent团队将协同处理</div>
                </div>
            </div>
        </div>
        
        <!-- Agent状态进度条 -->
        <div class="progress-container">
            <div class="progress-title">
                <span>📊 Agent处理状态</span>
                <span id="activeCount">0/9 活跃</span>
            </div>
            <div class="progress-grid" id="progressGrid"></div>
        </div>
        
        <!-- 底部输入区 -->
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="taskInput" placeholder="输入需求，如：需要开发一个用户数据管理系统，请评估需求和排期">
                <button id="sendBtn" onclick="submitTask()">发送</button>
            </div>
            <div class="quick-actions">
                <button class="quick-btn" onclick="quickTask('需求分析')">📋 需求分析</button>
                <button class="quick-btn" onclick="quickTask('架构设计')">🏗️ 架构设计</button>
                <button class="quick-btn" onclick="quickTask('成本评估')">💰 成本评估</button>
                <button class="quick-btn" onclick="quickTask('项目排期')">📅 项目排期</button>
                <button class="quick-btn" onclick="quickTask('方案PPT')">📊 方案PPT</button>
                <button class="quick-btn" onclick="clearChat()">🗑️ 清空</button>
            </div>
        </div>
    </div>
    
    <script>
        let agents = {};
        let messages = [];
        let progress = {};
        let isProcessing = false;
        
        // Agent ID -> 中文名和角色映射
        const agentNames = {
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
        
        // 按优先级排序的Agent
        const agentOrder = ['fuyao', 'nanqiao', 'yuheng', 'caiwei', 'zhijin', 'zhutai', 'gongchi', 'chengcai', 'zhegui'];
        
        function init() {
            fetchProgress();
            renderProgressBars();
            setInterval(fetchProgress, 1000);
        }
        
        async function fetchProgress() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                agents = data.agents;
                messages = data.messages || [];
                progress = data.progress || {};
                
                renderMessages();
                updateProgressBars();
                updateStatus();
            } catch (e) { console.error('刷新失败:', e); }
        }
        
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            
            if (messages.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">💬</div>
                        <div class="text">输入您的需求，Agent团队将协同处理</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '';
            messages.slice(-50).forEach(msg => {
                const agent = agentNames[msg.from_agent] || { name: msg.from_agent, role: '', emoji: '🤖' };
                const typeClass = msg.msg_type === 'broadcast' ? 'broadcast' : msg.msg_type === 'answer' ? 'answer' : 'message';
                
                const div = document.createElement('div');
                div.className = `message ${typeClass}`;
                div.innerHTML = `
                    <div class="meta">
                        <span>${msg.msg_type === 'broadcast' ? '📢 广播' : msg.msg_type === 'answer' ? '💬 回复' : '💬 消息'}</span>
                        <span>${msg.timestamp.split('T')[1].split('.')[0]}</span>
                    </div>
                    <div>
                        <span class="agent-name">${agent.emoji} ${agent.name}</span>
                        <span class="agent-role">${agent.role}</span>
                    </div>
                    <div class="content">${msg.content}</div>
                `;
                container.appendChild(div);
            });
            
            // 滚动到底部
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function renderProgressBars() {
            const grid = document.getElementById('progressGrid');
            grid.innerHTML = '';
            
            agentOrder.forEach(agentId => {
                const agent = agentNames[agentId];
                if (!agent) return;
                
                const div = document.createElement('div');
                div.className = 'progress-item';
                div.id = `progress-${agentId}`;
                div.innerHTML = `
                    <div class="emoji">${agent.emoji}</div>
                    <div class="info">
                        <div class="name">${agent.name}</div>
                        <div class="role">${agent.role}</div>
                        <div class="bar"><div class="bar-fill" style="width: 0%"></div></div>
                    </div>
                    <div class="percent">0%</div>
                `;
                grid.appendChild(div);
            });
        }
        
        function updateProgressBars() {
            let activeCount = 0;
            
            agentOrder.forEach(agentId => {
                const item = document.getElementById(`progress-${agentId}`);
                if (!item) return;
                
                const agentProgress = progress[agentId] || 0;
                const barFill = item.querySelector('.bar-fill');
                const percent = item.querySelector('.percent');
                
                barFill.style.width = agentProgress + '%';
                percent.textContent = agentProgress + '%';
                
                if (agentProgress > 0 && agentProgress < 100) {
                    item.classList.add('active');
                    activeCount++;
                } else {
                    item.classList.remove('active');
                }
                
                if (agentProgress === 100) {
                    barFill.style.background = '#2d5a27';
                } else {
                    barFill.style.background = 'linear-gradient(90deg, #C93832, #006EBD)';
                }
            });
            
            document.getElementById('activeCount').textContent = `${activeCount}/9 活跃`;
        }
        
        function updateStatus() {
            const badge = document.getElementById('statusBadge');
            const processing = Object.values(progress).some(p => p > 0 && p < 100);
            
            if (processing) {
                badge.textContent = '● 处理中...';
                badge.style.color = '#FFC107';
            } else {
                badge.textContent = '● 系统就绪';
                badge.style.color = '#4CAF50';
            }
        }
        
        async function submitTask() {
            if (isProcessing) return;
            
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) { alert('请输入任务内容'); return; }
            
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            input.value = '';
            
            try {
                const response = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
                const data = await response.json();
                
                if (data.status === 'ok') {
                    // 开始轮询进度
                    pollProgress();
                }
            } catch (e) { 
                alert('提交失败'); 
            }
            
            setTimeout(() => {
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            }, 3000);
        }
        
        async function pollProgress() {
            for (let i = 0; i < 30; i++) {
                await new Promise(r => setTimeout(r, 500));
                const response = await fetch('/api/progress');
                const data = await response.json();
                progress = data.progress || {};
                updateProgressBars();
                
                // 检查是否全部完成
                const allDone = Object.values(progress).every(p => p === 0 || p === 100);
                if (allDone && Object.values(progress).some(p => p === 100)) {
                    break;
                }
            }
        }
        
        function quickTask(type) {
            const tasks = {
                '需求分析': '请完成需求分析，输出需求规格说明书',
                '架构设计': '请设计系统架构方案',
                '成本评估': '请评估项目成本和投入',
                '项目排期': '请制定项目计划和里程碑',
                '方案PPT': '请制作方案汇报PPT'
            };
            document.getElementById('taskInput').value = tasks[type];
            submitTask();
        }
        
        async function clearChat() {
            await fetch('/api/clear', {method: 'POST'});
            progress = {};
            renderProgressBars();
        }
        
        // 回车提交
        document.getElementById('taskInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') submitTask();
        });
        
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
    status['messages'] = messages_for_display[-50:]
    status['progress'] = agent_progress.copy()
    return jsonify(status)


@app.route('/api/progress')
def api_progress():
    return jsonify({'progress': agent_progress.copy()})


@app.route('/api/task', methods=['POST'])
def api_task():
    """接收任务并分配给Agent，模拟Agent响应"""
    global agent_progress
    
    data = request.json
    task_desc = data.get('task', '')
    
    # 重置进度
    agent_progress = {aid: 0 for aid in framework.scheduler.agents.keys()}
    
    # 1. 拆解任务
    tasks = framework.decompose_task(task_desc)
    
    # 2. 广播任务通知
    framework.broadcast('nanqiao', f'收到任务：{task_desc}')
    agent_progress['nanqiao'] = 100
    
    # 3. 如果任务没有分配Agent，默认让多个Agent响应
    has_assignee = any(t.assignee for t in tasks)
    if not has_assignee:
        for task in tasks:
            task.assignee = 'caiwei'
    
    # 4. 分配任务
    for task in tasks:
        if task.assignee:
            framework.task_decomposer.assign_tasks([task])
    
    # 动态生成响应
    def generate_response(agent_id, task_content):
        import random
        
        project_keywords = ['系统', '平台', '项目', '方案', '应用']
        project_name = '该项目'
        for kw in project_keywords:
            if kw in task_content:
                project_name = task_content.split(kw)[0][-10:] + kw
                break
        
        responses = {
            'caiwei': [
                f'【需求分析】收到任务：{project_name}。我将采用"先诊断后开方"方法论，首先进行业务调研和干系人访谈，梳理核心需求。预计输出：需求规格说明书、用户故事地图、验收标准清单。',
                f'【需求分析】{project_name}需求分析启动。已识别关键干系人，准备开展需求调研。将输出：业务流程图、用例图、数据字典。',
                f'【需求分析】理解您的需求。{project_name}的核心目标是？我需要了解：1.业务痛点 2.用户画像 3.预期成果。'
            ],
            'zhijin': [
                f'【架构设计】基于{project_name}需求，设计六层架构：接入层→API网关→业务服务层→AI推理层→数据中台→基础设施层。',
                f'【架构设计】已完成{project_name}架构蓝图。核心组件：前端(Vue3)、后端(Spring Cloud)、AI推理(TensorFlow)。',
                f'【架构设计】{project_name}的技术约束是什么？是否需要对接现有系统？我将输出：系统架构图、接口设计文档。'
            ],
            'zhutai': [
                f'【成本评估】{project_name}成本估算：开发成本约120万，运维成本约50万/年。建议采用分期建设策略。',
                f'【成本评估】根据{project_name}规模，推荐配置：应用服务器4台、数据库主从2套。月度成本约8-12万。',
                f'【成本评估】已启动成本分析。需要确认：1.项目周期 2.团队规模 3.是否采购商业软件。'
            ],
            'gongchi': [
                f'【详细设计】{project_name}详细设计启动。将输出：数据库ER图、接口文档（RESTful API）、类图、时序图。',
                f'【详细设计】已完成核心模块设计：用户中心、权限管理、业务引擎、数据看板。',
                f'【详细设计】{project_name}的性能要求是什么？QPS预估？我将据此设计缓存策略。'
            ],
            'yuheng': [
                f'【项目管理】{project_name}项目计划已创建。关键里程碑：需求评审(Week2)、设计评审(Week4)、开发完成(Week12)、上线(Week16)。',
                f'【项目管理】{project_name}进度安排：需求分析5天、架构设计3天、详细设计7天、开发30天、测试15天。',
                f'【项目管理】{project_name}期望上线时间是？团队配置建议：PM1人、架构师1人、开发5人、测试2人。'
            ],
            'chengcai': [
                f'【PPT设计】{project_name}方案PPT框架已准备。大纲：项目背景→需求分析→解决方案→技术架构→实施计划→成本预算。',
                f'【PPT设计】已启动汇报材料设计。风格：电信红主色调，专业商务风。预计20页。交付时间：2天。',
                f'【PPT设计】{project_name}的汇报对象是？技术评审还是管理层？我将调整内容深度。'
            ],
            'zhegui': [
                f'【资源整理】{project_name}相关资源已归档：技术文档12份、案例参考5份、行业报告3份。',
                f'【资源整理】已收集所需资源：需求模板、架构模板、测试用例模板、项目计划模板。',
                f'【资源整理】{project_name}是否有历史项目可参考？我将整理相关资料并建立项目知识库。'
            ],
            'fuyao': [
                f'【总指挥】{project_name}任务已分配。采薇负责需求分析，织锦负责架构设计。预计整体交付周期：4-6周。',
                f'【总指挥】{project_name}启动！关键节点：Week2需求冻结、Week4设计评审、Week12开发完成。请玉衡跟进进度。',
                f'【总指挥】收到任务。{project_name}优先级评定：A级。调配资源：需求组2人、架构组1人、开发组5人。'
            ],
        }
        
        agent_responses = responses.get(agent_id, [f'收到任务，正在处理{project_name}...'])
        return random.choice(agent_responses)
    
    def simulate_response(task_id, agent_id, delay, task_content):
        # 模拟进度：0% → 30% → 60% → 100%
        if agent_id:
            agent_progress[agent_id] = 0
            
            # 阶段1：开始处理 (30%)
            time.sleep(delay * 0.3)
            agent_progress[agent_id] = 30
            
            # 阶段2：处理中 (60%)
            time.sleep(delay * 0.3)
            agent_progress[agent_id] = 60
            
            # 阶段3：完成 (100%)
            time.sleep(delay * 0.4)
            
            if agent_id in framework.scheduler.agents:
                response = generate_response(agent_id, task_content)
                
                framework.send(
                    from_agent=agent_id,
                    to_agents=['nanqiao'],
                    content=response,
                    msg_type=MessageType.ANSWER
                )
                
                framework.scheduler.complete_task(task_id)
            
            agent_progress[agent_id] = 100
    
    # 启动模拟响应线程
    for i, task in enumerate(tasks):
        t = threading.Thread(target=simulate_response, args=(task.id, task.assignee, 2 + i * 1.5, task_desc))
        t.start()
    
    return jsonify({
        'status': 'ok', 
        'tasks': [{'id': t.id, 'desc': t.description, 'assignee': t.assignee} for t in tasks]
    })


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """清空消息"""
    global messages_for_display, agent_progress
    messages_for_display = []
    agent_progress = {}
    framework.bus.message_history.clear()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 多Agent协作平台 V3")
    print("=" * 60)
    print("访问地址: http://120.48.169.242:5001")
    print("功能: 进度条 + 异步处理 + 实时反馈")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
