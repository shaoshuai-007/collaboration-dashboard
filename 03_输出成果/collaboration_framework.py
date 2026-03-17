#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 - 核心模块
Collaboration Framework for Multi-Agent System

Author: 南乔
Date: 2026-03-13
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set
from datetime import datetime
import uuid
import asyncio
from collections import defaultdict, deque
import threading
import json


# ==================== 消息类型 ====================

class MessageType(Enum):
    """消息类型"""
    TASK = "task"              # 任务消息
    QUESTION = "question"      # 提问
    ANSWER = "answer"          # 回答
    FEEDBACK = "feedback"      # 反馈
    BROADCAST = "broadcast"    # 广播
    SYSTEM = "system"          # 系统消息
    NOTIFICATION = "notification"  # 通知


@dataclass
class Message:
    """消息结构"""
    from_agent: str                    # 发送者
    to_agents: List[str]               # 接收者列表
    content: str                       # 消息内容
    msg_type: MessageType = MessageType.TASK
    priority: int = 5                  # 优先级 1-10
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None     # 回复的消息ID
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agents": self.to_agents,
            "content": self.content,
            "msg_type": self.msg_type.value,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "reply_to": self.reply_to,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            id=data["id"],
            from_agent=data["from_agent"],
            to_agents=data["to_agents"],
            content=data["content"],
            msg_type=MessageType(data["msg_type"]),
            priority=data["priority"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            reply_to=data.get("reply_to"),
            metadata=data.get("metadata", {})
        )


# ==================== Agent角色定义 ====================

class ReplyStyle(Enum):
    """回复风格"""
    PROFESSIONAL = "专业"      # 专业严谨
    CONCISE = "简洁"          # 简洁明了
    DETAILED = "详细"         # 详细全面
    FRIENDLY = "亲切"         # 亲切友好
    STRICT = "严谨"           # 严谨规范


@dataclass
class AgentRole:
    """Agent角色定义"""
    agent_id: str                       # Agent标识
    name: str                           # 名称
    role: str                           # 角色描述
    emoji: str = "🤖"                   # 表情符号
    
    # 发言规则
    speak_priority: int = 5             # 发言优先级（1-10）
    speak_cooldown: int = 3             # 发言冷却时间（秒）
    max_speak_duration: int = 120       # 最大发言时长（秒）
    
    # 回复风格
    style: ReplyStyle = ReplyStyle.PROFESSIONAL
    
    # 能力标签
    capabilities: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    
    # 状态
    is_active: bool = True
    current_task: Optional[str] = None
    last_speak_time: Optional[datetime] = None
    
    def can_speak(self) -> bool:
        """检查是否可以发言"""
        if not self.is_active:
            return False
        if self.last_speak_time:
            elapsed = (datetime.now() - self.last_speak_time).total_seconds()
            if elapsed < self.speak_cooldown:
                return False
        return True
    
    def record_speak(self):
        """记录发言"""
        self.last_speak_time = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "emoji": self.emoji,
            "speak_priority": self.speak_priority,
            "speak_cooldown": self.speak_cooldown,
            "style": self.style.value,
            "capabilities": self.capabilities,
            "expertise": self.expertise,
            "is_active": self.is_active,
            "current_task": self.current_task
        }


# ==================== 冲突处理器 ====================

class ConflictType(Enum):
    """冲突类型"""
    SPEAK = "speak"              # 发言冲突
    TASK = "task"                # 任务冲突
    OPINION = "opinion"          # 观点冲突
    RESOURCE = "resource"        # 资源冲突


@dataclass
class Conflict:
    """冲突记录"""
    conflict_type: ConflictType
    agents: List[str]
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolution: Optional[str] = None


