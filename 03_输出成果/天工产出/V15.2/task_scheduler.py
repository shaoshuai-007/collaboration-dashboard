# -*- coding: utf-8 -*-
"""
task_scheduler.py - 任务调度引擎
负责任务的创建、分配、进度更新、完成等核心调度逻辑
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from task_store import (
    TaskStore, Task, Agent, TaskStatus, AgentStatus,
    get_store
)


class SchedulerError(Exception):
    """调度器错误基类"""
    pass


class TaskNotFoundError(SchedulerError):
    """任务不存在"""
    pass


class AgentNotFoundError(SchedulerError):
    """Agent不存在"""
    pass


class InvalidStatusError(SchedulerError):
    """无效状态"""
    pass


class AgentNotAvailableError(SchedulerError):
    """Agent不可用"""
    pass


class TaskScheduler:
    """
    任务调度器
    负责任务生命周期管理和Agent分配
    """
    
    def __init__(self, store: Optional[TaskStore] = None):
        self.store = store or get_store()
    
    def create_task(self, task_info: Dict[str, Any]) -> str:
        """
        创建任务
        
        Args:
            task_info: 任务信息字典，包含：
                - title: 任务标题（必需）
                - description: 任务描述
                - agent: 指定Agent ID（可选）
                - metadata: 额外元数据
        
        Returns:
            task_id: 任务ID
        
        Raises:
            ValueError: 参数错误
            AgentNotFoundError: 指定的Agent不存在
            AgentNotAvailableError: 指定的Agent不可用
        """
        # 参数验证
        if "title" not in task_info:
            raise ValueError("任务标题(title)是必需的")
        
        # 生成任务ID
        task_id = task_info.get("task_id") or self._generate_task_id()
        
        # 创建任务对象
        task = Task(
            task_id=task_id,
            title=task_info["title"],
            description=task_info.get("description", ""),
            metadata=task_info.get("metadata", {})
        )
        
        # 保存任务
        self.store.create_task(task)
        
        # 如果指定了Agent，立即分配
        if "agent" in task_info and task_info["agent"]:
            self.assign_agent(task_id, task_info["agent"])
        
        return task_id
    
    def assign_agent(self, task_id: str, agent_id: str) -> None:
        """
        分配Agent到任务
        
        Args:
            task_id: 任务ID
            agent_id: Agent ID
        
        Raises:
            TaskNotFoundError: 任务不存在
            AgentNotFoundError: Agent不存在
            AgentNotAvailableError: Agent不可用
            InvalidStatusError: 任务状态不允许分配
        """
        # 检查任务
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        # 检查任务状态
        if task.status not in (TaskStatus.PENDING, TaskStatus.ASSIGNED):
            raise InvalidStatusError(f"任务状态 [{task.status.value}] 不允许分配Agent")
        
        # 检查Agent
        agent = self.store.get_agent(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent不存在: {agent_id}")
        
        # 检查Agent可用性
        if agent.status != AgentStatus.ONLINE:
            raise AgentNotAvailableError(f"Agent [{agent.name}] 当前状态: {agent.status.value}")
        
        # 如果之前有Agent，释放它
        if task.agent and task.agent != agent_id:
            self.store.update_agent(task.agent, 
                status=AgentStatus.ONLINE,
                current_task=None
            )
        
        # 分配Agent
        self.store.update_task(task_id,
            agent=agent_id,
            status=TaskStatus.ASSIGNED
        )
        
        # 更新Agent状态
        self.store.update_agent(agent_id,
            status=AgentStatus.BUSY,
            current_task=task_id
        )
        
        # 记录日志
        self.store.add_task_log(task_id, "INFO", 
            f"Agent [{agent.name}] 已分配到任务")
    
    def start_task(self, task_id: str) -> None:
        """
        启动任务执行
        
        Args:
            task_id: 任务ID
        
        Raises:
            TaskNotFoundError: 任务不存在
            InvalidStatusError: 任务状态不允许启动
        """
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        if task.status != TaskStatus.ASSIGNED:
            raise InvalidStatusError(f"任务状态 [{task.status.value}] 不允许启动")
        
        self.store.update_task(task_id, status=TaskStatus.RUNNING)
        self.store.add_task_log(task_id, "INFO", "任务开始执行")
    
    def update_progress(self, task_id: str, progress: int, message: str = "") -> None:
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度值（0-100）
            message: 进度消息
        
        Raises:
            TaskNotFoundError: 任务不存在
            ValueError: 进度值无效
        """
        if not 0 <= progress <= 100:
            raise ValueError("进度值必须在 0-100 之间")
        
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        self.store.update_task(task_id, progress=progress)
        
        if message:
            self.store.add_task_log(task_id, "INFO", 
                f"进度更新: {progress}% - {message}")
        else:
            self.store.add_task_log(task_id, "DEBUG", 
                f"进度更新: {progress}%")
    
    def complete_task(self, task_id: str, output: Optional[Dict[str, Any]] = None) -> None:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            output: 任务产出
        
        Raises:
            TaskNotFoundError: 任务不存在
        """
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        # 更新任务状态
        self.store.update_task(task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            output=output
        )
        
        # 释放Agent
        if task.agent:
            self.store.update_agent(task.agent,
                status=AgentStatus.ONLINE,
                current_task=None
            )
        
        self.store.add_task_log(task_id, "INFO", "任务完成")
    
    def fail_task(self, task_id: str, error_message: str) -> None:
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误信息
        
        Raises:
            TaskNotFoundError: 任务不存在
        """
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        # 更新任务状态
        self.store.update_task(task_id,
            status=TaskStatus.FAILED,
            error_message=error_message
        )
        
        # 释放Agent
        if task.agent:
            self.store.update_agent(task.agent,
                status=AgentStatus.ONLINE,
                current_task=None
            )
        
        self.store.add_task_log(task_id, "ERROR", f"任务失败: {error_message}")
    
    def cancel_task(self, task_id: str, reason: str = "") -> None:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            reason: 取消原因
        
        Raises:
            TaskNotFoundError: 任务不存在
        """
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        # 更新任务状态
        self.store.update_task(task_id,
            status=TaskStatus.CANCELLED,
            error_message=reason or "任务已取消"
        )
        
        # 释放Agent
        if task.agent:
            self.store.update_agent(task.agent,
                status=AgentStatus.ONLINE,
                current_task=None
            )
        
        self.store.add_task_log(task_id, "WARNING", 
            f"任务已取消: {reason}" if reason else "任务已取消")
    
    def auto_assign_task(self, task_id: str) -> Optional[str]:
        """
        自动分配Agent
        
        Args:
            task_id: 任务ID
        
        Returns:
            分配的Agent ID，如果没有可用Agent则返回None
        
        Raises:
            TaskNotFoundError: 任务不存在
        """
        task = self.store.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"任务不存在: {task_id}")
        
        # 获取可用Agent
        available_agents = self.store.get_available_agents()
        if not available_agents:
            self.store.add_task_log(task_id, "WARNING", "没有可用的Agent")
            return None
        
        # 简单策略：选择第一个可用Agent
        # TODO: 可以扩展为更复杂的分配策略
        selected_agent = available_agents[0]
        self.assign_agent(task_id, selected_agent.agent_id)
        
        return selected_agent.agent_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务状态字典，任务不存在返回None
        """
        task = self.store.get_task(task_id)
        if not task:
            return None
        return task.to_dict()
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取Agent状态
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent状态字典，Agent不存在返回None
        """
        agent = self.store.get_agent(agent_id)
        if not agent:
            return None
        return agent.to_dict()
    
    def register_agent(self, agent_info: Dict[str, Any]) -> str:
        """
        注册Agent
        
        Args:
            agent_info: Agent信息，包含：
                - name: Agent名称（必需）
                - capabilities: 能力列表
        
        Returns:
            agent_id: Agent ID
        
        Raises:
            ValueError: 参数错误
        """
        if "name" not in agent_info:
            raise ValueError("Agent名称(name)是必需的")
        
        agent_id = agent_info.get("agent_id") or self._generate_agent_id()
        
        agent = Agent(
            agent_id=agent_id,
            name=agent_info["name"],
            status=AgentStatus.ONLINE,
            capabilities=agent_info.get("capabilities", []),
            metadata=agent_info.get("metadata", {})
        )
        
        self.store.register_agent(agent)
        
        return agent_id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        注销Agent
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否成功注销
        """
        agent = self.store.get_agent(agent_id)
        if not agent:
            return False
        
        # 如果Agent有正在执行的任务，标记为失败
        if agent.current_task:
            self.fail_task(agent.current_task, f"Agent [{agent.name}] 已注销")
        
        # 删除Agent（或者标记为离线）
        self.store.update_agent(agent_id, 
            status=AgentStatus.OFFLINE,
            current_task=None
        )
        
        return True
    
    # ==================== 辅助方法 ====================
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{uuid.uuid4().hex[:12]}"
    
    def _generate_agent_id(self) -> str:
        """生成Agent ID"""
        return f"agent_{uuid.uuid4().hex[:8]}"


# 全局单例
_scheduler_instance: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler()
    return _scheduler_instance
