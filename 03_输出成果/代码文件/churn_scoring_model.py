#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电信用户流失预警 - 流失评分模型
作者：知微
日期：2026-03-21
功能：设计流失风险评分模型，包括多维度评分和综合风险评估
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, precision_recall_curve, classification_report
import warnings
warnings.filterwarnings('ignore')


class ChurnScoringModel:
    """流失风险评分模型"""
    
    def __init__(self):
        """初始化模型"""
        self.scaler = MinMaxScaler(feature_range=(0, 100))
        self.feature_weights = {}
        self.model = None
        self.feature_importance = None
        
    def calculate_consumption_score(self, features: pd.DataFrame) -> pd.Series:
        """
        计算消费行为评分（0-100分，分数越高风险越大）
        
        Parameters:
        -----------
        features : 特征表
        
        Returns:
        --------
        Series : 消费行为评分
        """
        print(">>> 计算消费行为评分...")
        
        score = pd.Series(0, index=features.index)
        
        # 1. 消费下降评分（占比30%）
        if 'fee_decline_rate' in features.columns:
            decline_score = np.clip(-features['fee_decline_rate'] * 100, 0, 100)
            score += decline_score * 0.30
        
        # 2. 消费波动评分（占比20%）
        if 'fee_volatility' in features.columns:
            volatility_score = np.clip(features['fee_volatility'] * 50, 0, 100)
            score += volatility_score * 0.20
        
        # 3. 欠费次数评分（占比25%）
        if 'arrears_count' in features.columns:
            arrears_score = np.clip(features['arrears_count'] * 20, 0, 100)
            score += arrears_score * 0.25
        
        # 4. 套餐变更评分（占比15%）
        if 'package_change_count' in features.columns:
            pkg_change_score = np.clip(features['package_change_count'] * 25, 0, 100)
            score += pkg_change_score * 0.15
        
        # 5. ARPU下降评分（占比10%）
        if 'arpu' in features.columns:
            # ARPU越低，风险越高
            arpu_percentile = features['arpu'].rank(pct=True)
            arpu_score = (1 - arpu_percentile) * 100
            score += arpu_score * 0.10
        
        return score
    
    def calculate_communication_score(self, features: pd.DataFrame) -> pd.Series:
        """
        计算通信行为评分（0-100分，分数越高风险越大）
        
        Parameters:
        -----------
        features : 特征表
        
        Returns:
        --------
        Series : 通信行为评分
        """
        print(">>> 计算通信行为评分...")
        
        score = pd.Series(0, index=features.index)
        
        # 1. 通话活跃度下降评分（占比30%）
        if 'call_decline_rate' in features.columns:
            call_decline_score = np.clip(-features['call_decline_rate'] * 100, 0, 100)
            score += call_decline_score * 0.30
        
        # 2. 沉默天数评分（占比25%）
        if 'silent_days' in features.columns:
            silent_score = np.clip(features['silent_days'] * 5, 0, 100)
            score += silent_score * 0.25
        
        # 3. 主被叫比异常评分（占比20%）
        if 'out_in_ratio' in features.columns:
            # 比例过低或过高都异常
            ratio_deviation = np.abs(features['out_in_ratio'] - 1)
            ratio_score = np.clip(ratio_deviation * 50, 0, 100)
            score += ratio_score * 0.20
        
        # 4. 流量使用下降评分（占比15%）
        if 'data_decline_rate' in features.columns:
            data_decline_score = np.clip(-features['data_decline_rate'] * 100, 0, 100)
            score += data_decline_score * 0.15
        
        # 5. 流量使用率评分（占比10%）
        if 'data_usage_rate' in features.columns:
            # 使用率过低可能预示流失
            low_usage_score = np.clip((0.3 - features['data_usage_rate']) * 200, 0, 100)
            score += low_usage_score * 0.10
        
        return score
    
    def calculate_interaction_score(self, features: pd.DataFrame) -> pd.Series:
        """
        计算交互行为评分（0-100分，分数越高风险越大）
        
        Parameters:
        -----------
        features : 特征表
        
        Returns:
        --------
        Series : 交互行为评分
        """
        print(">>> 计算交互行为评分...")
        
        score = pd.Series(0, index=features.index)
        
        # 1. 投诉次数评分（占比35%）
        if 'complaint_count_sum' in features.columns:
            complaint_score = np.clip(features['complaint_count_sum'] * 20, 0, 100)
            score += complaint_score * 0.35
        
        # 2. 问题未解决评分（占比25%）
        if 'resolution_rate' in features.columns:
            unresolved_score = (1 - features['resolution_rate']) * 100
            score += unresolved_score * 0.25
        
        # 3. 满意度评分（占比20%）
        if 'satisfaction_score_mean' in features.columns:
            # 满意度越低，风险越高
            sat_score = np.clip((3 - features['satisfaction_score_mean']) * 50, 0, 100)
            score += sat_score * 0.20
        
        # 4. 投诉升级评分（占比10%）
        if 'has_escalation' in features.columns:
            escalation_score = features['has_escalation'] * 100
            score += escalation_score * 0.10
        
        # 5. APP使用频率评分（占比10%）
        if 'app_usage_count_sum' in features.columns:
            # 使用频率过低可能预示流失
            app_usage_percentile = features['app_usage_count_sum'].rank(pct=True)
            low_usage_score = (1 - app_usage_percentile) * 100
            score += low_usage_score * 0.10
        
        return score
    
    def calculate_time_series_score(self, features: pd.DataFrame) -> pd.Series:
        """
        计算时间序列评分（0-100分，分数越高风险越大）
        
        Parameters:
        -----------
        features : 特征表
        
        Returns:
        --------
        Series : 时间序列评分
        """
        print(">>> 计算时间序列评分...")
        
        score = pd.Series(0, index=features.index)
        
        # 1. 活跃度衰减评分（占比40%）
        if 'activity_decay' in features.columns:
            decay_score = np.clip(-features['activity_decay'] * 100, 0, 100)
            score += decay_score * 0.40
        
        # 2. 近期消费变化评分（占比30%）
        if 'recent_fee_change' in features.columns:
            recent_change_score = np.clip(-features['recent_fee_change'] * 100, 0, 100)
            score += recent_change_score * 0.30
        
        # 3. 消费连续性评分（占比30%）
        if 'consumption_continuity' in features.columns:
            continuity_score = (1 - features['consumption_continuity']) * 100
            score += continuity_score * 0.30
        
        return score
    
    def calculate_comprehensive_score(self, features: pd.DataFrame,
                                     weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        计算综合流失风险评分
        
        Parameters:
        -----------
        features : 特征表
        weights : 各维度权重
        
        Returns:
        --------
        DataFrame : 包含各维度评分和综合评分的表
        """
        print("\n" + "="*60)
        print("开始计算流失风险评分...")
        print("="*60)
        
        # 默认权重
        if weights is None:
            weights = {
                'consumption': 0.30,
                'communication': 0.35,
                'interaction': 0.25,
                'time_series': 0.10
            }
        
        # 计算各维度评分
        scores = pd.DataFrame()
        scores['user_id'] = features['user_id']
        
        scores['consumption_score'] = self.calculate_consumption_score(features)
        scores['communication_score'] = self.calculate_communication_score(features)
        scores['interaction_score'] = self.calculate_interaction_score(features)
        scores['time_series_score'] = self.calculate_time_series_score(features)
        
        # 计算综合评分
        scores['churn_risk_score'] = (
            scores['consumption_score'] * weights['consumption'] +
            scores['communication_score'] * weights['communication'] +
            scores['interaction_score'] * weights['interaction'] +
            scores['time_series_score'] * weights['time_series']
        )
        
        # 四舍五入
        scores['churn_risk_score'] = scores['churn_risk_score'].round(2)
        
        print("\n评分统计：")
        print(scores[['consumption_score', 'communication_score', 
                     'interaction_score', 'churn_risk_score']].describe())
        
        return scores
    
    def define_risk_levels(self, scores: pd.DataFrame) -> pd.DataFrame:
        """
        定义风险等级
        
        Parameters:
        -----------
        scores : 评分表
        
        Returns:
        --------
        DataFrame : 包含风险等级的评分表
        """
        print("\n>>> 定义风险等级...")
        
        def get_risk_level(score):
            if score >= 70:
                return '极高风险'
            elif score >= 50:
                return '高风险'
            elif score >= 30:
                return '中风险'
            elif score >= 15:
                return '低风险'
            else:
                return '安全'
        
        def get_risk_code(level):
            risk_codes = {
                '极高风险': 'R5',
                '高风险': 'R4',
                '中风险': 'R3',
                '低风险': 'R2',
                '安全': 'R1'
            }
            return risk_codes.get(level, 'R1')
        
        def get_priority(level):
            priorities = {
                '极高风险': 'P0-紧急',
                '高风险': 'P1-重要',
                '中风险': 'P2-关注',
                '低风险': 'P3-观察',
                '安全': 'P4-正常'
            }
            return priorities.get(level, 'P4-正常')
        
        scores['risk_level'] = scores['churn_risk_score'].apply(get_risk_level)
        scores['risk_code'] = scores['risk_level'].apply(get_risk_code)
        scores['priority'] = scores['risk_level'].apply(get_priority)
        
        # 风险等级分布
        print("\n风险等级分布：")
        risk_distribution = scores['risk_level'].value_counts()
        for level, count in risk_distribution.items():
            pct = count / len(scores) * 100
            print(f"  {level}: {count} 人 ({pct:.1f}%)")
        
        return scores
    
    def identify_key_risk_factors(self, features: pd.DataFrame, 
                                  scores: pd.DataFrame) -> pd.DataFrame:
        """
        识别关键风险因素
        
        Parameters:
        -----------
        features : 特征表
        scores : 评分表
        
        Returns:
        --------
        DataFrame : 包含关键风险因素的表
        """
        print("\n>>> 识别关键风险因素...")
        
        risk_factors = pd.DataFrame()
        risk_factors['user_id'] = features['user_id']
        
        # 定义风险因素识别规则
        risk_factors['risk_factors'] = ''
        
        for idx in risk_factors.index:
            factors = []
            
            # 消费类风险因素
            if features.loc[idx].get('fee_decline_rate', 0) < -0.3:
                factors.append('消费大幅下降')
            if features.loc[idx].get('arrears_count', 0) > 2:
                factors.append('频繁欠费')
            if features.loc[idx].get('package_change_count', 0) > 1:
                factors.append('套餐频繁变更')
            
            # 通信类风险因素
            if features.loc[idx].get('call_decline_rate', 0) < -0.5:
                factors.append('通话活跃度下降')
            if features.loc[idx].get('silent_days', 0) > 7:
                factors.append('出现沉默期')
            if features.loc[idx].get('data_decline_rate', 0) < -0.4:
                factors.append('流量使用下降')
            
            # 交互类风险因素
            if features.loc[idx].get('complaint_count_sum', 0) > 3:
                factors.append('投诉次数过多')
            if features.loc[idx].get('resolution_rate', 1) < 0.5:
                factors.append('问题未解决')
            if features.loc[idx].get('satisfaction_score_mean', 5) < 3:
                factors.append('满意度低')
            if features.loc[idx].get('has_escalation', 0) == 1:
                factors.append('投诉升级')
            
            risk_factors.loc[idx, 'risk_factors'] = '、'.join(factors) if factors else '无明显风险因素'
            risk_factors.loc[idx, 'risk_factor_count'] = len(factors)
        
        # 合并到评分表
        scores = scores.merge(risk_factors, on='user_id', how='left')
        
        return scores
    
    def build_prediction_model(self, features: pd.DataFrame, 
                               labels: pd.Series = None) -> Dict:
        """
        构建流失预测模型
        
        Parameters:
        -----------
        features : 特征表
        labels : 流失标签（1=流失，0=未流失）
        
        Returns:
        --------
        Dict : 模型信息和评估结果
        """
        print("\n" + "="*60)
        print("构建流失预测模型...")
        print("="*60)
        
        # 如果没有标签，使用评分作为概率
        if labels is None:
            print("警告：没有真实标签，使用评分模拟...")
            labels = (features.get('churn_risk_score', pd.Series(0, index=features.index)) > 50).astype(int)
        
        # 准备特征
        feature_cols = [col for col in features.columns 
                       if col not in ['user_id', 'risk_level', 'risk_code', 
                                     'priority', 'risk_factors', 'churn_risk_score']]
        
        X = features[feature_cols].select_dtypes(include=[np.number])
        y = labels
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 标准化
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 训练多个模型
        models = {
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        results = {}
        best_model = None
        best_auc = 0
        
        for name, model in models.items():
            print(f"\n训练 {name}...")
            model.fit(X_train_scaled, y_train)
            
            # 评估
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            auc = roc_auc_score(y_test, y_pred_proba)
            
            results[name] = {
                'model': model,
                'auc': auc,
                'feature_importance': None
            }
            
            # 获取特征重要性
            if hasattr(model, 'feature_importances_'):
                importance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                results[name]['feature_importance'] = importance
            
            print(f"  AUC: {auc:.4f}")
            
            if auc > best_auc:
                best_auc = auc
                best_model = model
        
        # 选择最佳模型
        self.model = best_model
        print(f"\n最佳模型: {type(best_model).__name__}, AUC: {best_auc:.4f}")
        
        # 特征重要性
        if hasattr(best_model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 重要特征：")
            print(self.feature_importance.head(10))
        
        return results
    
    def generate_churn_score_report(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        生成流失评分报告
        
        Parameters:
        -----------
        features : 特征表
        
        Returns:
        --------
        DataFrame : 完整的流失评分报告
        """
        # 计算综合评分
        scores = self.calculate_comprehensive_score(features)
        
        # 定义风险等级
        scores = self.define_risk_levels(scores)
        
        # 识别关键风险因素
        scores = self.identify_key_risk_factors(features, scores)
        
        # 合并关键特征
        key_features = ['user_id', 'age', 'gender', 'city', 'customer_type',
                       'arpu', 'call_count_sum', 'data_usage_sum', 
                       'complaint_count_sum', 'satisfaction_score_mean']
        
        available_features = [f for f in key_features if f in features.columns]
        report = features[available_features].merge(scores, on='user_id', how='left')
        
        return report


def run_churn_scoring():
    """运行流失评分流程"""
    print("\n" + "="*70)
    print("电信用户流失预警 - 流失评分模型")
    print("="*70)
    
    # 加载特征数据
    try:
        features = pd.read_csv('/root/.openclaw/workspace/03_输出成果/模型文件/user_features.csv')
        print(f"已加载特征数据: {features.shape}")
    except FileNotFoundError:
        print("特征文件不存在，请先运行特征工程模块")
        return None
    
    # 初始化评分模型
    scoring_model = ChurnScoringModel()
    
    # 生成评分报告
    report = scoring_model.generate_churn_score_report(features)
    
    # 保存报告
    output_path = '/root/.openclaw/workspace/03_输出成果/模型文件/churn_score_report.csv'
    report.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n评分报告已保存: {output_path}")
    
    # 保存高风险用户名单
    high_risk_users = report[report['risk_level'].isin(['极高风险', '高风险'])]
    high_risk_path = '/root/.openclaw/workspace/03_输出成果/模型文件/high_risk_users.csv'
    high_risk_users.to_csv(high_risk_path, index=False, encoding='utf-8-sig')
    print(f"高风险用户名单已保存: {high_risk_path}")
    
    return report


if __name__ == "__main__":
    run_churn_scoring()