class ConflictResolver:
    """冲突处理器"""
    
    def __init__(self):
        self.conflict_history: List[Conflict] = []
        self.resolution_strategies = {
            ConflictType.SPEAK: self._resolve_speak_conflict,
            ConflictType.TASK: self._resolve_task_conflict,
            ConflictType.OPINION: self._resolve_opinion_conflict,
            ConflictType.RESOURCE: self._resolve_resource_conflict,
        }
    
    def detect_conflict(self, agents: List[AgentRole], context: dict) -> Optional[Conflict]:
        """检测冲突"""
        # 检测发言冲突
        can_speak_agents = [a for a in agents if a.can_speak()]
        if len(can_speak_agents) > 1:
            # 多个Agent同时可以发言
            return Conflict(
                conflict_type=ConflictType.SPEAK,
                agents=[a.agent_id for a in can_speak_agents],
                description=f"{len(can_speak_agents)}个Agent同时请求发言"
            )
        return None
    
    def resolve(self, conflict: Conflict, agents: Dict[str, AgentRole]) -> str:
        """解决冲突"""
        strategy = self.resolution_strategies.get(conflict.conflict_type)
        if strategy:
            winner = strategy(conflict, agents)
            conflict.resolution = f"Winner: {winner}"
            self.conflict_history.append(conflict)
            return winner
        return conflict.agents[0]  # 默认返回第一个
    
    def _resolve_speak_conflict(self, conflict: Conflict, agents: Dict[str, AgentRole]) -> str:
        """解决发言冲突 - 优先级裁决"""
        # 按优先级排序
        sorted_agents = sorted(
            conflict.agents,
            key=lambda aid: agents[aid].speak_priority if aid in agents else 0,
            reverse=True
        )
        return sorted_agents[0]
    
    def _resolve_task_conflict(self, conflict: Conflict, agents: Dict[str, AgentRole]) -> str:
        """解决任务冲突 - 能力匹配"""
        # 简化实现：返回优先级最高的
        return self._resolve_speak_conflict(conflict, agents)
    
    def _resolve_opinion_conflict(self, conflict: Conflict, agents: Dict[str, AgentRole]) -> str:
        """解决观点冲突 - 扶摇裁决"""
        if "fuyao" in agents:
            return "fuyao"
        return self._resolve_speak_conflict(conflict, agents)
    
    def _resolve_resource_conflict(self, conflict: Conflict, agents: Dict[str, AgentRole]) -> str:
        """解决资源冲突 - 排队机制"""
        # 返回最早请求的（简化实现）
        return conflict.agents[0]


# ==================== 协作调度器 ====================

class SchedulerState(Enum):
    """调度器状态"""
    IDLE = "idle"           # 空闲
    ACTIVE = "active"       # 活跃
    PAUSED = "paused"       # 暂停


