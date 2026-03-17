#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议纪要生成器
- 自动生成完整会议纪要
- 包含基本信息、各角色分析、讨论过程、关键决策、后续行动
- 支持导出Markdown和Word格式

Author: 南乔
Date: 2026-03-15
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# 导入模块
try:
    from collaboration_dashboard_v14 import AGENTS, AGENT_NAMES
except ImportError:
    from multi_round_discussion import AGENTS, AGENT_NAMES

from multi_round_discussion import RoundResult, DiscussionMessage


class MeetingMinutesGenerator:
    """会议纪要生成器"""
    
    def __init__(self):
        self.template_version = "V1.0"
    
    def generate(self, structured_intent: dict, discussion_result: dict) -> str:
        """
        生成会议纪要
        
        Args:
            structured_intent: 结构化意图
            discussion_result: 讨论结果
        
        Returns:
            Markdown格式的会议纪要
        """
        sections = [
            self._generate_title(),
            self._generate_basic_info(structured_intent, discussion_result),
            self._generate_customer_intent(structured_intent),
            self._generate_role_analysis(discussion_result.get('rounds', [])),
            self._generate_discussion_table(discussion_result.get('rounds', [])),
            self._generate_key_decisions(discussion_result.get('key_decisions', [])),
            self._generate_risks(discussion_result.get('rounds', [])),
            self._generate_outputs(structured_intent),
            self._generate_actions(structured_intent),
            self._generate_footer()
        ]
        
        return "\n\n".join(sections)
    
    def _generate_title(self) -> str:
        """生成标题"""
        return "# 会议纪要"
    
    def _generate_basic_info(self, structured_intent: dict, discussion_result: dict) -> str:
        """生成基本信息"""
        
        participants = structured_intent.get('participants', [])
        participants_cn = [AGENT_NAMES.get(p, p) for p in participants]
        
        rounds = discussion_result.get('rounds', [])
        round_count = len(rounds)
        
        consensus_reached = discussion_result.get('consensus_reached', False)
        consensus_status = "✅ 已达成" if consensus_reached else "⚠️ 未完全达成"
        
        return f"""## 一、基本信息

**📋 项目名称**：{structured_intent.get('project_name', '待定')}

**📌 任务类型**：{structured_intent.get('task_name', '需求分析')}

**🕐 会议时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}

**👥 参与人**：{'、'.join(participants_cn)}

**⚡ 复杂度**：{structured_intent.get('complexity', 'medium')}

**🔄 讨论轮次**：{round_count}轮

**✅ 共识状态**：{consensus_status}"""
    
    def _generate_customer_intent(self, structured_intent: dict) -> str:
        """生成客户意图"""
        
        return f"""## 二、客户意图

{structured_intent.get('structured_intent', '待明确')}"""
    
    def _generate_role_analysis(self, rounds) -> str:
        """生成各角色分析"""
        
        if not rounds:
            return "## 三、各角色分析\n\n暂无讨论内容"
        
        # 按角色分组（只取第一轮的发言作为专业分析）
        role_views = {}
        first_round = rounds[0] if rounds else None
        
        if first_round:
            # 支持dict和RoundResult两种格式
            if isinstance(first_round, dict):
                messages = first_round.get('messages', [])
                for msg in messages:
                    speaker_name = msg.get('speaker_name', msg.get('speaker', '未知'))
                    if speaker_name not in role_views:
                        role_views[speaker_name] = type('obj', (object,), {
                            'speaker_name': speaker_name,
                            'content': msg.get('content', '')
                        })()
            else:
                for msg in first_round.messages:
                    if msg.speaker_name not in role_views:
                        role_views[msg.speaker_name] = msg
        
        # 生成内容
        content = "## 三、各角色分析"
        
        for speaker_name, msg in role_views.items():
            agent = self._get_agent_by_name(speaker_name)
            role_name = agent.role if agent else "专家"
            
            # 提取关键观点（按句号分割，取前3句）
            content_text = msg.content if hasattr(msg, 'content') else str(msg)
            sentences = content_text.replace('\n', '。').split('。')
            key_points = [s.strip() for s in sentences if s.strip()][:3]
            
            content += f"\n\n### {role_name}（{speaker_name}）\n"
            for point in key_points:
                if point:
                    content += f"- {point}\n"
        
        return content
    
    def _generate_discussion_table(self, rounds) -> str:
        """生成讨论过程"""
        
        if not rounds:
            return "## 四、讨论过程\n\n暂无讨论内容"
        
        content = "## 四、讨论过程\n\n"
        
        for round_result in rounds:
            # 支持dict和RoundResult两种格式
            if isinstance(round_result, dict):
                round_num = round_result.get('round_num', 1)
                messages = round_result.get('messages', [])
                for msg in messages:
                    speaker_name = msg.get('speaker_name', msg.get('speaker', '未知'))
                    msg_content = msg.get('content', '')
                    msg_round = msg.get('round_num', round_num)
                    is_challenge = msg.get('is_challenge', False)
                    challenge_target = msg.get('challenge_target', '')
                    reply_to = msg.get('reply_to', '')
                    
                    # 观点摘要
                    summary = msg_content[:100].replace('\n', ' ')
                    if len(msg_content) > 100:
                        summary += "..."
                    
                    # 互动标记
                    interaction = ""
                    if is_challenge:
                        if challenge_target:
                            interaction = f" ⚠️ 质疑{challenge_target}"
                        else:
                            interaction = " ⚠️ 提出质疑"
                    elif reply_to:
                        interaction = f" → 回应{reply_to}"
                    
                    content += f"**第{msg_round}轮 | {speaker_name}**{interaction}\n\n{summary}\n\n---\n\n"
            else:
                for msg in round_result.messages:
                    # 观点摘要
                    summary = msg.content[:100].replace('\n', ' ')
                    if len(msg.content) > 100:
                        summary += "..."
                    
                    # 互动标记
                    interaction = ""
                    if msg.is_challenge:
                        if msg.challenge_target:
                            interaction = f" ⚠️ 质疑{msg.challenge_target}"
                        else:
                            interaction = " ⚠️ 提出质疑"
                    elif msg.reply_to:
                        interaction = f" → 回应{msg.reply_to}"
                    
                    content += f"**第{msg.round_num}轮 | {msg.speaker_name}**{interaction}\n\n{summary}\n\n---\n\n"
        
        return content
    
    def _generate_key_decisions(self, key_decisions: List[str]) -> str:
        """生成关键决策"""
        
        content = "## 五、关键决策\n"
        
        if not key_decisions:
            content += "\n暂无明确决策。"
            return content
        
        for i, decision in enumerate(key_decisions, 1):
            content += f"\n{i}. {decision}"
        
        return content
    
    def _generate_risks(self, rounds) -> str:
        """生成风险提示"""
        
        # 风险关键词
        risk_keywords = ['风险', '问题', '隐患', '挑战', '困难', '注意', '风险提示']
        
        risks = []
        for round_result in rounds:
            # 支持dict和RoundResult两种格式
            if isinstance(round_result, dict):
                messages = round_result.get('messages', [])
                for msg in messages:
                    speaker_name = msg.get('speaker_name', msg.get('speaker', '未知'))
                    content = msg.get('content', '')
                    for keyword in risk_keywords:
                        if keyword in content:
                            # 提取包含风险关键词的句子
                            sentences = content.replace('\n', '。').split('。')
                            for sentence in sentences:
                                if keyword in sentence and len(sentence) > 5:
                                    risks.append(f"{speaker_name}：{sentence.strip()}")
                            break
            else:
                for msg in round_result.messages:
                    for keyword in risk_keywords:
                        if keyword in msg.content:
                            # 提取包含风险关键词的句子
                            sentences = msg.content.replace('\n', '。').split('。')
                            for sentence in sentences:
                                if keyword in sentence and len(sentence) > 5:
                                    risks.append(f"{msg.speaker_name}：{sentence.strip()}")
                            break
        
        content = "## 六、风险提示\n"
        
        if not risks:
            content += "\n暂无明显风险提示。"
            return content
        
        # 去重
        unique_risks = list(set(risks))[:5]
        
        for i, risk in enumerate(unique_risks, 1):
            content += f"\n{i}. {risk}"
        
        return content
    
    def _generate_outputs(self, structured_intent: dict) -> str:
        """生成后续产出物"""
        
        outputs = structured_intent.get('outputs', [])
        
        content = "## 七、后续产出物\n\n"
        
        if not outputs:
            content += "待确定"
            return content
        
        for i, output in enumerate(outputs, 1):
            name = output.get('name', '待确定')
            owner = output.get('owner', '待定')
            
            # 预计完成时间：根据复杂度推算
            complexity = structured_intent.get('complexity', 'medium')
            days_map = {'low': 2, 'medium': 3, 'high': 5}
            days = days_map.get(complexity, 3)
            deadline = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            content += f"**{i}. {name}**\n   - 负责人：{owner}\n   - 预计完成：{deadline}\n\n"
        
        return content
    
    def _generate_actions(self, structured_intent: dict) -> str:
        """生成后续行动"""
        
        outputs = structured_intent.get('outputs', [])
        
        content = "## 八、后续行动\n\n"
        
        if not outputs:
            content += "待确定"
            return content
        
        for i, output in enumerate(outputs, 1):
            name = output.get('name', '待确定')
            owner = output.get('owner', '待定')
            
            # 截止日期
            complexity = structured_intent.get('complexity', 'medium')
            days_map = {'low': 2, 'medium': 3, 'high': 5}
            days = days_map.get(complexity, 3)
            deadline = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            action = f"完成{name}"
            content += f"**{i}. {action}**\n   - 负责人：{owner}\n   - 截止日期：{deadline}\n\n"
        
        return content
    
    def _generate_footer(self) -> str:
        """生成页脚"""
        
        return f"""---

*会议纪要由多智能体协作平台自动生成*
*模板版本：{self.template_version}*
*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
    
    def _get_agent_by_name(self, name: str):
        """根据名称获取Agent"""
        for agent_key, agent in AGENTS.items():
            if agent.name == name:
                return agent
        return None
    
    def export_to_file(self, content: str, filename: str = None) -> str:
        """
        导出到文件
        
        Args:
            content: 会议纪要内容
            filename: 文件名（可选）
        
        Returns:
            文件路径
        """
        import os
        
        if not filename:
            filename = f"会议纪要_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = os.path.join("/root/.openclaw/workspace/03_输出成果/会议纪要", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


# ==================== 测试用例 ====================
if __name__ == '__main__':
    # 创建测试数据
    from nanqiao_intent_analyzer import NanqiaoIntentAnalyzer
    
    analyzer = NanqiaoIntentAnalyzer()
    intent = analyzer.analyze("做一个智能客服系统的需求分析")
    
    # 模拟讨论结果
    from multi_round_discussion import RoundResult, DiscussionMessage
    
    mock_round = RoundResult(
        round_num=1,
        messages=[
            DiscussionMessage(
                round_num=1,
                speaker='caiwei',
                speaker_name='采薇',
                content='从需求分析角度，智能客服系统需要包含以下核心功能：智能问答、意图识别、多轮对话、知识库管理。验收标准为响应时间<2秒，准确率>90%。',
                is_challenge=False,
                challenge_target='',
                reply_to=''
            ),
            DiscussionMessage(
                round_num=1,
                speaker='yuheng',
                speaker_name='玉衡',
                content='从项目角度，建议分两期实施。第一期先实现核心功能，工期约2周。存在技术风险，需要提前验证AI模型的准确率。',
                is_challenge=False,
                challenge_target='',
                reply_to=''
            ),
        ],
        challenge_count=0,
        has_consensus=True
    )
    
    mock_result = {
        'rounds': [mock_round],
        'consensus_reached': True,
        'key_decisions': ['采用分两期实施策略', '先验证AI模型准确率']
    }
    
    # 生成会议纪要
    generator = MeetingMinutesGenerator()
    minutes = generator.generate(intent.__dict__, mock_result)
    
    print("=" * 60)
    print("会议纪要生成测试")
    print("=" * 60)
    print(minutes)
    
    # 导出到文件
    filepath = generator.export_to_file(minutes)
    print(f"\n✅ 已导出到：{filepath}")
