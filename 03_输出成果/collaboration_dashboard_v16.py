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
sys.path.insert(0, '/root/.openclaw/workspace/03_输出成果')

from group_manager import group_manager, GroupManager
from message_persistence import message_persistence, MessagePersistence
from nanqiao_scheduler import NanqiaoScheduler
from intent_scheduler import IntelligentScheduler, TASK_TYPES, TaskCategory

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

# 初始化V15智能调度器（四层意图识别）
intent_scheduler = IntelligentScheduler()
# 初始化智能意图识别调度器
intent_scheduler = IntelligentScheduler()

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
    
    # 如果是用户消息，触发南乔智能调度
    if from_type == 'user':
        # 扩大任务关键词识别范围
        task_keywords = ['帮我', '做一个', '做一', '分析', '设计', '开发', '写', '做', 
                       '需求', '方案', '架构', 'PPT', '文档', '接口', '数据库',
                       '项目', '任务', '评估', '报价', '售前', '技术', '实现',
                       '生成', '创建', '制作', '整理', '规划', '优化', '改进']
        
        # 检查是否是任务请求
        is_task = any(keyword in content for keyword in task_keywords)
        
        # 如果是任务，触发调度
        if is_task:
            print(f"📋 检测到任务请求: {content[:50]}...")
            threading.Thread(target=handle_task_dispatch, args=(content,)).start()
        else:
            # 非任务消息，南乔自动回复
            auto_reply = scheduler.get_auto_reply(content)
            if auto_reply:
                reply_msg = group_manager.create_message(
                    from_type='agent',
                    from_id='nanqiao',
                    content=auto_reply
                )
                message_persistence.save_message({
                    'msg_id': reply_msg.msg_id,
                    'group_id': reply_msg.group_id,
                    'from_type': reply_msg.from_type,
                    'from_id': reply_msg.from_id,
                    'from_name': reply_msg.from_name,
                    'from_emoji': reply_msg.from_emoji,
                    'content': reply_msg.content,
                    'mentions': reply_msg.mentions,
                    'reply_to': reply_msg.reply_to,
                    'seq': reply_msg.seq,
                    'created_at': reply_msg.created_at
                })
                push_to_sse_clients({
                    'type': 'new_message',
                    'message': {
                        'msg_id': reply_msg.msg_id,
                        'group_id': reply_msg.group_id,
                        'from_type': reply_msg.from_type,
                        'from_id': reply_msg.from_id,
                        'from_name': reply_msg.from_name,
                        'from_emoji': reply_msg.from_emoji,
                        'content': reply_msg.content,
                        'mentions': reply_msg.mentions,
                        'reply_to': reply_msg.reply_to,
                        'seq': reply_msg.seq,
                        'created_at': reply_msg.created_at
                    }
                })
    
    return jsonify({
        'success': True,
        'message': {
            'msg_id': msg.msg_id,
            'content': msg.content,
            'seq': msg.seq
        }
    })


def handle_task_dispatch(content):
    """处理任务调度 - 使用完整四层意图识别"""
    try:
        # 使用智能意图识别（IntelligentScheduler的process方法）
        result = intent_scheduler.process(content)
        
        print(f"🎯 意图识别结果: {result}")
        
        # 根据识别结果进行调度
        if result.get('task_code'):
            task_code = result['task_code']
            task_name = result.get('task_name', '')
            confidence = result.get('confidence', 0)
            
            # 获取任务信息
            task_info = TASK_TYPES.get(task_code)
            
            if task_info:
                # 创建任务消息
                dispatch_msg = f"🌿 收到任务请求：{task_name}\n\n"
                dispatch_msg += f"📋 任务类型：{task_code}\n"
                dispatch_msg += f"📝 任务描述：{task_info.description}\n"
                dispatch_msg += f"📄 产出物：{task_info.output_template}\n"
                dispatch_msg += f"🎯 置信度：{confidence:.0%}\n\n"
                
                # 简单调度 - 直接分配给对应Agent
                agent_map = {
                    'REQ': '采薇', 'DES': '织锦', 'DEV': '天工',
                    'PM': '玉衡', 'TEST': '测试', 'DEPLOY': '部署'
                }
                prefix = task_code.split('-')[0] if '-' in task_code else ''
                assigned_agent = agent_map.get(prefix, '南乔')
                
                dispatch_msg += f"👤 分配：@{assigned_agent} 请开始工作\n"
                
                # 创建南乔的消息
                msg = group_manager.create_message(
                    from_type='agent',
                    from_id='nanqiao',
                    content=dispatch_msg
                )
                
                # 保存并推送
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
                
                print(f"✅ 任务调度完成: {task_code}")
        else:
            # 未识别到任务，使用简单回复
            msg = group_manager.create_message(
                from_type='agent',
                from_id='nanqiao',
                content=f"🌿 收到消息：{content[:50]}...\n\n暂未识别为具体任务，如有需要请详细说明需求～"
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
                
    except Exception as e:
        print(f"❌ 任务调度失败: {e}")
        import traceback
        traceback.print_exc()


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
