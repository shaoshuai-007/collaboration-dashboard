# -*- coding: utf-8 -*-
"""
task_api.py - 任务调度API (Flask Blueprint)
基于工尺的API设计实现
"""

import json
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, Response, stream_with_context
from datetime import datetime
import time
import threading

from task_store import TaskStatus, AgentStatus, get_store
from task_scheduler import (
    TaskScheduler, get_scheduler,
    TaskNotFoundError, AgentNotFoundError, 
    InvalidStatusError, AgentNotAvailableError
)


# 创建Blueprint
task_bp = Blueprint('tasks', __name__, url_prefix='/api/v15.2')

# 获取调度器和存储实例
scheduler = get_scheduler()
store = get_store()


# ==================== 任务API ====================

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """
    创建任务
    
    Request Body:
        {
            "title": "任务标题",
            "description": "任务描述",
            "agent": "agent_id",  // 可选，指定Agent
            "metadata": {}        // 可选，元数据
        }
    
    Response:
        {
            "success": true,
            "task_id": "task_xxx"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON"
            }), 400
        
        task_id = scheduler.create_task(data)
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "任务创建成功"
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except AgentNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except AgentNotAvailableError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """
    获取任务列表
    
    Query Params:
        status: 按状态筛选 (pending/assigned/running/completed/failed/cancelled)
        limit: 返回数量限制
    
    Response:
        {
            "success": true,
            "tasks": [...],
            "total": 10
        }
    """
    try:
        status_filter = request.args.get('status')
        limit = request.args.get('limit', type=int)
        
        status = None
        if status_filter:
            try:
                status = TaskStatus(status_filter)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": f"无效的状态值: {status_filter}"
                }), 400
        
        tasks = store.get_all_tasks(status=status)
        
        if limit:
            tasks = tasks[:limit]
        
        return jsonify({
            "success": True,
            "tasks": [t.to_dict() for t in tasks],
            "total": len(tasks)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """
    查询任务状态
    
    Response:
        {
            "success": true,
            "task": {...}
        }
    """
    try:
        task = scheduler.get_task_status(task_id)
        
        if not task:
            return jsonify({
                "success": False,
                "error": f"任务不存在: {task_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "task": task
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/assign', methods=['POST'])
def assign_task(task_id: str):
    """
    分配Agent到任务
    
    Request Body:
        {
            "agent_id": "agent_xxx"
        }
    
    或者自动分配:
        {
            "auto": true
        }
    """
    try:
        data = request.get_json() or {}
        agent_id = data.get('agent_id')
        auto = data.get('auto', False)
        
        if auto:
            # 自动分配
            assigned_agent = scheduler.auto_assign_task(task_id)
            if not assigned_agent:
                return jsonify({
                    "success": False,
                    "error": "没有可用的Agent"
                }), 409
            
            return jsonify({
                "success": True,
                "agent_id": assigned_agent,
                "message": "Agent已自动分配"
            })
        else:
            # 手动分配
            if not agent_id:
                return jsonify({
                    "success": False,
                    "error": "缺少 agent_id 参数"
                }), 400
            
            scheduler.assign_agent(task_id, agent_id)
            
            return jsonify({
                "success": True,
                "agent_id": agent_id,
                "message": "Agent已分配"
            })
            
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except AgentNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except AgentNotAvailableError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except InvalidStatusError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/start', methods=['POST'])
def start_task(task_id: str):
    """
    启动任务
    """
    try:
        scheduler.start_task(task_id)
        
        return jsonify({
            "success": True,
            "message": "任务已启动"
        })
        
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except InvalidStatusError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 409
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/progress', methods=['PUT'])
def update_progress(task_id: str):
    """
    更新任务进度
    
    Request Body:
        {
            "progress": 50,
            "message": "进度消息"
        }
    """
    try:
        data = request.get_json()
        if not data or 'progress' not in data:
            return jsonify({
                "success": False,
                "error": "缺少 progress 参数"
            }), 400
        
        progress = data['progress']
        message = data.get('message', '')
        
        scheduler.update_progress(task_id, progress, message)
        
        return jsonify({
            "success": True,
            "progress": progress,
            "message": "进度已更新"
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id: str):
    """
    完成任务
    
    Request Body:
        {
            "output": { ... }  // 任务产出
        }
    """
    try:
        data = request.get_json() or {}
        output = data.get('output')
        
        scheduler.complete_task(task_id, output)
        
        return jsonify({
            "success": True,
            "message": "任务已完成"
        })
        
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/fail', methods=['POST'])
def fail_task(task_id: str):
    """
    标记任务失败
    
    Request Body:
        {
            "error": "错误信息"
        }
    """
    try:
        data = request.get_json() or {}
        error_message = data.get('error', '未知错误')
        
        scheduler.fail_task(task_id, error_message)
        
        return jsonify({
            "success": True,
            "message": "任务已标记为失败"
        })
        
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id: str):
    """
    取消任务
    
    Request Body:
        {
            "reason": "取消原因"
        }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        scheduler.cancel_task(task_id, reason)
        
        return jsonify({
            "success": True,
            "message": "任务已取消"
        })
        
    except TaskNotFoundError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/output', methods=['GET'])
