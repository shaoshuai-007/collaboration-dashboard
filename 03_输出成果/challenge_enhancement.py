#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质疑增强模块
- 在现有流程中增强质疑机制
- 向后兼容，保障现有功能不受影响
- 通过开关控制新功能

Author: 南乔
Date: 2026-03-15
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import time

# ==================== 质疑分类体系 ====================

class ChallengeCategory(Enum):
    """质疑分类"""
    TECHNICAL = "技术可行性"      # 技术方案是否可行
    COST = "成本效益"             # 成本是否可控
    SCHEDULE = "时间周期"         # 工期是否合理
    REQUIREMENT = "需求覆盖"      # 需求是否完整
    ARCHITECTURE = "架构设计"     # 架构是否合理
    RISK = "风险管理"             # 风险是否可控
    RESOURCE = "资源保障"         # 资源是否充足
    COMPLIANCE = "合规安全"       # 是否符合规范


class ChallengeIntensity(Enum):
    """质疑强度"""
    SUGGESTION = 1      # 建议性质（轻微）
    CONCERN = 2         # 担忧性质（中等）
    OBJECTION = 3       # 反对性质（严重）
    BLOCKER = 4         # 阻塞性质（致命）


# 强度对应的共识度扣分
INTENSITY_PENALTY = {
    ChallengeIntensity.SUGGESTION: 2,
    ChallengeIntensity.CONCERN: 5,
    ChallengeIntensity.OBJECTION: 10,
    ChallengeIntensity.BLOCKER: 20,
}

# 强度对应的显示样式
INTENSITY_DISPLAY = {
    ChallengeIntensity.SUGGESTION: ("💡", "建议", "#67C23A"),
    ChallengeIntensity.CONCERN: ("😟", "担忧", "#E6A23C"),
    ChallengeIntensity.OBJECTION: ("❌", "反对", "#F56C6C"),
    ChallengeIntensity.BLOCKER: ("🚫", "阻塞", "#909399"),
}


# ==================== 结构化质疑 ====================

