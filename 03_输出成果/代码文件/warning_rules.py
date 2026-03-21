#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电信用户流失预警 - 预警规则模块
作者：知微
日期：2026-03-21
功能：定义预警阈值、预警等级和预警触发规则
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json


class ChurnWarningSystem:
    """流失预警系统"""
    
    def __init__(self):
        """初始化预警系统"""
        # 预警等级定义
        self.warning_levels = {
            'R5': {
                'name': '红色预警',
                'description': '极高风险用户，即将流失',
                'score_range': (70, 100),
                'color': '#FF0000',
                'priority': 'P0',
                'response_time': '24小时内',
                'action': '立即介入'
            },
            'R4': {
                'name': '橙色预警',
                'description': '高风险用户，有较大流失可能性',
                'score_range': (50, 70),
                'color': '#FF8C00',
                'priority': 'P1',
                'response_time': '48小时内',
                'action': '优先关注'
            },
            'R3': {
                'name': '黄色预警',
                'description': '中等风险用户，存在流失隐患',
                'score_range': (30, 50),
                'color': '#FFD700',
                'priority': 'P2',
                'response_time': '一周内',
                'action': '持续跟进'
            },
            'R2': {
                'name': '蓝色预警',
                'description': '低风险用户，需保持关注',
                'score_range': (15, 30),
                'color': '#4169E1',
                'priority': 'P3',
                'response_time': '一个月内',
                'action': '定期关怀'
            },
            'R1': {
                'name': '绿色安全',
                'description': '安全用户，流失风险低',
                'score_range': (0, 15),
                'color': '#32CD32',
                'priority': 'P4',
                'response_time': '正常维护',
                'action': '保持服务'
            }
        }
        
        # 预警触发规则
        self.trigger_rules = self._define_trigger_rules()
        
        # 预警历史记录
        self.warning_history = []
    
    def _define_trigger_rules(self) -> List[Dict]:
        """
        定义预警触发规则
        
        Returns:
        --------
        List[Dict] : 预警规则列表
        """
        rules = [
            # ========== 极高风险规则（R5）==========
            {
                'rule_id': 'R5-001',
                'rule_name': '综合评分极高风险',
                'condition': 'churn_risk_score >= 70',
                'warning_level': 'R5',
                'description': '综合流失风险评分达到70分以上',
                'weight': 1.0
            },
            {
                'rule_id': 'R5-002',
                'rule_name': '多维度高风险',
                'condition': 'consumption_score >= 60 AND communication_score >= 60 AND interaction_score >= 60',
                'warning_level': 'R5',
                'description': '消费、通信、交互三个维度均为高风险',
                'weight': 0.9
            },
            {
                'rule_id': 'R5-003',
                'rule_name': '投诉升级+满意度低',
                'condition': 'has_escalation = 1 AND satisfaction_score_mean < 2',
                'warning_level': 'R5',
                'description': '投诉已升级且满意度评分低于2分',
                'weight': 0.95
            },
            
            # ========== 高风险规则（R4）==========
            {
                'rule_id': 'R4-001',
                'rule_name': '综合评分高风险',
                'condition': 'churn_risk_score >= 50 AND churn_risk_score < 70',
                'warning_level': 'R4',
                'description': '综合流失风险评分在50-70分之间',
                'weight': 1.0
            },
            {
                'rule_id': 'R4-002',
                'rule_name': '消费大幅下降',
                'condition': 'fee_decline_rate < -0.4 AND consumption_score >= 50',
                'warning_level': 'R4',
                'description': '消费下降超过40%且消费风险评分>=50',
                'weight': 0.85
            },
            {
                'rule_id': 'R4-003',
                'rule_name': '活跃度急剧下降',
                'condition': 'call_decline_rate < -0.6 OR activity_decay < -0.3',
                'warning_level': 'R4',
                'description': '通话活跃度下降超过60%或衰减指数<-0.3',
                'weight': 0.8
            },
            {
                'rule_id': 'R4-004',
                'rule_name': '高频投诉',
                'condition': 'complaint_count_sum >= 5 OR (complaint_count_sum >= 3 AND resolution_rate < 0.5)',
                'warning_level': 'R4',
                'description': '投诉次数>=5次，或投诉>=3次且解决率<50%',
                'weight': 0.88
            },
            
            # ========== 中等风险规则（R3）==========
            {
                'rule_id': 'R3-001',
                'rule_name': '综合评分中风险',
                'condition': 'churn_risk_score >= 30 AND churn_risk_score < 50',
                'warning_level': 'R3',
                'description': '综合流失风险评分在30-50分之间',
                'weight': 1.0
            },
            {
                'rule_id': 'R3-002',
                'rule_name': '消费下降',
                'condition': 'fee_decline_rate < -0.2 AND fee_decline_rate >= -0.4',
                'warning_level': 'R3',
                'description': '消费下降20%-40%',
                'weight': 0.7
            },
            {
                'rule_id': 'R3-003',
                'rule_name': '沉默期出现',
                'condition': 'silent_days >= 7 AND silent_days < 14',
                'warning_level': 'R3',
                'description': '出现7-14天的沉默期',
                'weight': 0.65
            },
            {
                'rule_id': 'R3-004',
                'rule_name': '套餐变更频繁',
                'condition': 'package_change_count >= 2',
                'warning_level': 'R3',
                'description': '近期套餐变更次数>=2次',
                'weight': 0.6
            },
            {
                'rule_id': 'R3-005',
                'rule_name': '满意度下降',
                'condition': 'satisfaction_score_mean < 3 AND satisfaction_score_mean >= 2',
                'warning_level': 'R3',
                'description': '满意度评分在2-3分之间',
                'weight': 0.55
            },
            
            # ========== 低风险规则（R2）==========
            {
                'rule_id': 'R2-001',
                'rule_name': '综合评分低风险',
                'condition': 'churn_risk_score >= 15 AND churn_risk_score < 30',
                'warning_level': 'R2',
                'description': '综合流失风险评分在15-30分之间',
                'weight': 1.0
            },
            {
                'rule_id': 'R2-002',
                'rule_name': '轻微消费下降',
                'condition': 'fee_decline_rate < -0.1 AND fee_decline_rate >= -0.2',
                'warning_level': 'R2',
                'description': '消费轻微下降10%-20%',
                'weight': 0.4
            },
            {
                'rule_id': 'R2-003',
                'rule_name': '短期沉默',
                'condition': 'silent_days >= 3 AND silent_days < 7',
                'warning_level': 'R2',
                'description': '出现3-7天的沉默期',
                'weight': 0.35
            },
            {
                'rule_id': 'R2-004',
                'rule_name': '有过投诉但已解决',
                'condition': 'complaint_count_sum >= 1 AND resolution_rate >= 0.8',
                'warning_level': 'R2',
                'description': '有投诉记录但解决率>=80%',
                'weight': 0.3
            },
            
            # ========== 安全规则（R1）==========
            {
                'rule_id': 'R1-001',
                'rule_name': '综合评分安全',
                'condition': 'churn_risk_score < 15',
                'warning_level': 'R1',
                'description': '综合流失风险评分低于15分',
                'weight': 1.0
            }
        ]
        
        return rules
    
    def apply_warning_rules(self, scores: pd.DataFrame) -> pd.DataFrame:
        """
        应用预警规则
        
        Parameters:
        -----------
        scores : 评分表
        
        Returns:
        --------
        DataFrame : 包含预警信息的表
        """
        print("\n" + "="*60)
        print("应用预警规则...")
        print("="*60)
        
        warnings_df = pd.DataFrame()
        warnings_df['user_id'] = scores['user_id']
        warnings_df['churn_risk_score'] = scores['churn_risk_score']
        
        # 存储触发的规则
        triggered_rules = []
        final_warning_levels = []
        
        for idx in scores.index:
            user_triggered = []
            max_level = 'R1'
            max_weight = 0
            
            # 检查每条规则
            for rule in self.trigger_rules:
                if self._check_rule(scores.loc[idx], rule['condition']):
                    user_triggered.append({
                        'rule_id': rule['rule_id'],
                        'rule_name': rule['rule_name'],
                        'warning_level': rule['warning_level'],
                        'weight': rule['weight']
                    })
                    
                    # 确定最高预警等级
                    level_order = {'R5': 5, 'R4': 4, 'R3': 3, 'R2': 2, 'R1': 1}
                    if level_order[rule['warning_level']] > level_order[max_level]:
                        max_level = rule['warning_level']
                        max_weight = rule['weight']
                    elif rule['warning_level'] == max_level and rule['weight'] > max_weight:
                        max_weight = rule['weight']
            
            triggered_rules.append(user_triggered)
            final_warning_levels.append(max_level)
        
        warnings_df['triggered_rules'] = triggered_rules
        warnings_df['warning_level'] = final_warning_levels
        warnings_df['triggered_rule_count'] = warnings_df['triggered_rules'].apply(len)
        
        # 添加预警详情
        warnings_df['warning_name'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['name']
        )
        warnings_df['warning_description'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['description']
        )
        warnings_df['warning_color'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['color']
        )
        warnings_df['priority'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['priority']
        )
        warnings_df['response_time'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['response_time']
        )
        warnings_df['recommended_action'] = warnings_df['warning_level'].map(
            lambda x: self.warning_levels[x]['action']
        )
        
        # 统计预警分布
        print("\n预警等级分布：")
        warning_stats = warnings_df['warning_level'].value_counts().sort_index(ascending=False)
        for level, count in warning_stats.items():
            level_info = self.warning_levels[level]
            print(f"  {level} - {level_info['name']}: {count} 人 ({count/len(warnings_df)*100:.1f}%)")
        
        return warnings_df
    
    def _check_rule(self, row: pd.Series, condition: str) -> bool:
        """
        检查单条规则条件
        
        Parameters:
        -----------
        row : 单行数据
        condition : 规则条件字符串
        
        Returns:
        --------
        bool : 是否触发规则
        """
        try:
            # 替换条件中的字段名为实际值
            eval_condition = condition
            
            # 处理字段名
            import re
            fields = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', condition)
            for field in fields:
                if field in row.index:
                    value = row[field]
                    if pd.isna(value):
                        return False
                    if isinstance(value, str):
                        eval_condition = eval_condition.replace(field, f'"{value}"')
                    else:
                        eval_condition = eval_condition.replace(field, str(value))
            
            # 简化的条件评估
            # 将AND替换为and，OR替换为or
            eval_condition = eval_condition.replace(' AND ', ' and ')
            eval_condition = eval_condition.replace(' OR ', ' or ')
            eval_condition = eval_condition.replace(' = ', ' == ')
            
            return eval(eval_condition)
        except:
            return False
    
    def generate_warning_report(self, scores: pd.DataFrame) -> pd.DataFrame:
        """
        生成预警报告
        
        Parameters:
        -----------
        scores : 评分表
        
        Returns:
        --------
        DataFrame : 预警报告
        """
        # 应用预警规则
        warnings_df = self.apply_warning_rules(scores)
        
        # 合并评分信息
        report = scores.merge(warnings_df, on='user_id', how='left', suffixes=('', '_warning'))
        
        # 按风险等级排序
        level_order = {'R5': 5, 'R4': 4, 'R3': 3, 'R2': 2, 'R1': 1}
        report['level_order'] = report['warning_level'].map(level_order)
        report = report.sort_values(['level_order', 'churn_risk_score'], ascending=[False, False])
        
        return report
    
    def get_priority_users(self, report: pd.DataFrame, 
                          level: str = 'R5') -> pd.DataFrame:
        """
        获取指定等级的优先处理用户
        
        Parameters:
        -----------
        report : 预警报告
        level : 预警等级
        
        Returns:
        --------
        DataFrame : 优先处理用户列表
        """
        return report[report['warning_level'] == level].copy()
    
    def export_warning_config(self, filepath: str):
        """
        导出预警配置
        
        Parameters:
        -----------
        filepath : 导出文件路径
        """
        config = {
            'warning_levels': self.warning_levels,
            'trigger_rules': self.trigger_rules,
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"预警配置已导出: {filepath}")


