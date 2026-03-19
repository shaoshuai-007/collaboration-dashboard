#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团智能协作平台 V16.0
"讨论→实施" 全流程闭环 + 群组协作模式
作者：南乔 🌿
日期：2026-03-19
"""

from flask import Flask, render_template, jsonify, request, Response, stream_with_context
import json
import time
import queue
import threading
from datetime import datetime
import sys
import os

# 添加模块路径
sys.path.insert(0, '/root/.openclaw/workspace/modules')

from group_manager import group_manager, GroupManager
from message_persistence import message_persistence, MessagePersistence
from nanqiao_scheduler import NanqiaoScheduler

# 创建Flask应用
app = Flask(__name__,
            template_folder='/root/.openclaw/workspace/templates',
            static_folder='/root/.openclaw/workspace/static')

# 手动添加CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# 初始化调度器
scheduler = NanqiaoScheduler(group_manager, message_persistence)

# SSE订阅者
sse_clients = {}
client_id_counter = 0


# ===== 页面路由 =====

@app.route('/')
def index():
    """主页 - 重定向到群聊"""
    return render_template('group_chat.html')


@app.route('/group')
def group_chat():
    """群聊页面"""
    return render_template('group_chat.html')


# ===== API接口 =====

@app.route('/api/v16/agents', methods=['GET'])
def get_agents():
    """获取所有Agent"""
    agents = group_manager.get_all_agents()
    return jsonify({
        'success': True,
        'agents': agents,
        'total': len(agents)
    })


@app.route('/api/v16/agent/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """获取指定Agent"""
    agent = group_manager.get_agent(agent_id)
    if agent:
        return jsonify({
            'success': True,
            'agent': {
                'agent_id': agent.agent_id,
                'name': agent.name,
                'role': agent.role,
                'emoji': agent.emoji,
                'status': agent.status,
                'current_task': agent.current_task
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Agent不存在'}), 404


@app.route('/api/v16/messages', methods=['GET'])
def get_messages():
    """获取消息列表"""
    limit = int(request.args.get('limit', 50))
    before_seq = request.args.get('before_seq')
    before_seq = int(before_seq) if before_seq else None
    
    messages = group_manager.get_messages(limit=limit, before_seq=before_seq)
    return jsonify({
        'success': True,
        'messages': messages,
        'total': len(messages)
    })


@app.route('/api/v16/messages', methods=['POST'])
def create_message():
    """创建消息"""
    data = request.get_json()
    
    from_type = data.get('from_type', 'user')
    from_id = data.get('from_id', 'shaoshuai')
    content = data.get('content', '')
    mentions = data.get('mentions')
    reply_to = data.get('reply_to')
    
    if not content:
        return jsonify({'success': False, 'error': '消息内容不能为空'}), 400
    
    # 创建消息
    msg = group_manager.create_message(
        from_type=from_type,
        from_id=from_id,
        content=content,
        mentions=mentions,
        reply_to=reply_to
    )
    
    # 保存到数据库
    message_persistence.save_message({
        'msg_id': msg.msg_id,
        'group_id': msg.group_id,
        'from_type': msg.from_type,
        'from_id': msg.from_id,
        'from_name': msg.from_name,
        'from_emoji': msg.from_emoji,
        'content': msg.content,
        'mentions': msg.mentions,
        'reply_to': msg.reply_to,
        'seq': msg.seq,
        'created_at': msg.created_at
    })
    
    # 推送给所有SSE客户端
    push_to_sse_clients({
        'type': 'new_message',
        'message': {
            'msg_id': msg.msg_id,
            'group_id': msg.group_id,
            'from_type': msg.from_type,
            'from_id': msg.from_id,
            'from_name': msg.from_name,
            'from_emoji': msg.from_emoji,
            'content': msg.content,
            'mentions': msg.mentions,
            'reply_to': msg.reply_to,
            'seq': msg.seq,
            'created_at': msg.created_at
        }
    })
    
    # 如果是用户消息，触发南乔调度
    if from_type == 'user':
        # 检查是否是任务调度
        if '@' in content and any(keyword in content for keyword in ['帮我', '做一个', '分析', '设计', '开发']):
            # 异步调度任务
            threading.Thread(target=handle_task_dispatch, args=(content,)).start()
    
    return jsonify({
        'success': True,
        'message': {
            'msg_id': msg.msg_id,
            'content': msg.content,
            'seq': msg.seq
        }
    })


def handle_task_dispatch(content):
    """处理任务调度"""
    try:
        # 使用调度器分析任务
        result = scheduler.dispatch_task(content)
        
        # 推送南乔的响应消息
        msg = result.get('message_obj')
        if msg:
            push_to_sse_clients({
                'type': 'new_message',
                'message': msg
            })
        
        # 推送任务更新
        push_to_sse_clients({
            'type': 'task_update',
            'task': result['task']
        })
        
        print(f"✅ 任务调度完成: {result['task']['task_id']}")
    except Exception as e:
        print(f"❌ 任务调度失败: {e}")


@app.route('/api/v16/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    group_id = request.args.get('group_id', 'jiuxing_main')
    status = request.args.get('status')
    
    tasks = message_persistence.get_tasks(group_id=group_id, status=status)
    return jsonify({
        'success': True,
        'tasks': tasks,
        'total': len(tasks)
    })


@app.route('/api/v16/tasks', methods=['POST'])
def create_task():
    """创建任务"""
    data = request.get_json()
    
    title = data.get('title', '')
    description = data.get('description', '')
    assignee = data.get('assignee')
    
    if not title:
        return jsonify({'success': False, 'error': '任务标题不能为空'}), 400
    
    # 使用调度器创建任务
    result = scheduler.dispatch_task(description or title)
    
    return jsonify({
        'success': True,
        'task': result['task']
    })


@app.route('/api/v16/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取指定任务"""
    tasks = message_persistence.get_tasks()
    task = next((t for t in tasks if t['task_id'] == task_id), None)
    
    if task:
        return jsonify({'success': True, 'task': task})
    else:
        return jsonify({'success': False, 'error': '任务不存在'}), 404