class CollaborationScheduler:
    """协作调度器"""
    
    def __init__(self):
        self.agents: Dict[str, AgentRole] = {}
        self.speak_queue: deque = deque()      # 发言队列
        self.current_speaker: Optional[str] = None
        self.state: SchedulerState = SchedulerState.IDLE
        self.conflict_resolver = ConflictResolver()
        self.lock = threading.Lock()
        
        # 任务管理
        self.task_queue: deque = deque()
        self.active_tasks: Dict[str, str] = {}  # task_id -> agent_id
        self.completed_tasks: List[str] = []
    
    def register_agent(self, agent: AgentRole):
        """注册Agent"""
        with self.lock:
            self.agents[agent.agent_id] = agent
            print(f"[Scheduler] 注册Agent: {agent.emoji} {agent.name} ({agent.role})")
    
    def request_speak(self, agent_id: str) -> bool:
        """请求发言权"""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            # 检查是否可以发言
            if not agent.can_speak():
                return False
            
            # 检查当前发言者
            if self.current_speaker is None:
                self.current_speaker = agent_id
                agent.record_speak()
                print(f"[Scheduler] {agent.emoji} {agent.name} 获得发言权")
                return True
            else:
                # 加入队列
                if agent_id not in self.speak_queue:
                    self.speak_queue.append(agent_id)
                    print(f"[Scheduler] {agent.emoji} {agent.name} 加入发言队列")
                return False
    
    def release_speak(self, agent_id: str):
        """释放发言权"""
        with self.lock:
            if self.current_speaker == agent_id:
                self.current_speaker = None
                print(f"[Scheduler] {self.agents[agent_id].emoji} {self.agents[agent_id].name} 释放发言权")
                
                # 处理队列中的下一个
                if self.speak_queue:
                    next_agent = self.speak_queue.popleft()
                    self.current_speaker = next_agent
                    self.agents[next_agent].record_speak()
                    print(f"[Scheduler] {self.agents[next_agent].emoji} {self.agents[next_agent].name} 获得发言权")
    
    def get_speak_order(self, context: str = None) -> List[str]:
        """获取发言顺序（按优先级）"""
        with self.lock:
            # 计算动态优先级
            agent_priorities = []
            for agent_id, agent in self.agents.items():
                priority = agent.speak_priority
                
                # 上下文加权（简化实现）
                if context and any(exp in context for exp in agent.expertise):
                    priority += 2
                
                agent_priorities.append((agent_id, priority))
            
            # 按优先级排序
            agent_priorities.sort(key=lambda x: x[1], reverse=True)
            return [aid for aid, _ in agent_priorities]
    
    def assign_task(self, task_id: str, task_desc: str, agent_id: str) -> bool:
        """分配任务"""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.active_tasks[task_id] = agent_id
            self.agents[agent_id].current_task = task_id
            print(f"[Scheduler] 任务 {task_id} 分配给 {self.agents[agent_id].emoji} {self.agents[agent_id].name}")
            return True
    
    def complete_task(self, task_id: str):
        """完成任务"""
        with self.lock:
            if task_id in self.active_tasks:
                agent_id = self.active_tasks.pop(task_id)
                if agent_id in self.agents:
                    self.agents[agent_id].current_task = None
                self.completed_tasks.append(task_id)
                print(f"[Scheduler] 任务 {task_id} 已完成")


# ==================== 通信总线 ====================

class CommunicationMode(Enum):
    """通信模式"""
    ONE_TO_ONE = "one_to_one"       # 一对一
    ONE_TO_MANY = "one_to_many"     # 一对多
    MANY_TO_MANY = "many_to_many"   # 多对多
    BROADCAST = "broadcast"         # 广播


class CommunicationBus:
    """通信总线"""
    
    def __init__(self, scheduler: CollaborationScheduler):
        self.scheduler = scheduler
        self.message_history: List[Message] = []
        self.agent_inboxes: Dict[str, deque] = defaultdict(deque)
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # topic -> agents
        self.lock = threading.Lock()
        
        # 消息处理器
        self.message_handlers: List[callable] = []
    
    def register_handler(self, handler: callable):
        """注册消息处理器"""
        self.message_handlers.append(handler)
    
    def send(self, message: Message) -> bool:
        """发送消息"""
        with self.lock:
            # 记录历史
            self.message_history.append(message)
            
            # 分发到收件箱
            for agent_id in message.to_agents:
                if agent_id in self.scheduler.agents:
                    self.agent_inboxes[agent_id].append(message)
                    print(f"[Bus] {message.from_agent} → {agent_id}: {message.content[:50]}...")
            
            # 触发处理器
            for handler in self.message_handlers:
                try:
                    handler(message)
                except Exception as e:
                    print(f"[Bus] Handler error: {e}")
            
            return True
    
    def send_to_one(self, from_agent: str, to_agent: str, content: str, **kwargs) -> bool:
        """一对一发送"""
        message = Message(
            from_agent=from_agent,
            to_agents=[to_agent],
            content=content,
            **kwargs
        )
        return self.send(message)
    
    def send_to_many(self, from_agent: str, to_agents: List[str], content: str, **kwargs) -> bool:
        """一对多发送"""
        message = Message(
            from_agent=from_agent,
            to_agents=to_agents,
            content=content,
            **kwargs
        )
        return self.send(message)
    
    def broadcast(self, from_agent: str, content: str, **kwargs) -> bool:
        """广播给所有Agent"""
        all_agents = list(self.scheduler.agents.keys())
        message = Message(
            from_agent=from_agent,
            to_agents=all_agents,
            content=content,
            msg_type=MessageType.BROADCAST,
            **kwargs
        )
        return self.send(message)
    
    def get_messages(self, agent_id: str, limit: int = 10) -> List[Message]:
        """获取Agent的消息"""
        with self.lock:
            messages = list(self.agent_inboxes[agent_id])[-limit:]
            return messages
    
    def subscribe(self, agent_id: str, topics: List[str]):
        """订阅主题"""
        with self.lock:
            for topic in topics:
                self.subscriptions[topic].add(agent_id)
            print(f"[Bus] {agent_id} 订阅了: {topics}")
    
    def publish(self, topic: str, message: Message):
        """发布到主题"""
        with self.lock:
            subscribers = self.subscriptions.get(topic, set())
            message.to_agents = list(subscribers)
            self.send(message)
    
    def get_history(self, limit: int = 50) -> List[Message]:
        """获取消息历史"""
        return self.message_history[-limit:]


