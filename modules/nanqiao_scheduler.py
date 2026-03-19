#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南乔调度器模块 - V16.0
功能：智能任务调度、Agent分配、风险预警、团队协调
作者：南乔 🌿
日期：2026-03-19
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re


class NanqiaoScheduler:
    """南乔调度器 - 团队Leader"""
    
    def __init__(self, group_manager, message_persistence):
        self.group_manager = group_manager
        self.message_persistence = message_persistence
        
        # Agent能力映射
        self.agent_capabilities = {
            'caiwei': ['需求分析', '需求文档', '用户故事', '验收标准'],
            'zhijin': ['架构设计', '技术选型', '系统架构', '技术方案'],
            'zhutai': ['售前方案', '竞品分析', '报价单', '销售话术'],
            'chengcai': ['方案设计', 'PPT设计', '方案撰写', '演示材料'],
            'gongchi': ['系统设计', '接口设计', '数据库设计', '技术规范'],
            'yuheng': ['项目管理', '风险管控', '项目计划', '进度跟踪'],
            'zhegui': ['知识管理', '资源整理', '学习计划', '文档归档'],
            'fuyao': ['任务协调', '团队调度', '进度监控', '冲突解决'],
            'tianong': ['开发实现', '代码编写', 'API开发', '技术实现'],
            'zhiwei': ['数据分析', '用户画像', '数据可视化', '报表分析']
        }
        
        # 任务类型到Agent的映射
        self.task_type_mapping = {
            '需求': 'caiwei',
            '需求文档': 'caiwei',
            '需求分析': 'caiwei',
            '架构': 'zhijin',
            '架构设计': 'zhijin',
            '技术选型': 'zhijin',
            '售前': 'zhutai',
            '竞品': 'zhutai',
            'PPT': 'chengcai',
            '方案': 'chengcai',
            '接口': 'gongchi',
            '数据库': 'gongchi',
            '系统设计': 'gongchi',
            '项目': 'yuheng',
            '风险': 'yuheng',
            '知识': 'zhegui',
            '协调': 'fuyao',
            '开发': 'tianong',
            '代码': 'tianong',
            '数据': 'zhiwei',
            '分析': 'zhiwei'
        }
    
    def analyze_task(self, task_description: str) -> Dict:
        """分析任务，确定负责人和协作人"""
        
        # 提取关键词
        keywords = self._extract_keywords(task_description)
        
        # 确定主负责人
        primary_agent = self._determine_primary_agent(keywords)
        
        # 确定协作人
        collaborators = self._determine_collaborators(keywords, primary_agent)
        
        # 估算工期
        estimated_duration = self._estimate_duration(task_description)
        
        # 识别风险
        risks = self._identify_risks(task_description)
        
        return {
            'primary_agent': primary_agent,
            'collaborators': collaborators,
            'keywords': keywords,
            'estimated_duration': estimated_duration,
            'risks': risks
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 检查任务类型关键词
        for keyword in self.task_type_mapping.keys():
            if keyword in text:
                keywords.append(keyword)
        
        return list(set(keywords))
    
    def _determine_primary_agent(self, keywords: List[str]) -> str:
        """确定主负责人"""
        if not keywords:
            return 'fuyao'  # 默认由扶摇协调
        
        # 统计每个Agent匹配的关键词数量
        agent_scores = {}
        for keyword in keywords:
            if keyword in self.task_type_mapping:
                agent_id = self.task_type_mapping[keyword]
                agent_scores[agent_id] = agent_scores.get(agent_id, 0) + 1
        
        # 返回得分最高的Agent
        if agent_scores:
            return max(agent_scores, key=agent_scores.get)
        
        return 'fuyao'
    
    def _determine_collaborators(self, keywords: List[str], primary_agent: str) -> List[str]:
        """确定协作人"""
        collaborators = []
        
        # 常见协作模式
        collaboration_patterns = {
            'caiwei': ['gongchi', 'yuheng'],  # 需求分析需要系统设计和项目管理
            'zhijin': ['gongchi', 'tianong'],  # 架构设计需要系统设计和开发
            'gongchi': ['tianong', 'yuheng'],  # 系统设计需要开发和项目管理
            'chengcai': ['caiwei', 'zhutai'],  # 方案设计需要需求分析和售前
        }
        
        if primary_agent in collaboration_patterns:
            collaborators = collaboration_patterns[primary_agent]
        
        return collaborators
    
    def _estimate_duration(self, task_description: str) -> str:
        """估算工期"""
        # 简单的工期估算逻辑
        if '系统' in task_description or '平台' in task_description:
            return '5-10天'
        elif '模块' in task_description:
            return '3-5天'
        elif '文档' in task_description or '分析' in task_description:
            return '1-3天'
        else:
            return '1-2天'
    
    def _identify_risks(self, task_description: str) -> List[str]:
        """识别风险"""
        risks = []
        
        risk_keywords = {
            '工期': '工期可能偏紧',
            '紧急': '时间紧迫，需要快速响应',
            '复杂': '需求复杂度较高',
            '新技术': '涉及新技术，需要学习成本',
            '集成': '系统集成可能有兼容性问题',
            '性能': '性能要求较高',
            '安全': '安全要求较高'
        }
        
        for keyword, risk in risk_keywords.items():
            if keyword in task_description:
                risks.append(risk)
        
        return risks
    
    def dispatch_task(self, task_description: str, user_message: str = None) -> Dict:
        """调度任务 - 南乔核心能力"""
        
        # 分析任务
        analysis = self.analyze_task(task_description)
        
        # 创建任务
        task = self.group_manager.create_task(
            title=task_description[:50],  # 取前50字符作为标题
            description=task_description,
            assignee=analysis['primary_agent']
        )
        
        # 更新任务协作人
        task.collaborators = analysis['collaborators']
        
        # 保存任务
        self.message_persistence.save_task({
            'task_id': task.task_id,
            'group_id': task.group_id,
            'title': task.title,
            'description': task.description,
            'status': 'pending',
            'progress': 0,
            'assignee': task.assignee,
            'collaborators': task.collaborators,
            'created_at': task.created_at
        })
        
        # 生成调度消息
        dispatch_message = self._generate_dispatch_message(task, analysis)
        
        # 发送消息到群
        msg = self.group_manager.create_message(
            from_type='agent',
            from_id='nanqiao',
            content=dispatch_message
        )
        
        # 保存消息
        self.message_persistence.save_message({
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
        
        return {
            'task': {
                'task_id': task.task_id,
                'title': task.title,
                'assignee': task.assignee,
                'collaborators': task.collaborators,
                'description': task.description,
                'created_at': task.created_at
            },
            'message': dispatch_message,
            'message_obj': {
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
            },
            'analysis': analysis
        }
    
    def _generate_dispatch_message(self, task, analysis: Dict) -> str:
        """生成调度消息"""
        
        agent = self.group_manager.get_agent(task.assignee)
        agent_name = agent.name if agent else task.assignee
        
        message = f"收到新任务：{task.title}\n\n"
        message += f"@{agent_name} 请负责此任务"
        
        if analysis['collaborators']:
            collaborator_names = []
            for collab_id in analysis['collaborators']:
                collab = self.group_manager.get_agent(collab_id)
                if collab:
                    collaborator_names.append(f"@{collab.name}")
            
            if collaborator_names:
                message += f"，{' '.join(collaborator_names)} 请协助"
        
        message += f"\n\n工期估算：{analysis['estimated_duration']}"
        
        if analysis['risks']:
            message += f"\n\n⚠️ 风险提示：\n"
            for risk in analysis['risks']:
                message += f"• {risk}\n"
        
        return message
    
    def handle_agent_response(self, agent_id: str, response: str, task_id: str = None):
        """处理Agent响应"""
        
        agent = self.group_manager.get_agent(agent_id)
        if not agent:
            return
        
        # 发送Agent消息到群
        msg = self.group_manager.create_message(
            from_type='agent',
            from_id=agent_id,
            content=response
        )
        
        # 保存消息
        self.message_persistence.save_message({
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
        
        # 检查是否是任务完成报告
        if '完成' in response and task_id:
            self.group_manager.update_task_progress(task_id, 100, 'completed')
    
    def generate_daily_summary(self) -> str:
        """生成每日总结"""
        
        # 获取今日任务
        tasks = self.message_persistence.get_tasks()
        
        # 统计
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
        running_tasks = len([t for t in tasks if t['status'] == 'running'])
        
        # 生成总结
        summary = f"📊 每日团队总结\n\n"
        summary += f"📋 任务统计：\n"
        summary += f"• 总任务：{total_tasks}个\n"
        summary += f"• 已完成：{completed_tasks}个\n"
        summary += f"• 进行中：{running_tasks}个\n\n"
        
        # Agent状态
        summary += f"👥 团队状态：\n"
        agents = self.group_manager.get_all_agents()
        for agent in agents:
            status_emoji = '🟢' if agent['status'] == 'online' else '🔵' if agent['status'] == 'busy' else '⚪'
            summary += f"• {status_emoji} {agent['emoji']}{agent['name']} - {agent['role']}\n"
        
        return summary
    
    def coordinate_collaboration(self, task_id: str, agents: List[str]):
        """协调多Agent协作"""
        
        message = f"🤝 协作提醒\n\n"
        
        agent_names = []
        for agent_id in agents:
            agent = self.group_manager.get_agent(agent_id)
            if agent:
                agent_names.append(f"@{agent.name}")
        
        message += f"{' '.join(agent_names)} 请协作完成此任务\n"
        message += f"任务ID：{task_id}"
        
        # 发送协调消息
        msg = self.group_manager.create_message(
            from_type='agent',
            from_id='nanqiao',
            content=message
        )
        
        return msg


# 用于后续集成
class SchedulerIntegration:
    """调度器集成类"""
    
    def __init__(self):
        from .group_manager import group_manager
        from .message_persistence import message_persistence
        
        self.scheduler = NanqiaoScheduler(group_manager, message_persistence)


if __name__ == '__main__':
    # 测试
    from group_manager import GroupManager
    from message_persistence import MessagePersistence
    
    gm = GroupManager()
    mp = MessagePersistence()
    scheduler = NanqiaoScheduler(gm, mp)
    
    # 测试任务分析
    analysis = scheduler.analyze_task('帮我做一个需求分析和架构设计')
    print(f"任务分析: {analysis}")
    
    # 测试任务调度
    result = scheduler.dispatch_task('帮我做一个AI智能配案系统的需求分析')
    print(f"调度结果: {result}")
