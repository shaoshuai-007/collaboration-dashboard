#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成本估算模型
- 人天估算
- 预算估算
- 报价单生成

Author: 南乔
Date: 2026-03-14
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class CostEstimation:
    """成本估算结果"""
    # 输入参数
    project_name: str
    team_size: int
    duration_months: int
    complexity: str  # 简单/中等/复杂
    tech_stack: List[str]
    cloud_service: bool
    
    # 计算结果
    man_days: int
    labor_cost: float
    cloud_cost: float
    risk_reserve: float
    total_cost: float
    
    # 明细
    breakdown: Dict


class CostEstimator:
    """成本估算器"""
    
    # 复杂度系数
    COMPLEXITY_FACTORS = {
        '简单': 0.8,
        '中等': 1.0,
        '复杂': 1.3,
        '极复杂': 1.6
    }
    
    # 人天单价（元）
    DAILY_RATE = 1500
    
    # 云服务月费参考
    CLOUD_MONTHLY_COSTS = {
        '小型': 3000,
        '中型': 8000,
        '大型': 20000
    }
    
    def estimate(
        self,
        project_name: str,
        team_size: int,
        duration_months: int,
        complexity: str = '中等',
        tech_stack: List[str] = None,
        cloud_service: bool = True,
        cloud_tier: str = '中型'
    ) -> CostEstimation:
        """
        估算项目成本
        
        Args:
            project_name: 项目名称
            team_size: 团队规模（人）
            duration_months: 项目周期（月）
            complexity: 复杂度（简单/中等/复杂/极复杂）
            tech_stack: 技术栈
            cloud_service: 是否需要云服务
            cloud_tier: 云服务规格（小型/中型/大型）
        
        Returns:
            CostEstimation: 估算结果
        """
        if tech_stack is None:
            tech_stack = ['Java', 'Vue', 'MySQL']
        
        # 获取复杂度系数
        complexity_factor = self.COMPLEXITY_FACTORS.get(complexity, 1.0)
        
        # 计算人天
        work_days_per_month = 20
        man_days = int(team_size * duration_months * work_days_per_month * complexity_factor)
        
        # 人力成本
        labor_cost = man_days * self.DAILY_RATE
        
        # 云服务成本
        cloud_cost = 0
        if cloud_service:
            cloud_monthly = self.CLOUD_MONTHLY_COSTS.get(cloud_tier, 8000)
            cloud_cost = cloud_monthly * duration_months
        
        # 风险储备（10%）
        risk_reserve = (labor_cost + cloud_cost) * 0.1
        
        # 总成本
        total_cost = labor_cost + cloud_cost + risk_reserve
        
        # 明细
        breakdown = {
            '人力': {
                '人天': man_days,
                '单价': self.DAILY_RATE,
                '小计': labor_cost
            },
            '云服务': {
                '规格': cloud_tier if cloud_service else '无',
                '月费': self.CLOUD_MONTHLY_COSTS.get(cloud_tier, 0) if cloud_service else 0,
                '小计': cloud_cost
            },
            '风险储备': {
                '比例': '10%',
                '小计': risk_reserve
            }
        }
        
        return CostEstimation(
            project_name=project_name,
            team_size=team_size,
            duration_months=duration_months,
            complexity=complexity,
            tech_stack=tech_stack,
            cloud_service=cloud_service,
            man_days=man_days,
            labor_cost=labor_cost,
            cloud_cost=cloud_cost,
            risk_reserve=risk_reserve,
            total_cost=total_cost,
            breakdown=breakdown
        )
    
    def generate_report(self, estimation: CostEstimation) -> str:
        """生成成本估算报告"""
        report = f"""
══════════════════════════════════════════════════════
                    成本估算报告
══════════════════════════════════════════════════════

项目名称：{estimation.project_name}
估算时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

────────────────────────────────────────────────────
                    项目参数
────────────────────────────────────────────────────
团队规模：{estimation.team_size}人
项目周期：{estimation.duration_months}个月
复杂程度：{estimation.complexity}
技术栈：{', '.join(estimation.tech_stack)}
云服务：{'需要' if estimation.cloud_service else '不需要'}

────────────────────────────────────────────────────
                    成本明细
────────────────────────────────────────────────────

【人力成本】
  人天数：{estimation.man_days}人天
  单  价：{self.DAILY_RATE}元/人天
  小  计：{estimation.labor_cost:,.0f}元

【云服务成本】
  月  费：{estimation.breakdown['云服务']['月费']:,.0f}元/月
  周  期：{estimation.duration_months}个月
  小  计：{estimation.cloud_cost:,.0f}元

【风险储备】
  比  例：10%
  小  计：{estimation.risk_reserve:,.0f}元

══════════════════════════════════════════════════════
                    总成本：{estimation.total_cost:,.0f}元
══════════════════════════════════════════════════════

备注：
1. 人天单价按{self.DAILY_RATE}元/人天估算
2. 风险储备按10%计提，用于应对不可预见情况
3. 实际成本可能因需求变更、市场波动等因素调整

══════════════════════════════════════════════════════
"""
        return report
    
    def to_dict(self, estimation: CostEstimation) -> Dict:
        """转换为字典"""
        return {
            'project_name': estimation.project_name,
            'team_size': estimation.team_size,
            'duration_months': estimation.duration_months,
            'complexity': estimation.complexity,
            'tech_stack': estimation.tech_stack,
            'cloud_service': estimation.cloud_service,
            'man_days': estimation.man_days,
            'labor_cost': estimation.labor_cost,
            'cloud_cost': estimation.cloud_cost,
            'risk_reserve': estimation.risk_reserve,
            'total_cost': estimation.total_cost,
            'breakdown': estimation.breakdown
        }


# 测试
if __name__ == '__main__':
    estimator = CostEstimator()
    
    print("=" * 60)
    print("💰 成本估算模型测试")
    print("=" * 60)
    
    # 测试估算
    result = estimator.estimate(
        project_name='智能客服系统',
        team_size=5,
        duration_months=6,
        complexity='中等',
        tech_stack=['Java', 'Vue', 'MySQL', 'Redis'],
        cloud_service=True,
        cloud_tier='中型'
    )
    
    # 生成报告
    report = estimator.generate_report(result)
    print(report)
    
    # 导出字典
    print("\n字典格式：")
    print(json.dumps(estimator.to_dict(result), ensure_ascii=False, indent=2))
