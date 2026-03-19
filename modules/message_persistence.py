#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息持久化模块 - V16.0
功能：消息存储、历史查询、缓存管理
作者：南乔 🌿
日期：2026-03-19
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading


class MessagePersistence:
    """消息持久化管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = '/root/.openclaw/workspace/data/messages.db'
        
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message (
                    msg_id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    from_type TEXT NOT NULL,
                    from_id TEXT NOT NULL,
                    from_name TEXT NOT NULL,
                    from_emoji TEXT,
                    content TEXT NOT NULL,
                    mentions TEXT,
                    reply_to TEXT,
                    seq INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 创建索引
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_time ON message(group_id, created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_seq ON message(seq)')
            except:
                pass
            
            # 任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task (
                    task_id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    assignee TEXT,
                    collaborators TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
            ''')
            
            # 决策表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decision (
                    decision_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    choice TEXT NOT NULL,
                    reason TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Agent记忆表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_memory (
                    memory_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER DEFAULT 50,
                    related_task TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT
                )
            ''')
            
            # 知识库表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    knowledge_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    keywords TEXT,
                    source_task TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def save_message(self, message: Dict) -> bool:
        """保存消息"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO message 
                    (msg_id, group_id, from_type, from_id, from_name, from_emoji, 
                     content, mentions, reply_to, seq, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message['msg_id'],
                    message['group_id'],
                    message['from_type'],
                    message['from_id'],
                    message['from_name'],
                    message.get('from_emoji', ''),
                    message['content'],
                    json.dumps(message.get('mentions', [])),
                    message.get('reply_to'),
                    message['seq'],
                    message['created_at']
                ))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    def get_messages(self, group_id: str, limit: int = 50, before_seq: int = None) -> List[Dict]:
        """获取消息列表"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if before_seq:
                    cursor.execute('''
                        SELECT * FROM message 
                        WHERE group_id = ? AND seq < ?
                        ORDER BY seq DESC
                        LIMIT ?
                    ''', (group_id, before_seq, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM message 
                        WHERE group_id = ?
                        ORDER BY seq DESC
                        LIMIT ?
                    ''', (group_id, limit))
                
                rows = cursor.fetchall()
                conn.close()
                
                messages = []
                for row in rows:
                    msg = dict(row)
                    msg['mentions'] = json.loads(msg['mentions']) if msg['mentions'] else []
                    messages.append(msg)
                
                # 反转顺序（从旧到新）
                messages.reverse()
                return messages
        except Exception as e:
            print(f"获取消息失败: {e}")
            return []
    
    def search_messages(self, group_id: str, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索消息"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM message 
                    WHERE group_id = ? AND content LIKE ?
                    ORDER BY seq DESC
                    LIMIT ?
                ''', (group_id, f'%{keyword}%', limit))
                
                rows = cursor.fetchall()
                conn.close()
                
                messages = []
                for row in rows:
                    msg = dict(row)
                    msg['mentions'] = json.loads(msg['mentions']) if msg['mentions'] else []
                    messages.append(msg)
                
                return messages
        except Exception as e:
            print(f"搜索消息失败: {e}")
            return []
    
    def save_task(self, task: Dict) -> bool:
        """保存任务"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO task 
                    (task_id, group_id, title, description, status, progress, 
                     assignee, collaborators, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task['task_id'],
                    task['group_id'],
                    task['title'],
                    task.get('description', ''),
                    task.get('status', 'pending'),
                    task.get('progress', 0),
                    task.get('assignee'),
                    json.dumps(task.get('collaborators', [])),
                    task['created_at'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"保存任务失败: {e}")
            return False
    
    def get_tasks(self, group_id: str = None, status: str = None) -> List[Dict]:
        """获取任务列表"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if group_id and status:
                    cursor.execute('''
                        SELECT * FROM task 
                        WHERE group_id = ? AND status = ?
                        ORDER BY created_at DESC
                    ''', (group_id, status))
                elif group_id:
                    cursor.execute('''
                        SELECT * FROM task 
                        WHERE group_id = ?
                        ORDER BY created_at DESC
                    ''', (group_id,))
                elif status:
                    cursor.execute('''
                        SELECT * FROM task 
                        WHERE status = ?
                        ORDER BY created_at DESC
                    ''', (status,))
                else:
                    cursor.execute('''
                        SELECT * FROM task 
                        ORDER BY created_at DESC
                    ''')
                
                rows = cursor.fetchall()
                conn.close()
                
                tasks = []
                for row in rows:
                    task = dict(row)
                    task['collaborators'] = json.loads(task['collaborators']) if task['collaborators'] else []
                    tasks.append(task)
                
                return tasks
        except Exception as e:
            print(f"获取任务失败: {e}")
            return []
    
    def save_agent_memory(self, agent_id: str, memory_type: str, content: str, 
                         importance: int = 50, related_task: str = None) -> bool:
        """保存Agent记忆"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{agent_id}"
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 设置过期时间
                if memory_type == 'short':
                    expires_at = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                elif memory_type == 'medium':
                    expires_at = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    expires_at = None
                
                cursor.execute('''
                    INSERT INTO agent_memory 
                    (memory_id, agent_id, memory_type, content, importance, 
                     related_task, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (memory_id, agent_id, memory_type, content, importance, 
                     related_task, created_at, expires_at))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"保存记忆失败: {e}")
            return False
    
    def get_agent_memories(self, agent_id: str, memory_type: str = None, 
                          limit: int = 10) -> List[Dict]:
        """获取Agent记忆"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 清理过期记忆
                cursor.execute('''
                    DELETE FROM agent_memory 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                
                if memory_type:
                    cursor.execute('''
                        SELECT * FROM agent_memory 
                        WHERE agent_id = ? AND memory_type = ?
                        ORDER BY importance DESC, created_at DESC
                        LIMIT ?
                    ''', (agent_id, memory_type, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM agent_memory 
                        WHERE agent_id = ?
                        ORDER BY importance DESC, created_at DESC
                        LIMIT ?
                    ''', (agent_id, limit))
                
                rows = cursor.fetchall()
                conn.commit()
                conn.close()
                
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取记忆失败: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 消息数量
                cursor.execute('SELECT COUNT(*) FROM message')
                message_count = cursor.fetchone()[0]
                
                # 任务数量
                cursor.execute('SELECT COUNT(*) FROM task')
                task_count = cursor.fetchone()[0]
                
                # 记忆数量
                cursor.execute('SELECT COUNT(*) FROM agent_memory')
                memory_count = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'message_count': message_count,
                    'task_count': task_count,
                    'memory_count': memory_count
                }
        except Exception as e:
            print(f"获取统计失败: {e}")
            return {
                'message_count': 0,
                'task_count': 0,
                'memory_count': 0
            }


# 全局单例
message_persistence = MessagePersistence()


if __name__ == '__main__':
    # 测试
    mp = MessagePersistence()
    
    # 测试保存消息
    test_msg = {
        'msg_id': 'msg_test_001',
        'group_id': 'jiuxing_main',
        'from_type': 'user',
        'from_id': 'shaoshuai',
        'from_name': '少帅',
        'from_emoji': '👤',
        'content': '测试消息',
        'mentions': ['caiwei'],
        'reply_to': None,
        'seq': 1,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    result = mp.save_message(test_msg)
    print(f"保存消息: {result}")
    
    # 测试获取消息
    msgs = mp.get_messages('jiuxing_main')
    print(f"消息列表: {len(msgs)}条")
    
    # 测试统计
    stats = mp.get_statistics()
    print(f"统计信息: {stats}")
