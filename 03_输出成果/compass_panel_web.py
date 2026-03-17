#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程 - 实时协作面板 (Web版)
Flask Application

Author: 南乔
Date: 2026-03-13
"""

from flask import Flask, render_template_string, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# 配色方案
COLORS = {
    'primary': '#C93832',
    'secondary': '#006EBD',
    'neutral': '#595959',
}

# Agent数据
AGENTS = [
    {'name': '采薇', 'role': '需求分析专家', 'emoji': '🌸', 'status': 'done'},
    {'name': '织锦', 'role': '架构设计师', 'emoji': '🧵', 'status': 'done'},
    {'name': '筑台', 'role': '售前工程师', 'emoji': '🏗️', 'status': 'done'},
    {'name': '呈彩', 'role': '方案PPT设计师', 'emoji': '🎨', 'status': 'pending'},
    {'name': '工尺', 'role': '详细设计师', 'emoji': '📐', 'status': 'pending'},
    {'name': '玉衡', 'role': '项目经理', 'emoji': '⚖️', 'status': 'pending'},
    {'name': '折桂', 'role': '资源管家', 'emoji': '📚', 'status': 'done'},
    {'name': '扶摇', 'role': '总指挥', 'emoji': '🌀', 'status': 'done'},
    {'name': '南乔', 'role': '主控Agent', 'emoji': '🌿', 'status': 'active'},
]

# 消息数据
MESSAGES = [
    {'agent': '采薇', 'emoji': '🌸', 'content': '采用"先诊断后开方"方法论，完成三层根因分析。核心需求：准确率75%→90%、响应3s→<1s、500+标签维度。', 'time': '21:41'},
    {'agent': '织锦', 'emoji': '🧵', 'content': '评审采薇产出：方法论正确✅ 需求可实现但具挑战🔴 准确率目标建议分阶段达成(80%→85%→90%)。', 'time': '21:45'},
    {'agent': '扶摇', 'emoji': '🌀', 'content': '反馈合理，批准调整：工期修正为7-8月、数据质量评估、降级机制、特征注册中心纳入二期。', 'time': '21:41'},
    {'agent': '筑台', 'emoji': '🏗️', 'content': '成本更新：低配445万/年(+23.6%)、高配700万/年(+20.7%)。双模型切换：文心主+通义备。', 'time': '21:43'},
    {'agent': '织锦', 'emoji': '🧵', 'content': '架构方案：六层架构（接入→网关→业务→AI推理→特征工程→数据存储）。核心模块：配案决策引擎+特征注册中心+降级策略。', 'time': '21:50'},
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 实时协作面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        
        .header {
            text-align: center;
            padding: 24px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            margin-bottom: 24px;
        }
        .header h1 {
            font-size: 28px;
            color: #C93832;
            margin-bottom: 8px;
        }
        .header p { color: #888; font-size: 14px; }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .agent-card {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #595959;
            transition: all 0.3s;
        }
        .agent-card:hover { transform: translateY(-2px); }
        .agent-card.done { border-left-color: #2d5a27; }
        .agent-card.active { border-left-color: #C93832; background: rgba(201,56,50,0.15); }
        .agent-card.pending { opacity: 0.6; }
        
        .agent-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
        .agent-role { font-size: 12px; color: #888; margin-bottom: 8px; }
        .agent-status {
            font-size: 11px;
            padding: 4px 12px;
            border-radius: 4px;
            display: inline-block;
        }
        .status-done { background: #2d5a27; }
        .status-active { background: #C93832; animation: pulse 2s infinite; }
        .status-pending { background: #595959; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .chat-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            max-height: 400px;
            overflow-y: auto;
        }
        .chat-panel::-webkit-scrollbar { width: 6px; }
        .chat-panel::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        .chat-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }
        
        .message {
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 12px;
            background: rgba(0,110,189,0.3);
        }
        .message .from { font-size: 11px; color: #888; margin-bottom: 4px; }
        .message .content { font-size: 14px; line-height: 1.6; }
        .message .time { font-size: 10px; color: #666; text-align: right; margin-top: 4px; }
        
        .stats-panel {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
        }
        
        .progress-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 12px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #C93832, #006EBD);
            width: 70%;
            transition: width 0.5s;
        }
        
        .stats-row {
            display: flex;
            gap: 24px;
            font-size: 12px;
            color: #888;
        }
        .stat-item { display: flex; align-items: center; gap: 6px; }
        
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .refresh-btn:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧭 指南针工程 - 实时协作面板</h1>
            <p>湖北电渠AI智能配案系统升级 | 9 Agent协作中</p>
        </div>
        
        <div class="agents-grid">
            {% for agent in agents %}
            <div class="agent-card {{ agent.status }}">
                <div class="agent-name">{{ agent.emoji }} {{ agent.name }}</div>
                <div class="agent-role">{{ agent.role }}</div>
                <span class="agent-status status-{{ agent.status }}">
                    {% if agent.status == 'done' %}✅ 已完成
                    {% elif agent.status == 'active' %}🔄 进行中
                    {% else %}⏳ 等待中{% endif %}
                </span>
            </div>
            {% endfor %}
        </div>
        
        <h3 style="margin-bottom: 12px; color: #888;">💬 实时对话流</h3>
        <div class="chat-panel">
            {% for msg in messages %}
            <div class="message">
                <div class="from">{{ msg.emoji }} {{ msg.agent }}</div>
                <div class="content">{{ msg.content }}</div>
                <div class="time">{{ msg.time }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="stats-panel">
            <div style="margin-bottom: 8px; color: #888;">📊 项目进度</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress"></div>
            </div>
            <div class="stats-row">
                <div class="stat-item">💬 消息: <strong>{{ messages|length }}</strong></div>
                <div class="stat-item">⏱️ 耗时: <strong>12分钟</strong></div>
                <div class="stat-item">🎯 活跃Agent: <strong>{{ agents|selectattr('status', 'ne', 'pending')|list|length }}/{{ agents|length }}</strong></div>
                <div class="stat-item">📍 当前阶段: <strong>架构评审</strong></div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 刷新状态</button>
    
    <script>
        // 自动刷新（每30秒）
        // setTimeout(() => location.reload(), 30000);
        
        // 模拟进度更新
        let progress = 70;
        setInterval(() => {
            if (progress < 100) {
                progress += 1;
                document.getElementById('progress').style.width = progress + '%';
            }
        }, 5000);
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, agents=AGENTS, messages=MESSAGES)


@app.route('/api/agents')
def api_agents():
    return jsonify(AGENTS)


@app.route('/api/messages')
def api_messages():
    return jsonify(MESSAGES)


if __name__ == '__main__':
    print("🧭 指南针工程 - 实时协作面板")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("API接口:")
    print("  - http://localhost:5000/api/agents")
    print("  - http://localhost:5000/api/messages")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
