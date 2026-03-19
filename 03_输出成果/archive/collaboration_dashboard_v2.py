#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 - Web界面集成版 V2
支持真实任务输入和Agent响应模拟

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


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 多Agent协作平台 V2</title>
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
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 26px; color: #C93832; margin-bottom: 6px; }
        .header p { color: #888; font-size: 13px; }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 20px;
        }
        @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
        
        .left-panel { display: flex; flex-direction: column; gap: 20px; }
        
        /* 任务输入区 */
        .task-input-panel {
            background: rgba(0,110,189,0.15);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid rgba(0,110,189,0.3);
        }
        .task-input-panel h3 { font-size: 14px; margin-bottom: 12px; color: #006EBD; }
        .task-input-row { display: flex; gap: 10px; }
        .task-input-row input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 14px;
        }
        .task-input-row input::placeholder { color: #888; }
        .task-input-row button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            color: white;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .task-input-row button:hover { transform: scale(1.02); }
        
        /* Agent卡片 */
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 10px;
        }
        .agent-card {
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 12px;
            border-left: 3px solid #595959;
            transition: all 0.3s;
        }
        .agent-card:hover { transform: translateY(-2px); }
        .agent-card.speaking { border-left-color: #C93832; background: rgba(201,56,50,0.15); animation: pulse 1.5s infinite; }
        .agent-card.active { border-left-color: #006EBD; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .agent-name { font-size: 13px; font-weight: 600; margin-bottom: 3px; }
        .agent-role { font-size: 10px; color: #888; margin-bottom: 5px; }
        .agent-status {
            font-size: 9px;
            padding: 2px 6px;
            border-radius: 3px;
            display: inline-block;
        }
        .status-idle { background: #595959; }
        .status-speaking { background: #C93832; }
        .status-working { background: #006EBD; }
        .priority-badge { font-size: 9px; background: rgba(255,255,255,0.15); padding: 1px 5px; border-radius: 2px; margin-left: 4px; }
        
        /* 对话面板 */
        .chat-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 16px;
            flex: 1;
            min-height: 350px;
            display: flex;
            flex-direction: column;
        }
        .chat-header { font-size: 13px; color: #888; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .chat-messages { flex: 1; overflow-y: auto; padding-right: 6px; }
        
        .message {
            margin-bottom: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            background: rgba(0,110,189,0.2);
        }
        .message.broadcast { background: rgba(201,56,50,0.2); border-left: 2px solid #C93832; }
        .message.task { background: rgba(45,90,39,0.2); border-left: 2px solid #2d5a27; }
        .message.answer { background: rgba(0,110,189,0.25); }
        .message .meta { font-size: 10px; color: #888; margin-bottom: 3px; display: flex; justify-content: space-between; }
        .message .content { font-size: 12px; line-height: 1.5; }
        .message .from { color: #C93832; font-weight: 600; }
        
        /* 右侧面板 */
        .right-panel {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .panel-section h3 { font-size: 13px; color: #888; margin-bottom: 10px; }
        
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .stat-box { background: rgba(0,0,0,0.2); border-radius: 8px; padding: 10px; text-align: center; }
        .stat-value { font-size: 22px; font-weight: bold; color: #C93832; }
        .stat-label { font-size: 10px; color: #888; }
        
        .control-btn {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            margin-bottom: 6px;
            transition: all 0.2s;
        }
        .control-btn:hover { transform: scale(1.01); }
        .btn-primary { background: linear-gradient(135deg, #C93832, #006EBD); color: white; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: white; }
        
        .event-log {
            font-size: 10px;
            color: #888;
            max-height: 120px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            padding: 8px;
        }
        
        .progress-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; margin-top: 10px; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #C93832, #006EBD); transition: width 0.5s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧭 指南针工程 - 多Agent协作平台</h1>
            <p>输入任务 → 自动分配Agent → 实时协作响应</p>
        </div>
        
        <div class="main-grid">
            <div class="left-panel">
                <!-- 任务输入区 -->
                <div class="task-input-panel">
                    <h3>📝 输入您的需求/任务</h3>
                    <div class="task-input-row">
                        <input type="text" id="taskInput" placeholder="例如：请完成湖北电渠AI智能配案系统的需求分析...">
                        <button onclick="submitTask()">🚀 提交任务</button>
                    </div>
                </div>
                
                <!-- Agent状态 -->
                <div class="agents-grid" id="agentsGrid"></div>
                
                <!-- 对话面板 -->
                <div class="chat-panel">
                    <div class="chat-header">💬 协作对话流 (共 <span id="msgCount">0</span> 条消息)</div>
                    <div class="chat-messages" id="chatMessages"></div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="panel-section">
                    <h3>📊 协作状态</h3>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-value" id="agentCount">9</div>
                            <div class="stat-label">Agent</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" id="taskCount">0</div>
                            <div class="stat-label">进行中</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>🎮 快捷操作</h3>
                    <button class="control-btn btn-primary" onclick="quickTask('需求分析')">📋 发起需求分析</button>
                    <button class="control-btn btn-secondary" onclick="quickTask('架构设计')">🏗️ 发起架构设计</button>
                    <button class="control-btn btn-secondary" onclick="quickTask('成本评估')">💰 发起成本评估</button>
                    <button class="control-btn btn-secondary" onclick="clearMessages()">🗑️ 清空对话</button>
                </div>
                
                <div class="panel-section">
                    <h3>📜 事件日志</h3>
                    <div class="event-log" id="eventLog"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let agents = {};
        let messages = [];
        
        // Agent ID -> 中文名和角色映射
        const agentNames = {
            'nanqiao': '🌿 南乔(主控Agent)',
            'caiwei': '🌸 采薇(需求分析专家)',
            'zhijin': '🧵 织锦(架构设计师)',
            'zhutai': '🏗️ 筑台(售前工程师)',
            'gongchi': '📐 工尺(详细设计师)',
            'yuheng': '⚖️ 玉衡(项目经理)',
            'chengcai': '🎨 呈彩(PPT设计师)',
            'zhegui': '📚 折桂(资源管家)',
            'fuyao': '🌀 扶摇(总指挥)'
        };
        
        function getAgentDisplayName(agentId) {
            return agentNames[agentId] || agentId;
        }
        
        function init() {
            refreshStatus();
            setInterval(refreshStatus, 2000);
        }
        
        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                agents = data.agents;
                messages = data.messages || [];
                renderAgents();
                renderMessages();
                updateStats(data);
            } catch (e) { console.error('刷新失败:', e); }
        }
        
        function renderAgents() {
            const grid = document.getElementById('agentsGrid');
            grid.innerHTML = '';
            const sorted = Object.values(agents).sort((a, b) => b.speak_priority - a.speak_priority);
            sorted.forEach(agent => {
                const hasTask = agent.current_task !== null;
                const card = document.createElement('div');
                card.className = `agent-card ${hasTask ? 'active' : ''}`;
                card.innerHTML = `
                    <div class="agent-name">${agent.emoji} ${agent.name}<span class="priority-badge">P${agent.speak_priority}</span></div>
                    <div class="agent-role">${agent.role}</div>
                    <span class="agent-status ${hasTask ? 'status-working' : 'status-idle'}">
                        ${hasTask ? '💼 工作中' : '💤 空闲'}
                    </span>
                `;
                grid.appendChild(card);
            });
        }
        
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            messages.slice(-30).forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.msg_type}`;
                // 转换to_agents为中文名
                const toNames = msg.to_agents.map(id => getAgentDisplayName(id).split('(')[0]);
                const toStr = msg.to_agents.length > 5 ? '全体' : toNames.join(', ');
                div.innerHTML = `
                    <div class="meta">
                        <span>${msg.msg_type === 'broadcast' ? '📢 广播' : msg.msg_type === 'task' ? '📋 任务' : msg.msg_type === 'answer' ? '💬 回复' : '💬 消息'}</span>
                        <span>${msg.timestamp.split('T')[1].split('.')[0]}</span>
                    </div>
                    <div class="content"><span class="from">${getAgentDisplayName(msg.from_agent)}</span> → ${toStr}: ${msg.content}</div>
                `;
                container.appendChild(div);
            });
            container.scrollTop = container.scrollHeight;
            document.getElementById('msgCount').textContent = messages.length;
        }
        
        function updateStats(data) {
            document.getElementById('agentCount').textContent = Object.keys(agents).length;
            document.getElementById('taskCount').textContent = Object.keys(data.active_tasks || {}).length;
            const progress = Math.min((messages.length / 15) * 100, 100);
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        async function submitTask() {
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) { alert('请输入任务内容'); return; }
            
            try {
                const response = await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
                const data = await response.json();
                addEvent('任务提交: ' + content.substring(0, 20) + '...');
                input.value = '';
            } catch (e) { alert('提交失败'); }
        }
        
        async function quickTask(type) {
            const tasks = {
                '需求分析': '请完成项目的需求分析文档',
                '架构设计': '请输出系统架构设计方案',
                '成本评估': '请评估项目成本'
            };
            document.getElementById('taskInput').value = tasks[type];
            submitTask();
        }
        
        function clearMessages() {
            fetch('/api/clear', {method: 'POST'});
            addEvent('对话已清空');
        }
        
        function addEvent(text) {
            const log = document.getElementById('eventLog');
            const time = new Date().toLocaleTimeString('zh-CN');
            log.innerHTML = `<div>[${time}] ${text}</div>` + log.innerHTML;
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
    return jsonify(status)


@app.route('/api/task', methods=['POST'])
def api_task():
    """接收任务并分配给Agent，模拟Agent响应"""
    data = request.json
    task_desc = data.get('task', '')
    
    # 1. 拆解任务
    tasks = framework.decompose_task(task_desc)
    
    # 2. 广播任务通知
    framework.broadcast('nanqiao', f'收到任务：{task_desc[:50]}...')
    
    # 3. 如果任务没有分配Agent，默认让多个Agent响应
    has_assignee = any(t.assignee for t in tasks)
    if not has_assignee:
        # 默认分配给采薇进行需求分析
        for task in tasks:
            task.assignee = 'caiwei'
    
    # 4. 分配任务并模拟Agent响应
    for task in tasks:
        if task.assignee:
            framework.task_decomposer.assign_tasks([task])
    
    # 动态生成响应（根据任务内容）
    def generate_response(agent_id, task_content):
        """根据任务内容生成动态响应"""
        import random
        
        # 提取项目名称或关键词
        project_keywords = ['系统', '平台', '项目', '方案', '应用']
        project_name = '该项目'
        for kw in project_keywords:
            if kw in task_content:
                project_name = task_content.split(kw)[0][-10:] + kw
                break
        
        responses = {
            'caiwei': [
                f'【需求分析】收到任务：{project_name}。我将采用"先诊断后开方"方法论，首先进行业务调研和干系人访谈，梳理核心需求。预计输出：需求规格说明书、用户故事地图、验收标准清单。完成时间：约30分钟。',
                f'【需求分析】{project_name}需求分析启动。已识别关键干系人，准备开展需求调研。将输出：业务流程图、用例图、数据字典。请确认是否有紧急需求？',
                f'【需求分析】理解您的需求。{project_name}的核心目标是？我需要了解：1.业务痛点 2.用户画像 3.预期成果。请补充背景信息。'
            ],
            'zhijin': [
                f'【架构设计】基于{project_name}需求，设计六层架构：接入层→API网关→业务服务层→AI推理层→数据中台→基础设施层。技术选型建议：微服务架构 + Kubernetes + PostgreSQL。',
                f'【架构设计】已完成{project_name}架构蓝图。核心组件：前端(Vue3)、后端(Spring Cloud)、AI推理(TensorFlow)、存储(分布式数据库)。预计开发周期：3个月。',
                f'【架构设计】收到。{project_name}的技术约束是什么？是否需要对接现有系统？我将输出：系统架构图、接口设计文档、部署方案。'
            ],
            'zhutai': [
                f'【成本评估】{project_name}成本估算：开发成本约120万（含人力、测试），运维成本约50万/年，基础设施约30万/年。总计：约200万首年投入。建议采用分期建设策略。',
                f'【成本评估】根据{project_name}规模，推荐配置：应用服务器4台、数据库主从2套、AI推理卡2张。月度成本约8-12万。ROI分析报告待输出。',
                f'【成本评估】已启动成本分析。需要确认：1.项目周期 2.团队规模 3.是否采购商业软件。我将输出详细预算表。'
            ],
            'gongchi': [
                f'【详细设计】{project_name}详细设计启动。将输出：数据库ER图（约50张表）、接口文档（RESTful API约100个）、类图、时序图。设计原则：高内聚低耦合。',
                f'【详细设计】已完成{project_name}核心模块设计：用户中心、权限管理、业务引擎、数据看板。技术栈：Spring Boot + MyBatis + Redis。',
                f'【详细设计】收到需求。{project_name}的性能要求是什么？QPS预估？我将据此设计缓存策略和数据库分片方案。'
            ],
            'yuheng': [
                f'【项目管理】{project_name}项目计划已创建。关键里程碑：需求评审(Week2)、设计评审(Week4)、开发完成(Week12)、UAT测试(Week14)、上线(Week16)。风险项已识别3条。',
                f'【项目管理】{project_name}进度安排：需求分析5天、架构设计3天、详细设计7天、开发30天、测试15天。RACI矩阵已定义，请确认各角色分工。',
                f'【项目管理】收到任务。{project_name}期望上线时间是？团队配置建议：PM1人、架构师1人、开发5人、测试2人。我将输出甘特图和里程碑计划。'
            ],
            'chengcai': [
                f'【PPT设计】{project_name}方案PPT框架已准备。大纲：项目背景→需求分析→解决方案→技术架构→实施计划→成本预算→预期收益。待设计评审后开始制作。',
                f'【PPT设计】已启动{project_name}汇报材料设计。风格：电信红主色调，专业商务风。预计20页，包含架构图、流程图、数据图表。交付时间：2天。',
                f'【PPT设计】收到。{project_name}的汇报对象是？技术评审还是管理层？我将调整内容深度和呈现方式。'
            ],
            'zhegui': [
                f'【资源整理】{project_name}相关资源已归档：技术文档12份、案例参考5份、行业报告3份。已上传知识库，可供团队查阅。',
                f'【资源整理】已收集{project_name}所需资源：需求模板、架构模板、测试用例模板、项目计划模板。位于共享目录：/docs/templates/',
                f'【资源整理】收到任务。{project_name}是否有历史项目可参考？我将整理相关资料并建立项目知识库。'
            ],
            'fuyao': [
                f'【总指挥】{project_name}任务已分配。采薇负责需求分析，织锦负责架构设计。各Agent按优先级协作，有问题及时上报。预计整体交付周期：4-6周。',
                f'【总指挥】{project_name}启动！关键节点：Week2需求冻结、Week4设计评审、Week12开发完成。请玉衡跟进进度，各Agent配合协作。',
                f'【总指挥】收到任务。{project_name}优先级评定：A级。调配资源：需求组2人、架构组1人、开发组5人。按标准流程执行，每周汇报进度。'
            ],
        }
        
        agent_responses = responses.get(agent_id, [f'收到任务，正在处理{project_name}...'])
        return random.choice(agent_responses)
    
    def simulate_response(task_id, agent_id, delay, task_content):
        time.sleep(delay)
        if agent_id and agent_id in framework.scheduler.agents:
            response = generate_response(agent_id, task_content)
            
            framework.send(
                from_agent=agent_id,
                to_agents=['nanqiao'],
                content=response,
                msg_type=MessageType.ANSWER
            )
            
            # 完成任务
            framework.scheduler.complete_task(task_id)
    
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
    global messages_for_display
    messages_for_display = []
    framework.bus.message_history.clear()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 多Agent协作平台 V2")
    print("=" * 60)
    print("访问地址: http://120.48.169.242:5001")
    print("功能: 输入任务 → 自动分配 → Agent响应")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