class WarningThresholdManager:
    """预警阈值管理器"""
    
    def __init__(self):
        """初始化阈值管理器"""
        # 默认阈值配置
        self.thresholds = {
            'score_thresholds': {
                'R5': {'min': 70, 'max': 100},
                'R4': {'min': 50, 'max': 70},
                'R3': {'min': 30, 'max': 50},
                'R2': {'min': 15, 'max': 30},
                'R1': {'min': 0, 'max': 15}
            },
            'feature_thresholds': {
                'fee_decline_rate': {
                    'critical': -0.4,
                    'warning': -0.2,
                    'attention': -0.1
                },
                'call_decline_rate': {
                    'critical': -0.6,
                    'warning': -0.4,
                    'attention': -0.2
                },
                'complaint_count': {
                    'critical': 5,
                    'warning': 3,
                    'attention': 1
                },
                'silent_days': {
                    'critical': 14,
                    'warning': 7,
                    'attention': 3
                },
                'satisfaction_score': {
                    'critical': 2,
                    'warning': 3,
                    'attention': 3.5
                }
            },
            'dimension_weights': {
                'consumption': 0.30,
                'communication': 0.35,
                'interaction': 0.25,
                'time_series': 0.10
            }
        }
    
    def get_threshold_status(self, value: float, 
                            threshold_config: Dict) -> str:
        """
        获取阈状态
        
        Parameters:
        -----------
        value : 特征值
        threshold_config : 阈值配置
        
        Returns:
        --------
        str : 状态（critical/warning/attention/normal）
        """
        # 判断是上升型还是下降型阈值
        if threshold_config.get('critical', 0) > threshold_config.get('attention', 0):
            # 上升型（如投诉次数）
            if value >= threshold_config['critical']:
                return 'critical'
            elif value >= threshold_config['warning']:
                return 'warning'
            elif value >= threshold_config['attention']:
                return 'attention'
            else:
                return 'normal'
        else:
            # 下降型（如满意度）
            if value <= threshold_config['critical']:
                return 'critical'
            elif value <= threshold_config['warning']:
                return 'warning'
            elif value <= threshold_config['attention']:
                return 'attention'
            else:
                return 'normal'
    
    def adjust_thresholds(self, adjustments: Dict):
        """
        调整阈值
        
        Parameters:
        -----------
        adjustments : 阈值调整配置
        """
        for category, values in adjustments.items():
            if category in self.thresholds:
                self.thresholds[category].update(values)
        
        print("阈值已更新")


