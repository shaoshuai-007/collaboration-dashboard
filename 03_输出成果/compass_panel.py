#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程 - 实时协作面板
PyQt6 GUI Application

Author: 南乔
Date: 2026-03-13
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QScrollArea, QProgressBar, QGroupBox, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush


# 配色方案（三原色定理）
COLORS = {
    'primary': '#C93832',      # 电信红 60%
    'secondary': '#006EBD',    # 深蓝 30%
    'neutral': '#595959',      # 灰色 10%
    'bg_dark': '#1a1a2e',
    'bg_light': '#16213e',
    'text_white': '#ffffff',
    'text_gray': '#888888',
    'success': '#2d5a27',
    'warning': '#f39c12',
    'error': '#e74c3c'
}


class AgentCard(QFrame):
    """Agent状态卡片"""
    
    def __init__(self, name: str, role: str, emoji: str, status: str = 'pending'):
        super().__init__()
        self.name = name
        self.role = role
        self.emoji = emoji
        self.status = status
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # Agent名称
        name_label = QLabel(f"{self.emoji} {self.name}")
        name_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_white']};")
        layout.addWidget(name_label)
        
        # Agent角色
        role_label = QLabel(self.role)
        role_label.setFont(QFont("Microsoft YaHei", 10))
        role_label.setStyleSheet(f"color: {COLORS['text_gray']};")
        layout.addWidget(role_label)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Microsoft YaHei", 9))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.update_status(self.status)
        self.setStyleSheet(f"""
            AgentCard {{
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                border-left: 4px solid {COLORS['neutral']};
            }}
        """)
    
    def update_status(self, status: str):
        """更新状态"""
        self.status = status
        status_config = {
            'done': {'text': '✅ 已完成', 'color': COLORS['success'], 'border': COLORS['success']},
            'active': {'text': '🔄 进行中', 'color': COLORS['primary'], 'border': COLORS['primary']},
            'pending': {'text': '⏳ 等待中', 'color': COLORS['neutral'], 'border': COLORS['neutral']},
            'error': {'text': '❌ 异常', 'color': COLORS['error'], 'border': COLORS['error']}
        }
        
        config = status_config.get(status, status_config['pending'])
        self.status_label.setText(config['text'])
        self.status_label.setStyleSheet(f"""
            background-color: {config['color']};
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        
        # 更新边框颜色
        self.setStyleSheet(f"""
            AgentCard {{
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                border-left: 4px solid {config['border']};
            }}
        """)


class MessageBubble(QFrame):
    """消息气泡"""
    
    def __init__(self, agent_name: str, emoji: str, content: str, is_user: bool = False):
        super().__init__()
        self.agent_name = agent_name
        self.emoji = emoji
        self.content = content
        self.is_user = is_user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 发送者
        from_label = QLabel(f"{self.emoji} {self.agent_name}")
        from_label.setFont(QFont("Microsoft YaHei", 9))
        from_label.setStyleSheet(f"color: {COLORS['text_gray']};")
        layout.addWidget(from_label)
        
        # 消息内容
        content_label = QLabel(self.content)
        content_label.setFont(QFont("Microsoft YaHei", 11))
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"color: {COLORS['text_white']};")
        layout.addWidget(content_label)
        
        # 时间戳
        time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        time_label.setFont(QFont("Microsoft YaHei", 8))
        time_label.setStyleSheet(f"color: {COLORS['text_gray']};")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(time_label)
        
        # 样式
        bg_color = COLORS['primary'] if self.is_user else COLORS['secondary']
        self.setStyleSheet(f"""
            MessageBubble {{
                background-color: rgba({self._hex_to_rgb(bg_color)}, 0.3);
                border-radius: 12px;
            }}
        """)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """十六进制转RGB"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"


class CollaborationPanel(QMainWindow):
    """实时协作面板主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧭 指南针工程 - 实时协作面板")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Agent数据
        self.agents = [
            {'name': '采薇', 'role': '需求分析专家', 'emoji': '🌸', 'status': 'done'},
            {'name': '织锦', 'role': '架构设计师', 'emoji': '🧵', 'status': 'active'},
            {'name': '筑台', 'role': '售前工程师', 'emoji': '🏗️', 'status': 'done'},
            {'name': '呈彩', 'role': '方案PPT设计师', 'emoji': '🎨', 'status': 'pending'},
            {'name': '工尺', 'role': '详细设计师', 'emoji': '📐', 'status': 'pending'},
            {'name': '玉衡', 'role': '项目经理', 'emoji': '⚖️', 'status': 'pending'},
            {'name': '折桂', 'role': '资源管家', 'emoji': '📚', 'status': 'done'},
            {'name': '扶摇', 'role': '总指挥', 'emoji': '🌀', 'status': 'done'},
            {'name': '南乔', 'role': '主控Agent', 'emoji': '🌿', 'status': 'active'},
        ]
        
        # 消息数据
        self.messages = [
            {'agent': '采薇', 'emoji': '🌸', 'content': '采用"先诊断后开方"方法论，完成三层根因分析。核心需求：准确率75%→90%、响应3s→<1s、500+标签维度。'},
            {'agent': '织锦', 'emoji': '🧵', 'content': '评审采薇产出：方法论正确✅ 需求可实现但具挑战🔴 准确率目标建议分阶段达成(80%→85%→90%)。'},
            {'agent': '扶摇', 'emoji': '🌀', 'content': '反馈合理，批准调整：工期修正为7-8月、数据质量评估、降级机制、特征注册中心纳入二期。'},
            {'agent': '筑台', 'emoji': '🏗️', 'content': '成本更新：低配445万/年(+23.6%)、高配700万/年(+20.7%)。双模型切换：文心主+通义备。'},
            {'agent': '织锦', 'emoji': '🧵', 'content': '架构方案：六层架构（接入→网关→业务→AI推理→特征工程→数据存储）。核心模块：配案决策引擎+特征注册中心+降级策略。'},
        ]
        
        self.agent_cards = {}
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 标题区域
        self.setup_header(main_layout)
        
        # Agent状态网格
        self.setup_agents_grid(main_layout)
        
        # 消息面板
        self.setup_chat_panel(main_layout)
        
        # 进度和统计
        self.setup_stats_panel(main_layout)
    
    def setup_header(self, parent_layout):
        """标题区域"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 10px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(8)
        
        # 主标题
        title = QLabel("🧭 指南针工程 - 实时协作面板")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("湖北电渠AI智能配案系统升级 | 9 Agent协作中")
        subtitle.setFont(QFont("Microsoft YaHei", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_gray']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        parent_layout.addWidget(header_frame)
    
    def setup_agents_grid(self, parent_layout):
        """Agent状态网格"""
        agents_frame = QFrame()
        agents_layout = QGridLayout(agents_frame)
        agents_layout.setSpacing(12)
        
        for i, agent in enumerate(self.agents):
            card = AgentCard(
                name=agent['name'],
                role=agent['role'],
                emoji=agent['emoji'],
                status=agent['status']
            )
            row = i // 3
            col = i % 3
            agents_layout.addWidget(card, row, col)
            self.agent_cards[agent['name']] = card
        
        parent_layout.addWidget(agents_frame)
    
    def setup_chat_panel(self, parent_layout):
        """消息面板"""
        chat_group = QGroupBox("💬 实时对话流")
        chat_group.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        chat_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_white']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
            }}
        """)
        
        chat_layout = QVBoxLayout(chat_group)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }}
        """)
        
        # 消息容器
        messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(messages_widget)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.addStretch()
        
        # 添加消息
        for msg in self.messages:
            bubble = MessageBubble(
                agent_name=msg['agent'],
                emoji=msg['emoji'],
                content=msg['content']
            )
            self.messages_layout.addWidget(bubble)
        
        scroll.setWidget(messages_widget)
        chat_layout.addWidget(scroll)
        
        parent_layout.addWidget(chat_group, stretch=1)
    
    def setup_stats_panel(self, parent_layout):
        """统计面板"""
        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(12)
        
        # 进度条
        progress_label = QLabel("📊 项目进度")
        progress_label.setFont(QFont("Microsoft YaHei", 10))
        progress_label.setStyleSheet(f"color: {COLORS['text_gray']};")
        stats_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(70)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.1);
                height: 8px;
                text-align: center;
                color: white;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 4px;
            }}
        """)
        stats_layout.addWidget(self.progress_bar)
        
        # 统计数据
        stats_h_layout = QHBoxLayout()
        stats_items = [
            ("💬 消息", "15条"),
            ("⏱️ 耗时", "12分钟"),
            ("🎯 活跃Agent", "9/9"),
            ("📍 当前阶段", "架构评审")
        ]
        
        for icon_text, value in stats_items:
            stat_label = QLabel(f"{icon_text}: {value}")
            stat_label.setFont(QFont("Microsoft YaHei", 10))
            stat_label.setStyleSheet(f"color: {COLORS['text_gray']};")
            stats_h_layout.addWidget(stat_label)
        
        stats_layout.addLayout(stats_h_layout)
        parent_layout.addWidget(stats_frame)
    
    def apply_dark_theme(self):
        """应用深色主题"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['bg_dark']}, stop:1 {COLORS['bg_light']});
            }}
            QWidget {{
                color: {COLORS['text_white']};
            }}
        """)
    
    def add_message(self, agent_name: str, emoji: str, content: str):
        """添加新消息"""
        bubble = MessageBubble(agent_name, emoji, content)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
    
    def update_agent_status(self, agent_name: str, status: str):
        """更新Agent状态"""
        if agent_name in self.agent_cards:
            self.agent_cards[agent_name].update_status(status)
    
    def update_progress(self, value: int):
        """更新进度"""
        self.progress_bar.setValue(value)


def main():
    app = QApplication(sys.argv)
    
    # 设置应用字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建主窗口
    window = CollaborationPanel()
    window.show()
    
    # 示例：添加新消息
    QTimer.singleShot(3000, lambda: window.add_message(
        '筑台', '🏗️', 
        '技术选型建议：文心主模型 + 通义备用 + 三级降级架构。年度成本优化至36万。'
    ))
    
    # 示例：更新Agent状态
    QTimer.singleShot(5000, lambda: window.update_agent_status('织锦', 'done'))
    QTimer.singleShot(5000, lambda: window.update_agent_status('呈彩', 'active'))
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
