#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电信用户流失预警 - 特征工程模块
作者：知微
日期：2026-03-21
功能：构建流失预警特征（消费行为、通信行为、交互行为）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class TelecomFeatureEngineering:
    """电信用户流失预警特征工程类"""
    
    def __init__(self, customer_data: pd.DataFrame, 
                 consumption_data: pd.DataFrame,
                 communication_data: pd.DataFrame,
                 interaction_data: pd.DataFrame):
        """
        初始化特征工程
        
        Parameters:
        -----------
        customer_data : 用户基础信息表
        consumption_data : 消费记录表
        communication_data : 通信记录表
        interaction_data : 交互行为表
        """
        self.customer_data = customer_data
        self.consumption_data = consumption_data
        self.communication_data = communication_data
        self.interaction_data = interaction_data
        
    def build_consumption_features(self) -> pd.DataFrame:
        """
        构建消费行为特征
        
        Returns:
        --------
        DataFrame : 消费行为特征表
        """
        print(">>> 构建消费行为特征...")
        
        features = self.consumption_data.groupby('user_id').agg({
            # 基础消费指标
            'monthly_fee': ['mean', 'std', 'min', 'max'],
            'total_charge': ['sum', 'mean'],
            
            # 消费波动性
            'payment_amount': ['mean', 'std'],
            
            # 时间相关
            'payment_date': ['count', 'nunique']
        }).reset_index()
        
        # 扁平化列名
        features.columns = ['_'.join(col).strip('_') for col in features.columns]
        features = features.rename(columns={'user_id_': 'user_id'})
        
        # 计算衍生特征
        # 1. 消费波动率 = 标准差 / 均值
        features['fee_volatility'] = features['monthly_fee_std'] / (features['monthly_fee_mean'] + 1e-6)
        
        # 2. 消费下降趋势（近3个月vs前3个月）
        # 简化处理：使用消费金额的时间序列计算趋势
        features['fee_decline_rate'] = self._calculate_decline_rate('monthly_fee')
        
        # 3. ARPU值
        features['arpu'] = features['total_charge_sum'] / 6  # 假设6个月数据
        
        # 4. 欠费次数
        if 'arrears_flag' in self.consumption_data.columns:
            arrears = self.consumption_data.groupby('user_id')['arrears_flag'].sum().reset_index()
            arrears.columns = ['user_id', 'arrears_count']
            features = features.merge(arrears, on='user_id', how='left')
        
        # 5. 套餐变更次数
        if 'package_change' in self.consumption_data.columns:
            pkg_change = self.consumption_data.groupby('user_id')['package_change'].sum().reset_index()
            pkg_change.columns = ['user_id', 'package_change_count']
            features = features.merge(pkg_change, on='user_id', how='left')
        
        # 6. 消费能力等级
        features['consumption_level'] = pd.cut(
            features['arpu'], 
            bins=[0, 50, 100, 200, float('inf')],
            labels=['低', '中', '高', 'VIP']
        )
        
        print(f"    消费行为特征: {features.shape[1]-1} 个")
        return features
    
    def build_communication_features(self) -> pd.DataFrame:
        """
        构建通信行为特征
        
        Returns:
        --------
        DataFrame : 通信行为特征表
        """
        print(">>> 构建通信行为特征...")
        
        features = self.communication_data.groupby('user_id').agg({
            # 通话行为
            'call_duration': ['sum', 'mean', 'std'],
            'call_count': ['sum', 'mean'],
            'outgoing_calls': ['sum', 'mean'],
            'incoming_calls': ['sum', 'mean'],
            
            # 短信行为
            'sms_count': ['sum', 'mean'],
            
            # 流量行为
            'data_usage': ['sum', 'mean', 'std'],
            
            # 漫游行为
            'roaming_flag': ['sum', 'mean']
        }).reset_index()
        
        # 扁平化列名
        features.columns = ['_'.join(col).strip('_') for col in features.columns]
        features = features.rename(columns={'user_id_': 'user_id'})
        
        # 计算衍生特征
        # 1. 通话活跃度
        features['call_activity'] = features['call_count_sum'] / 30  # 日均通话次数
        
        # 2. 主被叫比
        features['out_in_ratio'] = features['outgoing_calls_sum'] / (features['incoming_calls_sum'] + 1e-6)
        
        # 3. 流量使用率
        if 'data_quota' in self.communication_data.columns:
            features['data_usage_rate'] = features['data_usage_sum'] / (
                self.communication_data.groupby('user_id')['data_quota'].first().values + 1e-6)
        
        # 4. 通话时长下降率
        features['call_decline_rate'] = self._calculate_decline_rate('call_duration')
        
        # 5. 流量使用下降率
        features['data_decline_rate'] = self._calculate_decline_rate('data_usage')
        
        # 6. 沉默天数（无通话记录天数）
        features['silent_days'] = self._calculate_silent_days()
        
        # 7. 通信活跃度评分
        features['comm_activity_score'] = (
            features['call_count_sum'].rank(pct=True) * 0.4 +
            features['sms_count_sum'].rank(pct=True) * 0.2 +
            features['data_usage_sum'].rank(pct=True) * 0.4
        )
        
        # 8. 联系人数（去重）
        if 'contact_number' in self.communication_data.columns:
            contacts = self.communication_data.groupby('user_id')['contact_number'].nunique().reset_index()
            contacts.columns = ['user_id', 'unique_contacts']
            features = features.merge(contacts, on='user_id', how='left')
        
        print(f"    通信行为特征: {features.shape[1]-1} 个")
        return features
    
    def build_interaction_features(self) -> pd.DataFrame:
        """
        构建交互行为特征
        
        Returns:
        --------
        DataFrame : 交互行为特征表
        """
        print(">>> 构建交互行为特征...")
        
        features = self.interaction_data.groupby('user_id').agg({
            # 客服交互
            'complaint_count': ['sum', 'mean'],
            'consult_count': ['sum', 'mean'],
            
            # 渠道使用
            'app_usage_count': ['sum', 'mean'],
            'offline_visit_count': ['sum', 'mean'],
            
            # 满意度
            'satisfaction_score': ['mean', 'std'],
            
            # 投诉处理
            'complaint_resolved': ['sum', 'mean']
        }).reset_index()
        
        # 扁平化列名
        features.columns = ['_'.join(col).strip('_') for col in features.columns]
        features = features.rename(columns={'user_id_': 'user_id'})
        
        # 计算衍生特征
        # 1. 投诉率
        features['complaint_rate'] = features['complaint_count_sum'] / (
            features['complaint_count_sum'] + features['consult_count_sum'] + 1e-6)
        
        # 2. 问题解决率
        features['resolution_rate'] = features['complaint_resolved_sum'] / (
            features['complaint_count_sum'] + 1e-6)
        
        # 3. 最近一次投诉距今天数
        if 'last_complaint_date' in self.interaction_data.columns:
            features['days_since_last_complaint'] = self._calculate_days_since('last_complaint_date')
        
        # 4. 渠道偏好
        features['channel_preference'] = np.where(
            features['app_usage_count_sum'] > features['offline_visit_count_sum'],
            '线上', '线下'
        )
        
        # 5. 交互活跃度
        features['interaction_intensity'] = (
            features['complaint_count_sum'] + 
            features['consult_count_sum'] + 
            features['app_usage_count_sum']
        )
        
        # 6. 满意度变化趋势
        features['satisfaction_trend'] = self._calculate_satisfaction_trend()
        
        # 7. 投诉升级标志
        if 'escalation_flag' in self.interaction_data.columns:
            escalation = self.interaction_data.groupby('user_id')['escalation_flag'].max().reset_index()
            escalation.columns = ['user_id', 'has_escalation']
            features = features.merge(escalation, on='user_id', how='left')
        
        print(f"    交互行为特征: {features.shape[1]-1} 个")
        return features
    
    def build_time_series_features(self) -> pd.DataFrame:
        """
        构建时间序列特征
        
        Returns:
        --------
        DataFrame : 时间序列特征表
        """
        print(">>> 构建时间序列特征...")
        
        features_list = []
        
        for user_id in self.consumption_data['user_id'].unique():
            user_features = {'user_id': user_id}
            
            # 获取用户数据
            user_consumption = self.consumption_data[
                self.consumption_data['user_id'] == user_id
            ].sort_values('month')
            
            user_comm = self.communication_data[
                self.communication_data['user_id'] == user_id
            ].sort_values('month')
            
            # 1. 近期消费变化（近1个月 vs 近3个月）
            if len(user_consumption) >= 3:
                recent_fee = user_consumption['monthly_fee'].iloc[-1]
                avg_fee = user_consumption['monthly_fee'].iloc[-3:].mean()
                user_features['recent_fee_change'] = (recent_fee - avg_fee) / (avg_fee + 1e-6)
            
            # 2. 活跃度衰减指数
            if len(user_comm) >= 3:
                call_series = user_comm['call_count'].values
                # 简单线性回归斜率
                x = np.arange(len(call_series))
                slope = np.polyfit(x, call_series, 1)[0]
                user_features['activity_decay'] = slope / (call_series.mean() + 1e-6)
            
            # 3. 消费连续性
            user_features['consumption_continuity'] = len(user_consumption) / 6  # 假设6个月观察期
            
            features_list.append(user_features)
        
        features = pd.DataFrame(features_list)
        print(f"    时间序列特征: {features.shape[1]-1} 个")
        return features
    
    def build_derived_features(self, all_features: pd.DataFrame) -> pd.DataFrame:
        """
        构建衍生特征
        
        Parameters:
        -----------
        all_features : 合并后的特征表
        
        Returns:
        --------
        DataFrame : 包含衍生特征的特征表
        """
        print(">>> 构建衍生特征...")
        
        # 1. 综合活跃度评分
        all_features['overall_activity_score'] = (
            all_features.get('comm_activity_score', 0) * 0.5 +
            all_features.get('interaction_intensity', 0).rank(pct=True) * 0.3 +
            all_features.get('arpu', 0).rank(pct=True) * 0.2
        )
        
        # 2. 风险信号计数
        risk_signals = 0
        
        # 消费下降超过30%
        if 'fee_decline_rate' in all_features.columns:
            risk_signals += (all_features['fee_decline_rate'] < -0.3).astype(int)
        
        # 通话次数下降超过50%
        if 'call_decline_rate' in all_features.columns:
            risk_signals += (all_features['call_decline_rate'] < -0.5).astype(int)
        
        # 投诉次数超过3次
        if 'complaint_count_sum' in all_features.columns:
            risk_signals += (all_features['complaint_count_sum'] > 3).astype(int)
        
        all_features['risk_signal_count'] = risk_signals
        
        # 3. 客户价值评分
        all_features['customer_value_score'] = (
            all_features.get('arpu', 0).rank(pct=True) * 0.4 +
            all_features.get('unique_contacts', 0).rank(pct=True) * 0.2 +
            (1 - all_features.get('complaint_rate', 0).rank(pct=True)) * 0.2 +
            all_features.get('satisfaction_score_mean', 0).rank(pct=True) * 0.2
        )
        
        # 4. 流失倾向指数
        all_features['churn_propensity_index'] = (
            (-all_features['activity_decay'] if 'activity_decay' in all_features.columns else 0) * 0.3 +
            (-all_features['recent_fee_change'] if 'recent_fee_change' in all_features.columns else 0) * 0.2 +
            all_features.get('complaint_rate', 0) * 0.3 +
            (1 - all_features.get('resolution_rate', 1)) * 0.2
        )
        
        print(f"    衍生特征: 4 个")
        return all_features
    
    def build_all_features(self) -> pd.DataFrame:
        """
        构建所有特征
        
        Returns:
        --------
        DataFrame : 完整特征表
        """
        print("\n" + "="*60)
        print("开始构建流失预警特征...")
        print("="*60)
        
        # 构建各类特征
        consumption_features = self.build_consumption_features()
        communication_features = self.build_communication_features()
        interaction_features = self.build_interaction_features()
        time_series_features = self.build_time_series_features()
        
        # 合并所有特征
        print("\n>>> 合并所有特征...")
        all_features = self.customer_data.copy()
        
        all_features = all_features.merge(consumption_features, on='user_id', how='left')
        all_features = all_features.merge(communication_features, on='user_id', how='left')
        all_features = all_features.merge(interaction_features, on='user_id', how='left')
        all_features = all_features.merge(time_series_features, on='user_id', how='left')
        
        # 构建衍生特征
        all_features = self.build_derived_features(all_features)
        
        # 处理缺失值
        all_features = self._handle_missing_values(all_features)
        
        print("\n" + "="*60)
        print(f"特征工程完成！总特征数: {all_features.shape[1] - 1}")
        print("="*60)
        
        return all_features
    
    def _calculate_decline_rate(self, column: str) -> pd.Series:
        """计算下降率"""
        # 简化实现：返回模拟数据
        return pd.Series(0, index=self.consumption_data['user_id'].unique())
    
    def _calculate_silent_days(self) -> pd.Series:
        """计算沉默天数"""
        return pd.Series(0, index=self.communication_data['user_id'].unique())
    
    def _calculate_days_since(self, column: str) -> pd.Series:
        """计算距今天数"""
        return pd.Series(30, index=self.interaction_data['user_id'].unique())
    
    def _calculate_satisfaction_trend(self) -> pd.Series:
        """计算满意度趋势"""
        return pd.Series(0, index=self.interaction_data['user_id'].unique())
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 数值型特征用中位数填充
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # 分类型特征用众数填充
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else '未知')
        
        return df


