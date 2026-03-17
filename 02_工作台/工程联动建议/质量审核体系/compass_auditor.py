#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程自动审核工具
自动审核各步骤的输入输出，生成审核报告
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================
# 审核模型配置
# ============================================================

# 各步骤审核标准
AUDIT_STANDARDS = {
    "step1": {
        "name": "需求文档",
        "input_checks": [
            "需求来源明确（客户访谈/邮件/会议纪要）",
            "需求描述清晰，无模糊表述",
            "需求信息完整，包含背景、目标、范围",
            "需求方已确认需求内容",
            "需求优先级已明确"
        ],
        "output_items": {
            "需求背景（20分）": 20,
            "需求描述（30分）": 30,
            "需求目标（20分）": 20,
            "约束条件（10分）": 10,
            "验收标准（20分）": 20
        },
        "quality_items": {
            "文档格式规范": 10
        }
    },
    "step2": {
        "name": "思维导图",
        "input_checks": [
            "步骤1需求文档已完成（评分≥70分）",
            "已充分理解需求文档内容",
            "已提取核心需求、痛点、目标",
            "已准备头脑风暴素材"
        ],
        "output_items": {
            "需求理解（25分）": 25,
            "痛点分析（25分）": 25,
            "解决方案想法（20分）": 20,
            "优先级评估（20分）": 20,
            "结构完整（10分）": 10
        },
        "quality_items": {
            "想法可行性、评估合理性": 10
        }
    },
    "step3": {
        "name": "方案举措Excel",
        "input_checks": [
            "步骤2思维导图已完成（评分≥70分）",
            "优先级评估已完成，P1方案已确定",
            "已提取解决方案想法",
            "已准备方案举措素材"
        ],
        "output_items": {
            "方案标题（10分）": 10,
            "建设目标（20分）": 20,
            "具体举措（30分）": 30,
            "预期效果（30分）": 30,
            "PPT页码（10分）": 10
        },
        "quality_items": {
            "目标量化、举措可行": 10
        }
    },
    "step4": {
        "name": "PPT",
        "input_checks": [
            "步骤3方案举措Excel已完成（评分≥70分）",
            "PPT大纲已明确（20页结构）",
            "方案举措素材已准备",
            "设计风格已确定"
        ],
        "output_items": {
            "封面完整（5分）": 5,
            "目录清晰（5分）": 5,
            "方案背景（10分）": 10,
            "方案目标（10分）": 10,
            "解决举措（30分）": 30,
            "实施计划（10分）": 10,
            "预期效果（10分）": 10,
            "风险保障（10分）": 10,
            "总结完整（10分）": 10
        },
        "quality_items": {
            "格式统一、图表清晰": 5,
            "逻辑清晰、视觉美观": 5
        }
    },
    "step5": {
        "name": "详细设计文档",
        "input_checks": [
            "PPT方案已评审通过（客户/领导确认）",
            "方案内容已确认",
            "评审意见已整理",
            "设计要求已明确"
        ],
        "output_items": {
            "系统架构（20分）": 20,
            "接口设计（20分）": 20,
            "数据库设计（20分）": 20,
            "UI设计（20分）": 20,
            "安全设计（10分）": 10,
            "附录完整（10分）": 10
        },
        "quality_items": {
            "架构合理、设计可行": 10
        }
    },
    "step6": {
        "name": "项目管控计划",
        "input_checks": [
            "步骤5详细设计文档已完成（评分≥70分）",
            "项目资源已确认（人力、预算、时间）",
            "项目团队已组建",
            "项目启动条件已满足"
        ],
        "output_items": {
            "甘特图（25分）": 25,
            "资源表（20分）": 20,
            "RACI矩阵（20分）": 20,
            "风险清单（20分）": 20,
            "沟通计划（15分）": 15
        },
        "quality_items": {
            "计划可行、风险可控": 10
        }
    }
}

# ============================================================
# 审核工具类
# ============================================================

