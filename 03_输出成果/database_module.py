#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化模块
- SQLite数据库存储
- 对话历史记录
- 决策追溯
- 统计分析

Author: 南乔
Date: 2026-03-14
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading


# ==================== 数据库配置 ====================
DB_PATH = Path("/root/.openclaw/workspace/03_输出成果/data/collaboration.db")


# ==================== 数据模型 ====================
@dataclass
class DiscussionRecord:
    """讨论记录"""
    id: Optional[int]
    session_id: str
    task: str
    task_code: str
    complexity: str
    start_time: datetime
    end_time: Optional[datetime]
    consensus_level: int
    participants: str  # JSON array
    key_points: str    # JSON array
    risks: str         # JSON array
    decisions: str     # JSON array
    output_template: str
    status: str  # active, completed, archived


@dataclass
class TurnRecord:
    """发言记录"""
    id: Optional[int]
    session_id: str
    turn_id: int
    speaker: str
    speaker_name: str
    speaker_role: str
    content: str
    timestamp: datetime
    msg_type: str
    is_challenging: bool
    reply_to: str
    phase: str  # 聚焦讨论、风险辩论、共识输出


@dataclass
class AgentStats:
    """Agent统计"""
    agent_id: str
    total_discussions: int
    total_turns: int
    total_challenges: int
    avg_consensus: float
    last_active: datetime


