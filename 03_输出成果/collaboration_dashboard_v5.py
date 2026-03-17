#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协作框架 V5 - 自主协作版
支持：角色认知、动态调度、辩论反驳、共识收敛

Author: 南乔
Date: 2026-03-13
"""

from flask import Flask, render_template_string, jsonify, request
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import time
import random
import re

app = Flask(__name__)

# ==================== 角色认知系统 ====================

class RiskPreference(Enum):
    """风险偏好"""
    CONSERVATIVE = "保守"      # 偏向稳定、低风险
    MODERATE = "稳健"          # 平衡风险与收益
    AGGRESSIVE = "激进"        # 偏向创新、高风险

class Stance(Enum):
    """立场"""
    COST_FIRST = "成本优先"      # 成本控制为主
    QUALITY_FIRST = "质量优先"   # 技术质量为主
    SCHEDULE_FIRST = "进度优先"  # 交付时间为主
    BALANCED = "平衡折中"        # 综合考虑

@dataclass
class AgentPersona:
    """Agent角色认知"""
    agent_id: str
    name: str
    role: str
    emoji: str
    stance: Stance                    # 立场
    risk_preference: RiskPreference   # 风险偏好
    expertise: List[str]              # 专业领域
    boundaries: List[str]             # 专业边界（不擅长的）
    concern_points: List[str]         # 关注点（会质疑的点）
    
    def should_challenge(self, topic: str, content: str) -> Tuple[bool, str]:
        """判断是否应该提出质疑"""
        # 检查是否触及关注点
        for concern in self.concern_points:
            if concern in content or concern in topic:
                return True, concern
        
        # 检查立场冲突
        if "成本" in content and self.stance == Stance.QUALITY_FIRST:
            if any(word in content for word in ["高", "贵", "增加", "提升"]):
                return True, "成本过高"
        
        if "复杂" in content and self.stance == Stance.COST_FIRST:
            return True, "架构过于复杂"
        
        if "时间" in content or "周期" in content:
            if self.stance == Stance.SCHEDULE_FIRST:
                if any(word in content for word in ["长", "久", "延迟"]):
                    return True, "周期过长"
        
        return False, ""
    
    def generate_challenge(self, trigger: str, context: str) -> str:
        """生成质疑/反驳内容"""
        challenges = {
            "成本过高": [
                f"我理解技术方案很重要，但{trigger}会带来较大成本压力。建议考虑分阶段投入，先用最小可行方案验证效果。",
                f"从成本角度看，当前方案的投入产出比需要评估。能否简化部分模块，降低初期投入？",
                f"预算是重要约束。建议我们对比一下高配和低配方案的成本差异，再决策。"
            ],
            "架构过于复杂": [
                f"这个方案技术先进，但复杂度较高。运维成本和人员要求都要考虑，是否有更轻量的方案？",
                f"微服务架构优势明显，但也带来分布式问题。初期团队规模有限，建议从单体起步。",
                f"架构设计要考虑落地难度。过于复杂会增加开发周期和风险，建议分步演进。"
            ],
            "周期过长": [
                f"项目周期直接关系到投入成本和市场时机。建议压缩非核心功能，优先上线核心模块。",
                f"时间成本也是成本。能否采用敏捷方式，缩短迭代周期，快速验证？",
                f"进度风险需要评估。长周期意味着更多不确定性，建议设置阶段性里程碑。"
            ],
            "技术风险": [
                f"新技术引入需要评估团队熟悉程度。建议进行技术预研，降低实施风险。",
                f"技术选型要考虑可维护性。过度依赖新技术可能带来长期风险。",
                f"建议我们先做技术验证，确保关键路径可行后再全面铺开。"
            ],
            "需求范围": [
                f"需求边界需要明确。范围蔓延是项目失败的常见原因，建议固定核心需求。",
                f"功能太多会分散资源。建议用MoSCoW法则排序，优先交付最有价值的部分。",
                f"用户需求和理解之间可能有偏差。建议先做原型验证，再详细设计。"
            ]
        }
        
        templates = challenges.get(trigger, [f"我对{trigger}有一些疑虑，建议进一步讨论。"])
        return random.choice(templates)


# 定义所有Agent的角色认知
AGENT_PERSONAS = {
    'nanqiao': AgentPersona(
        agent_id='nanqiao', name='南乔', role='主控Agent', emoji='🌿',
        stance=Stance.BALANCED, risk_preference=RiskPreference.MODERATE,
        expertise=['需求整理', '任务协调', '进度跟踪', '成果汇总'],
        boundaries=['技术细节', '成本核算'],
        concern_points=['需求范围', '进度风险']
    ),
    'caiwei': AgentPersona(
        agent_id='caiwei', name='采薇', role='需求分析专家', emoji='🌸',
        stance=Stance.QUALITY_FIRST, risk_preference=RiskPreference.MODERATE,
        expertise=['需求调研', '用户故事', '验收标准', '业务流程'],
        boundaries=['技术实现', '成本核算'],
        concern_points=['需求范围', '用户体验', '业务价值']
    ),
    'zhijin': AgentPersona(
        agent_id='zhijin', name='织锦', role='架构设计师', emoji='🧵',
        stance=Stance.QUALITY_FIRST, risk_preference=RiskPreference.AGGRESSIVE,
        expertise=['架构设计', '技术选型', '系统设计', '性能优化'],
        boundaries=['成本核算', '项目管理'],
        concern_points=['技术风险', '扩展性', '性能']
    ),
    'zhutai': AgentPersona(
        agent_id='zhutai', name='筑台', role='售前工程师', emoji='🏗️',
        stance=Stance.COST_FIRST, risk_preference=RiskPreference.CONSERVATIVE,
        expertise=['成本评估', '方案报价', '竞品分析', 'ROI计算'],
        boundaries=['代码实现', '需求细节'],
        concern_points=['成本过高', '投入产出比', '风险控制']
    ),
    'gongchi': AgentPersona(
        agent_id='gongchi', name='工尺', role='详细设计师', emoji='📐',
        stance=Stance.QUALITY_FIRST, risk_preference=RiskPreference.MODERATE,
        expertise=['详细设计', '接口设计', '数据库设计', '代码规范'],
        boundaries=['成本核算', '项目管理'],
        concern_points=['实现难度', '技术细节', '代码质量']
    ),
    'yuheng': AgentPersona(
        agent_id='yuheng', name='玉衡', role='项目经理', emoji='⚖️',
        stance=Stance.SCHEDULE_FIRST, risk_preference=RiskPreference.CONSERVATIVE,
        expertise=['项目计划', '风险管理', '团队协调', '进度跟踪'],
        boundaries=['技术细节', '需求细节'],
        concern_points=['周期过长', '资源不足', '风险累积']
    ),
    'chengcai': AgentPersona(
        agent_id='chengcai', name='呈彩', role='PPT设计师', emoji='🎨',
        stance=Stance.BALANCED, risk_preference=RiskPreference.MODERATE,
        expertise=['PPT设计', '方案呈现', '视觉设计', '演示培训'],
        boundaries=['技术细节', '成本核算'],
        concern_points=['时间安排', '修改次数']
    ),
    'zhegui': AgentPersona(
        agent_id='zhegui', name='折桂', role='资源管家', emoji='📚',
        stance=Stance.BALANCED, risk_preference=RiskPreference.CONSERVATIVE,
        expertise=['资源整理', '知识管理', '文档归档', '案例参考'],
        boundaries=['决策判断', '技术评估'],
        concern_points=['资料完整', '版本管理']
    ),
    'fuyao': AgentPersona(
        agent_id='fuyao', name='扶摇', role='总指挥', emoji='🌀',
        stance=Stance.BALANCED, risk_preference=RiskPreference.MODERATE,
        expertise=['决策判断', '资源调配', '风险仲裁', '团队协调'],
        boundaries=['具体执行'],
        concern_points=['决策风险', '团队协作', '目标达成']
    )
}


# ==================== 对话记忆系统 ====================

@dataclass
class ConversationTurn:
    """对话轮次"""
    turn_id: int
    speaker: str
    speaker_name: str
    content: str
    timestamp: str
    msg_type: str = "answer"  # answer, challenge, support, conclusion
    is_challenging: bool = False
    challenged_agent: Optional[str] = None

class ConversationMemory:
    """对话记忆"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: List[ConversationTurn] = []
        self.turn_count: int = 0
        self.current_topic: str = ""
        self.controversy_points: List[str] = []  # 争议点
        self.resolved_points: List[str] = []     # 已解决的争议
        self.no_conflict_rounds: int = 0         # 无冲突轮次
    
    def add_turn(self, speaker: str, speaker_name: str, content: str, 
                 msg_type: str = "answer", is_challenging: bool = False,
                 challenged_agent: Optional[str] = None) -> ConversationTurn:
        self.turn_count += 1
        turn = ConversationTurn(
            turn_id=self.turn_count,
            speaker=speaker,
            speaker_name=speaker_name,
            content=content,
            timestamp=datetime.now().isoformat(),
            msg_type=msg_type,
            is_challenging=is_challenging,
            challenged_agent=challenged_agent
        )
        self.history.append(turn)
        
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return turn
    
    def get_recent(self, limit: int = 10) -> List[ConversationTurn]:
        return self.history[-limit:]
    
    def get_last_speaker(self) -> Optional[str]:
        if self.history:
            return self.history[-1].speaker
        return None
    
    def get_last_n_speakers(self, n: int = 3) -> List[str]:
        speakers = []
        for turn in reversed(self.history[-n:]):
            speakers.append(turn.speaker)
        return speakers
    
    def has_recent_challenge(self) -> bool:
        """最近是否有质疑"""
        for turn in reversed(self.history[-3:]):
            if turn.is_challenging:
                return True
        return False
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.history:
            return ""
        
        recent = self.get_recent(5)
        parts = []
        for turn in recent:
            prefix = "【质疑】" if turn.is_challenging else ""
            parts.append(f"{prefix}{turn.speaker_name}: {turn.content[:50]}...")
        
        return "\n".join(parts)
    
    def clear(self):
        self.history.clear()
        self.turn_count = 0
        self.current_topic = ""
        self.controversy_points.clear()
        self.resolved_points.clear()
        self.no_conflict_rounds = 0