class CompassAuditor:
    """指南针工程审核工具"""
    
    def __init__(self):
        self.audit_results = {}
    
    def audit_input(self, step: str, checks: List[str]) -> Dict:
        """
        审核输入
        
        Args:
            step: 步骤编号（step1-step6）
            checks: 审核项列表
        
        Returns:
            审核结果字典
        """
        results = []
        passed = 0
        total = len(checks)
        
        print(f"\n{'='*70}")
        print(f"步骤{step[-1]}：{AUDIT_STANDARDS[step]['name']} - 输入审核")
        print(f"{'='*70}\n")
        
        for i, check in enumerate(checks, 1):
            # 模拟审核（实际应用中需要根据实际情况判断）
            print(f"□ {check}")
            # 这里可以添加实际的审核逻辑
            # result = self._check_input_item(check)
            # results.append({"item": check, "passed": result})
        
        print(f"\n输入审核项：{total}项")
        print(f"通过：{passed}项")
        print(f"不通过：{total - passed}项")
        
        return {
            "step": step,
            "type": "input",
            "total": total,
            "passed": passed,
            "results": results
        }
    
    def audit_output(self, step: str, scores: Dict[str, int]) -> Dict:
        """
        审核输出
        
        Args:
            step: 步骤编号（step1-step6）
            scores: 各项得分字典
        
        Returns:
            审核结果字典
        """
        standard = AUDIT_STANDARDS[step]
        output_items = standard["output_items"]
        quality_items = standard["quality_items"]
        
        print(f"\n{'='*70}")
        print(f"步骤{step[-1]}：{standard['name']} - 输出审核")
        print(f"{'='*70}\n")
        
        # 计算内容审核得分
        content_score = 0
        content_max = sum(output_items.values())
        
        print("【内容审核】")
        print(f"{'审核项':<30} {'满分':>8} {'得分':>8} {'备注':<20}")
        print("-" * 70)
        
        for item, max_score in output_items.items():
            item_name = item.split("（")[0]
            actual_score = scores.get(item_name, 0)
            content_score += actual_score
            print(f"{item:<30} {max_score:>8} {actual_score:>8} {'':<20}")
        
        print("-" * 70)
        print(f"{'内容审核小计':<30} {content_max:>8} {content_score:>8}")
        
        # 计算质量审核得分
        quality_score = 0
        quality_max = sum(quality_items.values())
        
        print(f"\n【质量审核】")
        print(f"{'审核项':<30} {'满分':>8} {'得分':>8}")
        print("-" * 70)
        
        for item, max_score in quality_items.items():
            actual_score = scores.get(item, 0)
            quality_score += actual_score
            print(f"{item:<30} {max_score:>8} {actual_score:>8}")
        
        print("-" * 70)
        print(f"{'质量审核小计':<30} {quality_max:>8} {quality_score:>8}")
        
        # 计算总分
        total_score = content_score + quality_score
        total_max = content_max + quality_max
        
        print(f"\n{'='*70}")
        print(f"总分：{total_score}/{total_max}")
        
        # 确定等级
        if total_score >= 90:
            grade = "A级"
            conclusion = "优秀，可直接进入下一步"
        elif total_score >= 80:
            grade = "B级"
            conclusion = "良好，小幅优化后进入下一步"
        elif total_score >= 70:
            grade = "C级"
            conclusion = "合格，需要优化后进入下一步"
        else:
            grade = "D级"
            conclusion = "不合格，需要重新编写"
        
        print(f"审核结论：{grade} - {conclusion}")
        print(f"{'='*70}")
        
        return {
            "step": step,
            "type": "output",
            "content_score": content_score,
            "quality_score": quality_score,
            "total_score": total_score,
            "grade": grade,
            "conclusion": conclusion
        }
    
    def generate_report(self, step: str, input_result: Dict, output_result: Dict, 
                       suggestions: List[str] = None) -> str:
        """
        生成审核报告
        
        Args:
            step: 步骤编号
            input_result: 输入审核结果
            output_result: 输出审核结果
            suggestions: 改进建议列表
        
        Returns:
            审核报告文本
        """
        standard = AUDIT_STANDARDS[step]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
{'='*70}
                  指南针工程质量审核报告
{'='*70}

审核步骤：步骤{step[-1]} - {standard['name']}
审核时间：{timestamp}
审核人：[审核人姓名]

{'='*70}
                          输入审核
{'='*70}

审核项                    状态  说明
{'-'*70}
"""
        
        for item in input_result.get("results", []):
            status = "✅" if item["passed"] else "❌"
            report += f"{item['item']:<30} {status}\n"
        
        input_conclusion = "通过" if input_result["passed"] == input_result["total"] else "不通过"
        report += f"\n输入审核结论：{input_conclusion}\n"
        
        report += f"""
{'='*70}
                          输出审核
{'='*70}

审核项                    满分  得分  备注
{'-'*70}
"""
        
        for item, max_score in standard["output_items"].items():
            # 这里需要从output_result获取实际得分
            actual_score = output_result.get("scores", {}).get(item.split("（")[0], 0)
            report += f"{item:<30} {max_score:>5} {actual_score:>5}\n"
        
        for item, max_score in standard["quality_items"].items():
            actual_score = output_result.get("scores", {}).get(item, 0)
            report += f"{item:<30} {max_score:>5} {actual_score:>5}\n"
        
        report += f"""
{'-'*70}
总分                      100   {output_result['total_score']}

输出审核结论：{output_result['grade']} - {output_result['conclusion']}

{'='*70}
                          改进建议
{'='*70}
"""
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                report += f"{i}. {suggestion}\n"
        else:
            report += "无改进建议\n"
        
        report += f"""
{'='*70}
审核人：__________ 日期：__________
{'='*70}
"""
        
        return report


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序"""
    print("="*70)
    print("指南针工程自动审核工具")
    print("="*70)
    print()
    
    # 创建审核工具实例
    auditor = CompassAuditor()
    
    # 示例：审核步骤1
    print("\n【示例】步骤1：需求文档审核")
    print("-"*70)
    
    # 输入审核
    input_checks = AUDIT_STANDARDS["step1"]["input_checks"]
    input_result = auditor.audit_input("step1", input_checks)
    
    # 输出审核（示例得分）
    example_scores = {
        "需求背景": 18,
        "需求描述": 25,
        "需求目标": 18,
        "约束条件": 8,
        "验收标准": 18,
        "文档格式规范": 8
    }
    
    output_result = auditor.audit_output("step1", example_scores)
    
    # 生成审核报告
    suggestions = [
        "建议补充约束条件中的技术约束",
        "验收标准建议增加具体的量化指标"
    ]
    
    report = auditor.generate_report("step1", input_result, output_result, suggestions)
    
    print("\n【审核报告】")
    print(report)
    
    print("\n【使用说明】")
    print("1. 调用 audit_input() 进行输入审核")
    print("2. 调用 audit_output() 进行输出审核")
    print("3. 调用 generate_report() 生成审核报告")
    print("4. 根据审核结论决定是否进入下一步")


if __name__ == "__main__":
    main()