# ==================== 数据库管理器 ====================
class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._initialized = True
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 讨论记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discussions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    task TEXT NOT NULL,
                    task_code TEXT,
                    complexity TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    consensus_level INTEGER DEFAULT 0,
                    participants TEXT,
                    key_points TEXT,
                    risks TEXT,
                    decisions TEXT,
                    output_template TEXT,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 发言记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_id INTEGER NOT NULL,
                    speaker TEXT NOT NULL,
                    speaker_name TEXT,
                    speaker_role TEXT,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    msg_type TEXT DEFAULT 'answer',
                    is_challenging BOOLEAN DEFAULT 0,
                    reply_to TEXT,
                    phase TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES discussions(session_id)
                )
            ''')
            
            # Agent统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_stats (
                    agent_id TEXT PRIMARY KEY,
                    total_discussions INTEGER DEFAULT 0,
                    total_turns INTEGER DEFAULT 0,
                    total_challenges INTEGER DEFAULT 0,
                    avg_consensus REAL DEFAULT 0.0,
                    last_active DATETIME,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discussions_session ON discussions(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_turns_speaker ON turns(speaker)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discussions_status ON discussions(status)')
            
            conn.commit()
    
    # ==================== 讨论记录操作 ====================
    
    def create_discussion(self, session_id: str, task: str, task_code: str = '',
                         complexity: str = 'medium', output_template: str = '') -> int:
        """创建讨论记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO discussions 
                (session_id, task, task_code, complexity, start_time, output_template, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            ''', (session_id, task, task_code, complexity, datetime.now(), output_template))
            conn.commit()
            return cursor.lastrowid
    
    def update_discussion(self, session_id: str, **kwargs):
        """更新讨论记录"""
        allowed_fields = ['end_time', 'consensus_level', 'participants', 
                         'key_points', 'risks', 'decisions', 'status']
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return
        
        values.append(session_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE discussions 
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', values)
            conn.commit()
    
    def get_discussion(self, session_id: str) -> Optional[Dict]:
        """获取讨论记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM discussions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_discussions(self, status: str = None, limit: int = 20, offset: int = 0) -> List[Dict]:
        """列出讨论记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM discussions 
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (status, limit, offset))
            else:
                cursor.execute('''
                    SELECT * FROM discussions 
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 发言记录操作 ====================
    
    def add_turn(self, session_id: str, turn_id: int, speaker: str, 
                 speaker_name: str, speaker_role: str, content: str,
                 msg_type: str = 'answer', is_challenging: bool = False,
                 reply_to: str = '', phase: str = '聚焦讨论') -> int:
        """添加发言记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO turns
                (session_id, turn_id, speaker, speaker_name, speaker_role, 
                 content, timestamp, msg_type, is_challenging, reply_to, phase)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, turn_id, speaker, speaker_name, speaker_role,
                  content, datetime.now(), msg_type, is_challenging, reply_to, phase))
            conn.commit()
            return cursor.lastrowid
    
    def get_turns(self, session_id: str) -> List[Dict]:
        """获取讨论的所有发言"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM turns 
                WHERE session_id = ?
                ORDER BY turn_id ASC
            ''', (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_turns(self, keyword: str, limit: int = 50) -> List[Dict]:
        """搜索发言内容"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, d.task 
                FROM turns t
                JOIN discussions d ON t.session_id = d.session_id
                WHERE t.content LIKE ?
                ORDER BY t.timestamp DESC
                LIMIT ?
            ''', (f'%{keyword}%', limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Agent统计操作 ====================
    
    def update_agent_stats(self, agent_id: str, discussions_delta: int = 0,
                          turns_delta: int = 0, challenges_delta: int = 0,
                          consensus: int = None):
        """更新Agent统计"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否存在
            cursor.execute('SELECT * FROM agent_stats WHERE agent_id = ?', (agent_id,))
            exists = cursor.fetchone()
            
            if exists:
                # 更新
                if consensus is not None:
                    cursor.execute('''
                        UPDATE agent_stats 
                        SET total_discussions = total_discussions + ?,
                            total_turns = total_turns + ?,
                            total_challenges = total_challenges + ?,
                            avg_consensus = (avg_consensus * total_discussions + ?) / (total_discussions + 1),
                            last_active = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE agent_id = ?
                    ''', (discussions_delta, turns_delta, challenges_delta, 
                          consensus, datetime.now(), agent_id))
                else:
                    cursor.execute('''
                        UPDATE agent_stats 
                        SET total_discussions = total_discussions + ?,
                            total_turns = total_turns + ?,
                            total_challenges = total_challenges + ?,
                            last_active = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE agent_id = ?
                    ''', (discussions_delta, turns_delta, challenges_delta,
                          datetime.now(), agent_id))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO agent_stats 
                    (agent_id, total_discussions, total_turns, total_challenges, 
                     avg_consensus, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (agent_id, discussions_delta, turns_delta, challenges_delta,
                      consensus or 0, datetime.now()))
            
            conn.commit()
    
    def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """获取Agent统计"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agent_stats WHERE agent_id = ?', (agent_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_agent_stats(self) -> List[Dict]:
        """获取所有Agent统计"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM agent_stats 
                ORDER BY total_turns DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 统计分析 ====================
    
    def get_statistics(self) -> Dict:
        """获取整体统计"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 讨论总数
            cursor.execute('SELECT COUNT(*) FROM discussions')
            total_discussions = cursor.fetchone()[0]
            
            # 发言总数
            cursor.execute('SELECT COUNT(*) FROM turns')
            total_turns = cursor.fetchone()[0]
            
            # 质疑总数
            cursor.execute('SELECT COUNT(*) FROM turns WHERE is_challenging = 1')
            total_challenges = cursor.fetchone()[0]
            
            # 平均共识度
            cursor.execute('SELECT AVG(consensus_level) FROM discussions WHERE consensus_level > 0')
            avg_consensus = cursor.fetchone()[0] or 0
            
            # 任务类型分布
            cursor.execute('''
                SELECT task_code, COUNT(*) as count 
                FROM discussions 
                WHERE task_code IS NOT NULL AND task_code != ''
                GROUP BY task_code
                ORDER BY count DESC
                LIMIT 10
            ''')
            task_distribution = [{'task_code': row[0], 'count': row[1]} 
                                for row in cursor.fetchall()]
            
            return {
                'total_discussions': total_discussions,
                'total_turns': total_turns,
                'total_challenges': total_challenges,
                'avg_consensus': round(avg_consensus, 1),
                'task_distribution': task_distribution
            }


# ==================== 全局实例 ====================
db = DatabaseManager()


# ==================== 测试 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("数据持久化模块测试")
    print("=" * 60)
    
    # 创建讨论
    session_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    print(f"\n1. 创建讨论: {session_id}")
    db.create_discussion(session_id, "智能客服系统需求分析", "REQ-02", "medium", "需求规格说明书")
    
    # 添加发言
    print("\n2. 添加发言记录...")
    db.add_turn(session_id, 1, 'BA', '采薇', '需求分析师', 
               '【需求分析】我梳理了核心需求。主要功能点已识别。')
    db.add_turn(session_id, 2, 'TA', '织锦', '技术架构师',
               '【架构设计】推荐微服务架构。', is_challenging=False)
    db.add_turn(session_id, 3, 'CA', '筑台', '成本分析师',
               '【成本质疑】微服务架构成本较高。', is_challenging=True, reply_to='织锦')
    
    # 更新讨论
    print("\n3. 更新讨论记录...")
    db.update_discussion(session_id,
                         end_time=datetime.now(),
                         consensus_level=75,
                         participants=['采薇', '织锦', '筑台'],
                         key_points=['核心需求已识别', '推荐微服务架构'],
                         risks=['微服务架构成本较高'],
                         status='completed')
    
    # 更新Agent统计
    print("\n4. 更新Agent统计...")
    db.update_agent_stats('BA', discussions_delta=1, turns_delta=1, consensus=75)
    db.update_agent_stats('TA', discussions_delta=1, turns_delta=1, consensus=75)
    db.update_agent_stats('CA', discussions_delta=1, turns_delta=1, challenges_delta=1, consensus=75)
    
    # 查询讨论
    print("\n5. 查询讨论记录...")
    discussion = db.get_discussion(session_id)
    print(f"   任务: {discussion['task']}")
    print(f"   共识度: {discussion['consensus_level']}%")
    print(f"   状态: {discussion['status']}")
    
    # 查询发言
    print("\n6. 查询发言记录...")
    turns = db.get_turns(session_id)
    for turn in turns:
        challenge_mark = " [质疑]" if turn['is_challenging'] else ""
        print(f"   [{turn['turn_id']}] {turn['speaker_name']}{challenge_mark}: {turn['content'][:30]}...")
    
    # 统计信息
    print("\n7. 统计信息...")
    stats = db.get_statistics()
    print(f"   总讨论数: {stats['total_discussions']}")
    print(f"   总发言数: {stats['total_turns']}")
    print(f"   总质疑数: {stats['total_challenges']}")
    print(f"   平均共识度: {stats['avg_consensus']}%")
    
    print("\n✅ 数据持久化模块测试完成")
    print(f"   数据库位置: {DB_PATH}")
