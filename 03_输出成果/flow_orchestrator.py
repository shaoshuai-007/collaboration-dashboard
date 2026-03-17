#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三阶段协作流程编排器
- 阶段一：聚焦讨论（精准调度）
- 阶段二：风险辩论（全员参与）
- 阶段三：共识输出（结构化文档）

Author: 南乔
Date: 2026-03-14
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json


# ==================== 流程阶段定义 ====================
class Phase(Enum):
    """协作流程阶段"""
    FOCUS_DISCUSSION = "聚焦讨论"
    RISK_DEBATE = "风险辩论"
    CONSENSUS_OUTPUT = "共识输出"


@dataclass
class PhaseConfig:
    """阶段配置"""
    phase: Phase
    trigger_condition: str
    participants_rule: str
    max_rounds: int
    time_limit_seconds: int


# 阶段配置
PHASE_CONFIGS = {
    Phase.FOCUS_DISCUSSION: PhaseConfig(
        phase=Phase.FOCUS_DISCUSSION,
        trigger_condition="任务开始时自动触发",
        participants_rule="RACI矩阵中R和A角色必选，C角色按复杂度选择",
        max_rounds=5,
        time_limit_seconds=120
    ),
    Phase.RISK_DEBATE: PhaseConfig(
        phase=Phase.RISK_DEBATE,
        trigger_condition="高复杂度任务触发",
        participants_rule="所有Agent参与，重点质疑风险",
        max_rounds=3,
        time_limit_seconds=90
    ),
    Phase.CONSENSUS_OUTPUT: PhaseConfig(
        phase=Phase.CONSENSUS_OUTPUT,
        trigger_condition="讨论结束后自动触发",
        participants_rule="PM（项目经理）整合输出",
        max_rounds=1,
        time_limit_seconds=30
    )
}


# ==================== 讨论状态管理 ====================
@dataclass
class DiscussionState:
    """讨论状态"""
    current_phase: Phase
    current_round: int
    current_speaker: Optional[str]
    speaking_order: List[str]
    challenges: List[Tuple[str, str, str]]  # (质疑者, 被质疑者, 质疑内容)
    agreements: List[Tuple[str, str]]  # (同意者, 同意内容)
    key_points: List[str]
    risks: List[str]
    decisions: List[str]
    consensus_level: int
    phase_history: List[Dict]
    start_time: datetime
    
    def to_dict(self) -> Dict:
        return {
            'current_phase': self.current_phase.value,
            'current_round': self.current_round,
            'current_speaker': self.current_speaker,
            'speaking_order': self.speaking_order,
            'challenges_count': len(self.challenges),
            'agreements_count': len(self.agreements),
            'key_points_count': len(self.key_points),
            'risks_count': len(self.risks),
            'decisions_count': len(self.decisions),
            'consensus_level': self.consensus_level,
            'phase_history': [
                {'phase': p['phase'].value, 'rounds': p['rounds']}
                for p in self.phase_history
            ]
        }