def run_warning_system():
    """运行预警系统"""
    print("\n" + "="*70)
    print("电信用户流失预警 - 预警规则系统")
    print("="*70)
    
    # 加载评分数据
    try:
        scores = pd.read_csv('/root/.openclaw/workspace/03_输出成果/模型文件/churn_score_report.csv')
        print(f"已加载评分数据: {scores.shape}")
    except FileNotFoundError:
        print("评分文件不存在，请先运行评分模型")
        return None
    
    # 初始化预警系统
    warning_system = ChurnWarningSystem()
    
    # 生成预警报告
    warning_report = warning_system.generate_warning_report(scores)
    
    # 导出预警配置
    config_path = '/root/.openclaw/workspace/03_输出成果/模型文件/warning_config.json'
    warning_system.export_warning_config(config_path)
    
    # 保存预警报告
    output_path = '/root/.openclaw/workspace/03_输出成果/报告文档/warning_report.csv'
    warning_report.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n预警报告已保存: {output_path}")
    
    # 生成优先处理名单
    for level in ['R5', 'R4']:
        priority_users = warning_system.get_priority_users(warning_report, level)
        if len(priority_users) > 0:
            filename = f'/root/.openclaw/workspace/03_输出成果/报告文档/{level}_priority_users.csv'
            priority_users.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"{level}优先处理名单已保存: {filename}")
    
    return warning_report


if __name__ == "__main__":
    run_warning_system()