# ==================== 任务拆解器 ====================

@dataclass
class Task:
    """任务结构"""
    id: str
    description: str
    assignee: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5
    status: str = "pending"  # pending, active, completed
    metadata: Dict = field(default_factory=dict)


class TaskDecomposer:
    """任务拆解器"""
    
    def __init__(self, scheduler: CollaborationScheduler):
        self.scheduler = scheduler
    
    def decompose(self, task_description: str) -> List[Task]:
        """拆解任务"""
        tasks = []
        
        # 根据关键词拆解（简化实现）
        task_patterns = {
            "需求": ("需求分析", "caiwei"),
            "架构": ("架构设计", "zhijin"),
            "成本": ("成本评估", "zhutai"),
            "PPT": ("方案PPT", "chengcai"),
            "设计": ("详细设计", "gongchi"),
            "项目": ("项目管控", "yuheng"),
            "资源": ("资源整理", "zhegui"),
        }
        
        for keyword, (task_name, assignee) in task_patterns.items():
            if keyword in task_description:
                task_id = f"task_{len(tasks)+1}"
                tasks.append(Task(
                    id=task_id,
                    description=task_name,
                    assignee=assignee,
                    priority=self._get_priority(task_name)
                ))
        
        # 如果没有匹配，创建通用任务
        if not tasks:
            tasks.append(Task(
                id="task_1",
                description=task_description,
                priority=5
            ))
        
        return tasks
    
    def _get_priority(self, task_name: str) -> int:
        """获取任务优先级"""
        priority_map = {
            "需求分析": 7,
            "架构设计": 6,
            "成本评估": 5,
            "方案PPT": 4,
            "详细设计": 5,
            "项目管控": 8,
            "资源整理": 3,
        }
        return priority_map.get(task_name, 5)
    
    def assign_tasks(self, tasks: List[Task]) -> Dict[str, str]:
        """分配任务"""
        assignments = {}
        for task in tasks:
            if task.assignee:
                self.scheduler.assign_task(task.id, task.description, task.assignee)
                assignments[task.id] = task.assignee
        return assignments


# ==================== 协作框架 ====================

