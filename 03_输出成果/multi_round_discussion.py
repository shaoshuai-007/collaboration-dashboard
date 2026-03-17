#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮讨论执行器
- 支持多轮循环讨论
- Agent互相回应、质疑、补充
- 共识检测机制
- V15.1增强：第一轮并行调用（提升效率）

Author: 南乔
Date: 2026-03-15
Updated: 2026-03-18 (V15.1并行优化)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 导入现有模块（从collaboration_dashboard_v14）
# 注意：AGENTS和AGENT_NAMES定义在collaboration_dashboard_v14.py中
try:
    from collaboration_dashboard_v14 import AGENTS, AGENT_NAMES
except ImportError:
    # 如果导入失败，使用默认定义
    from dataclasses import dataclass
    
    @dataclass
    class AgentPersona:
        agent_id: str
        name: str
        role: str
        system_prompt: str
        color: str
    
    AGENTS = {
        'caiwei': AgentPersona('caiwei', '采薇', '需求分析专家', '你是采薇，需求分析专家。', '#409EFF'),
        'zhijin': AgentPersona('zhijin', '织锦', '架构设计师', '你是织锦，架构设计师。', '#67C23A'),
        'yuheng': AgentPersona('yuheng', '玉衡', '项目经理', '你是玉衡，项目经理。', '#F56C6C'),
        'chengcai': AgentPersona('chengcai', '呈彩', '方案设计师', '你是呈彩，方案设计师。', '#FF9800'),
        'gongchi': AgentPersona('gongchi', '工尺', '系统设计师', '你是工尺，系统设计师。', '#607D8B'),
        'zhutai': AgentPersona('zhutai', '筑台', '售前工程师', '你是筑台，售前工程师。', '#E6A23C'),
        'fuyao': AgentPersona('fuyao', '扶摇', '总指挥', '你是扶摇，总指挥。', '#165DFF'),
        'zhegui': AgentPersona('zhegui', '折桂', '资源管家', '你是折桂，资源管家。', '#00BCD4'),
    }
    
    AGENT_NAMES = {aid: agent.name for aid, agent in AGENTS.items()}


@dataclass
class DiscussionMessage:
    """讨论消息"""
    round_num: int           # 轮次
    speaker: str             # 发言者ID
    speaker_name: str        # 发言者名称
    content: str             # 发言内容
    is_challenge: bool       # 是否质疑
    challenge_target: str    # 质疑对象
    reply_to: str            # 回应对象
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RoundResult:
    """单轮讨论结果"""
    round_num: int
    messages: List[DiscussionMessage]
    challenge_count: int
    has_consensus: bool