@app.route('/api/v16/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    data = request.get_json()
    
    progress = data.get('progress')
    status = data.get('status')
    
    group_manager.update_task_progress(task_id, progress or 0, status)
    
    # 推送更新
    push_to_sse_clients({
        'type': 'task_update',
        'task_id': task_id,
        'progress': progress,
        'status': status
    })
    
    return jsonify({'success': True})


@app.route('/api/v16/dispatch', methods=['POST'])
def dispatch_task():
    """调度任务"""
    data = request.get_json()
    task_description = data.get('task', '')
    
    if not task_description:
        return jsonify({'success': False, 'error': '任务描述不能为空'}), 400
    
    result = scheduler.dispatch_task(task_description)
    
    return jsonify({
        'success': True,
        'task': result['task'],
        'message': result['message']
    })


@app.route('/api/v16/group/status', methods=['GET'])
def get_group_status():
    """获取群组状态"""
    status = group_manager.get_group_status()
    stats = message_persistence.get_statistics()
    
    return jsonify({
        'success': True,
        'group': status,
        'statistics': stats
    })


# ===== SSE事件流 =====

@app.route('/api/v16/events')
def sse_events():
    """SSE事件流"""
    def event_stream():
        global client_id_counter
        client_id_counter += 1
        client_id = f"client_{client_id_counter}"
        
        # 创建消息队列
        q = queue.Queue()
        sse_clients[client_id] = q
        
        print(f"📡 SSE客户端连接: {client_id}")
        
        try:
            # 发送连接成功消息
            yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\n\n"
            
            # 持续推送消息
            while True:
                try:
                    # 等待消息，超时30秒发送心跳
                    data = q.get(timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    # 发送心跳
                    yield f": heartbeat\n\n"
        except GeneratorExit:
            # 客户端断开
            print(f"📡 SSE客户端断开: {client_id}")
            if client_id in sse_clients:
                del sse_clients[client_id]
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


def push_to_sse_clients(data):
    """推送消息给所有SSE客户端"""
    for client_id, q in list(sse_clients.items()):
        try:
            q.put_nowait(data)
        except:
            pass


# ===== 兼容旧版API =====

@app.route('/api/v15.2/agents', methods=['GET'])
def legacy_get_agents():
    """兼容旧版API"""
    return get_agents()


@app.route('/api/v15.2/tasks', methods=['GET'])
def legacy_get_tasks():
    """兼容旧版API"""
    return get_tasks()


# ===== 测试接口 =====

@app.route('/api/v16/test', methods=['POST'])
def test_message():
    """测试消息"""
    # 模拟南乔发送消息
    msg = group_manager.create_message(
        from_type='agent',
        from_id='nanqiao',
        content='🌿 你好！我是南乔，九星智囊团的Leader。有什么可以帮助你的吗？'
    )
    
    message_persistence.save_message({
        'msg_id': msg.msg_id,
        'group_id': msg.group_id,
        'from_type': msg.from_type,
        'from_id': msg.from_id,
        'from_name': msg.from_name,
        'from_emoji': msg.from_emoji,
        'content': msg.content,
        'mentions': msg.mentions,
        'reply_to': msg.reply_to,
        'seq': msg.seq,
        'created_at': msg.created_at
    })
    
    push_to_sse_clients({
        'type': 'new_message',
        'message': {
            'msg_id': msg.msg_id,
            'group_id': msg.group_id,
            'from_type': msg.from_type,
            'from_id': msg.from_id,
            'from_name': msg.from_name,
            'from_emoji': msg.from_emoji,
            'content': msg.content,
            'mentions': msg.mentions,
            'reply_to': msg.reply_to,
            'seq': msg.seq,
            'created_at': msg.created_at
        }
    })
    
    return jsonify({'success': True, 'message': '测试消息已发送'})


# ===== 启动 =====

if __name__ == '__main__':
    print("🌿 九星智囊团智能协作平台 V16.0 启动中...")
    print("📍 访问地址: http://localhost:5001/group")
    print("📡 API文档: /api/v16/")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