# ==================== 动态调度器 ====================

class DynamicScheduler:
    """动态调度器 - 基于上下文决定下一个发言者"""
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.speaking_queue: List[str] = []  # 待发言队列
        self.max_rounds = 15                  # 最大轮次
        self.current_round = 0
    
    def decide_next_speaker(self, task: str) -> Optional[str]:
        """决定下一个发言者"""
        self.current_round += 1
        
        # 检查是否超过最大轮次
        if self.current_round > self.max_rounds:
            return 'fuyao'  # 总指挥强制结束
        
        # 检查共识收敛
        if self.memory.no_conflict_rounds >= 2:
            return 'fuyao'  # 连续2轮无冲突，结束
        
        # 获取最近的发言者，避免重复
        recent_speakers = self.memory.get_last_n_speakers(2)
        
        # 根据上下文决定
        context = self.memory.get_context_summary()
        
        # 如果最近有质疑，优先让被质疑者回应
        if self.memory.has_recent_challenge():
            last_turn = self.memory.history[-1]
            if last_turn.challenged_agent and last_turn.challenged_agent not in recent_speakers:
                return last_turn.challenged_agent
        
        # 根据任务阶段选择
        phase = self._determine_phase()
        
        # 阶段性发言顺序
        phase_speakers = {
            'initial': ['caiwei', 'zhijin'],           # 初始：需求+架构
            'discussion': ['zhutai', 'yuheng'],        # 讨论：成本+项目
            'challenge': ['zhijin', 'zhutai', 'gongchi'],  # 质疑期
            'resolution': ['yuheng', 'fuyao'],         # 决策期
            'conclusion': ['fuyao', 'nanqiao']         # 收尾
        }
        
        candidates = phase_speakers.get(phase, phase_speakers['initial'])
        
        # 选择第一个未在最近发言的候选人
        for speaker in candidates:
            if speaker not in recent_speakers:
                return speaker
        
        # 如果都在最近发言过，选择争议相关的Agent
        return self._select_by_controversy()
    
    def _determine_phase(self) -> str:
        """判断当前对话阶段"""
        turn_count = len(self.memory.history)
        
        if turn_count <= 2:
            return 'initial'
        elif turn_count <= 6:
            return 'discussion'
        elif self.memory.has_recent_challenge():
            return 'challenge'
        elif self.memory.no_conflict_rounds > 0:
            return 'resolution'
        else:
            return 'discussion'
    
    def _select_by_controversy(self) -> str:
        """根据争议点选择发言者"""
        if "成本" in self.memory.current_topic:
            return 'zhutai'
        elif "架构" in self.memory.current_topic or "技术" in self.memory.current_topic:
            return 'zhijin'
        elif "进度" in self.memory.current_topic or "时间" in self.memory.current_topic:
            return 'yuheng'
        else:
            return random.choice(['caiwei', 'zhijin', 'zhutai', 'yuheng'])
    
    def should_end(self) -> bool:
        """是否应该结束对话"""
        if self.current_round > self.max_rounds:
            return True
        if self.memory.no_conflict_rounds >= 2:
            return True
        return False
    
    def reset(self):
        self.speaking_queue.clear()
        self.current_round = 0