@dataclass
class StructuredChallenge:
    """结构化质疑"""
    challenge_id: str                   # 质疑ID
    challenger: str                     # 质疑者ID
    challenger_name: str                # 质疑者名称
    target_agent: str                   # 被质疑者ID
    target_agent_name: str              # 被质疑者名称
    target_point: str                   # 被质疑的观点
    
    category: ChallengeCategory         # 质疑类型
    intensity: ChallengeIntensity       # 质疑强度
    
    reason: str                         # 质疑原因
    suggestion: str = ""                # 改进建议
    
    status: str = "pending"             # pending/accepted/rejected/resolved
    response: str = ""                  # 回应内容
    response_time: str = ""             # 回应时间
    
    round_num: int = 0                  # 发生轮次
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典（用于API返回）"""
        emoji, label, color = INTENSITY_DISPLAY[self.intensity]
        return {
            'challenge_id': self.challenge_id,
            'challenger': self.challenger,
            'challenger_name': self.challenger_name,
            'target_agent': self.target_agent,
            'target_agent_name': self.target_agent_name,
            'target_point': self.target_point[:100] if self.target_point else "",
            'category': self.category.value,
            'intensity': self.intensity.value,
            'intensity_label': label,
            'intensity_emoji': emoji,
            'intensity_color': color,
            'reason': self.reason,
            'suggestion': self.suggestion,
            'status': self.status,
            'response': self.response,
            'round_num': self.round_num,
            'timestamp': self.timestamp
        }


# ==================== 质疑检测器 ====================

class ChallengeDetector:
    """质疑检测器（增强版）"""
    
    # 质疑关键词（按强度分类）
    INTENSITY_KEYWORDS = {
        ChallengeIntensity.BLOCKER: [
            '完全不可行', '绝对不行', '必须修改', '严重问题', '致命缺陷',
            '完全反对', '无法接受', '根本行不通'
        ],
        ChallengeIntensity.OBJECTION: [
            '反对', '不同意', '不可行', '有问题', '无法实施',
            '成本过高', '周期太长', '风险太大', '不可接受'
        ],
        ChallengeIntensity.CONCERN: [
            '质疑', '担忧', '担心', '值得商榷', '需要考虑',
            '存在风险', '有一定问题', '需要验证', '建议评估'
        ],
        ChallengeIntensity.SUGGESTION: [
            '建议', '可以考虑', '或许', '可能需要', '建议补充',
            '有一点想法', '提个小建议', '小问题'
        ]
    }
    
    # 质疑类型关键词
    CATEGORY_KEYWORDS = {
        ChallengeCategory.TECHNICAL: [
            '技术', '架构', '性能', '扩展', '稳定性', '可维护',
            '技术栈', '框架', '接口', '数据库'
        ],
        ChallengeCategory.COST: [
            '成本', '预算', '投入', '费用', '开支', '性价比', 'ROI'
        ],
        ChallengeCategory.SCHEDULE: [
            '工期', '时间', '周期', '进度', '延期', '赶工', '排期'
        ],
        ChallengeCategory.REQUIREMENT: [
            '需求', '功能', '用户', '场景', '边界', '验收', '覆盖'
        ],
        ChallengeCategory.RISK: [
            '风险', '隐患', '问题', '挑战', '不确定', '不可控'
        ],
        ChallengeCategory.RESOURCE: [
            '资源', '人力', '团队', '人员', '设备', '服务器'
        ],
        ChallengeCategory.COMPLIANCE: [
            '合规', '安全', '隐私', '法规', '规范', '标准'
        ]
    }
    
    def detect(self, response: str, speaker_id: str, speaker_name: str,
               history: List[dict], agents: dict) -> Optional[StructuredChallenge]:
        """
        检测质疑
        
        Args:
            response: Agent发言内容
            speaker_id: 发言者ID
            speaker_name: 发言者名称
            history: 历史消息列表
            agents: Agent字典
        
        Returns:
            StructuredChallenge 或 None
        """
        # 1. 检测是否有质疑
        intensity = self._detect_intensity(response)
        if not intensity:
            return None
        
        # 2. 检测质疑对象
        target_agent, target_agent_name, target_point = self._detect_target(
            response, history, agents, speaker_id
        )
        if not target_agent:
            return None
        
        # 3. 检测质疑类型
        category = self._detect_category(response)
        
        # 4. 生成质疑ID
        challenge_id = f"CH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{speaker_id[:4]}"
        
        # 5. 提取质疑原因
        reason = self._extract_reason(response)
        
        # 6. 创建结构化质疑
        challenge = StructuredChallenge(
            challenge_id=challenge_id,
            challenger=speaker_id,
            challenger_name=speaker_name,
            target_agent=target_agent,
            target_agent_name=target_agent_name,
            target_point=target_point,
            category=category,
            intensity=intensity,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
        
        return challenge
    
    def _detect_intensity(self, response: str) -> Optional[ChallengeIntensity]:
        """检测质疑强度"""
        for intensity, keywords in self.INTENSITY_KEYWORDS.items():
            for kw in keywords:
                if kw in response:
                    return intensity
        return None
    
    def _detect_target(self, response: str, history: List[dict], 
                       agents: dict, speaker_id: str) -> Tuple[str, str, str]:
        """检测质疑对象"""
        # 从历史消息中找被质疑者
        for agent_id, agent in agents.items():
            if agent_id == speaker_id:
                continue
            
            agent_name = agent.name if hasattr(agent, 'name') else agent.get('name', '')
            if not agent_name:
                continue
            
            # 检查是否提到了该Agent
            if agent_name in response:
                # 找到该Agent最近的发言
                target_point = ""
                for msg in reversed(history):
                    if msg.get('speaker') == agent_id:
                        target_point = msg.get('content', '')
                        break
                
                return agent_id, agent_name, target_point
        
        # 如果没有明确提到，找最近发言的其他Agent
        for msg in reversed(history):
            if msg.get('speaker') != speaker_id:
                target_id = msg.get('speaker', '')
                target_name = msg.get('speaker_name', '')
                target_point = msg.get('content', '')
                return target_id, target_name, target_point
        
        return "", "", ""
    
    def _detect_category(self, response: str) -> ChallengeCategory:
        """检测质疑类型"""
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in response:
                    return category
        return ChallengeCategory.TECHNICAL  # 默认技术类
    
    def _extract_reason(self, response: str) -> str:
        """提取质疑原因"""
        # 简单提取：返回包含质疑关键词的句子
        sentences = response.replace('。', '。\n').split('\n')
        for sentence in sentences:
            for intensity_keywords in self.INTENSITY_KEYWORDS.values():
                for kw in intensity_keywords:
                    if kw in sentence:
                        return sentence.strip()
        return response[:100]  # 默认返回前100字符


# ==================== 质疑链路追踪 ====================

class ChallengeChain:
    """质疑链路追踪"""
    
    def __init__(self):
        self.chains: List[dict] = []  # [{challenge, responses, resolution}]
        self.challenge_counter = 0
    
    def add_challenge(self, challenge: StructuredChallenge) -> str:
        """添加质疑"""
        self.challenge_counter += 1
        challenge.challenge_id = f"CH-{self.challenge_counter:03d}"
        
        self.chains.append({
            'challenge': challenge,
            'responses': [],
            'resolution': None
        })
        
        return challenge.challenge_id
    
    def add_response(self, challenge_id: str, agent_id: str, agent_name: str,
                     response: str, accepts: bool) -> bool:
        """添加回应"""
        for chain in self.chains:
            if chain['challenge'].challenge_id == challenge_id:
                chain['responses'].append({
                    'agent': agent_id,
                    'agent_name': agent_name,
                    'content': response,
                    'accepts': accepts,
                    'timestamp': datetime.now().isoformat()
                })
                
                # 更新质疑状态
                if accepts:
                    chain['challenge'].status = "accepted"
                else:
                    chain['challenge'].status = "rejected"
                
                chain['challenge'].response = response
                chain['challenge'].response_time = datetime.now().isoformat()
                
                return True
        return False
    
    def resolve(self, challenge_id: str, resolution: str) -> bool:
        """解决质疑"""
        for chain in self.chains:
            if chain['challenge'].challenge_id == challenge_id:
                chain['resolution'] = resolution
                chain['challenge'].status = "resolved"
                return True
        return False
    
    def get_pending_challenges(self) -> List[StructuredChallenge]:
        """获取待回应的质疑"""
        return [
            chain['challenge'] 
            for chain in self.chains 
            if chain['challenge'].status == "pending"
        ]
    
    def get_challenges_for_agent(self, agent_id: str) -> List[StructuredChallenge]:
        """获取针对某个Agent的待回应质疑"""
        return [
            chain['challenge']
            for chain in self.chains
            if chain['challenge'].target_agent == agent_id 
            and chain['challenge'].status == "pending"
        ]
    
    def to_summary(self) -> str:
        """生成质疑链路总结"""
        if not self.chains:
            return "本次讨论无质疑。"
        
        summary = "## 质疑链路总结\n\n"
        
        for i, chain in enumerate(self.chains, 1):
            challenge = chain['challenge']
            emoji, label, _ = INTENSITY_DISPLAY[challenge.intensity]
            
            summary += f"### 质疑 {i} {emoji} {label}\n\n"
            summary += f"- **质疑者**：{challenge.challenger_name}\n"
            summary += f"- **被质疑者**：{challenge.target_agent_name}\n"
            summary += f"- **质疑类型**：{challenge.category.value}\n"
            summary += f"- **质疑内容**：{challenge.reason}\n"
            summary += f"- **状态**：{challenge.status}\n"
            
            if chain['responses']:
                summary += f"\n**回应记录**：\n"
                for resp in chain['responses']:
                    status = "✅ 接受" if resp['accepts'] else "❌ 拒绝"
                    summary += f"- {resp['agent_name']}：{status}\n"
            
            if chain['resolution']:
                summary += f"\n**解决结果**：{chain['resolution']}\n"
            
            summary += "\n---\n\n"
        
        return summary
    
    def to_dict_list(self) -> List[dict]:
        """转换为字典列表（用于API返回）"""
        return [chain['challenge'].to_dict() for chain in self.chains]


# ==================== 增强版共识度计算器 ====================

class EnhancedConsensusCalculator:
    """增强版共识度计算器"""
    
    # 各维度权重
    DIMENSION_WEIGHTS = {
        'requirement': 0.2,
        'technical': 0.25,
        'cost': 0.2,
        'schedule': 0.2,
        'risk': 0.15,
    }
    
    # 质疑类型到维度的映射
    CATEGORY_TO_DIMENSION = {
        ChallengeCategory.REQUIREMENT: 'requirement',
        ChallengeCategory.TECHNICAL: 'technical',
        ChallengeCategory.ARCHITECTURE: 'technical',
        ChallengeCategory.COST: 'cost',
        ChallengeCategory.SCHEDULE: 'schedule',
        ChallengeCategory.RISK: 'risk',
        ChallengeCategory.RESOURCE: 'schedule',
        ChallengeCategory.COMPLIANCE: 'risk',
    }
    
    def calculate(self, challenges: List[StructuredChallenge]) -> dict:
        """
        计算多维度共识度
        
        Args:
            challenges: 质疑列表
        
        Returns:
            {
                'total': 总体共识度,
                'dimensions': 各维度共识度,
                'grade': 共识等级,
                'challenge_count': 质疑数量,
                'pending_count': 待回应数量
            }
        """
        # 初始化各维度
        dimensions = {
            'requirement': 100,
            'technical': 100,
            'cost': 100,
            'schedule': 100,
            'risk': 100,
        }
        
        # 按维度扣分
        for challenge in challenges:
            dimension = self.CATEGORY_TO_DIMENSION.get(challenge.category, 'technical')
            penalty = INTENSITY_PENALTY[challenge.intensity]
            dimensions[dimension] = max(0, dimensions[dimension] - penalty)
        
        # 计算总体共识度（加权平均）
        total = sum(
            dimensions[k] * self.DIMENSION_WEIGHTS[k] 
            for k in dimensions
        )
        
        # 获取共识等级
        grade = self._get_grade(total)
        
        # 统计待回应数量
        pending_count = sum(1 for c in challenges if c.status == 'pending')
        
        return {
            'total': round(total, 1),
            'dimensions': dimensions,
            'grade': grade,
            'challenge_count': len(challenges),
            'pending_count': pending_count
        }
    
    def _get_grade(self, consensus: float) -> str:
        """获取共识等级"""
        if consensus >= 85:
            return 'A - 高度共识'
        elif consensus >= 70:
            return 'B - 基本共识'
        elif consensus >= 50:
            return 'C - 部分分歧'
        elif consensus >= 30:
            return 'D - 较大分歧'
        else:
            return 'E - 严重分歧'


# ==================== 质疑提示生成器 ====================

class ChallengePromptGenerator:
    """质疑提示生成器"""
    
    # 各角色的质疑焦点
    AGENT_FOCUS = {
        'caiwei': {
            'focus': ['需求缺失', '用户故事不完整', '验收标准不清晰', '边界场景遗漏'],
            'prompt': '请从需求覆盖角度审视方案，确保需求完整无遗漏'
        },
        'zhijin': {
            'focus': ['性能瓶颈', '扩展性不足', '技术债务', '单点故障'],
            'prompt': '请从架构角度审视方案，指出可能的技术风险'
        },
        'zhutai': {
            'focus': ['成本超支', '工期延误', '资源不足', 'ROI不达标'],
            'prompt': '请从成本和工期角度审视方案，评估可行性'
        },
        'yuheng': {
            'focus': ['进度风险', '资源冲突', '范围蔓延', '依赖风险'],
            'prompt': '请从项目管理角度审视方案，识别风险点'
        },
        'gongchi': {
            'focus': ['接口设计缺陷', '数据库瓶颈', '性能问题', '兼容性'],
            'prompt': '请从系统设计角度审视方案，指出技术隐患'
        },
        'chengcai': {
            'focus': ['用户体验问题', '界面设计缺陷', '交互流程不合理'],
            'prompt': '请从用户体验角度审视方案，指出设计问题'
        }
    }
    
    def generate_challenge_prompt(self, agent_id: str, round_num: int, 
                                   history: List[dict]) -> str:
        """
        生成质疑提示
        
        Args:
            agent_id: Agent ID
            round_num: 轮次
            history: 历史消息
        
        Returns:
            质疑提示
        """
        agent_focus = self.AGENT_FOCUS.get(agent_id, {})
        
        if round_num == 1:
            # 第一轮：专业分析，不强制质疑
            return ""
        
        elif round_num == 2:
            # 第二轮：鼓励质疑
            focus_items = agent_focus.get('focus', [])
            focus_text = "、".join(focus_items[:3]) if focus_items else "潜在风险"
            
            return f"""