# ==================== 流程编排器 ====================
class FlowOrchestrator:
    """三阶段流程编排器"""
    
    def __init__(self):
        self.phase_configs = PHASE_CONFIGS
        self.state: Optional[DiscussionState] = None
    
    def initialize(self, schedule_result: Dict) -> DiscussionState:
        """
        初始化讨论流程
        
        Args:
            schedule_result: 智能调度结果
        
        Returns:
            初始状态
        """
        complexity = schedule_result.get('complexity', 'medium')
        discussion_flow = schedule_result.get('discussion_flow', [])
        
        self.state = DiscussionState(
            current_phase=Phase.FOCUS_DISCUSSION,
            current_round=0,
            current_speaker=None,
            speaking_order=discussion_flow.copy(),
            challenges=[],
            agreements=[],
            key_points=[],
            risks=[],
            decisions=[],
            consensus_level=0,
            phase_history=[],
            start_time=datetime.now()
        )
        
        return self.state
    
    def next_speaker(self) -> Optional[str]:
        """
        获取下一个发言者
        
        Returns:
            Agent ID 或 None（表示阶段结束）
        """
        if not self.state:
            return None
        
        # 当前阶段是否还有发言者
        if self.state.current_round < len(self.state.speaking_order):
            self.state.current_round += 1
            self.state.current_speaker = self.state.speaking_order[self.state.current_round - 1]
            return self.state.current_speaker
        
        # 当前阶段结束，判断是否进入下一阶段
        return self._advance_phase()
    
    def _advance_phase(self) -> Optional[str]:
        """推进到下一阶段"""
        # 记录当前阶段历史
        self.state.phase_history.append({
            'phase': self.state.current_phase,
            'rounds': self.state.current_round
        })
        
        # 判断下一阶段
        if self.state.current_phase == Phase.FOCUS_DISCUSSION:
            # 检查是否需要风险辩论
            if self._should_trigger_risk_debate():
                self.state.current_phase = Phase.RISK_DEBATE
                self.state.current_round = 0
                self.state.speaking_order = self._get_risk_debate_order()
                return 'nanqiao'  # 南乔宣布进入风险辩论
            else:
                # 直接进入共识输出
                return self._enter_consensus_phase()
        
        elif self.state.current_phase == Phase.RISK_DEBATE:
            return self._enter_consensus_phase()
        
        # 流程结束
        return None
    
    def _should_trigger_risk_debate(self) -> bool:
        """判断是否触发风险辩论"""
        # 条件1：有重大质疑
        if len(self.state.challenges) >= 2:
            return True
        
        # 条件2：共识度低
        if self.state.consensus_level < 60:
            return True
        
        # 条件3：有明确风险
        if len(self.state.risks) >= 1:
            return True
        
        return False
    
    def _get_risk_debate_order(self) -> List[str]:
        """获取风险辩论发言顺序"""
        # 所有Agent参与，但质疑者优先
        all_agents = ['BA', 'TA', 'UX', 'RA', 'CA', 'PM', 'PD', 'SD', 'QA']
        
        # 质疑者优先
        challengers = [c[0] for c in self.state.challenges]
        others = [a for a in all_agents if a not in challengers]
        
        return challengers + others
    
    def _enter_consensus_phase(self) -> str:
        """进入共识输出阶段"""
        self.state.current_phase = Phase.CONSENSUS_OUTPUT
        self.state.current_round = 0
        self.state.speaking_order = ['PM']  # PM整合输出
        return 'nanqiao'  # 南乔宣布进入共识输出
    
    def record_response(self, agent_id: str, content: str, is_challenge: bool = False, 
                       reply_to: str = "", agreements: List[str] = None, risks: List[str] = None):
        """
        记录Agent响应
        
        Args:
            agent_id: Agent ID
            content: 响应内容
            is_challenge: 是否质疑
            reply_to: 回复对象
            agreements: 同意点
            risks: 风险点
        """
        if not self.state:
            return
        
        if is_challenge and reply_to:
            self.state.challenges.append((agent_id, reply_to, content))
        
        if agreements:
            for point in agreements:
                self.state.agreements.append((agent_id, point))
                if point not in self.state.key_points:
                    self.state.key_points.append(point)
        
        if risks:
            for risk in risks:
                if risk not in self.state.risks:
                    self.state.risks.append(risk)
        
        # 更新共识度
        self._update_consensus_level()
    
    def _update_consensus_level(self):
        """更新共识度"""
        if not self.state:
            return
        
        total_turns = self.state.current_round
        challenges_count = len(self.state.challenges)
        
        if total_turns == 0:
            self.state.consensus_level = 100
        else:
            # 基础共识度 = 100 - 质疑数 * 10
            base = 100 - challenges_count * 10
            # 同意点加分
            agreement_bonus = min(len(self.state.agreements) * 5, 20)
            # 风险暴露扣分
            risk_penalty = min(len(self.state.risks) * 5, 15)
            
            self.state.consensus_level = max(0, min(100, base + agreement_bonus - risk_penalty))
    
    def generate_consensus_report(self, task: str, output_template: str) -> Dict:
        """
        生成共识报告
        
        Returns:
            共识报告数据
        """
        if not self.state:
            return {}
        
        return {
            'task': task,
            'output_template': output_template,
            'consensus_level': self.state.consensus_level,
            'key_points': self.state.key_points,
            'risks': self.state.risks,
            'decisions': self.state.decisions,
            'challenges': [
                {'challenger': c[0], 'target': c[1], 'content': c[2]}
                for c in self.state.challenges
            ],
            'phase_summary': [
                {
                    'phase': p['phase'].value,
                    'rounds': p['rounds'],
                    'config': {
                        'max_rounds': self.phase_configs[p['phase']].max_rounds,
                        'time_limit': self.phase_configs[p['phase']].time_limit_seconds
                    }
                }
                for p in self.state.phase_history
            ],
            'duration_seconds': (datetime.now() - self.state.start_time).total_seconds()
        }
    
    def get_phase_prompt(self) -> str:
        """获取当前阶段的提示语"""
        if not self.state:
            return ""
        
        phase = self.state.current_phase
        config = self.phase_configs[phase]
        
        prompts = {
            Phase.FOCUS_DISCUSSION: f"""【阶段一：聚焦讨论】
目标：针对任务进行专业深入的分析
参与角色：{', '.join(self.state.speaking_order)}
最大轮次：{config.max_rounds}轮
时限：{config.time_limit_seconds}秒

请基于您的专业领域发表意见，如有不同观点请明确指出。""",
            
            Phase.RISK_DEBATE: f"""【阶段二：风险辩论】
目标：充分暴露方案潜在风险
参与角色：全员参与
最大轮次：{config.max_rounds}轮
时限：{config.time_limit_seconds}秒

请重点质疑方案中可能存在的风险和问题，确保决策质量。""",
            
            Phase.CONSENSUS_OUTPUT: f"""【阶段三：共识输出】
目标：整合讨论结果，形成结构化输出
产出物：{config}
共识度：{self.state.consensus_level}%

项目经理请整合各方意见，输出最终结论。"""
        }
        
        return prompts.get(phase, "")
    
    def is_flow_complete(self) -> bool:
        """判断流程是否完成"""
        if not self.state:
            return False
        
        return self.state.current_phase == Phase.CONSENSUS_OUTPUT and self.state.current_round >= 1


