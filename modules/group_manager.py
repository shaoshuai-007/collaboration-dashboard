#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群组管理模块 - V16.0
功能：群组创建、成员管理、消息路由、@提及处理
作者：南乔 🌿
日期：2026-03-19
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import threading
import queue


@dataclass
class Agent:
    """Agent数据结构"""
    agent_id: str
    name: str
    role: str
    emoji: str
    status: str = 'online'  # online, busy, offline
    current_task: Optional[str] = None


@dataclass
class Message:
    """消息数据结构"""
    msg_id: str
    group_id: str
    from_type: str  # 'user' or 'agent'
    from_id: str
    from_name: str
    from_emoji: str
    content: str
    mentions: List[str]  # @的Agent列表
    reply_to: Optional[str] = None
    seq: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@dataclass
class Task:
    """任务数据结构"""
    task_id: str
    group_id: str
    title: str
    description: str
    status: str = 'pending'  # pending, running, completed, failed
    progress: int = 0
    assignee: Optional[str] = None
    collaborators: List[str] = None
    created_at: str = ""
    
    def __post_init__(self):
        if self.collaborators is None:
            self.collaborators = []
        if not self.created_at:
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class GroupManager:
    """群组管理器"""
    
    def __init__(self):
        # 九星智囊团成员
        self.agents: Dict[str, Agent] = {
            'nanqiao': Agent('nanqiao', '南乔', '用户助手', '🌿', 'online'),
            'caiwei': Agent('caiwei', '采薇', '需求分析师', '🌸', 'online'),
            'zhijin': Agent('zhijin', '织锦', '架构设计师', '🧵', 'online'),
            'zhutai': Agent('zhutai', '筑台', '售前工程师', '🏗️', 'online'),
            'chengcai': Agent('chengcai', '呈彩', '方案设计师', '🎨', 'online'),
            'gongchi': Agent('gongchi', '工尺', '系统设计师', '📐', 'online'),
            'yuheng': Agent('yuheng', '玉衡', '项目经理', '⚖️', 'online'),
            'zhegui': Agent('zhegui', '折桂', '资源管家', '📚', 'online'),
            'fuyao': Agent('fuyao', '扶摇', '总指挥', '🌀', 'online'),
        }
        
        # 全员群
        self.main_group_id = 'jiuxing_main'
        self.main_group_name = '九星智囊团全员群'
        
        # 消息存储
        self.messages: List[Message] = []
        self.message_seq = 0
        self.message_lock = threading.Lock()
        
        # 任务存储
        self.tasks: Dict[str, Task] = {}
        
        # 消息队列（用于SSE推送）
        self.message_queue = queue.Queue()
        
        # 消息订阅者
        self.subscribers: Dict[str, queue.Queue] = {}
    
    def get_all_agents(self) -> List[Dict]:
        """获取所有Agent"""
        return [asdict(agent) for agent in self.agents.values()]
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取指定Agent"""
        return self.agents.get(agent_id)
    
    def update_agent_status(self, agent_id: str, status: str, current_task: str = None):
        """更新Agent状态"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            if current_task:
                self.agents[agent_id].current_task = current_task
    
    def create_message(self, from_type: str, from_id: str, content: str, 
                      mentions: List[str] = None, reply_to: str = None) -> Message:
        """创建消息"""
        
        with self.message_lock:
            self.message_seq += 1
            
            # 获取发送者信息
            if from_type == 'agent' and from_id in self.agents:
                agent = self.agents[from_id]
                from_name = agent.name
                from_emoji = agent.emoji
            else:
                from_name = '少帅'
                from_emoji = '👤'
            
            # 提取@提及
            if mentions is None:
                mentions = self.extract_mentions(content)
            
            msg = Message(
                msg_id=f"msg_{uuid.uuid4().hex[:12]}",
                group_id=self.main_group_id,
                from_type=from_type,
                from_id=from_id,
                from_name=from_name,
                from_emoji=from_emoji,
                content=content,
                mentions=mentions,
                reply_to=reply_to,
                seq=self.message_seq
            )
            
            self.messages.append(msg)
            
            # 推送到队列
            self.message_queue.put(msg)
            self.broadcast_message(msg)
            
            return msg
    
    def extract_mentions(self, content: str) -> List[str]:
        """从内容中提取@提及"""
        import re
        # 匹配 @Agent名 格式
        pattern = r'@(\w+)'
        matches = re.findall(pattern, content)
        
        mentions = []
        for name in matches:
            # 根据名字查找Agent
            for agent_id, agent in self.agents.items():
                if agent.name == name or agent_id == name:
                    mentions.append(agent_id)
                    break
        
        # 检查@all
        if '@all' in content or '@所有人' in content:
            mentions = list(self.agents.keys())
        
        return mentions
    
    def get_messages(self, limit: int = 50, before_seq: int = None) -> List[Dict]:
        """获取消息列表"""
        with self.message_lock:
            if before_seq:
                msgs = [m for m in self.messages if m.seq < before_seq]
            else:
                msgs = self.messages
            
            # 返回最新的limit条
            msgs = msgs[-limit:] if len(msgs) > limit else msgs
            return [asdict(m) for m in msgs]
    
    def subscribe(self, client_id: str) -> queue.Queue:
        """订阅消息"""
        q = queue.Queue()
        self.subscribers[client_id] = q
        return q
    
    def unsubscribe(self, client_id: str):
        """取消订阅"""
        if client_id in self.subscribers:
            del self.subscribers[client_id]
    
    def broadcast_message(self, message: Message):
        """广播消息给所有订阅者"""
        msg_dict = asdict(message)
        for client_id, q in self.subscribers.items():
            try:
                q.put_nowait(msg_dict)
            except:
                pass
    
    def create_task(self, title: str, description: str, assignee: str = None) -> Task:
        """创建任务"""
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:12]}",
            group_id=self.main_group_id,
            title=title,
            description=description,
            assignee=assignee
        )
        self.tasks[task.task_id] = task
        return task
    
    def get_tasks(self) -> List[Dict]:
        """获取所有任务"""
        return [asdict(task) for task in self.tasks.values()]
    
    def update_task_progress(self, task_id: str, progress: int, status: str = None):
        """更新任务进度"""
        if task_id in self.tasks:
            self.tasks[task_id].progress = progress
            if status:
                self.tasks[task_id].status = status
    
    def get_group_status(self) -> Dict:
        """获取群组状态"""
        return {
            'group_id': self.main_group_id,
            'group_name': self.main_group_name,
            'member_count': len(self.agents),
            'online_count': sum(1 for a in self.agents.values() if a.status == 'online'),
            'message_count': len(self.messages),
            'task_count': len(self.tasks)
        }


# 全局单例
group_manager = GroupManager()


if __name__ == '__main__':
    # 测试
    gm = GroupManager()
    
    # 测试创建消息
    msg = gm.create_message('user', 'shaoshuai', '大家好，开始工作！@采薇 @织锦')
    print(f"创建消息: {msg}")
    
    # 测试获取消息
    msgs = gm.get_messages()
    print(f"消息列表: {len(msgs)}条")
    
    # 测试获取Agent
    agents = gm.get_all_agents()
    print(f"Agent列表: {len(agents)}个")
    
    # 测试群组状态
    status = gm.get_group_status()
    print(f"群组状态: {status}")