# ==================== 响应生成器 ====================

class IntelligentResponseGenerator:
    """智能响应生成器"""
    
    def generate(self, agent_id: str, persona: AgentPersona, 
                 task: str, memory: ConversationMemory,
                 is_challenging: bool = False,
                 challenge_target: Optional[str] = None) -> str:
        """生成智能响应"""
        
        context = memory.get_context_summary()
        
        # 如果是质疑回应
        if is_challenging and challenge_target:
            return self._generate_challenge_response(agent_id, persona, challenge_target, context)
        
        # 检查是否需要质疑前一个发言
        if memory.history:
            last_turn = memory.history[-1]
            should_challenge, trigger = persona.should_challenge(task, last_turn.content)
            if should_challenge and agent_id != last_turn.speaker:
                return persona.generate_challenge(trigger, last_turn.content)
        
        # 正常发言
        return self._generate_normal_response(agent_id, persona, task, memory)
    
    def _generate_normal_response(self, agent_id: str, persona: AgentPersona,
                                   task: str, memory: ConversationMemory) -> str:
        """生成正常响应"""
        
        # 提取项目名称
        project = self._extract_project_name(task)
        
        responses = {
            'caiwei': [
                f"【需求分析】{project}的核心需求我已梳理。主要功能点包括：用户管理、权限控制、数据统计。建议下一步由织锦进行架构设计，确定技术选型。",
                f"【需求分析】经过调研，{project}的用户画像已明确。核心用户是企业内部人员，日活预计500-1000人。验收标准：响应时间<2s，支持100并发。",
                f"【需求分析】需求边界已定义。包含{random.randint(8,15)}个功能模块，排除移动端需求。建议采用敏捷开发，首期交付核心功能。"
            ],
            'zhijin': [
                f"【架构设计】基于需求分析，我设计微服务架构：接入层→API网关→业务服务→数据中台。技术栈：Spring Cloud + Kubernetes + PostgreSQL。这套架构扩展性强，但初期投入会大一些。",
                f"【架构设计】方案已完成。推荐采用前后端分离，前端Vue3，后端Spring Boot微服务，数据库PostgreSQL+Redis。部署在K8s上，支持弹性伸缩。",
                f"【架构设计】从技术角度，建议{project}采用云原生架构。优势是高可用、易扩展，但需要团队有DevOps能力。初期可以先从单体起步，逐步演进。"
            ],
            'zhutai': [
                f"【成本评估】看到织锦的微服务方案，我有些担心成本。这套架构初期投入约150-200万，运维成本每年50万以上。对于{project}这个规模，是否可以先简化架构？",
                f"【成本评估】从投入产出角度分析，{project}首年总成本约180万，预计节省人工成本50万/年，ROI约3.6年回本。建议分阶段投入，降低风险。",
                f"【成本评估】成本明细：开发人力100万、基础设施30万、第三方服务20万、测试运维30万。高配方案成本翻倍，需要权衡收益。"
            ],
            'yuheng': [
                f"【项目管理】从进度角度，{project}开发周期预计12-16周。关键路径：需求分析→架构设计→开发→测试→上线。建议设置4个里程碑，每周同步进度。",
                f"【项目管理】看到大家的分析，我有些担心进度风险。微服务架构开发周期长，建议分阶段交付：首期8周上线核心功能，二期完善扩展功能。",
                f"【项目管理】项目计划已制定。团队配置：PM1人、架构师1人、开发5人、测试2人。风险项：需求变更、技术难点、资源冲突。已制定应对措施。"
            ],
            'gongchi': [
                f"【详细设计】基于架构方案，数据库设计约30张表，核心接口约50个。技术细节：用户表支持千万级，采用分库分表；缓存策略用Redis集群。",
                f"【详细设计】接口文档已输出。RESTful风格，统一返回格式，支持分页和筛选。预计开发工时：后端60人天，前端40人天。",
                f"【详细设计】从实现角度，建议核心模块优先开发。复杂功能可以简化实现，后续迭代优化。代码规范已制定，采用Git Flow分支管理。"
            ],
            'fuyao': [
                f"【总指挥】综合大家的分析，{project}方案已基本明确。采纳分阶段方案：首期核心功能，二期扩展完善。采薇负责需求验收，织锦把控技术质量，玉衡跟进进度。",
                f"【总指挥】经过讨论，团队意见已统一。项目启动！A级优先级，资源已调配。每周五进度汇报，有问题及时上报。预计{random.randint(3,4)}个月交付。",
                f"【总指挥】决策结果：采用中配方案，分两期交付。首期预算控制在120万以内。团队按计划执行，关键节点我来决策。"
            ],
            'nanqiao': [
                f"【主控】收到需求，我将协调团队完成{project}的分析。请各位按专业分工协作，有问题及时提出。",
                f"【主控】感谢各位的分析，核心要点已整理。如有补充请继续发言，否则我将汇总成果。",
                f"【主控】任务已完成。输出成果：需求文档、架构方案、成本预算、项目计划。请查阅并反馈。"
            ],
            'zhegui': [
                f"【资源整理】{project}相关资源已整理：技术文档15份、案例参考8份、行业报告5份。已上传知识库供团队查阅。",
                f"【资源整理】补充一份相似项目案例，供参考。该项目历时4个月，团队8人，首期投入100万。"
            ],
            'chengcai': [
                f"【PPT设计】方案材料准备中。大纲：项目背景→需求分析→解决方案→技术架构→实施计划→成本预算。预计2天完成。",
                f"【PPT设计】需要确认汇报对象是技术评审还是管理层？我将调整内容深度和呈现方式。"
            ]
        }
        
        agent_responses = responses.get(agent_id, [f"收到任务，正在处理..."])
        return random.choice(agent_responses)
    
    def _generate_challenge_response(self, agent_id: str, persona: AgentPersona,
                                      target_id: str, context: str) -> str:
        """生成质疑回应"""
        
        target_name = AGENT_PERSONAS[target_id].name
        
        responses = {
            'zhijin': [
                f"我理解筑台的顾虑。微服务确实有成本，但考虑到{project}的长期发展，这套架构更灵活。建议分阶段上线：首期简化部署，二期再优化架构。",
                f"技术架构要平衡短期成本和长期价值。我们可以从最小可用版本起步，控制初期投入在80万以内，后续根据业务增长逐步扩展。"
            ],
            'zhutai': [
                f"织锦的架构方案很完善，但从成本角度我建议先做最小可行产品(MVP)。把预算控制在100万以内，验证效果后再追加投入。",
                f"成本核算是我的职责。微服务方案的投入确实偏高，建议我们先对比一下单体架构和微服务架构的成本差异，再决策。"
            ],
            'yuheng': [
                f"从项目管理角度，我支持分阶段方案。首期8周交付核心功能，降低风险。时间就是成本，压缩周期能减少不确定性。",
                f"进度和质量要平衡。过度压缩进度会影响代码质量，后期维护成本更高。建议预留20%缓冲时间。"
            ],
            'fuyao': [
                f"经过讨论，团队意见已基本统一。采纳分阶段方案，平衡成本、质量和进度。首期聚焦核心功能，二期完善扩展。",
                f"各位的顾虑都有道理。我的决策是：采用中配方案，预算控制在120万，周期12周。有异议的请说明理由。"
            ]
        }
        
        agent_responses = responses.get(agent_id, [
            f"我理解{target_name}的观点。让我们进一步讨论，找到最佳方案。"
        ])
        
        response = random.choice(agent_responses)
        
        # 替换项目名称
        project = "本项目"
        return response.replace("{project}", project)
    
    def _extract_project_name(self, task: str) -> str:
        """提取项目名称"""
        for kw in ['系统', '平台', '项目', '应用']:
            if kw in task:
                idx = task.find(kw)
                return task[max(0, idx-8):idx+len(kw)]
        return "本项目"