class CollaborationFramework:
    """多Agent协作框架"""
    
    def __init__(self):
        self.scheduler = CollaborationScheduler()
        self.bus = CommunicationBus(self.scheduler)
        self.task_decomposer = TaskDecomposer(self.scheduler)
        
        # 注册默认Agent
        self._register_default_agents()
    
    def _register_default_agents(self):
        """注册默认Agent"""
        default_agents = [
            AgentRole(
                agent_id="nanqiao", name="南乔", role="主控Agent", emoji="🌿",
                speak_priority=9, style=ReplyStyle.FRIENDLY,
                capabilities=["协调", "调度"], expertise=["全局协调"]
            ),
            AgentRole(
                agent_id="caiwei", name="采薇", role="需求分析专家", emoji="🌸",
                speak_priority=7, style=ReplyStyle.PROFESSIONAL,
                capabilities=["需求分析", "文档编写"], expertise=["需求"]
            ),
            AgentRole(
                agent_id="zhijin", name="织锦", role="架构设计师", emoji="🧵",
                speak_priority=6, style=ReplyStyle.DETAILED,
                capabilities=["架构设计", "技术选型"], expertise=["架构"]
            ),
            AgentRole(
                agent_id="zhutai", name="筑台", role="售前工程师", emoji="🏗️",
                speak_priority=5, style=ReplyStyle.PROFESSIONAL,
                capabilities=["成本评估", "方案设计"], expertise=["成本", "方案"]
            ),
            AgentRole(
                agent_id="chengcai", name="呈彩", role="方案PPT设计师", emoji="🎨",
                speak_priority=4, style=ReplyStyle.CONCISE,
                capabilities=["PPT设计", "方案呈现"], expertise=["PPT"]
            ),
            AgentRole(
                agent_id="gongchi", name="工尺", role="详细设计师", emoji="📐",
                speak_priority=5, style=ReplyStyle.STRICT,
                capabilities=["详细设计", "接口设计"], expertise=["设计"]
            ),
            AgentRole(
                agent_id="yuheng", name="玉衡", role="项目经理", emoji="⚖️",
                speak_priority=8, style=ReplyStyle.PROFESSIONAL,
                capabilities=["项目管理", "进度控制"], expertise=["项目"]
            ),
            AgentRole(
                agent_id="zhegui", name="折桂", role="资源管家", emoji="📚",
                speak_priority=3, style=ReplyStyle.CONCISE,
                capabilities=["资源管理", "知识沉淀"], expertise=["资源"]
            ),
            AgentRole(
                agent_id="fuyao", name="扶摇", role="总指挥", emoji="🌀",
                speak_priority=10, style=ReplyStyle.PROFESSIONAL,
                capabilities=["全局协调", "决策"], expertise=["协调", "决策"]
            ),
        ]
        
        for agent in default_agents:
            self.scheduler.register_agent(agent)
    
    def send(self, from_agent: str, to_agents: List[str], content: str, **kwargs) -> bool:
        """发送消息"""
        message = Message(
            from_agent=from_agent,
            to_agents=to_agents if isinstance(to_agents, list) else [to_agents],
            content=content,
            **kwargs
        )
        return self.bus.send(message)
    
    def broadcast(self, from_agent: str, content: str, **kwargs) -> bool:
        """广播消息"""
        return self.bus.broadcast(from_agent, content, **kwargs)
    
    def decompose_task(self, task: str) -> List[Task]:
        """拆解任务"""
        return self.task_decomposer.decompose(task)
    
    def get_status(self) -> dict:
        """获取状态"""
        return {
            "agents": {aid: agent.to_dict() for aid, agent in self.scheduler.agents.items()},
            "current_speaker": self.scheduler.current_speaker,
            "speak_queue": list(self.scheduler.speak_queue),
            "active_tasks": self.scheduler.active_tasks,
            "message_count": len(self.bus.message_history)
        }


# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧭 多Agent协作框架 - 测试")
    print("=" * 60)
    
    # 创建框架
    framework = CollaborationFramework()
    
    # 测试发言顺序
    print("\n📋 发言顺序测试:")
    order = framework.scheduler.get_speak_order("架构设计需求")
    for i, aid in enumerate(order):
        agent = framework.scheduler.agents[aid]
        print(f"  {i+1}. {agent.emoji} {agent.name} (优先级: {agent.speak_priority})")
    
    # 测试消息发送
    print("\n💬 消息发送测试:")
    framework.send("nanqiao", ["caiwei", "zhijin"], "请完成需求分析和架构设计", msg_type=MessageType.TASK)
    
    # 测试广播
    print("\n📢 广播测试:")
    framework.broadcast("fuyao", "项目启动，请各位准备！")
    
    # 测试任务拆解
    print("\n🔧 任务拆解测试:")
    tasks = framework.decompose_task("完成湖北电渠AI智能配案系统的需求分析、架构设计和成本评估")
    for task in tasks:
        print(f"  • {task.description} → {task.assignee}")
    
    # 获取状态
    print("\n📊 框架状态:")
    status = framework.get_status()
    print(f"  Agent数量: {len(status['agents'])}")
    print(f"  消息数量: {status['message_count']}")
    print(f"  当前发言者: {status['current_speaker']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