⚠️ 【质疑环节】

请审视前面的发言，找出至少1个潜在问题：
- 重点关注：{focus_text}

如果有不同意见，请使用以下格式：
【质疑】我对XX的观点提出质疑，原因是...，建议...

注意：质疑不是挑刺，而是为了发现问题、规避风险。
"""
        
        else:
            # 第三轮：回应质疑
            return """
📋 【质疑回应】

如果前面有质疑你的观点，请回应：
1. 接受质疑并说明如何调整
2. 或者解释原因，证明原方案合理
"""
    
    def generate_response_prompt(self, challenge: StructuredChallenge) -> str:
        """
        生成回应提示
        
        Args:
            challenge: 质疑对象
        
        Returns:
            回应提示
        """
        emoji, label, _ = INTENSITY_DISPLAY[challenge.intensity]
        
        return f"""
📢 你被质疑了！

{emoji} **{label}级质疑**（{challenge.category.value}）

**质疑者**：{challenge.challenger_name}
**质疑内容**：{challenge.reason}

请从你的专业角度回应这个质疑：
1. 如果质疑合理，请说明如何调整方案
2. 如果质疑不合理，请解释原因
3. 或者提出折中方案

**注意**：必须在本轮发言中回应此质疑！
"""


# ==================== 质疑增强管理器 ====================

class ChallengeEnhancementManager:
    """质疑增强管理器"""
    
    def __init__(self, enable_enhancement: bool = True):
        """
        初始化
        
        Args:
            enable_enhancement: 是否启用增强功能（默认启用，向后兼容）
        """
        self.enable_enhancement = enable_enhancement
        
        # 初始化各组件
        self.detector = ChallengeDetector()
        self.chain = ChallengeChain()
        self.calculator = EnhancedConsensusCalculator()
        self.prompt_generator = ChallengePromptGenerator()
    
    def process_message(self, response: str, speaker_id: str, speaker_name: str,
                        history: List[dict], agents: dict, round_num: int) -> Optional[StructuredChallenge]:
        """
        处理消息（检测质疑）
        
        Args:
            response: 发言内容
            speaker_id: 发言者ID
            speaker_name: 发言者名称
            history: 历史消息
            agents: Agent字典
            round_num: 当前轮次
        
        Returns:
            StructuredChallenge 或 None
        """
        if not self.enable_enhancement:
            return None
        
        # 检测质疑
        challenge = self.detector.detect(response, speaker_id, speaker_name, history, agents)
        
        if challenge:
            challenge.round_num = round_num
            self.chain.add_challenge(challenge)
        
        return challenge
    
    def get_challenge_prompt(self, agent_id: str, round_num: int, 
                              history: List[dict]) -> str:
        """获取质疑提示"""
        if not self.enable_enhancement:
            return ""
        return self.prompt_generator.generate_challenge_prompt(agent_id, round_num, history)
    
    def get_response_prompt(self, agent_id: str) -> Optional[str]:
        """获取回应提示"""
        if not self.enable_enhancement:
            return None
        
        # 获取针对该Agent的待回应质疑
        challenges = self.chain.get_challenges_for_agent(agent_id)
        
        # 调试日志
        print(f"[质疑增强] get_response_prompt({agent_id}): 找到{len(challenges)}条质疑")
        if self.chain.chains:
            for c in self.chain.chains:
                ch = c['challenge']
                print(f"  - 质疑: {ch.challenger_name} → {ch.target_agent_name} ({ch.target_agent}), 状态: {ch.status}")
        
        if not challenges:
            return None
        
        # 返回最新的质疑
        latest = challenges[-1]
        return self.prompt_generator.generate_response_prompt(latest)
    
    def get_consensus(self) -> dict:
        """获取共识度"""
        if not self.enable_enhancement:
            return {'total': 70, 'grade': 'B - 基本共识', 'dimensions': {}}
        
        return self.calculator.calculate(self.chain.chains)
    
    def get_challenges(self) -> List[dict]:
        """获取所有质疑"""
        return self.chain.to_dict_list()
    
    def get_challenge_summary(self) -> str:
        """获取质疑总结"""
        if not self.enable_enhancement:
            return ""
        return self.chain.to_summary()
    
    def reset(self):
        """重置状态"""
        self.chain = ChallengeChain()


# ==================== 导出 ====================

__all__ = [
    'ChallengeCategory',
    'ChallengeIntensity',
    'StructuredChallenge',
    'ChallengeDetector',
    'ChallengeChain',
    'EnhancedConsensusCalculator',
    'ChallengePromptGenerator',
    'ChallengeEnhancementManager',
]


# ==================== 测试 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("质疑增强模块测试")
    print("=" * 60)
    
    # 创建管理器
    manager = ChallengeEnhancementManager(enable_enhancement=True)
    
    # 模拟Agent字典
    agents = {
        'zhijin': type('Agent', (), {'name': '织锦'})(),
        'zhutai': type('Agent', (), {'name': '筑台'})(),
        'yuheng': type('Agent', (), {'name': '玉衡'})(),
    }
    
    # 模拟历史消息
    history = [
        {'speaker': 'zhijin', 'speaker_name': '织锦', 'content': '建议采用微服务架构，便于扩展。'},
    ]
    
    # 测试质疑检测
    test_response = "我反对这个方案，微服务架构成本过高，初期建议单体架构。"
    challenge = manager.process_message(
        test_response, 'zhutai', '筑台', history, agents, 2
    )
    
    if challenge:
        print(f"\n✅ 检测到质疑：")
        print(f"  - 质疑者：{challenge.challenger_name}")
        print(f"  - 被质疑者：{challenge.target_agent_name}")
        print(f"  - 质疑类型：{challenge.category.value}")
        print(f"  - 质疑强度：{challenge.intensity.name}")
        print(f"  - 质疑原因：{challenge.reason}")
    
    # 测试共识度计算
    consensus = manager.get_consensus()
    print(f"\n📊 共识度：{consensus['total']}% - {consensus['grade']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