# ==================== 全局状态 ====================

memory = ConversationMemory()
scheduler = DynamicScheduler(memory)
response_gen = IntelligentResponseGenerator()
agent_status: Dict[str, str] = {}
is_processing = False
current_task = ""


# ==================== HTML模板 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧭 指南针工程 - 自主协作平台 V5</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            background: #f0f2f5;
            color: #333;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        }
        .header h1 { font-size: 18px; font-weight: 600; }
        .header .info { font-size: 12px; opacity: 0.9; }
        .status-badge { display: flex; align-items: center; gap: 8px; }
        .status-badge .dot { width: 10px; height: 10px; background: #4CAF50; border-radius: 50%; }
        .status-badge .dot.active { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        
        .main { flex: 1; display: flex; overflow: hidden; }
        
        /* 左侧 */
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
        }
        .sidebar-header {
            padding: 16px;
            background: #fafafa;
            border-bottom: 1px solid #eee;
            font-size: 14px;
            font-weight: 600;
        }
        
        .agent-section { padding: 12px; }
        .agent-section h4 {
            font-size: 11px;
            color: #888;
            padding: 8px 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .agent-card {
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 6px;
            background: #fafafa;
            border-radius: 10px;
            border-left: 4px solid transparent;
            transition: all 0.3s;
        }
        .agent-card:hover { background: #f5f5f5; }
        .agent-card.speaking {
            border-left-color: #006EBD;
            background: #e3f2fd;
            transform: translateX(4px);
        }
        .agent-card.challenging { border-left-color: #ff9800; background: #fff3e0; }
        
        .agent-avatar {
            width: 40px; height: 40px;
            background: linear-gradient(135deg, #C93832, #006EBD);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 18px;
            margin-right: 12px;
        }
        .agent-info { flex: 1; }
        .agent-name { font-size: 13px; font-weight: 600; }
        .agent-role { font-size: 11px; color: #888; margin-top: 2px; }
        .agent-stance { 
            font-size: 10px; 
            color: #C93832; 
            margin-top: 4px;
            display: flex;
            gap: 4px;
        }
        .stance-tag {
            padding: 2px 6px;
            background: #fff0f0;
            border-radius: 4px;
        }
        
        /* 对话区 */
        .chat-area { flex: 1; display: flex; flex-direction: column; }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: linear-gradient(180deg, #fafbfc 0%, #f0f2f5 100%);
        }
        
        .message {
            margin-bottom: 16px;
            display: flex;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } }
        
        .message.user { justify-content: flex-end; }
        
        .msg-card {
            max-width: 75%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .message.user .msg-card { background: #C93832; color: white; }
        
        .msg-header {
            padding: 10px 14px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .message.user .msg-header { border-bottom-color: rgba(255,255,255,0.2); }
        
        .msg-speaker { display: flex; align-items: center; gap: 8px; }
        .msg-speaker .emoji { font-size: 16px; }
        .msg-speaker .name { font-size: 13px; font-weight: 600; }
        
        .msg-type-badge {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 4px;
            background: #e3f2fd;
            color: #1976d2;
        }
        .msg-type-badge.challenge { background: #fff3e0; color: #f57c00; }
        .msg-type-badge.conclusion { background: #e8f5e9; color: #388e3c; }
        
        .msg-time { font-size: 11px; color: #aaa; }
        .message.user .msg-time { color: rgba(255,255,255,0.7); }
        
        .msg-content {
            padding: 12px 14px;
            font-size: 13px;
            line-height: 1.7;
        }
        
        /* 输入区 */
        .input-area {
            background: white;
            border-top: 1px solid #e0e0e0;
            padding: 16px 20px;
        }
        .input-row {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .input-row input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-row input:focus { border-color: #006EBD; }
        .input-row button {
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(90deg, #C93832, #006EBD);
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .input-row button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(201,56,50,0.3); }
        .input-row button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .quick-actions { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
        .quick-btn {
            padding: 8px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: white;
            color: #666;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { border-color: #006EBD; color: #006EBD; background: #f5f9ff; }
        
        /* 空状态 */
        .empty-state { text-align: center; padding: 80px 40px; color: #999; }
        .empty-state .icon { font-size: 56px; margin-bottom: 20px; opacity: 0.6; }
        .empty-state .text { font-size: 14px; }
        
        /* 打字指示器 */
        .typing-bar {
            display: none;
            padding: 12px 20px;
            background: #fafafa;
            border-top: 1px solid #f0f0f0;
            font-size: 12px;
            color: #888;
            align-items: center;
            gap: 10px;
        }
        .typing-bar.show { display: flex; }
        .typing-dots span {
            display: inline-block;
            width: 6px; height: 6px;
            background: #888;
            border-radius: 50%;
            margin: 0 2px;
            animation: bounce 1s infinite;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
        
        /* 状态标签 */
        .status-label { font-size: 11px; padding: 3px 8px; border-radius: 4px; margin-left: auto; }
        .status-label.idle { background: #f5f5f5; color: #999; }
        .status-label.working { background: #e3f2fd; color: #1976d2; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🧭 指南针工程 - 自主协作平台</h1>
            <div class="info">角色认知 · 动态调度 · 辩论反驳 · 共识收敛</div>
        </div>
        <div class="status-badge">
            <div class="dot" id="statusDot"></div>
            <span id="statusText">系统就绪</span>
        </div>
    </div>
    
    <div class="main">
        <!-- 左侧Agent列表 -->
        <div class="sidebar">
            <div class="sidebar-header">👥 协作团队 · 自主决策</div>
            <div class="agent-section" id="agentSection"></div>
        </div>
        
        <!-- 对话区 -->
        <div class="chat-area">
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <div class="text">输入需求，Agent团队将自主协作、辩论决策</div>
                </div>
            </div>
            
            <div class="typing-bar" id="typingBar">
                <div class="typing-dots"><span></span><span></span><span></span></div>
                <span id="typingText">采薇正在思考...</span>
            </div>
            
            <div class="input-area">
                <div class="input-row">
                    <input type="text" id="taskInput" placeholder="输入需求，如：需要开发一个用户数据管理系统，预算100万以内">
                    <button id="sendBtn" onclick="submitTask()">发送</button>
                </div>
                <div class="quick-actions">
                    <button class="quick-btn" onclick="quickTask('需求分析并讨论方案')">📋 需求讨论</button>
                    <button class="quick-btn" onclick="quickTask('架构设计，考虑成本和进度平衡')">🏗️ 架构辩论</button>
                    <button class="quick-btn" onclick="quickTask('成本评估，给出不同方案对比')">💰 成本分析</button>
                    <button class="quick-btn" onclick="clearChat()">🗑️ 清空</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let conversations = [];
        let agentStatus = {};
        let isProcessing = false;
        
        const AGENTS = {
            'nanqiao': { name: '南乔', role: '主控Agent', emoji: '🌿', stance: '平衡', risk: '稳健' },
            'caiwei': { name: '采薇', role: '需求分析专家', emoji: '🌸', stance: '质量优先', risk: '稳健' },
            'zhijin': { name: '织锦', role: '架构设计师', emoji: '🧵', stance: '质量优先', risk: '激进' },
            'zhutai': { name: '筑台', role: '售前工程师', emoji: '🏗️', stance: '成本优先', risk: '保守' },
            'gongchi': { name: '工尺', role: '详细设计师', emoji: '📐', stance: '质量优先', risk: '稳健' },
            'yuheng': { name: '玉衡', role: '项目经理', emoji: '⚖️', stance: '进度优先', risk: '保守' },
            'chengcai': { name: '呈彩', role: 'PPT设计师', emoji: '🎨', stance: '平衡', risk: '稳健' },
            'zhegui': { name: '折桂', role: '资源管家', emoji: '📚', stance: '平衡', risk: '保守' },
            'fuyao': { name: '扶摇', role: '总指挥', emoji: '🌀', stance: '平衡', risk: '稳健' }
        };
        
        function init() {
            renderAgentList();
            fetchStatus();
            setInterval(fetchStatus, 1200);
        }
        
        function renderAgentList() {
            const container = document.getElementById('agentSection');
            container.innerHTML = '';
            
            const order = ['fuyao', 'nanqiao', 'yuheng', 'caiwei', 'zhijin', 'zhutai', 'gongchi', 'chengcai', 'zhegui'];
            
            order.forEach(id => {
                const agent = AGENTS[id];
                const status = agentStatus[id] || 'idle';
                
                const card = document.createElement('div');
                card.className = `agent-card ${status === 'speaking' ? 'speaking' : ''} ${status === 'challenging' ? 'challenging' : ''}`;
                card.id = `agent-${id}`;
                card.innerHTML = `
                    <div class="agent-avatar">${agent.emoji}</div>
                    <div class="agent-info">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-role">${agent.role}</div>
                        <div class="agent-stance">
                            <span class="stance-tag">${agent.stance}</span>
                            <span class="stance-tag">${agent.risk}</span>
                        </div>
                    </div>
                    <span class="status-label ${status}">${status === 'speaking' ? '发言中' : status === 'challenging' ? '质疑中' : ''}</span>
                `;
                container.appendChild(card);
            });
        }
        
        async function fetchStatus() {
            try {
                const response = await fetch('/api/conversation');
                const data = await response.json();
                conversations = data.conversations || [];
                agentStatus = data.agentStatus || {};
                
                renderMessages();
                updateAgentStatus();
                updateHeaderStatus(data.phase, data.round);
            } catch (e) { console.error(e); }
        }
        
        function renderMessages() {
            const container = document.getElementById('chatMessages');
            
            if (conversations.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">💬</div>
                        <div class="text">输入需求，Agent团队将自主协作、辩论决策</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '';
            
            conversations.forEach(conv => {
                const agent = AGENTS[conv.speaker] || { name: conv.speaker, emoji: '🤖' };
                const isUser = conv.speaker === 'user';
                const isChallenge = conv.is_challenging;
                const msgType = conv.msg_type;
                
                let typeBadge = '';
                if (msgType === 'challenge' || isChallenge) {
                    typeBadge = '<span class="msg-type-badge challenge">质疑</span>';
                } else if (msgType === 'conclusion') {
                    typeBadge = '<span class="msg-type-badge conclusion">结论</span>';
                }
                
                const msg = document.createElement('div');
                msg.className = `message ${isUser ? 'user' : ''} ${isChallenge ? 'challenge' : ''}`;
                msg.innerHTML = `
                    <div class="msg-card">
                        <div class="msg-header">
                            <div class="msg-speaker">
                                <span class="emoji">${agent.emoji}</span>
                                <span class="name">${agent.name}</span>
                                ${typeBadge}
                            </div>
                            <span class="msg-time">${conv.timestamp.split('T')[1].split('.')[0]}</span>
                        </div>
                        <div class="msg-content">${conv.content}</div>
                    </div>
                `;
                container.appendChild(msg);
            });
            
            container.scrollTop = container.scrollHeight;
        }
        
        function updateAgentStatus() {
            Object.keys(agentStatus).forEach(id => {
                const card = document.getElementById(`agent-${id}`);
                if (card) {
                    const status = agentStatus[id];
                    card.className = `agent-card ${status === 'speaking' ? 'speaking' : ''} ${status === 'challenging' ? 'challenging' : ''}`;
                    card.querySelector('.status-label').textContent = status === 'speaking' ? '发言中' : status === 'challenging' ? '质疑中' : '';
                    card.querySelector('.status-label').className = `status-label ${status}`;
                }
            });
        }
        
        function updateHeaderStatus(phase, round) {
            const dot = document.getElementById('statusDot');
            const text = document.getElementById('statusText');
            
            if (phase && phase !== 'idle') {
                dot.classList.add('active');
                text.textContent = `第${round}轮 · ${phase === 'initial' ? '初始分析' : phase === 'discussion' ? '方案讨论' : phase === 'challenge' ? '质疑辩论' : phase === 'resolution' ? '共识形成' : '总结收尾'}`;
            } else {
                dot.classList.remove('active');
                text.textContent = '系统就绪';
            }
        }
        
        async function submitTask() {
            if (isProcessing) return;
            
            const input = document.getElementById('taskInput');
            const content = input.value.trim();
            if (!content) { alert('请输入需求'); return; }
            
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            input.value = '';
            
            try {
                await fetch('/api/task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: content})
                });
            } catch (e) { alert('提交失败'); }
            
            setTimeout(() => {
                isProcessing = false;
                document.getElementById('sendBtn').disabled = false;
            }, 20000);
        }
        
        function quickTask(type) {
            document.getElementById('taskInput').value = type;
            submitTask();
        }
        
        async function clearChat() {
            await fetch('/api/clear', {method: 'POST'});
        }
        
        document.getElementById('taskInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') submitTask();
        });
        
        init();
    </script>
</body>
</html>
'''


# ==================== API路由 ====================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/conversation')
def api_conversation():
    """获取对话状态"""
    phase = 'idle'
    if len(memory.history) > 0:
        phase = scheduler._determine_phase()
    
    return jsonify({
        'conversations': [
            {'turn_id': t.turn_id, 'speaker': t.speaker, 'speaker_name': t.speaker_name,
             'content': t.content, 'timestamp': t.timestamp, 'msg_type': t.msg_type,
             'is_challenging': t.is_challenging, 'challenged_agent': t.challenged_agent}
            for t in memory.history
        ],
        'agentStatus': agent_status,
        'phase': phase,
        'round': scheduler.current_round
    })


@app.route('/api/task', methods=['POST'])
def api_task():
    """接收任务并启动自主协作对话"""
    global agent_status, is_processing, current_task
    
    data = request.json
    task = data.get('task', '')
    current_task = task
    
    # 重置状态
    agent_status = {aid: 'idle' for aid in AGENT_PERSONAS.keys()}
    memory.clear()
    scheduler.reset()
    
    # 添加用户消息
    memory.add_turn('user', '用户', task, 'answer')
    memory.current_topic = task
    
    # 启动自主协作线程
    def run_autonomous_collaboration():
        global agent_status
        
        # 1. 南乔广播接收
        time.sleep(0.5)
        agent_status['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', 
            f'收到您的需求：「{task[:40]}...」我将协调团队进行自主分析。请各位Agent基于专业立场发表意见，有疑虑可以提出质疑。',
            'answer')
        time.sleep(1.2)
        agent_status['nanqiao'] = 'idle'
        
        # 2. 采薇需求分析
        time.sleep(1)
        agent_status['caiwei'] = 'speaking'
        persona = AGENT_PERSONAS['caiwei']
        response = response_gen.generate('caiwei', persona, task, memory)
        memory.add_turn('caiwei', '采薇', response, 'answer')
        time.sleep(1.5)
        agent_status['caiwei'] = 'idle'
        
        # 3. 织锦架构设计（可能带质疑点）
        time.sleep(1)
        agent_status['zhijin'] = 'speaking'
        persona = AGENT_PERSONAS['zhijin']
        response = response_gen.generate('zhijin', persona, task, memory)
        memory.add_turn('zhijin', '织锦', response, 'answer')
        time.sleep(1.5)
        agent_status['zhijin'] = 'idle'
        
        # 4. 筑台成本评估（很可能质疑织锦的方案）
        time.sleep(1)
        agent_status['zhutai'] = 'speaking'
        persona = AGENT_PERSONAS['zhutai']
        
        # 检查是否应该质疑
        last_turn = memory.history[-1]
        should_challenge, trigger = persona.should_challenge(task, last_turn.content)
        
        if should_challenge:
            agent_status['zhutai'] = 'challenging'
            challenge_response = persona.generate_challenge(trigger, last_turn.content)
            memory.add_turn('zhutai', '筑台', challenge_response, 'challenge', 
                          is_challenging=True, challenged_agent='zhijin')
            memory.no_conflict_rounds = 0
        else:
            response = response_gen.generate('zhutai', persona, task, memory)
            memory.add_turn('zhutai', '筑台', response, 'answer')
            memory.no_conflict_rounds += 1
        
        time.sleep(1.5)
        agent_status['zhutai'] = 'idle'
        
        # 5. 织锦回应质疑（如果有）
        if memory.has_recent_challenge():
            time.sleep(1)
            agent_status['zhijin'] = 'speaking'
            response = response_gen.generate('zhijin', AGENT_PERSONAS['zhijin'], 
                                            task, memory, is_challenging=True, 
                                            challenge_target='zhutai')
            memory.add_turn('zhijin', '织锦', response, 'answer')
            time.sleep(1.5)
            agent_status['zhijin'] = 'idle'
        
        # 6. 玉衡项目管理
        time.sleep(1)
        agent_status['yuheng'] = 'speaking'
        persona = AGENT_PERSONAS['yuheng']
        
        # 检查是否应该质疑
        recent_content = " ".join([t.content for t in memory.get_recent(3)])
        should_challenge, trigger = persona.should_challenge(task, recent_content)
        
        if should_challenge and random.random() > 0.5:
            agent_status['yuheng'] = 'challenging'
            challenge_response = persona.generate_challenge(trigger, recent_content)
            memory.add_turn('yuheng', '玉衡', challenge_response, 'challenge',
                          is_challenging=True, challenged_agent='zhijin')
            memory.no_conflict_rounds = 0
        else:
            response = response_gen.generate('yuheng', persona, task, memory)
            memory.add_turn('yuheng', '玉衡', response, 'answer')
            memory.no_conflict_rounds += 1
        
        time.sleep(1.5)
        agent_status['yuheng'] = 'idle'
        
        # 7. 扶摇总结决策
        time.sleep(1)
        agent_status['fuyao'] = 'speaking'
        persona = AGENT_PERSONAS['fuyao']
        response = response_gen.generate('fuyao', persona, task, memory)
        memory.add_turn('fuyao', '扶摇', response, 'conclusion')
        time.sleep(1.2)
        agent_status['fuyao'] = 'idle'
        
        # 8. 南乔收尾
        time.sleep(0.8)
        agent_status['nanqiao'] = 'speaking'
        memory.add_turn('nanqiao', '南乔', 
            '协作完成。核心成果已输出：需求分析、架构方案、成本评估、项目计划。团队已达成共识，采用分阶段交付策略。请查阅决策结果。',
            'conclusion')
        time.sleep(0.5)
        agent_status['nanqiao'] = 'idle'
    
    thread = threading.Thread(target=run_autonomous_collaboration)
    thread.start()
    
    return jsonify({'status': 'ok'})


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """清空对话"""
    global agent_status
    memory.clear()
    scheduler.reset()
    agent_status = {aid: 'idle' for aid in AGENT_PERSONAS.keys()}
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("🧭 指南针工程 - 自主协作平台 V5")
    print("=" * 60)
    print("核心特性:")
    print("  ✓ 角色认知：立场、风险偏好、专业边界")
    print("  ✓ 动态调度：根据上下文决定发言顺序")
    print("  ✓ 辩论反驳：Agent可主动质疑、反驳")
    print("  ✓ 共识收敛：连续无冲突自动结束")
    print("=" * 60)
    print("访问地址: http://120.48.169.242:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