def get_task_output(task_id: str):
    """
    获取任务产出
    
    Response:
        {
            "success": true,
            "output": {...}
        }
    """
    try:
        task = store.get_task(task_id)
        
        if not task:
            return jsonify({
                "success": False,
                "error": f"任务不存在: {task_id}"
            }), 404
        
        if task.status != TaskStatus.COMPLETED:
            return jsonify({
                "success": False,
                "error": f"任务状态为 {task.status.value}，尚未完成"
            }), 400
        
        return jsonify({
            "success": True,
            "output": task.output
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/logs', methods=['GET'])
def get_task_logs(task_id: str):
    """
    获取任务日志
    
    Query Params:
        limit: 返回条数限制
    
    Response:
        {
            "success": true,
            "logs": [...]
        }
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        
        task = store.get_task(task_id)
        if not task:
            return jsonify({
                "success": False,
                "error": f"任务不存在: {task_id}"
            }), 404
        
        logs = store.get_task_logs(task_id, limit=limit)
        
        return jsonify({
            "success": True,
            "logs": [log.to_dict() for log in logs]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/tasks/<task_id>/logs/stream', methods=['GET'])
def stream_task_logs(task_id: str):
    """
    SSE实时日志流
    
    Server-Sent Events endpoint for real-time log streaming.
    Client connects and receives log updates as they happen.
    """
    try:
        task = store.get_task(task_id)
        if not task:
            return jsonify({
                "success": False,
                "error": f"任务不存在: {task_id}"
            }), 404
        
        def generate():
            """SSE事件生成器"""
            last_index = 0
            max_idle_time = 300  # 最大空闲时间（秒）
            idle_time = 0
            
            while True:
                # 获取新日志
                logs = store.get_task_logs(task_id, limit=1000)
                
                # 发送新日志
                if len(logs) > last_index:
                    for log in logs[last_index:]:
                        data = json.dumps(log.to_dict(), ensure_ascii=False)
                        yield f"data: {data}\n\n"
                    last_index = len(logs)
                    idle_time = 0
                else:
                    idle_time += 1
                
                # 检查任务是否已完成
                current_task = store.get_task(task_id)
                if current_task and current_task.status in (
                    TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED
                ):
                    # 发送结束事件
                    yield f"event: done\ndata: {current_task.status.value}\n\n"
                    break
                
                # 超时检查
                if idle_time >= max_idle_time:
                    yield f"event: timeout\ndata: 连接超时\n\n"
                    break
                
                # 心跳
                if idle_time % 30 == 0 and idle_time > 0:
                    yield f": heartbeat\n\n"
                
                time.sleep(1)
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


# ==================== Agent API ====================

@task_bp.route('/agents', methods=['GET'])
def list_agents():
    """
    获取Agent状态列表
    
    Query Params:
        status: 按状态筛选 (online/busy/offline/error)
    
    Response:
        {
            "success": true,
            "agents": [...]
        }
    """
    try:
        status_filter = request.args.get('status')
        
        status = None
        if status_filter:
            try:
                status = AgentStatus(status_filter)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": f"无效的状态值: {status_filter}"
                }), 400
        
        agents = store.get_all_agents(status=status)
        
        return jsonify({
            "success": True,
            "agents": [a.to_dict() for a in agents],
            "total": len(agents)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/agents', methods=['POST'])
def register_agent():
    """
    注册Agent
    
    Request Body:
        {
            "name": "Agent名称",
            "capabilities": ["capability1", "capability2"]
        }
    
    Response:
        {
            "success": true,
            "agent_id": "agent_xxx"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON"
            }), 400
        
        agent_id = scheduler.register_agent(data)
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "message": "Agent注册成功"
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """
    获取Agent详情
    
    Response:
        {
            "success": true,
            "agent": {...}
        }
    """
    try:
        agent = scheduler.get_agent_status(agent_id)
        
        if not agent:
            return jsonify({
                "success": False,
                "error": f"Agent不存在: {agent_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "agent": agent
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/agents/<agent_id>/heartbeat', methods=['POST'])
def agent_heartbeat(agent_id: str):
    """
    Agent心跳
    
    更新Agent的最后活跃时间
    """
    try:
        success = store.update_agent_heartbeat(agent_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Agent不存在: {agent_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "心跳更新成功"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@task_bp.route('/agents/<agent_id>', methods=['DELETE'])
def unregister_agent(agent_id: str):
    """
    注销Agent
    """
    try:
        success = scheduler.unregister_agent(agent_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Agent不存在: {agent_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Agent已注销"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


# ==================== 统计API ====================

@task_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    获取统计信息
    
    Response:
        {
            "success": true,
            "stats": {...}
        }
    """
    try:
        stats = store.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


# ==================== 错误处理 ====================

@task_bp.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "资源不存在"
    }), 404


@task_bp.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "方法不允许"
    }), 405


@task_bp.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500


# ==================== 注册Blueprint的辅助函数 ====================

def register_task_api(app):
    """
    将任务API注册到Flask应用
    
    Usage:
        from flask import Flask
        from task_api import register_task_api
        
        app = Flask(__name__)
        register_task_api(app)
    """
    app.register_blueprint(task_bp)
    return app


# ==================== 独立运行 ====================

if __name__ == '__main__':
    from flask import Flask
    
    app = Flask(__name__)
    register_task_api(app)
    
    print("=" * 50)
    print("任务调度API服务启动")
    print("API端点:")
    print("  POST   /api/v15.2/tasks              - 创建任务")
    print("  GET    /api/v15.2/tasks              - 任务列表")
    print("  GET    /api/v15.2/tasks/<task_id>    - 查询任务")
    print("  POST   /api/v15.2/tasks/<task_id>/assign   - 分配Agent")
    print("  POST   /api/v15.2/tasks/<task_id>/start    - 启动任务")
    print("  PUT    /api/v15.2/tasks/<task_id>/progress - 更新进度")
    print("  POST   /api/v15.2/tasks/<task_id>/complete - 完成任务")
    print("  POST   /api/v15.2/tasks/<task_id>/fail     - 标记失败")
    print("  POST   /api/v15.2/tasks/<task_id>/cancel   - 取消任务")
    print("  GET    /api/v15.2/tasks/<task_id>/output   - 获取产出")
    print("  GET    /api/v15.2/tasks/<task_id>/logs      - 获取日志")
    print("  GET    /api/v15.2/tasks/<task_id>/logs/stream - SSE日志流")
    print("  GET    /api/v15.2/agents              - Agent列表")
    print("  POST   /api/v15.2/agents              - 注册Agent")
    print("  GET    /api/v15.2/agents/<agent_id>   - Agent详情")
    print("  POST   /api/v15.2/agents/<agent_id>/heartbeat - Agent心跳")
    print("  DELETE /api/v15.2/agents/<agent_id>   - 注销Agent")
    print("  GET    /api/v15.2/stats               - 统计信息")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
