#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指南针工程自动审核服务 V1.0
提供自动化审核API，支持流程审核和价值审核

Author: 南乔
Date: 2026-03-23
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================
# 审核标准配置
# ============================================================

AUDIT_STANDARDS = {
    "step1": {
        "name": "需求文档",
        "description": "将客户需求转化为标准需求文档",
        "input_checks": [
            {"id": "source", "text": "需求来源明确（客户访谈/邮件/会议纪要）", "weight": 20},
            {"id": "clarity", "text": "需求描述清晰，无模糊表述", "weight": 20},
            {"id": "completeness", "text": "需求信息完整，包含背景、目标、范围", "weight": 20},
            {"id": "confirmed", "text": "需求方已确认需求内容", "weight": 20},
            {"id": "priority", "text": "需求优先级已明确", "weight": 20}
        ],
        "output_items": [
            {"id": "background", "name": "需求背景", "max_score": 20, "check_points": ["项目背景", "业务现状", "问题分析"]},
            {"id": "description", "name": "需求描述", "max_score": 30, "check_points": ["功能需求", "非功能需求", "业务场景"]},
            {"id": "goals", "name": "需求目标", "max_score": 20, "check_points": ["业务目标", "技术目标", "量化指标"]},
            {"id": "constraints", "name": "约束条件", "max_score": 10, "check_points": ["时间约束", "成本约束", "资源约束"]},
            {"id": "acceptance", "name": "验收标准", "max_score": 20, "check_points": ["功能验收", "性能验收", "业务验收"]}
        ],
        "quality_items": [
            {"id": "format", "name": "文档格式规范", "max_score": 5},
            {"id": "logic", "name": "逻辑清晰正确", "max_score": 5}
        ],
        "keywords": {
            "background": ["项目背景", "业务现状", "问题", "痛点", "现状分析"],
            "description": ["功能需求", "非功能需求", "业务场景", "用例", "用户故事"],
            "goals": ["目标", "指标", "KPI", "量化", "达成"],
            "constraints": ["约束", "限制", "时间", "成本", "资源"],
            "acceptance": ["验收", "测试", "标准", "验收标准"]
        }
    },
    "step2": {
        "name": "思维导图",
        "description": "分析需求，梳理痛点，形成解决方案想法",
        "input_checks": [
            {"id": "prev_step", "text": "步骤1需求文档已完成（评分≥70分）", "weight": 25},
            {"id": "understood", "text": "已充分理解需求文档内容", "weight": 25},
            {"id": "extracted", "text": "已提取核心需求、痛点、目标", "weight": 25},
            {"id": "prepared", "text": "已准备头脑风暴素材", "weight": 25}
        ],
        "output_items": [
            {"id": "understanding", "name": "需求理解", "max_score": 25, "check_points": ["核心需求", "次要需求", "隐性需求"]},
            {"id": "pain_points", "name": "痛点分析", "max_score": 25, "check_points": ["效率痛点", "体验痛点", "成本痛点"]},
            {"id": "solutions", "name": "解决方案想法", "max_score": 20, "check_points": ["方案数量≥3", "方案可行性"]},
            {"id": "priority", "name": "优先级评估", "max_score": 20, "check_points": ["评估标准", "评估结果"]},
            {"id": "structure", "name": "结构完整", "max_score": 10, "check_points": ["层次清晰", "逻辑连贯"]}
        ],
        "quality_items": [
            {"id": "feasibility", "name": "想法可行性", "max_score": 5},
            {"id": "reasonability", "name": "评估合理性", "max_score": 5}
        ],
        "keywords": {
            "understanding": ["需求", "核心需求", "隐性需求", "业务需求"],
            "pain_points": ["痛点", "问题", "效率", "体验", "成本"],
            "solutions": ["方案", "解决", "想法", "建议", "措施"],
            "priority": ["优先级", "重要", "紧急", "P1", "P2"],
            "structure": ["结构", "层次", "分类", "维度"]
        }
    },
    "step3": {
        "name": "方案举措Excel",
        "description": "将解决方案转化为可执行的方案举措",
        "input_checks": [
            {"id": "prev_step", "text": "步骤2思维导图已完成（评分≥70分）", "weight": 25},
            {"id": "p1_defined", "text": "优先级评估已完成，P1方案已确定", "weight": 25},
            {"id": "ideas_extracted", "text": "已提取解决方案想法", "weight": 25},
            {"id": "materials_ready", "text": "已准备方案举措素材", "weight": 25}
        ],
        "output_items": [
            {"id": "title", "name": "方案标题", "max_score": 10, "check_points": ["标题明确", "简洁"]},
            {"id": "objectives", "name": "建设目标", "max_score": 20, "check_points": ["目标明确", "可量化(SMART)"]},
            {"id": "measures", "name": "具体举措", "max_score": 30, "check_points": ["举措详细", "可执行", "数量≥3"]},
            {"id": "effects", "name": "预期效果", "max_score": 30, "check_points": ["效果量化", "可衡量"]},
            {"id": "ppt_mapping", "name": "PPT页码", "max_score": 10, "check_points": ["页码对应"]}
        ],
        "quality_items": [
            {"id": "quantified", "name": "目标量化", "max_score": 5},
            {"id": "feasible", "name": "举措可行", "max_score": 5}
        ],
        "keywords": {
            "title": ["方案", "项目", "建设", "实施"],
            "objectives": ["目标", "建设目标", "KPI", "指标", "SMART"],
            "measures": ["举措", "措施", "行动", "步骤", "实施"],
            "effects": ["效果", "预期", "收益", "提升", "降低"],
            "ppt_mapping": ["PPT", "页码", "章节"]
        }
    },
    "step4": {
        "name": "PPT方案",
        "description": "将方案转化为专业的汇报PPT",
        "input_checks": [
            {"id": "prev_step", "text": "步骤3方案举措Excel已完成（评分≥70分）", "weight": 25},
            {"id": "outline", "text": "PPT大纲已明确（20页结构）", "weight": 25},
            {"id": "materials", "text": "方案举措素材已准备", "weight": 25},
            {"id": "style", "text": "设计风格已确定", "weight": 25}
        ],
        "output_items": [
            {"id": "cover", "name": "封面完整", "max_score": 5, "check_points": ["标题", "副标题", "日期"]},
            {"id": "toc", "name": "目录清晰", "max_score": 5, "check_points": ["章节明确"]},
            {"id": "background", "name": "方案背景", "max_score": 10, "check_points": ["背景", "痛点", "必要性"]},
            {"id": "goals", "name": "方案目标", "max_score": 10, "check_points": ["业务目标", "技术目标", "量化目标"]},
            {"id": "solutions", "name": "解决举措", "max_score": 30, "check_points": ["方案完整", "≥4个方案"]},
            {"id": "plan", "name": "实施计划", "max_score": 10, "check_points": ["阶段", "里程碑", "资源"]},
            {"id": "effects", "name": "预期效果", "max_score": 10, "check_points": ["量化效果"]},
            {"id": "risks", "name": "风险保障", "max_score": 10, "check_points": ["风险", "应对措施"]},
            {"id": "summary", "name": "总结完整", "max_score": 10, "check_points": ["核心价值", "下一步"]}
        ],
        "quality_items": [
            {"id": "format", "name": "格式统一", "max_score": 3},
            {"id": "visual", "name": "视觉美观", "max_score": 4},
            {"id": "logic", "name": "逻辑清晰", "max_score": 3}
        ],
        "keywords": {
            "cover": ["封面", "标题", "副标题"],
            "toc": ["目录", "章节", "结构"],
            "background": ["背景", "现状", "问题", "必要性"],
            "goals": ["目标", "指标", "KPI"],
            "solutions": ["方案", "举措", "解决", "措施"],
            "plan": ["计划", "实施", "里程碑", "阶段"],
            "effects": ["效果", "预期", "收益"],
            "risks": ["风险", "保障", "应对"],
            "summary": ["总结", "价值", "下一步"]
        }
    },
    "step5": {
        "name": "详细设计文档",
        "description": "将方案转化为可实施的详细设计",
        "input_checks": [
            {"id": "reviewed", "text": "PPT方案已评审通过（客户/领导确认）", "weight": 25},
            {"id": "confirmed", "text": "方案内容已确认", "weight": 25},
            {"id": "feedback", "text": "评审意见已整理", "weight": 25},
            {"id": "requirements", "text": "设计要求已明确", "weight": 25}
        ],
        "output_items": [
            {"id": "architecture", "name": "系统架构", "max_score": 20, "check_points": ["总体架构", "技术架构", "部署架构"]},
            {"id": "api", "name": "接口设计", "max_score": 20, "check_points": ["接口规范", "接口列表", "接口示例"]},
            {"id": "database", "name": "数据库设计", "max_score": 20, "check_points": ["概念模型", "逻辑模型", "物理模型"]},
            {"id": "ui", "name": "UI设计", "max_score": 20, "check_points": ["原型设计", "交互设计", "视觉设计"]},
            {"id": "security", "name": "安全设计", "max_score": 10, "check_points": ["安全架构", "安全策略"]},
            {"id": "appendix", "name": "附录完整", "max_score": 10, "check_points": ["名词解释", "参考文档"]}
        ],
        "quality_items": [
            {"id": "reasonable", "name": "架构合理", "max_score": 5},
            {"id": "feasible", "name": "设计可行", "max_score": 5}
        ],
        "keywords": {
            "architecture": ["架构", "系统架构", "技术架构", "部署架构"],
            "api": ["接口", "API", "REST", "接口设计"],
            "database": ["数据库", "表", "字段", "ER图", "数据模型"],
            "ui": ["界面", "UI", "原型", "交互", "视觉"],
            "security": ["安全", "权限", "加密", "认证"],
            "appendix": ["附录", "名词", "参考"]
        }
    },
    "step6": {
        "name": "项目管控计划",
        "description": "制定项目管控计划，确保项目落地",
        "input_checks": [
            {"id": "prev_step", "text": "步骤5详细设计文档已完成（评分≥70分）", "weight": 25},
            {"id": "resources", "text": "项目资源已确认（人力、预算、时间）", "weight": 25},
            {"id": "team", "text": "项目团队已组建", "weight": 25},
            {"id": "ready", "text": "项目启动条件已满足", "weight": 25}
        ],
        "output_items": [
            {"id": "gantt", "name": "甘特图", "max_score": 25, "check_points": ["任务", "时间", "负责人", "进度"]},
            {"id": "resources", "name": "资源表", "max_score": 20, "check_points": ["人力", "设备", "预算"]},
            {"id": "raci", "name": "RACI矩阵", "max_score": 20, "check_points": ["任务", "角色责任"]},
            {"id": "risks", "name": "风险清单", "max_score": 20, "check_points": ["风险", "应对措施"]},
            {"id": "communication", "name": "沟通计划", "max_score": 15, "check_points": ["频率", "对象", "内容"]}
        ],
        "quality_items": [
            {"id": "plan_feasible", "name": "计划可行", "max_score": 5},
            {"id": "risk_controllable", "name": "风险可控", "max_score": 5}
        ],
        "keywords": {
            "gantt": ["甘特图", "进度", "时间", "任务", "里程碑"],
            "resources": ["资源", "人力", "预算", "设备"],
            "raci": ["RACI", "责任", "角色", "负责"],
            "risks": ["风险", "应对", "措施"],
            "communication": ["沟通", "会议", "汇报", "频率"]
        }
    }
}