# ==================== 流程执行器 ====================
class FlowExecutor:
    """流程执行器 - 用于实际执行讨论流程"""
    
    def __init__(self, orchestrator: FlowOrchestrator):
        self.orchestrator = orchestrator
    
    def execute_phase(self, phase: Phase, agents: List, memory, responder) -> Dict:
        """
        执行一个阶段的讨论
        
        Args:
            phase: 阶段
            agents: Agent字典
            memory: 对话记忆
            responder: 响应生成器
        
        Returns:
            阶段执行结果
        """
        results = []
        max_rounds = self.orchestrator.phase_configs[phase].max_rounds
        
        for round_num in range(max_rounds):
            speaker = self.orchestrator.next_speaker()
            
            if speaker is None:
                break
            
            if speaker == 'nanqiao':
                # 南乔宣布阶段转换
                prompt = self.orchestrator.get_phase_prompt()
                memory.add_turn('nanqiao', '南乔', prompt, msg_type='system')
                results.append({'speaker': 'nanqiao', 'type': 'phase_transition'})
                continue
            
            if speaker not in agents:
                continue
            
            # 生成响应
            agent = agents[speaker]
            task = memory.current_task
            response, is_challenge, reply_to = responder.generate(agent, task, memory)
            
            # 记录响应
            memory.add_turn(speaker, agent.name, response, 
                          is_challenging=is_challenge, reply_to=reply_to)
            
            # 分析响应内容
            agreements = self._extract_agreements(response)
            risks = self._extract_risks(response)
            
            self.orchestrator.record_response(
                speaker, response, is_challenge, reply_to, agreements, risks
            )
            
            results.append({
                'speaker': speaker,
                'content': response,
                'is_challenge': is_challenge,
                'reply_to': reply_to,
                'agreements': agreements,
                'risks': risks
            })
        
        return {
            'phase': phase.value,
            'rounds': len([r for r in results if r.get('type') != 'phase_transition']),
            'results': results
        }
    
    def _extract_agreements(self, content: str) -> List[str]:
        """从响应中提取同意点"""
        agreements = []
        keywords = ['同意', '认可', '支持', '可行', '合理']
        
        for keyword in keywords:
            if keyword in content:
                # 简单提取：找到关键词所在句子
                sentences = content.split('。')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) > 5:
                        agreements.append(sentence.strip())
                        break
        
        return agreements[:2]  # 最多提取2个
    
    def _extract_risks(self, content: str) -> List[str]:
        """从响应中提取风险点"""
        risks = []
        keywords = ['风险', '问题', '隐患', '挑战', '不确定性']
        
        for keyword in keywords:
            if keyword in content:
                sentences = content.split('。')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) > 5:
                        risks.append(sentence.strip())
                        break
        
        return risks[:2]  # 最多提取2个


# ==================== 测试 ====================
if __name__ == '__main__':
    # 创建编排器
    orchestrator = FlowOrchestrator()
    
    # 模拟调度结果
    schedule_result = {
        'task_code': 'REQ-02',
        'task_name': '需求分析',
        'complexity': 'medium',
        'discussion_flow': ['BA', 'TA', 'PM'],
        'output_template': '需求规格说明书(SRS)'
    }
    
    # 初始化
    state = orchestrator.initialize(schedule_result)
    print("=" * 60)
    print("三阶段协作流程编排器测试")
    print("=" * 60)
    print(f"\n初始状态：")
    print(f"  当前阶段：{state.current_phase.value}")
    print(f"  发言顺序：{state.speaking_order}")
    
    # 模拟发言
    print(f"\n模拟发言流程：")
    for i in range(5):
        speaker = orchestrator.next_speaker()
        if speaker is None:
            print(f"  轮次{i+1}: 流程结束")
            break
        print(f"  轮次{i+1}: {speaker}")
    
    # 生成报告
    print(f"\n共识报告：")
    report = orchestrator.generate_consensus_report(
        "智能客服系统需求分析",
        "需求规格说明书(SRS)"
    )
    print(f"  共识度：{report.get('consensus_level', 0)}%")
    print(f"  关键点：{len(report.get('key_points', []))}个")
    print(f"  风险点：{len(report.get('risks', []))}个")
    print(f"  质疑数：{len(report.get('challenges', []))}次")
    
    print("\n✅ 流程编排器测试完成")