class MultiRoundDiscussion:
    """多轮讨论执行器"""
    
    # 质疑关键词
    CHALLENGE_KEYWORDS = [
        '质疑', '反对', '不同意', '不可行', 
        '成本过高', '周期太长', '有风险',
        '我认为不对', '这个方案有问题', '建议修改',
        '值得商榷', '需要考虑', '存在问题'
    ]
    
    # 共识关键词
    CONSENSUS_KEYWORDS = [
        '同意', '认可', '可行', '没问题',
        '支持', '赞同', '接受', '可以'
    ]
    
    def __init__(self, llm_client=None):
        """
        初始化
        
        Args:
            llm_client: LLM客户端（可选，用于测试时mock）
        """
        self.llm_client = llm_client
        self.discussion_history: List[DiscussionMessage] = []
    
    def run(self, task: str, structured_intent: dict, 
            participants: List[str], max_rounds: int = 3) -> dict:
        """
        执行多轮讨论
        
        Args:
            task: 用户原始输入
            structured_intent: 结构化意图
            participants: 参与者列表
            max_rounds: 最大轮次
        
        Returns:
            {
                'rounds': [RoundResult, ...],
                'consensus_reached': bool,
                'final_consensus': str,
                'key_decisions': list
            }
        """
        self.discussion_history = []
        rounds = []
        consensus_reached = False
        
        for round_num in range(1, max_rounds + 1):
            print(f"[INFO] 开始第 {round_num} 轮讨论...")
            
            # 执行单轮讨论
            round_result = self._run_round(
                round_num, task, structured_intent, participants
            )
            rounds.append(round_result)
            
            # 检测是否达成共识
            if round_result.has_consensus:
                print(f"[INFO] 第 {round_num} 轮达成共识")
                consensus_reached = True
                break
            
            # 检测是否还有待回应的质疑
            if round_result.challenge_count == 0:
                print(f"[INFO] 第 {round_num} 轮无质疑，讨论结束")
                consensus_reached = True
                break
            
            print(f"[INFO] 第 {round_num} 轮有 {round_result.challenge_count} 个质疑，继续讨论")
        
        # 生成最终共识
        final_consensus = self._generate_final_consensus(rounds)
        
        # 提取关键决策
        key_decisions = self._extract_key_decisions(rounds)
        
        return {
            'rounds': rounds,
            'consensus_reached': consensus_reached,
            'final_consensus': final_consensus,
            'key_decisions': key_decisions,
            'discussion_history': self.discussion_history
        }
    
    def _run_round(self, round_num: int, task: str, 
                   structured_intent: dict, participants: List[str]) -> RoundResult:
        """执行单轮讨论"""
        
        messages = []
        challenge_count = 0
        has_consensus = False
        
        # ========== V15.1优化：第一轮使用并行调用 ==========
        if round_num == 1:
            print(f"[V15.1] 第一轮使用并行调用，参与者: {len(participants)}人")
            responses = self._generate_responses_parallel(
                participants, task, round_num, structured_intent
            )
            
            # 按原始顺序处理并行结果
            for agent_key in participants:
                if agent_key not in AGENTS:
                    continue
                if agent_key not in responses:
                    continue
                
                agent = AGENTS[agent_key]
                content = responses[agent_key]
                
                # 检测质疑
                is_challenge, challenge_target = self._detect_challenge(content)
                
                # 检测回应
                reply_to = self._detect_reply(content, messages)
                
                # 创建消息
                msg = DiscussionMessage(
                    round_num=round_num,
                    speaker=agent_key,
                    speaker_name=agent.name,
                    content=content,
                    is_challenge=is_challenge,
                    challenge_target=challenge_target,
                    reply_to=reply_to
                )
                messages.append(msg)
                self.discussion_history.append(msg)
                
                if is_challenge:
                    challenge_count += 1
        
        else:
            # 后续轮次：使用串行调用（保证讨论连贯性）
            print(f"[V15] 第{round_num}轮使用串行调用（保证讨论连贯性）")
            for agent_key in participants:
                if agent_key not in AGENTS:
                    continue
                
                agent = AGENTS[agent_key]
                
                # 生成发言
                content = self._generate_agent_response(
                    agent, task, round_num, structured_intent
                )
                
                # 检测质疑
                is_challenge, challenge_target = self._detect_challenge(content)
                
                # 检测回应
                reply_to = self._detect_reply(content, messages)
                
                # 创建消息
                msg = DiscussionMessage(
                    round_num=round_num,
                    speaker=agent_key,
                    speaker_name=agent.name,
                    content=content,
                    is_challenge=is_challenge,
                    challenge_target=challenge_target,
                    reply_to=reply_to
                )
                messages.append(msg)
                self.discussion_history.append(msg)
                
                if is_challenge:
                    challenge_count += 1
                
                # 添加延迟（模拟真实讨论）
                time.sleep(0.3)  # 优化：0.5→0.3秒
        
        # 检测本轮是否达成共识
        has_consensus = self._check_round_consensus(messages)
        
        return RoundResult(
            round_num=round_num,
            messages=messages,
            challenge_count=challenge_count,
            has_consensus=has_consensus
        )
    
    def _generate_responses_parallel(self, agents: List[str], task: str, 
                                      round_num: int, structured_intent: dict) -> Dict[str, str]:
        """并行生成多个Agent的响应（V15.1新增）"""
        
        results = {}
        
        def call_single(agent_key):
            """单个Agent调用"""
            if agent_key not in AGENTS:
                return agent_key, None
            agent = AGENTS[agent_key]
            content = self._generate_agent_response(agent, task, round_num, structured_intent)
            return agent_key, content
        
        # 并行调用（最多5个并发）
        max_workers = min(len(agents), 5)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(call_single, a): a for a in agents}
            
            for future in as_completed(futures, timeout=120):
                try:
                    agent_key, content = future.result(timeout=60)
                    if content:
                        results[agent_key] = content
                except Exception as e:
                    print(f"[V15.1] Agent调用失败: {e}")
        
        print(f"[V15.1] 并行调用完成，成功: {len(results)}/{len(agents)}")
        return results
    
    def _generate_agent_response(self, agent, task: str, round_num: int,
                                  structured_intent: dict) -> str:
        """生成Agent发言"""
        
        # 获取历史讨论内容
        context = self._get_context_for_round(round_num)
        
        # 根据轮次生成不同的prompt
        if round_num == 1:
            # 第一轮：专业分析
            prompt = f"""当前任务：{structured_intent.get('structured_intent', task)}

你是{agent.name}，角色是{agent.role}。

请从你的专业角度进行分析：
1. 核心观点（最重要的1-2点）
2. 关键要点（支撑观点的细节）
3. 风险提示（如有）

要求：
- 观点明确，逻辑清晰
- 简洁有力，不超过200字
- 体现专业视角"""
        
        elif round_num == 2:
            # 第二轮：补充碰撞
            prompt = f"""当前任务：{structured_intent.get('structured_intent', task)}

已有讨论：
{context}

你是{agent.name}，角色是{agent.role}。

请根据上述讨论发表意见：
1. 如果你有不同意见，请明确指出并说明理由
2. 如果有需要补充的观点，请补充
3. 如果认为方案可行，请确认

⚠️ 要求：
- 必须回应前面发言者的观点
- 形成真正的讨论，不要各说各的
- 简洁有力，不超过200字"""
        
        else:
            # 第三轮：共识确认
            prompt = f"""当前任务：{structured_intent.get('structured_intent', task)}

讨论历史：
{context}

你是{agent.name}，角色是{agent.role}。

请确认：
1. 是否还有未解决的问题？
2. 最终方案是什么？
3. 需要后续跟进的事项？

要求：简洁总结，不超过150字"""
        
        # 调用LLM
        if self.llm_client:
            response = self.llm_client.generate(agent.system_prompt, prompt)
        else:
            # 使用实际的千帆API
            from collaboration_dashboard_v14 import call_qianfan
            # 获取system_prompt
            system_prompt = agent.get_system_prompt() if hasattr(agent, 'get_system_prompt') else agent.system_prompt
            response = call_qianfan(system_prompt, prompt)
        
        return response.strip() if response else self._fallback_response(agent, round_num)
    
    def _fallback_response(self, agent, round_num: int) -> str:
        """降级响应"""
        fallbacks = {
            1: f"从{agent.role}角度分析，建议进一步明确需求和边界条件。",
            2: f"同意前面的分析，建议补充细节。",
            3: f"确认方案可行，可以推进。"
        }
        return fallbacks.get(round_num, "同意上述观点。")
    
    def _detect_challenge(self, response: str) -> Tuple[bool, str]:
        """检测质疑"""
        
        is_challenge = any(kw in response for kw in self.CHALLENGE_KEYWORDS)
        
        # 检测质疑对象
        challenge_target = ""
        for agent_key, agent in AGENTS.items():
            if agent.name in response and agent.name != "":
                challenge_target = agent.name
                break
        
        return is_challenge, challenge_target
    
    def _detect_reply(self, response: str, current_round_messages: List[DiscussionMessage]) -> str:
        """检测回应对象"""
        
        # 检测response中是否提到了某个Agent
        for agent_key, agent in AGENTS.items():
            if agent.name in response:
                # 确保不是自己在说自己
                for msg in current_round_messages:
                    if msg.speaker_name == agent.name:
                        return agent.name
        
        return ""
    
    def _get_context_for_round(self, round_num: int) -> str:
        """获取当前轮次的上下文"""
        
        if round_num == 1:
            return ""
        
        # 获取之前的讨论
        context_parts = []
        for msg in self.discussion_history:
            context_parts.append(f"【{msg.speaker_name}】{msg.content}")
        
        return "\n\n".join(context_parts)
    
    def _check_round_consensus(self, messages: List[DiscussionMessage]) -> bool:
        """检测本轮是否达成共识"""
        
        if not messages:
            return False
        
        # 统计共识关键词
        consensus_count = 0
        for msg in messages:
            if any(kw in msg.content for kw in self.CONSENSUS_KEYWORDS):
                consensus_count += 1
        
        # 如果超过一半的人表示同意，认为达成共识
        return consensus_count > len(messages) // 2
    
    def _generate_final_consensus(self, rounds: List[RoundResult]) -> str:
        """生成最终共识"""
        
        if not rounds:
            return "讨论完成，未形成明确共识。"
        
        # 提取最后一轮的所有发言（完整内容）
        last_round = rounds[-1]
        consensus_parts = []
        
        for msg in last_round.messages:
            # 不截断，显示完整内容
            consensus_parts.append(f"【{msg.speaker_name}】\n{msg.content}")
        
        return "\n\n".join(consensus_parts)
    
    def _extract_key_decisions(self, rounds: List[RoundResult]) -> List[str]:
        """提取关键决策"""
        
        decisions = []
        
        # 决策关键词
        decision_keywords = ['决策', '结论', '确定', '最终方案', '共识', '采纳']
        
        for round_result in rounds:
            for msg in round_result.messages:
                if any(kw in msg.content for kw in decision_keywords):
                    # 提取决策句子
                    sentences = msg.content.split('。')
                    for sentence in sentences:
                        if any(kw in sentence for kw in decision_keywords):
                            decisions.append(f"{msg.speaker_name}：{sentence}")
        
        return decisions[:5]  # 最多返回5条