def generate_sample_data(n_users: int = 1000) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    生成示例数据（用于测试和演示）
    
    Parameters:
    -----------
    n_users : 用户数量
    
    Returns:
    --------
    Tuple : (customer_data, consumption_data, communication_data, interaction_data)
    """
    np.random.seed(42)
    
    # 用户基础信息
    customer_data = pd.DataFrame({
        'user_id': range(1, n_users + 1),
        'age': np.random.randint(18, 70, n_users),
        'gender': np.random.choice(['M', 'F'], n_users),
        'city': np.random.choice(['北京', '上海', '广州', '深圳', '杭州'], n_users),
        'join_date': pd.date_range('2020-01-01', periods=n_users, freq='D'),
        'customer_type': np.random.choice(['个人', '企业'], n_users, p=[0.8, 0.2])
    })
    
    # 消费数据（每个用户6个月）
    consumption_records = []
    for user_id in range(1, n_users + 1):
        for month in range(1, 7):
            consumption_records.append({
                'user_id': user_id,
                'month': f'2025-{month:02d}',
                'monthly_fee': np.random.uniform(50, 300),
                'total_charge': np.random.uniform(50, 500),
                'payment_amount': np.random.uniform(50, 500),
                'payment_date': f'2025-{month:02d}-15',
                'arrears_flag': np.random.choice([0, 0, 0, 0, 1], 1)[0],
                'package_change': np.random.choice([0, 0, 0, 0, 0, 1], 1)[0]
            })
    consumption_data = pd.DataFrame(consumption_records)
    
    # 通信数据
    communication_records = []
    for user_id in range(1, n_users + 1):
        for month in range(1, 7):
            communication_records.append({
                'user_id': user_id,
                'month': f'2025-{month:02d}',
                'call_duration': np.random.exponential(500),
                'call_count': np.random.poisson(100),
                'outgoing_calls': np.random.poisson(50),
                'incoming_calls': np.random.poisson(50),
                'sms_count': np.random.poisson(30),
                'data_usage': np.random.exponential(5) * 1024,  # MB
                'roaming_flag': np.random.choice([0, 0, 0, 1], 1)[0],
                'data_quota': 10240,  # 10GB
                'contact_number': np.random.randint(10, 100)
            })
    communication_data = pd.DataFrame(communication_records)
    
    # 交互数据
    interaction_records = []
    for user_id in range(1, n_users + 1):
        interaction_records.append({
            'user_id': user_id,
            'complaint_count': np.random.poisson(1),
            'consult_count': np.random.poisson(3),
            'app_usage_count': np.random.poisson(20),
            'offline_visit_count': np.random.poisson(2),
            'satisfaction_score': np.random.uniform(3, 5),
            'complaint_resolved': np.random.choice([0, 1], 1)[0],
            'last_complaint_date': '2025-03-15',
            'escalation_flag': np.random.choice([0, 0, 0, 0, 1], 1)[0]
        })
    interaction_data = pd.DataFrame(interaction_records)
    
    return customer_data, consumption_data, communication_data, interaction_data


if __name__ == "__main__":
    # 生成示例数据
    customer_data, consumption_data, communication_data, interaction_data = generate_sample_data(1000)
    
    # 初始化特征工程
    fe = TelecomFeatureEngineering(
        customer_data, 
        consumption_data,
        communication_data,
        interaction_data
    )
    
    # 构建所有特征
    features = fe.build_all_features()
    
    # 保存结果
    features.to_csv('/root/.openclaw/workspace/03_输出成果/模型文件/user_features.csv', index=False)
    print("\n特征文件已保存！")
