#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程审核集成模块
用于各步骤输出物自动审核

使用方法：
    from compass_audit_integration import CompassAuditIntegration
    
    # 在输出物生成后调用
    audit = CompassAuditIntegration()
    result = audit.audit_output("step1", output_content, output_path)
    
    # 获取审核报告
    report = result['report']
    grade = result['grade']
    can_proceed = result['can_proceed']

Author: 南乔
Date: 2026-03-23
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# 添加compass_auditor_service路径
sys.path.insert(0, '/root/.openclaw/workspace/03_输出成果')
from compass_auditor_service import CompassAuditorService


class CompassAuditIntegration:
    """指南针工程审核集成"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化审核集成
        
        Args:
            output_dir: 审核报告输出目录，默认为工作目录
        """
        self.auditor = CompassAuditorService()
        self.output_dir = output_dir or '/root/.openclaw/workspace/03_输出成果/审核报告'
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def audit_output(self, step: str, content: str, output_path: str = None, 
                     prev_score: int = 100, auto_save: bool = True) -> Dict:
        """
        审核输出物
        
        Args:
            step: 步骤编号（step1-step6）
            content: 输出内容
            output_path: 输出文件路径（用于记录）
            prev_score: 上一步评分
            auto_save: 是否自动保存审核报告
        
        Returns:
            审核结果字典
        """
        # 执行审核
        result = self.auditor.audit_content(step, content, prev_score)
        
        # 生成报告
        report = self.auditor.generate_report(result)
        
        # 准备返回结果
        audit_result = {
            'step': step,
            'step_name': result.step_name,
            'timestamp': result.timestamp,
            'total_score': result.total_score,
            'grade': result.grade,
            'conclusion': result.conclusion,
            'can_proceed': result.can_proceed,
            'input_passed': result.input_passed,
            'suggestions': result.suggestions,
            'output_details': [
                {
                    'name': d.name,
                    'max_score': d.max_score,
                    'actual_score': d.actual_score,
                    'passed': d.passed,
                    'missing_points': d.missing_points
                } for d in result.output_details
            ],
            'report': report,
            'output_path': output_path
        }
        
        # 自动保存审核报告
        if auto_save and output_path:
            self._save_audit_report(step, report, result.grade, result.total_score, output_path)
        
        # 打印审核摘要
        self._print_audit_summary(audit_result)
        
        return audit_result
    
    def audit_value(self, all_outputs: Dict) -> Dict:
        """
        价值审核（全部完成后调用）
        
        Args:
            all_outputs: 所有步骤的输出内容
                {
                    'step1': {'content': '...', 'score': 85},
                    'step2': {'content': '...', 'score': 90},
                    ...
                }
        
        Returns:
            价值审核结果
        """
        # 价值审核维度
        value_check = {
            'problem_solving': 0,  # 问题解决度（30%）
            'goal_achievement': 0,  # 目标达成度（25%）
            'feasibility': 0,       # 方案可行性（25%）
            'knowledge沉淀': 0      # 知识沉淀度（20%）
        }
        
        # 简化实现：基于各步骤评分计算
        scores = [v.get('score', 0) for v in all_outputs.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 问题解决度：基于需求文档和思维导图
        if 'step1' in all_outputs and 'step2' in all_outputs:
            step1_score = all_outputs['step1'].get('score', 0)
            step2_score = all_outputs['step2'].get('score', 0)
            value_check['problem_solving'] = (step1_score + step2_score) / 2 * 0.3
        
        # 目标达成度：基于方案举措和PPT
        if 'step3' in all_outputs and 'step4' in all_outputs:
            step3_score = all_outputs['step3'].get('score', 0)
            step4_score = all_outputs['step4'].get('score', 0)
            value_check['goal_achievement'] = (step3_score + step4_score) / 2 * 0.25
        
        # 方案可行性：基于详细设计
        if 'step5' in all_outputs:
            value_check['feasibility'] = all_outputs['step5'].get('score', 0) * 0.25
        
        # 知识沉淀度：基于项目管控
        if 'step6' in all_outputs:
            value_check['knowledge沉淀'] = all_outputs['step6'].get('score', 0) * 0.2
        
        # 计算总分
        total_value_score = sum(value_check.values())
        
        # 确定等级
        if total_value_score >= 90:
            value_grade = 'S级'
            value_conclusion = '价值连城，可直接推广'
        elif total_value_score >= 80:
            value_grade = 'A级'
            value_conclusion = '高价值，建议采纳'
        elif total_value_score >= 70:
            value_grade = 'B级'
            value_conclusion = '有价值，优化后采纳'
        elif total_value_score >= 60:
            value_grade = 'C级'
            value_conclusion = '有参考价值'
        else:
            value_grade = 'D级'
            value_conclusion = '需重新打磨'
        
        return {
            'total_score': round(total_value_score, 1),
            'grade': value_grade,
            'conclusion': value_conclusion,
            'dimension_scores': value_check
        }
    
    def _save_audit_report(self, step: str, report: str, grade: str, 
                          score: int, output_path: str):
        """保存审核报告"""
        try:
            # 生成报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{step}_审核报告_{grade}_{score}分_{timestamp}.md"
            report_path = os.path.join(self.output_dir, report_filename)
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
                f.write(f"\n\n---\n")
                f.write(f"输出物路径：{output_path}\n")
                f.write(f"审核时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"✅ 审核报告已保存：{report_path}")
            
        except Exception as e:
            print(f"⚠️ 保存审核报告失败：{e}")
    
    def _print_audit_summary(self, result: Dict):
        """打印审核摘要"""
        grade_emoji = {
            'A级': '🟢',
            'B级': '🟡',
            'C级': '🟠',
            'D级': '🔴'
        }
        
        emoji = grade_emoji.get(result['grade'], '⚪')
        
        print("\n" + "=" * 60)
        print("🔍 指南针工程质量审核")
        print("=" * 60)
        print(f"步骤：步骤{result['step'][-1]} - {result['step_name']}")
        print(f"总分：{result['total_score']}/100")
        print(f"等级：{emoji} {result['grade']}")
        print(f"结论：{result['conclusion']}")
        print(f"可进入下一步：{'是' if result['can_proceed'] else '否'}")
        
        if result['suggestions']:
            print("\n💡 改进建议：")
            for i, sug in enumerate(result['suggestions'][:3], 1):
                print(f"  {i}. {sug}")
        
        print("=" * 60 + "\n")


# ============================================================
# 便捷函数（供各步骤脚本直接调用）
# ============================================================

def audit_step1(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤1：需求文档"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step1", content, output_path, prev_score)


def audit_step2(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤2：思维导图"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step2", content, output_path, prev_score)


def audit_step3(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤3：方案举措Excel"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step3", content, output_path, prev_score)


def audit_step4(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤4：PPT方案"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step4", content, output_path, prev_score)


def audit_step5(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤5：详细设计文档"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step5", content, output_path, prev_score)


def audit_step6(content: str, output_path: str = None, prev_score: int = 100) -> Dict:
    """审核步骤6：项目管控计划"""
    audit = CompassAuditIntegration()
    return audit.audit_output("step6", content, output_path, prev_score)


def audit_final_value(all_outputs: Dict) -> Dict:
    """价值审核（全部完成后调用）"""
    audit = CompassAuditIntegration()
    return audit.audit_value(all_outputs)


# ============================================================
# 主程序（测试）
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("指南针工程审核集成模块 V1.0")
    print("=" * 60)
    
    # 测试：步骤1审核
    test_content = """
一、需求背景
本项目旨在为湖北电信打造AI智能配案系统。

二、需求描述
1. 智能配案功能
2. 套餐对比功能

三、需求目标
提升营销效率50%。

四、验收标准
响应时间<3秒。
"""
    
    result = audit_step1(test_content, "/tmp/test.docx")
    
    print(f"\n审核结果：")
    print(f"- 总分：{result['total_score']}/100")
    print(f"- 等级：{result['grade']}")
    print(f"- 可进入下一步：{result['can_proceed']}")
