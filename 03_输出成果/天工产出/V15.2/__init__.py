# -*- coding: utf-8 -*-
"""
V15.2 任务调度模块
QQ任务调度功能后端核心组件
"""

from task_store import (
    TaskStore, Task, Agent, LogEntry,
    TaskStatus, AgentStatus,
    get_store
)

from task_scheduler import (
    TaskScheduler, get_scheduler,
    TaskNotFoundError, AgentNotFoundError,
    InvalidStatusError, AgentNotAvailableError
)

from task_api import task_bp, register_task_api


__all__ = [
    # 存储
    'TaskStore', 'Task', 'Agent', 'LogEntry',
    'TaskStatus', 'AgentStatus', 'get_store',
    
    # 调度器
    'TaskScheduler', 'get_scheduler',
    'TaskNotFoundError', 'AgentNotFoundError',
    'InvalidStatusError', 'AgentNotAvailableError',
    
    # API
    'task_bp', 'register_task_api'
]

__version__ = '15.2.0'