# ============================================================
# 审核结果数据结构
# ============================================================

class AuditGrade(Enum):
    """审核等级"""
    A = "A级"  # 90-100分
    B = "B级"  # 80-89分
    C = "C级"  # 70-79分
    D = "D级"  # <70分

@dataclass
class AuditItemResult:
    """审核项结果"""
    id: str
    name: str
    max_score: int
    actual_score: int
    passed: bool
    check_points: List[str]
    missing_points: List[str]
    suggestions: List[str]

@dataclass
class AuditResult:
    """审核结果"""
    step: str
    step_name: str
    timestamp: str
    input_passed: bool
    input_score: int
    input_details: List[Dict]
    output_score: int
    output_max_score: int
    output_details: List[AuditItemResult]
    quality_score: int
    quality_max_score: int
    quality_details: List[Dict]
    total_score: int
    grade: str
    conclusion: str
    suggestions: List[str]
    can_proceed: bool

# ============================================================
# 核心审核服务类
# ============================================================

class CompassAuditorService:
    """指南针工程审核服务"""
    
    def __init__(self):
        self.standards = AUDIT_STANDARDS
    
    def audit_content(self, step: str, content: str, prev_step_score: int = 100) -> AuditResult:
        """
        审核输出内容
        
        Args:
            step: 步骤编号（step1-step6）
            content: 输出内容（文本）
            prev_step_score: 上一步评分（用于输入审核）
        
        Returns:
            审核结果
        """
        if step not in self.standards:
            raise ValueError(f"无效的步骤编号: {step}")
        
        standard = self.standards[step]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. 输入审核
        input_result = self._audit_input(step, prev_step_score)
        
        # 2. 输出审核
        output_result = self._audit_output_content(step, content)
        
        # 3. 质量审核
        quality_result = self._audit_quality(step, content)
        
        # 4. 计算总分
        total_score = output_result["score"] + quality_result["score"]
        
        # 5. 确定等级
        grade, conclusion = self._determine_grade(total_score)
        
        # 6. 生成建议
        suggestions = self._generate_suggestions(step, output_result, quality_result)
        
        # 7. 构建结果
        result = AuditResult(
            step=step,
            step_name=standard["name"],
            timestamp=timestamp,
            input_passed=input_result["passed"],
            input_score=input_result["score"],
            input_details=input_result["details"],
            output_score=output_result["score"],
            output_max_score=output_result["max_score"],
            output_details=output_result["details"],
            quality_score=quality_result["score"],
            quality_max_score=quality_result["max_score"],
            quality_details=quality_result["details"],
            total_score=total_score,
            grade=grade,
            conclusion=conclusion,
            suggestions=suggestions,
            can_proceed=(total_score >= 70 and input_result["passed"])
        )
        
        return result
    
    def _audit_input(self, step: str, prev_step_score: int) -> Dict:
        """输入审核"""
        standard = self.standards[step]
        checks = standard["input_checks"]
        
        details = []
        total_weight = 0
        passed_weight = 0
        
        for check in checks:
            # 特殊处理：检查上一步评分
            if check["id"] == "prev_step":
                passed = prev_step_score >= 70
            elif check["id"] == "reviewed":
                # PPT评审通过需要外部确认，默认True
                passed = True
            else:
                # 其他检查项默认通过（实际应用中需要更精确的检查）
                passed = True
            
            details.append({
                "id": check["id"],
                "text": check["text"],
                "weight": check["weight"],
                "passed": passed
            })
            
            total_weight += check["weight"]
            if passed:
                passed_weight += check["weight"]
        
        score = int(passed_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "passed": score >= 70,
            "score": score,
            "details": details
        }
    
    def _audit_output_content(self, step: str, content: str) -> Dict:
        """输出内容审核"""
        standard = self.standards[step]
        items = standard["output_items"]
        keywords = standard.get("keywords", {})
        
        details = []
        total_score = 0
        max_score = 0
        
        for item in items:
            item_keywords = keywords.get(item["id"], [])
            check_points = item["check_points"]
            
            # 计算得分
            score, missing = self._check_item(content, item_keywords, check_points, item["max_score"])
            
            total_score += score
            max_score += item["max_score"]
            
            # 生成建议
            suggestions = []
            if score < item["max_score"]:
                if missing:
                    suggestions.append(f"建议补充：{', '.join(missing)}")
            
            details.append(AuditItemResult(
                id=item["id"],
                name=item["name"],
                max_score=item["max_score"],
                actual_score=score,
                passed=score >= item["max_score"] * 0.7,
                check_points=check_points,
                missing_points=missing,
                suggestions=suggestions
            ))
        
        return {
            "score": total_score,
            "max_score": max_score,
            "details": details
        }
    
    def _audit_quality(self, step: str, content: str) -> Dict:
        """质量审核"""
        standard = self.standards[step]
        items = standard["quality_items"]
        
        details = []
        total_score = 0
        max_score = 0
        
        for item in items:
            # 简单的质量检查
            score = item["max_score"]
            
            # 检查格式规范
            if item["id"] == "format":
                # 检查是否有清晰的段落结构
                if len(content) < 100:
                    score = int(item["max_score"] * 0.5)
            
            # 检查逻辑清晰
            elif item["id"] == "logic":
                # 检查是否有逻辑连接词
                logic_words = ["因此", "所以", "首先", "其次", "最后", "总之", "综上"]
                if not any(w in content for w in logic_words):
                    score = int(item["max_score"] * 0.7)
            
            total_score += score
            max_score += item["max_score"]
            
            details.append({
                "id": item["id"],
                "name": item["name"],
                "max_score": item["max_score"],
                "actual_score": score
            })
        
        return {
            "score": total_score,
            "max_score": max_score,
            "details": details
        }
    
    def _check_item(self, content: str, keywords: List[str], check_points: List[str], max_score: int) -> Tuple[int, List[str]]:
        """检查单个审核项"""
        content_lower = content.lower()
        
        # 统计关键词出现次数
        keyword_hits = 0
        for kw in keywords:
            if kw.lower() in content_lower:
                keyword_hits += 1
        
        # 检查检查点
        missing = []
        point_hits = 0
        for point in check_points:
            # 简单匹配：检查点是否在内容中
            if point in content or any(kw in content for kw in [point]):
                point_hits += 1
            else:
                missing.append(point)
        
        # 计算得分
        if keyword_hits == 0 and point_hits == 0:
            score = 0
        else:
            # 基于检查点覆盖率和关键词命中率计算得分
            point_ratio = point_hits / len(check_points) if check_points else 0
            keyword_ratio = keyword_hits / len(keywords) if keywords else 0
            combined_ratio = (point_ratio * 0.7 + keyword_ratio * 0.3)
            score = int(max_score * combined_ratio)
        
        return score, missing
    
    def _determine_grade(self, total_score: int) -> Tuple[str, str]:
        """确定审核等级"""
        if total_score >= 90:
            return "A级", "优秀，可直接进入下一步"
        elif total_score >= 80:
            return "B级", "良好，小幅优化后进入下一步"
        elif total_score >= 70:
            return "C级", "合格，需要优化后进入下一步"
        else:
            return "D级", "不合格，需要重新编写"
    
    def _generate_suggestions(self, step: str, output_result: Dict, quality_result: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于输出审核生成建议
        for detail in output_result["details"]:
            if detail.actual_score < detail.max_score:
                if detail.missing_points:
                    suggestions.append(f"【{detail.name}】建议补充：{', '.join(detail.missing_points)}")
        
        # 基于质量审核生成建议
        for detail in quality_result["details"]:
            if detail["actual_score"] < detail["max_score"]:
                suggestions.append(f"【{detail['name']}】需要优化")
        
        return suggestions
    
    def generate_report(self, result: AuditResult) -> str:
        """生成审核报告"""
        report = f"""
{'='*70}
              指南针工程质量审核报告
{'='*70}

审核步骤：步骤{result.step[-1]} - {result.step_name}
审核时间：{result.timestamp}

{'='*70}
                        输入审核
{'='*70}

"""
        for detail in result.input_details:
            status = "✅" if detail["passed"] else "❌"
            report += f"{status} {detail['text']}\n"
        
        report += f"\n输入审核结论：{'通过' if result.input_passed else '不通过'}\n"
        
        report += f"""
{'='*70}
                        输出审核
{'='*70}

{'审核项':<20} {'满分':>8} {'得分':>8} {'状态':>8}
{'-'*70}
"""
        for detail in result.output_details:
            status = "✅" if detail.passed else "⚠️"
            report += f"{detail.name:<20} {detail.max_score:>8} {detail.actual_score:>8} {status:>8}\n"
        
        report += f"{'-'*70}\n"
        report += f"{'输出审核小计':<20} {result.output_max_score:>8} {result.output_score:>8}\n"
        
        report += f"""
{'='*70}
                        质量审核
{'='*70}

{'审核项':<20} {'满分':>8} {'得分':>8}
{'-'*70}
"""
        for detail in result.quality_details:
            report += f"{detail['name']:<20} {detail['max_score']:>8} {detail['actual_score']:>8}\n"
        
        report += f"{'-'*70}\n"
        report += f"{'质量审核小计':<20} {result.quality_max_score:>8} {result.quality_score:>8}\n"
        
        report += f"""
{'='*70}
                        审核结论
{'='*70}

总分：{result.total_score}/100
等级：{result.grade}
结论：{result.conclusion}
是否可进入下一步：{'是' if result.can_proceed else '否'}

{'='*70}
                        改进建议
{'='*70}
"""
        if result.suggestions:
            for i, sug in enumerate(result.suggestions, 1):
                report += f"{i}. {sug}\n"
        else:
            report += "无改进建议，继续保持！\n"
        
        report += f"\n{'='*70}\n"
        
        return report
    
    def get_standards(self) -> Dict:
        """获取审核标准"""
        return self.standards
    
    def get_step_standard(self, step: str) -> Dict:
        """获取指定步骤的审核标准"""
        return self.standards.get(step, {})


# ============================================================
# API接口（供外部调用）
# ============================================================

def audit_step_output(step: str, content: str, prev_score: int = 100) -> Dict:
    """
    审核步骤输出物（API接口）
    
    Args:
        step: 步骤编号（step1-step6）
        content: 输出内容
        prev_score: 上一步评分
    
    Returns:
        审核结果字典
    """
    service = CompassAuditorService()
    result = service.audit_content(step, content, prev_score)
    return asdict(result)


def get_audit_summary(result: Dict) -> str:
    """
    获取审核摘要
    
    Args:
        result: 审核结果
    
    Returns:
        摘要文本
    """
    grade_emoji = {
        "A级": "🟢",
        "B级": "🟡",
        "C级": "🟠",
        "D级": "🔴"
    }
    
    emoji = grade_emoji.get(result["grade"], "⚪")
    
    summary = f"""
{emoji} 审核完成！

步骤：步骤{result['step'][-1]} - {result['step_name']}
总分：{result['total_score']}/100
等级：{result['grade']}
结论：{result['conclusion']}

{'✅ 可以进入下一步' if result['can_proceed'] else '⚠️ 需要优化后才能进入下一步'}
"""
    return summary


# ============================================================
# 主程序（测试）
# ============================================================

if __name__ == "__main__":
    print("="*70)
    print("指南针工程自动审核服务 V1.0")
    print("="*70)
    
    # 创建服务实例
    service = CompassAuditorService()
    
    # 测试：步骤1需求文档审核
    test_content = """
一、需求背景

1.1 项目背景
本项目旨在为湖北电信打造一套AI智能配案系统，通过AI技术实现套餐智能推荐，提升营销效率和客户满意度。

1.2 业务现状
当前湖北电信电渠渠道主要通过人工方式进行套餐推荐，存在效率低、准确率不高的问题。

1.3 问题分析
1. 人工配案效率低，平均每单耗时20分钟
2. 配案准确率不高，客户满意度待提升
3. 营销人员培训成本高

二、需求描述

2.1 功能需求
1. 智能配案：根据客户需求智能推荐套餐
2. 套餐对比：支持多套餐对比展示
3. 订单管理：支持订单查询和管理

2.2 非功能需求
1. 响应时间：<3秒
2. 并发用户：1000+
3. 可用性：99.9%

2.3 业务场景
场景1：营业厅新用户入网配案
场景2：存量用户套餐变更推荐
场景3：线上渠道智能推荐

三、需求目标

3.1 业务目标
1. 配案效率提升50%
2. 客户满意度提升20%

3.2 技术目标
1. 建立AI配案模型，准确率≥80%
2. 系统可用性≥99.9%

四、约束条件

4.1 时间约束
项目周期：3个月

4.2 成本约束
项目预算：XX万元

五、验收标准

5.1 功能验收
1. 支持智能配案功能
2. 支持套餐对比功能

5.2 性能验收
1. 响应时间<3秒
2. 并发支持1000+用户
"""
    
    result = service.audit_content("step1", test_content)
    
    # 输出报告
    report = service.generate_report(result)
    print(report)
    
    # 输出JSON结果
    print("\n【JSON结果】")
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
