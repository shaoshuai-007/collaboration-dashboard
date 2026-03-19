# -*- coding: utf-8 -*-
"""
task_store.py - 内存数据存储模块
用于任务列表、Agent状态、实时日志的存储
"""

import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"       # 等待分配
    ASSIGNED = "assigned"     # 已分配Agent
    RUNNING = "running"       # 执行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消


class AgentStatus(str, Enum):
    """Agent状态枚举"""
    ONLINE = "online"         # 在线空闲
    BUSY = "busy"             # 忙碌中
    OFFLINE = "offline"       # 离线
    ERROR = "error"           # 错误状态


@dataclass
class Task:
    """任务数据模型"""
    task_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    agent: Optional[str] = None
    progress: int = 0  # 0-100
    output: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "agent": self.agent,
            "progress": self.progress,
            "output": self.output,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class Agent:
    """Agent数据模型"""
    agent_id: str
    name: str
    status: AgentStatus = AgentStatus.OFFLINE
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task,
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "task_id": self.task_id,
            "metadata": self.metadata
        }


class TaskStore:
    """
    内存数据存储
    线程安全的任务、Agent、日志存储
    """
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._agents: Dict[str, Agent] = {}
        self._logs: Dict[str, List[LogEntry]] = {}  # task_id -> logs
        self._global_logs: List[LogEntry] = []
        self._lock = threading.RLock()
    
    # ==================== 任务操作 ====================
    
    def create_task(self, task: Task) -> None:
        """创建任务"""
        with self._lock:
            self._tasks[task.task_id] = task
            self._logs[task.task_id] = []
            self._add_log("INFO", f"任务创建: {task.title}", task.task_id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """获取所有任务，可按状态筛选"""
        with self._lock:
            tasks = list(self._tasks.values())
            if status:
                tasks = [t for t in tasks if t.status == status]
            return tasks
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务字段"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                if task_id in self._logs:
                    del self._logs[task_id]
                return True
            return False
    
    # ==================== Agent操作 ====================
    
    def register_agent(self, agent: Agent) -> None:
        """注册Agent"""
        with self._lock:
            self._agents[agent.agent_id] = agent
            self._add_log("INFO", f"Agent注册: {agent.name}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取Agent"""
        with self._lock:
            return self._agents.get(agent_id)
    
    def get_all_agents(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        """获取所有Agent，可按状态筛选"""
        with self._lock:
            agents = list(self._agents.values())
            if status:
                agents = [a for a in agents if a.status == status]
            return agents
    
    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """更新Agent字段"""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            for key, value in kwargs.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
            
            agent.last_heartbeat = datetime.now()
            return True
    
    def update_agent_heartbeat(self, agent_id: str) -> bool:
        """更新Agent心跳"""
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            agent.last_heartbeat = datetime.now()
            return True
    
    def get_available_agents(self) -> List[Agent]:
        """获取可用Agent（在线且空闲）"""
        with self._lock:
            return [
                a for a in self._agents.values()
                if a.status == AgentStatus.ONLINE
            ]
    
    # ==================== 日志操作 ====================
    
    def _add_log(self, level: str, message: str, task_id: Optional[str] = None, 
                 metadata: Optional[Dict] = None) -> None:
        """内部添加日志"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            task_id=task_id,
            metadata=metadata or {}
        )
        
        # 添加到全局日志
        self._global_logs.append(entry)
        
        # 添加到任务日志
        if task_id and task_id in self._logs:
            self._logs[task_id].append(entry)
    
    def add_task_log(self, task_id: str, level: str, message: str, 
                     metadata: Optional[Dict] = None) -> None:
        """添加任务日志"""
        with self._lock:
            self._add_log(level, message, task_id, metadata)
    
    def get_task_logs(self, task_id: str, limit: int = 100) -> List[LogEntry]:
        """获取任务日志"""
        with self._lock:
            logs = self._logs.get(task_id, [])
            return logs[-limit:] if limit > 0 else logs
    
    def get_global_logs(self, limit: int = 100) -> List[LogEntry]:
        """获取全局日志"""
        with self._lock:
            return self._global_logs[-limit:] if limit > 0 else self._global_logs
    
    def clear_task_logs(self, task_id: str) -> None:
        """清除任务日志"""
        with self._lock:
            if task_id in self._logs:
                self._logs[task_id] = []
    
    # ==================== 统计信息 ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            tasks_by_status = {}
            for status in TaskStatus:
                tasks_by_status[status.value] = len([
                    t for t in self._tasks.values() if t.status == status
                ])
            
            agents_by_status = {}
            for status in AgentStatus:
                agents_by_status[status.value] = len([
                    a for a in self._agents.values() if a.status == status
                ])
            
            return {
                "total_tasks": len(self._tasks),
                "total_agents": len(self._agents),
                "tasks_by_status": tasks_by_status,
                "agents_by_status": agents_by_status,
                "total_logs": len(self._global_logs)
            }


# 全局单例
_store_instance: Optional[TaskStore] = None
_store_lock = threading.Lock()


def get_store() -> TaskStore:
    """获取全局存储实例"""
    global _store_instance
    if _store_instance is None:
        with _store_lock:
            if _store_instance is None:
                _store_instance = TaskStore()
    return _store_instance
