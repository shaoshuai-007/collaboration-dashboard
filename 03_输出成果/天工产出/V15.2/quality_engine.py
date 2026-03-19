"""
质量审核引擎 - Quality Audit Engine
V15.2 多智能体协同平台核心模块

包含:
- StandardChecker: 标准检查器
- ExpertReviewer: 专家评审器
- FeedbackGenerator: 反馈生成器
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class CheckLevel(Enum):
    """检查级别枚举"""
    ERROR = "error"       # 错误级别 - 必须修复
    WARNING = "warning"   # 警告级别 - 建议修复
    INFO = "info"         # 信息级别 - 可选优化
    HINT = "hint"         # 提示级别 - 参考建议


class CheckCategory(Enum):
    """检查类别枚举"""
    COMPLETENESS = "completeness"   # 完整性
    CONSISTENCY = "consistency"     # 一致性
    CORRECTNESS = "correctness"     # 正确性
    READABILITY = "readability"     # 可读性
    COMPLIANCE = "compliance"       # 合规性
    PERFORMANCE = "performance"     # 性能
    SECURITY = "security"           # 安全性


@dataclass
class CheckResult:
    """
    检查结果
    
    表示单项检查的结果。
    """
    check_id: str = field(default_factory=lambda: str(uuid4()))
    check_name: str = ""
    category: CheckCategory = CheckCategory.CORRECTNESS
    level: CheckLevel = CheckLevel.INFO
    message: str = ""
    location: Optional[str] = None  # 问题位置（行号、章节名等）
    suggestion: Optional[str] = None  # 修复建议
    passed: bool = True
    score: float = 1.0  # 0.0 - 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "category": self.category.value,
            "level": self.level.value,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
            "passed": self.passed,
            "score": self.score,
            "metadata": self.metadata
        }


@dataclass
class ReviewReport:
    """
    评审报告
    
    表示完整的质量评审报告。
    """
    report_id: str = field(default_factory=lambda: str(uuid4()))
    product_id: str = ""
    product_name: str = ""
    check_results: list[CheckResult] = field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = True
    summary: str = ""
    recommendations: list[str] = field(default_factory=list)
    reviewed_at: datetime = field(default_factory=datetime.now)
    reviewer: str = "StandardChecker"
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def add_result(self, result: CheckResult) -> None:
        """添加检查结果"""
        self.check_results.append(result)
        if not result.passed and result.level == CheckLevel.ERROR:
            self.passed = False
    
    def calculate_overall_score(self) -> float:
        """
        计算总体评分
        
        Returns:
            总体评分 (0.0 - 1.0)
        """
        if not self.check_results:
            return 1.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        for result in self.check_results:
            # 根据级别设置权重
            weights = {
                CheckLevel.ERROR: 3.0,
                CheckLevel.WARNING: 2.0,
                CheckLevel.INFO: 1.0,
                CheckLevel.HINT: 0.5
            }
            weight = weights.get(result.level, 1.0)
            total_weight += weight
            weighted_score += weight * result.score
        
        self.overall_score = weighted_score / total_weight if total_weight > 0 else 1.0
        return self.overall_score
    
    def get_errors(self) -> list[CheckResult]:
        """获取所有错误级别的结果"""
        return [r for r in self.check_results if r.level == CheckLevel.ERROR and not r.passed]
    
    def get_warnings(self) -> list[CheckResult]:
        """获取所有警告级别的结果"""
        return [r for r in self.check_results if r.level == CheckLevel.WARNING]
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "report_id": self.report_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "check_count": len(self.check_results),
            "error_count": len(self.get_errors()),
            "warning_count": len(self.get_warnings()),
            "overall_score": self.overall_score,
            "passed": self.passed,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "reviewed_at": self.reviewed_at.isoformat(),
            "reviewer": self.reviewer
        }


class BaseChecker(ABC):
    """
    检查器基类
    
    所有检查器的抽象基类，定义检查器接口。
    """
    
    def __init__(self, name: str, category: CheckCategory):
        """
        初始化检查器
        
        Args:
            name: 检查器名称
            category: 检查类别
        """
        self.name = name
        self.category = category
    
    @abstractmethod
    def check(self, content: str, context: Optional[dict[str, Any]] = None) -> CheckResult:
        """
        执行检查
        
        Args:
            content: 要检查的内容
            context: 检查上下文
        
        Returns:
            检查结果
        """
        pass


class StandardChecker:
    """
    标准检查器
    
    执行一系列预定义的标准检查，验证产物质量。
    
    使用示例:
        checker = StandardChecker()
        checker.register_checker(CompletenessChecker())
        checker.register_checker(ConsistencyChecker())
        
        report = checker.check(content, {"product_name": "需求文档"})
        print(f"总体评分: {report.overall_score}")
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        初始化标准检查器
        
        Args:
            strict_mode: 严格模式，开启后警告也视为不通过
        """
        self.strict_mode = strict_mode
        self.checkers: list[BaseChecker] = []
        self._register_default_checkers()
    
    def _register_default_checkers(self) -> None:
        """注册默认检查器"""
        self.checkers.extend([
            CompletenessChecker(),
            FormatChecker(),
            StructureChecker(),
            LanguageChecker(),
        ])
    
    def register_checker(self, checker: BaseChecker) -> None:
        """
        注册自定义检查器
        
        Args:
            checker: 检查器实例
        """
        self.checkers.append(checker)
    
    def check(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None,
        categories: Optional[list[CheckCategory]] = None
    ) -> ReviewReport:
        """
        执行所有检查
        
        Args:
            content: 要检查的内容
            context: 检查上下文
            categories: 要检查的类别列表，为None时检查所有
        
        Returns:
            评审报告
        """
        context = context or {}
        
        report = ReviewReport(
            product_id=context.get("product_id", ""),
            product_name=context.get("product_name", "未命名产物"),
            reviewer="StandardChecker"
        )
        
        for checker in self.checkers:
            # 过滤检查类别
            if categories and checker.category not in categories:
                continue
            
            try:
                result = checker.check(content, context)
                report.add_result(result)
            except Exception as e:
                # 检查器异常时记录错误
                report.add_result(CheckResult(
                    check_name=checker.name,
                    category=checker.category,
                    level=CheckLevel.ERROR,
                    message=f"检查器执行异常: {str(e)}",
                    passed=False,
                    score=0.0
                ))
        
        # 计算总体评分
        report.calculate_overall_score()
        
        # 生成摘要
        error_count = len(report.get_errors())
        warning_count = len(report.get_warnings())
        report.summary = (
            f"检查完成，共 {len(report.check_results)} 项检查，"
            f"发现 {error_count} 个错误，{warning_count} 个警告，"
            f"总体评分 {report.overall_score:.2%}"
        )
        
        # 严格模式下，警告也导致不通过
        if self.strict_mode and warning_count > 0:
            report.passed = False
        
        return report


class CompletenessChecker(BaseChecker):
    """
    完整性检查器
    
    检查内容是否完整，是否包含必要的章节和元素。
    """
    
    REQUIRED_ELEMENTS = {
        "requirement_doc": ["概述", "需求", "功能"],
        "architecture_design": ["架构", "模块", "接口"],
        "solution_ppt": ["标题", "内容"],
        "project_plan": ["计划", "时间", "资源"],
    }
    
    def __init__(self):
        super().__init__("完整性检查器", CheckCategory.COMPLETENESS)
    
    def check(self, content: str, context: Optional[dict[str, Any]] = None) -> CheckResult:
        context = context or {}
        product_type = context.get("product_type", "")
        
        missing_elements = []
        required = self.REQUIRED_ELEMENTS.get(product_type, [])
        
        for element in required:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            return CheckResult(
                check_name=self.name,
                category=self.category,
                level=CheckLevel.ERROR,
                message=f"缺少必要元素: {', '.join(missing_elements)}",
                passed=False,
                score=0.5
            )
        
        return CheckResult(
            check_name=self.name,
            category=self.category,
            level=CheckLevel.INFO,
            message="内容完整，包含所有必要元素",
            passed=True,
            score=1.0
        )


class FormatChecker(BaseChecker):
    """
    格式检查器
    
    检查文档格式是否符合规范。
    """
    
    def __init__(self):
        super().__init__("格式检查器", CheckCategory.CORRECTNESS)
    
    def check(self, content: str, context: Optional[dict[str, Any]] = None) -> CheckResult:
        issues = []
        
        # 检查标题层级
        heading_pattern = r'^(#{1,6})\s+.+$'
        lines = content.split('\n')
        prev_level = 0
        
        for idx, line in enumerate(lines, 1):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                if level > prev_level + 1:
                    issues.append(f"第{idx}行: 标题层级跳跃 (从H{prev_level}到H{level})")
                prev_level = level
        
        # 检查代码块是否闭合
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues.append("代码块未正确闭合")
        
        if issues:
            return CheckResult(
                check_name=self.name,
                category=self.category,
                level=CheckLevel.WARNING,
                message="发现格式问题",
                location="多处",
                suggestion="\n".join(issues),
                passed=True,
                score=0.8
            )
        
        return CheckResult(
            check_name=self.name,
            category=self.category,
            level=CheckLevel.INFO,
            message="格式规范",
            passed=True,
            score=1.0
        )


class StructureChecker(BaseChecker):
    """
    结构检查器
    
    检查文档结构是否合理。
    """
    
    def __init__(self):
        super().__init__("结构检查器", CheckCategory.READABILITY)
    
    def check(self, content: str, context: Optional[dict[str, Any]] = None) -> CheckResult:
        lines = content.split('\n')
        total_lines = len(lines)
        
        issues = []
        
        # 检查段落长度
        paragraph_lines = 0
        for line in lines:
            if line.strip():
                paragraph_lines += 1
            else:
                if paragraph_lines > 20:
                    issues.append(f"段落过长 ({paragraph_lines}行)，建议分段")
                paragraph_lines = 0
        
        # 检查标题数量
        heading_count = sum(1 for line in lines if line.strip().startswith('#'))
        if total_lines > 100 and heading_count < 3:
            issues.append("长文档缺少标题结构")
        
        if issues:
            return CheckResult(
                check_name=self.name,
                category=self.category,
                level=CheckLevel.INFO,
                message="结构检查完成",
                suggestion="; ".join(issues),
                passed=True,
                score=0.9
            )
        
        return CheckResult(
            check_name=self.name,
            category=self.category,
            level=CheckLevel.INFO,
            message="结构合理",
            passed=True,
            score=1.0
        )


class LanguageChecker(BaseChecker):
    """
    语言检查器
    
    检查语言表达质量。
    """
    
    # 常见问题词汇
    FUZZY_WORDS = ["等等", "之类", "大概", "可能", "也许", "差不多"]
    
    def __init__(self):
        super().__init__("语言检查器", CheckCategory.READABILITY)
    
    def check(self, content: str, context: Optional[dict[str, Any]] = None) -> CheckResult:
        issues = []
        
        # 检查模糊词
        for word in self.FUZZY_WORDS:
            if word in content:
                count = content.count(word)
                issues.append(f"发现模糊词 '{word}' ({count}次)")
        
        # 检查标点符号
        if '。。' in content:
            issues.append("存在重复句号")
        if '，,' in content or ',，' in content:
            issues.append("标点符号混用")
        
        if issues:
            return CheckResult(
                check_name=self.name,
                category=self.category,
                level=CheckLevel.HINT,
                message="语言检查完成",
                suggestion="; ".join(issues),
                passed=True,
                score=0.85
            )
        
        return CheckResult(
            check_name=self.name,
            category=self.category,
            level=CheckLevel.INFO,
            message="语言表达清晰",
            passed=True,
            score=1.0
        )


class ExpertReviewer:
    """
    专家评审器
    
    基于领域专家知识进行深度评审，提供专业反馈。
    
    使用示例:
        reviewer = ExpertReviewer(domain="软件工程")
        review = reviewer.review(content, {
            "product_type": "requirement_doc",
            "requirements": ["用户管理", "权限控制"]
        })
    """
    
    # 领域专家知识库
    DOMAIN_KNOWLEDGE: dict[str, dict[str, Any]] = {
        "软件工程": {
            "requirement_keywords": ["用户", "功能", "接口", "性能", "安全"],
            "architecture_keywords": ["模块", "层次", "耦合", "内聚", "扩展性"],
            "quality_attributes": ["可维护性", "可测试性", "可扩展性", "安全性"],
        },
        "产品设计": {
            "requirement_keywords": ["用户需求", "场景", "体验", "交互"],
            "quality_attributes": ["易用性", "美观性", "一致性"],
        },
        "项目管理": {
            "requirement_keywords": ["里程碑", "资源", "风险", "进度"],
            "quality_attributes": ["可行性", "可控性", "清晰性"],
        }
    }
    
    def __init__(
        self,
        domain: str = "软件工程",
        expertise_level: str = "senior"
    ):
        """
        初始化专家评审器
        
        Args:
            domain: 领域名称
            expertise_level: 专家级别 (junior, senior, expert)
        """
        self.domain = domain
        self.expertise_level = expertise_level
        self.knowledge = self.DOMAIN_KNOWLEDGE.get(domain, {})
    
    def review(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None
    ) -> ReviewReport:
        """
        执行专家评审
        
        Args:
            content: 要评审的内容
            context: 评审上下文
        
        Returns:
            评审报告
        """
        context = context or {}
        
        report = ReviewReport(
            product_id=context.get("product_id", ""),
            product_name=context.get("product_name", "未命名产物"),
            reviewer=f"{self.domain}专家({self.expertise_level})"
        )
        
        # 领域关键词检查
        self._check_domain_keywords(content, report)
        
        # 质量属性检查
        self._check_quality_attributes(content, report)
        
        # 专业术语检查
        self._check_terminology(content, report)
        
        # 逻辑一致性检查
        self._check_logic_consistency(content, report, context)
        
        # 计算总体评分
        report.calculate_overall_score()
        
        # 生成专家建议
        self._generate_recommendations(report)
        
        return report
    
    def _check_domain_keywords(self, content: str, report: ReviewReport) -> None:
        """检查领域关键词覆盖"""
        keywords = self.knowledge.get("requirement_keywords", [])
        missing_keywords = [kw for kw in keywords if kw not in content]
        
        if missing_keywords:
            report.add_result(CheckResult(
                check_name="领域关键词检查",
                category=CheckCategory.COMPLETENESS,
                level=CheckLevel.WARNING,
                message=f"缺少{self.domain}领域关键词: {', '.join(missing_keywords[:3])}",
                passed=True,
                score=0.7
            ))
        else:
            report.add_result(CheckResult(
                check_name="领域关键词检查",
                category=CheckCategory.COMPLETENESS,
                level=CheckLevel.INFO,
                message="领域关键词覆盖完整",
                passed=True,
                score=1.0
            ))
    
    def _check_quality_attributes(self, content: str, report: ReviewReport) -> None:
        """检查质量属性考虑"""
        quality_attrs = self.knowledge.get("quality_attributes", [])
        mentioned_attrs = [attr for attr in quality_attrs if attr in content]
        
        coverage = len(mentioned_attrs) / len(quality_attrs) if quality_attrs else 1.0
        
        report.add_result(CheckResult(
            check_name="质量属性检查",
            category=CheckCategory.CORRECTNESS,
            level=CheckLevel.INFO if coverage > 0.5 else CheckLevel.WARNING,
            message=f"质量属性覆盖率: {coverage:.0%} ({len(mentioned_attrs)}/{len(quality_attrs)})",
            passed=True,
            score=coverage
        ))
    
    def _check_terminology(self, content: str, report: ReviewReport) -> None:
        """检查专业术语使用"""
        # 检查术语定义是否清晰
        if "术语" in content or "定义" in content:
            report.add_result(CheckResult(
                check_name="术语定义检查",
                category=CheckCategory.READABILITY,
                level=CheckLevel.INFO,
                message="包含术语定义说明",
                passed=True,
                score=1.0
            ))
        else:
            report.add_result(CheckResult(
                check_name="术语定义检查",
                category=CheckCategory.READABILITY,
                level=CheckLevel.HINT,
                message="建议添加术语定义章节",
                suggestion="添加术语定义可提高文档可读性",
                passed=True,
                score=0.9
            ))
    
    def _check_logic_consistency(
        self,
        content: str,
        report: ReviewReport,
        context: dict[str, Any]
    ) -> None:
        """检查逻辑一致性"""
        requirements = context.get("requirements", [])
        
        if requirements:
            covered_reqs = []
            for req in requirements:
                # 简单的关键词匹配
                if any(keyword in content for keyword in req.split() if len(keyword) > 1):
                    covered_reqs.append(req)
            
            coverage = len(covered_reqs) / len(requirements) if requirements else 1.0
            
            report.add_result(CheckResult(
                check_name="需求覆盖检查",
                category=CheckCategory.CONSISTENCY,
                level=CheckLevel.ERROR if coverage < 0.5 else CheckLevel.INFO,
                message=f"需求覆盖率: {coverage:.0%}",
                passed=coverage >= 0.5,
                score=coverage
            ))
    
    def _generate_recommendations(self, report: ReviewReport) -> None:
        """生成专家建议"""
        recommendations = []
        
        errors = report.get_errors()
        if errors:
            recommendations.append("优先修复以下问题: " + ", ".join(e.message for e in errors[:3]))
        
        warnings = report.get_warnings()
        if warnings:
            recommendations.append("建议改进: " + ", ".join(w.message for w in warnings[:3]))
        
        if report.overall_score < 0.7:
            recommendations.append(f"当前评分 {report.overall_score:.0%}，建议进行全面修订")
        elif report.overall_score < 0.9:
            recommendations.append(f"当前评分 {report.overall_score:.0%}，可进行细节优化")
        
        report.recommendations = recommendations
        
        # 生成摘要
        report.summary = (
            f"专家评审完成，{self.domain}领域评估，"
            f"总体评分 {report.overall_score:.0%}，"
            f"{'通过' if report.passed else '需改进'}"
        )


class FeedbackGenerator:
    """
    反馈生成器
    
    根据评审报告生成结构化反馈和改进建议。
    
    使用示例:
        generator = FeedbackGenerator()
        feedback = generator.generate(report)
        print(feedback.to_markdown())
    """
    
    def __init__(self, language: str = "zh-CN"):
        """
        初始化反馈生成器
        
        Args:
            language: 输出语言
        """
        self.language = language
    
    def generate(
        self,
        report: ReviewReport,
        format: str = "markdown"
    ) -> Feedback:
        """
        生成反馈
        
        Args:
            report: 评审报告
            format: 输出格式
        
        Returns:
            反馈对象
        """
        feedback = Feedback(
            product_id=report.product_id,
            product_name=report.product_name,
            overall_score=report.overall_score,
            passed=report.passed
        )
        
        # 分类处理检查结果
        for result in report.check_results:
            item = FeedbackItem(
                check_name=result.check_name,
                category=result.category.value,
                level=result.level.value,
                message=result.message,
                suggestion=result.suggestion,
                location=result.location
            )
            feedback.add_item(item)
        
        # 生成改进建议
        feedback.improvement_suggestions = self._generate_improvements(report)
        
        # 生成总结
        feedback.summary = self._generate_summary(report)
        
        return feedback
    
    def _generate_improvements(self, report: ReviewReport) -> list[str]:
        """生成改进建议"""
        suggestions = []
        
        # 根据错误生成建议
        errors = report.get_errors()
        for error in errors:
            if error.suggestion:
                suggestions.append(f"【{error.check_name}】{error.suggestion}")
            else:
                suggestions.append(f"【{error.check_name}】{error.message}")
        
        # 根据警告生成建议
        warnings = report.get_warnings()
        for warning in warnings[:5]:  # 最多5条警告建议
            if warning.suggestion:
                suggestions.append(f"[{warning.check_name}] {warning.suggestion}")
        
        # 添加报告中的建议
        suggestions.extend(report.recommendations)
        
        return suggestions
    
    def _generate_summary(self, report: ReviewReport) -> str:
        """生成反馈总结"""
        if report.passed:
            if report.overall_score >= 0.9:
                return "✅ 质量优秀，可直接发布"
            elif report.overall_score >= 0.7:
                return "✅ 质量良好，建议优化细节后发布"
            else:
                return "⚠️ 质量合格，建议改进后发布"
        else:
            return "❌ 质量不合格，需要修订后重新评审"
    
    def generate_quick_summary(self, report: ReviewReport) -> str:
        """
        生成快速摘要
        
        Args:
            report: 评审报告
        
        Returns:
            快速摘要文本
        """
        status = "✅ 通过" if report.passed else "❌ 未通过"
        return (
            f"【评审结果】{status}\n"
            f"【总体评分】{report.overall_score:.0%}\n"
            f"【错误数】{len(report.get_errors())}\n"
            f"【警告数】{len(report.get_warnings())}\n"
            f"【检查项】{len(report.check_results)}"
        )


@dataclass
class FeedbackItem:
    """
    反馈项
    
    表示单条反馈内容。
    """
    check_name: str = ""
    category: str = ""
    level: str = ""
    message: str = ""
    suggestion: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "check_name": self.check_name,
            "category": self.category,
            "level": self.level,
            "message": self.message,
            "suggestion": self.suggestion,
            "location": self.location
        }


@dataclass
class Feedback:
    """
    反馈
    
    表示完整的反馈内容。
    """
    feedback_id: str = field(default_factory=lambda: str(uuid4()))
    product_id: str = ""
    product_name: str = ""
    overall_score: float = 0.0
    passed: bool = True
    summary: str = ""
    items: list[FeedbackItem] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_item(self, item: FeedbackItem) -> None:
        """添加反馈项"""
        self.items.append(item)
    
    def to_markdown(self) -> str:
        """
        转换为Markdown格式
        
        Returns:
            Markdown格式的反馈内容
        """
        lines = [
            f"# 质量评审反馈\n",
            f"\n## 基本信息\n",
            f"- **产物名称**: {self.product_name}",
            f"- **总体评分**: {self.overall_score:.0%}",
            f"- **评审结果**: {'✅ 通过' if self.passed else '❌ 未通过'}",
            f"- **评审时间**: {self.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"\n## 评审总结\n{self.summary}\n"
        ]
        
        if self.items:
            lines.append("\n## 详细反馈\n")
            for item in self.items:
                level_emoji = {
                    "error": "🔴",
                    "warning": "🟡",
                    "info": "🔵",
                    "hint": "⚪"
                }.get(item.level, "•")
                
                lines.append(f"\n### {level_emoji} {item.check_name}\n")
                lines.append(f"- **类别**: {item.category}")
                lines.append(f"- **级别**: {item.level}")
                lines.append(f"- **描述**: {item.message}")
                if item.location:
                    lines.append(f"- **位置**: {item.location}")
                if item.suggestion:
                    lines.append(f"- **建议**: {item.suggestion}")
        
        if self.improvement_suggestions:
            lines.append("\n## 改进建议\n")
            for idx, suggestion in enumerate(self.improvement_suggestions, 1):
                lines.append(f"\n{idx}. {suggestion}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "feedback_id": self.feedback_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "overall_score": self.overall_score,
            "passed": self.passed,
            "summary": self.summary,
            "items": [item.to_dict() for item in self.items],
            "improvement_suggestions": self.improvement_suggestions,
            "created_at": self.created_at.isoformat()
        }


# 导出所有公共类
__all__ = [
    "CheckLevel",
    "CheckCategory",
    "CheckResult",
    "ReviewReport",
    "BaseChecker",
    "StandardChecker",
    "CompletenessChecker",
    "FormatChecker",
    "StructureChecker",
    "LanguageChecker",
    "ExpertReviewer",
    "FeedbackGenerator",
    "FeedbackItem",
    "Feedback",
]