# ==================== 测试用例 ====================
if __name__ == '__main__':
    # 创建测试数据
    from nanqiao_intent_analyzer import NanqiaoIntentAnalyzer
    
    analyzer = NanqiaoIntentAnalyzer()
    intent = analyzer.analyze("做一个智能客服系统的需求分析")
    
    print("=" * 60)
    print("多轮讨论执行器测试")
    print("=" * 60)
    print(f"\n任务：{intent.structured_intent}")
    print(f"参与者：{intent.participants}")
    print(f"轮次：{intent.discussion_rounds}")
    print("-" * 60)
    
    # 执行讨论
    discussion = MultiRoundDiscussion()
    result = discussion.run(
        task="做一个智能客服系统的需求分析",
        structured_intent=intent.__dict__,
        participants=intent.participants,
        max_rounds=intent.discussion_rounds
    )
    
    # 输出结果
    print("\n讨论结果：")
    print(f"共识达成：{result['consensus_reached']}")
    print(f"讨论轮次：{len(result['rounds'])}")
    
    for round_result in result['rounds']:
        print(f"\n--- 第 {round_result.round_num} 轮 ---")
        for msg in round_result.messages:
            challenge_mark = "⚠️" if msg.is_challenge else "✓"
            print(f"  {challenge_mark} {msg.speaker_name}：{msg.content[:80]}...")
    
    print("\n关键决策：")
    for decision in result['key_decisions']:
        print(f"  • {decision}")
