"""
单元测试 - 质量审核引擎
V15.2 多智能体协同平台

测试覆盖:
- StandardChecker
- ExpertReviewer
- FeedbackGenerator
"""

import pytest
from datetime import datetime
from typing import Any

from quality_engine import (
    CheckLevel,
    CheckCategory,
    CheckResult,
    ReviewReport,
    BaseChecker,
    StandardChecker,
    CompletenessChecker,
    FormatChecker,
    StructureChecker,
    LanguageChecker,
    ExpertReviewer,
    FeedbackGenerator,
    FeedbackItem,
    Feedback,
)


class TestCheckResult:
    """测试检查结果数据类"""
    
    def test_create_check_result(self):
        """测试创建检查结果"""
        result = CheckResult(
            check_name="格式检查",
            category=CheckCategory.CORRECTNESS,
            level=CheckLevel.WARNING,
            message="发现格式问题",
            passed=True,
            score=0.8
        )
        
        assert result.check_name == "格式检查"
        assert result.category == CheckCategory.CORRECTNESS
        assert result.level == CheckLevel.WARNING
        assert result.passed is True
        assert result.score == 0.8
    
    def test_check_result_to_dict(self):
        """测试检查结果转换为字典"""
        result = CheckResult(
            check_name="完整性检查",
            category=CheckCategory.COMPLETENESS,
            level=CheckLevel.ERROR,
            message="缺少必要章节",
            location="第3章",
            suggestion="添加缺失章节",
            passed=False
        )
        
        data = result.to_dict()
        
        assert data["check_name"] == "完整性检查"
        assert data["category"] == "completeness"
        assert data["level"] == "error"
        assert data["message"] == "缺少必要章节"
        assert data["suggestion"] == "添加缺失章节"


class TestReviewReport:
    """测试评审报告数据类"""
    
    def test_create_report(self):
        """测试创建评审报告"""
        report = ReviewReport(
            product_id="prod-001",
            product_name="需求文档",
            reviewer="StandardChecker"
        )
        
        assert report.product_id == "prod-001"
        assert report.product_name == "需求文档"
        assert report.passed is True  # 默认通过
    
    def test_add_result(self):
        """测试添加检查结果"""
        report = ReviewReport(product_name="测试文档")
        
        result1 = CheckResult(
            check_name="检查1",
            category=CheckCategory.CORRECTNESS,
            level=CheckLevel.INFO,
            message="正常",
            passed=True
        )
        result2 = CheckResult(
            check_name="检查2",
            category=CheckCategory.COMPLETENESS,
            level=CheckLevel.ERROR,
            message="错误",
            passed=False
        )
        
        report.add_result(result1)
        report.add_result(result2)
        
        assert len(report.check_results) == 2
        assert report.passed is False  # 有ERROR级别的不通过
    
    def test_calculate_overall_score(self):
        """测试计算总体评分"""
        report = ReviewReport(product_name="测试文档")
        
        report.add_result(CheckResult(
            check_name="检查1",
            level=CheckLevel.INFO,
            score=1.0
        ))
        report.add_result(CheckResult(
            check_name="检查2",
            level=CheckLevel.WARNING,
            score=0.8
        ))
        report.add_result(CheckResult(
            check_name="检查3",
            level=CheckLevel.ERROR,
            score=0.5
        ))
        
        score = report.calculate_overall_score()
        
        assert 0.0 <= score <= 1.0
        assert score < 1.0  # 有非满分项
    
    def test_get_errors_and_warnings(self):
        """测试获取错误和警告"""
        report = ReviewReport(product_name="测试文档")
        
        report.add_result(CheckResult(
            check_name="错误1",
            level=CheckLevel.ERROR,
            message="错误信息",
            passed=False
        ))
        report.add_result(CheckResult(
            check_name="警告1",
            level=CheckLevel.WARNING,
            message="警告信息"
        ))
        report.add_result(CheckResult(
            check_name="信息1",
            level=CheckLevel.INFO,
            message="信息"
        ))
        
        errors = report.get_errors()
        warnings = report.get_warnings()
        
        assert len(errors) == 1
        assert len(warnings) == 1
    
    def test_report_to_dict(self):
        """测试报告转换为字典"""
        report = ReviewReport(
            product_id="prod-001",
            product_name="测试文档",
            overall_score=0.85
        )
        
        data = report.to_dict()
        
        assert data["product_id"] == "prod-001"
        assert data["product_name"] == "测试文档"
        assert data["overall_score"] == 0.85


class TestCompletenessChecker:
    """测试完整性检查器"""
    
    @pytest.fixture
    def checker(self):
        return CompletenessChecker()
    
    def test_check_complete_content(self, checker):
        """测试完整内容"""
        content = """
        # 文档标题
        ## 概述
        这是概述内容
        ## 需求
        需求内容
        ## 功能
        功能描述
        """
        
        result = checker.check(content, {"product_type": "requirement_doc"})
        
        assert result.passed is True
        assert result.score == 1.0
    
    def test_check_incomplete_content(self, checker):
        """测试不完整内容"""
        content = """
        # 文档标题
        ## 概述
        这是概述内容
        """
        
        result = checker.check(content, {"product_type": "requirement_doc"})
        
        assert result.passed is False
        assert result.level == CheckLevel.ERROR
        assert "缺少必要元素" in result.message


class TestFormatChecker:
    """测试格式检查器"""
    
    @pytest.fixture
    def checker(self):
        return FormatChecker()
    
    def test_check_valid_format(self, checker):
        """测试有效格式"""
        content = """
        # 标题
        ## 二级标题
        ### 三级标题
        
        正文内容
        
        ```python
        code block
        ```
        """
        
        result = checker.check(content)
        
        assert result.passed is True
    
    def test_check_heading_skip(self, checker):
        """测试标题层级跳跃"""
        content = """
        # 一级标题
        ### 三级标题（跳过二级）
        """
        
        result = checker.check(content)
        
        assert "标题层级跳跃" in result.suggestion
    
    def test_check_unclosed_code_block(self, checker):
        """测试未闭合代码块"""
        content = """
        # 标题
        ```
        未闭合的代码块
        """
        
        result = checker.check(content)
        
        assert "代码块未正确闭合" in result.suggestion


class TestStructureChecker:
    """测试结构检查器"""
    
    @pytest.fixture
    def checker(self):
        return StructureChecker()
    
    def test_check_good_structure(self, checker):
        """测试良好结构"""
        content = """
        # 第一章
        内容1
        
        # 第二章
        内容2
        
        # 第三章
        内容3
        """
        
        result = checker.check(content)
        
        assert result.passed is True
        assert result.score == 1.0
    
    def test_check_long_paragraph(self, checker):
        """测试长段落"""
        lines = ["内容行" * 10] * 25
        content = "\n".join(lines)
        
        result = checker.check(content)
        
        assert "段落过长" in result.suggestion


class TestLanguageChecker:
    """测试语言检查器"""
    
    @pytest.fixture
    def checker(self):
        return LanguageChecker()
    
    def test_check_clear_language(self, checker):
        """测试清晰语言"""
        content = """
        系统需要实现用户管理功能。
        用户可以进行注册、登录操作。
        系统应保证数据安全。
        """
        
        result = checker.check(content)
        
        assert result.passed is True
        assert result.score == 1.0
    
    def test_check_fuzzy_words(self, checker):
        """测试模糊词"""
        content = """
        系统大概需要实现一些功能等等。
        可能还需要做之类的。
        """
        
        result = checker.check(content)
        
        assert result.level == CheckLevel.HINT
        assert "模糊词" in result.message
    
    def test_check_punctuation_issues(self, checker):
        """测试标点问题"""
        content = "这是内容。。还有更多内容。"
        
        result = checker.check(content)
        
        assert "重复句号" in result.message


class TestStandardChecker:
    """测试标准检查器"""
    
    @pytest.fixture
    def checker(self):
        return StandardChecker()
    
    def test_check_valid_document(self, checker):
        """测试检查有效文档"""
        content = """
        # 用户管理系统需求文档
        
        ## 概述
        本系统提供用户管理功能
        
        ## 需求
        1. 用户注册
        2. 用户登录
        
        ## 功能
        - 注册功能
        - 登录功能
        """
        
        report = checker.check(content, {
            "product_id": "doc-001",
            "product_name": "需求文档",
            "product_type": "requirement_doc"
        })
        
        assert isinstance(report, ReviewReport)
        assert len(report.check_results) > 0
        assert report.overall_score > 0
    
    def test_check_with_categories_filter(self, checker):
        """测试按类别过滤检查"""
        content = "# 文档\n内容"
        
        report = checker.check(
            content,
            categories=[CheckCategory.READABILITY]
        )
        
        # 只执行可读性相关的检查
        for result in report.check_results:
            assert result.category == CheckCategory.READABILITY
    
    def test_strict_mode(self):
        """测试严格模式"""
        checker = StandardChecker(strict_mode=True)
        
        content = "# 文档"
        report = checker.check(content, {
            "product_type": "requirement_doc"
        })
        
        # 严格模式下，警告也会导致不通过
        if len(report.get_warnings()) > 0:
            assert report.passed is False


class TestExpertReviewer:
    """测试专家评审器"""
    
    @pytest.fixture
    def reviewer(self):
        return ExpertReviewer(domain="软件工程")
    
    def test_review_document(self, reviewer):
        """测试评审文档"""
        content = """
        # 系统设计文档
        
        ## 概述
        本系统实现用户管理、权限控制功能。
        
        ## 用户模块
        用户可以进行注册、登录操作。
        
        ## 接口设计
        系统对外提供RESTful API接口。
        
        ## 性能要求
        系统需要具备高可用性和高性能。
        
        ## 安全设计
        采用OAuth2.0认证机制，确保安全性。
        """
        
        report = reviewer.review(content, {
            "product_id": "doc-001",
            "product_name": "设计文档",
            "requirements": ["用户管理", "权限控制"]
        })
        
        assert isinstance(report, ReviewReport)
        assert len(report.check_results) > 0
        assert report.reviewer == "软件工程专家(senior)"
    
    def test_domain_keywords_check(self, reviewer):
        """测试领域关键词检查"""
        content = "系统需要实现用户管理和接口设计功能"
        
        report = reviewer.review(content)
        
        # 检查关键词覆盖
        keyword_result = next(
            (r for r in report.check_results if "关键词" in r.check_name),
            None
        )
        assert keyword_result is not None
    
    def test_quality_attributes_check(self, reviewer):
        """测试质量属性检查"""
        content = "系统需要保证可维护性和可测试性"
        
        report = reviewer.review(content)
        
        quality_result = next(
            (r for r in report.check_results if "质量属性" in r.check_name),
            None
        )
        assert quality_result is not None
    
    def test_different_expertise_levels(self):
        """测试不同专家级别"""
        junior = ExpertReviewer(domain="软件工程", expertise_level="junior")
        senior = ExpertReviewer(domain="软件工程", expertise_level="senior")
        expert = ExpertReviewer(domain="软件工程", expertise_level="expert")
        
        content = "# 文档\n系统设计内容"
        
        junior_report = junior.review(content)
        senior_report = senior.review(content)
        expert_report = expert.review(content)
        
        assert "junior" in junior_report.reviewer
        assert "senior" in senior_report.reviewer
        assert "expert" in expert_report.reviewer


class TestFeedbackGenerator:
    """测试反馈生成器"""
    
    @pytest.fixture
    def generator(self):
        return FeedbackGenerator()
    
    @pytest.fixture
    def sample_report(self):
        """创建示例报告"""
        report = ReviewReport(
            product_id="prod-001",
            product_name="测试文档",
            overall_score=0.75,
            passed=True
        )
        
        report.add_result(CheckResult(
            check_name="完整性检查",
            category=CheckCategory.COMPLETENESS,
            level=CheckLevel.ERROR,
            message="缺少必要章节",
            suggestion="添加缺失章节",
            passed=False
        ))
        
        report.add_result(CheckResult(
            check_name="格式检查",
            category=CheckCategory.CORRECTNESS,
            level=CheckLevel.WARNING,
            message="格式需要优化",
            suggestion="调整格式",
            passed=True
        ))
        
        report.recommendations = ["建议1", "建议2"]
        
        return report
    
    def test_generate_feedback(self, generator, sample_report):
        """测试生成反馈"""
        feedback = generator.generate(sample_report)
        
        assert isinstance(feedback, Feedback)
        assert feedback.product_id == "prod-001"
        assert feedback.overall_score == 0.75
        assert feedback.passed is True
    
    def test_generate_quick_summary(self, generator, sample_report):
        """测试生成快速摘要"""
        summary = generator.generate_quick_summary(sample_report)
        
        assert "通过" in summary
        assert "75%" in summary
    
    def test_feedback_to_markdown(self, generator, sample_report):
        """测试反馈转换为Markdown"""
        feedback = generator.generate(sample_report)
        markdown = feedback.to_markdown()
        
        assert "质量评审反馈" in markdown
        assert "测试文档" in markdown
        assert "完整性检查" in markdown
    
    def test_feedback_to_dict(self, generator, sample_report):
        """测试反馈转换为字典"""
        feedback = generator.generate(sample_report)
        data = feedback.to_dict()
        
        assert data["product_id"] == "prod-001"
        assert data["overall_score"] == 0.75
        assert len(data["items"]) == 2


class TestFeedbackItem:
    """测试反馈项数据类"""
    
    def test_create_feedback_item(self):
        """测试创建反馈项"""
        item = FeedbackItem(
            check_name="格式检查",
            category="correctness",
            level="warning",
            message="格式问题",
            suggestion="调整格式"
        )
        
        assert item.check_name == "格式检查"
        assert item.category == "correctness"
        assert item.level == "warning"
    
    def test_feedback_item_to_dict(self):
        """测试反馈项转换为字典"""
        item = FeedbackItem(
            check_name="检查项",
            category="completeness",
            level="error",
            message="错误信息"
        )
        
        data = item.to_dict()
        
        assert data["check_name"] == "检查项"
        assert data["category"] == "completeness"
        assert data["level"] == "error"


class TestFeedback:
    """测试反馈数据类"""
    
    def test_create_feedback(self):
        """测试创建反馈"""
        feedback = Feedback(
            product_id="prod-001",
            product_name="测试文档",
            overall_score=0.85,
            passed=True,
            summary="质量良好"
        )
        
        assert feedback.product_id == "prod-001"
        assert feedback.overall_score == 0.85
        assert feedback.summary == "质量良好"
    
    def test_add_item(self):
        """测试添加反馈项"""
        feedback = Feedback(product_name="测试")
        
        item = FeedbackItem(
            check_name="检查项",
            category="correctness",
            level="info",
            message="信息"
        )
        
        feedback.add_item(item)
        
        assert len(feedback.items) == 1
    
    def test_feedback_to_markdown_with_items(self):
        """测试带项目的反馈Markdown转换"""
        feedback = Feedback(
            product_name="测试文档",
            overall_score=0.9,
            passed=True,
            summary="质量优秀"
        )
        
        feedback.add_item(FeedbackItem(
            check_name="格式检查",
            category="correctness",
            level="info",
            message="格式正确"
        ))
        
        feedback.add_item(FeedbackItem(
            check_name="完整性检查",
            category="completeness",
            level="warning",
            message="建议补充"
        ))
        
        markdown = feedback.to_markdown()
        
        assert "测试文档" in markdown
        assert "格式检查" in markdown
        assert "完整性检查" in markdown


class TestEnums:
    """测试枚举类"""
    
    def test_check_level_values(self):
        """测试检查级别枚举值"""
        assert CheckLevel.ERROR.value == "error"
        assert CheckLevel.WARNING.value == "warning"
        assert CheckLevel.INFO.value == "info"
        assert CheckLevel.HINT.value == "hint"
    
    def test_check_category_values(self):
        """测试检查类别枚举值"""
        assert CheckCategory.COMPLETENESS.value == "completeness"
        assert CheckCategory.CONSISTENCY.value == "consistency"
        assert CheckCategory.CORRECTNESS.value == "correctness"
        assert CheckCategory.READABILITY.value == "readability"


class TestBaseChecker:
    """测试检查器基类"""
    
    def test_base_checker_is_abstract(self):
        """测试基类是抽象类"""
        with pytest.raises(TypeError):
            BaseChecker(name="测试", category=CheckCategory.CORRECTNESS)
    
    def test_custom_checker(self):
        """测试自定义检查器"""
        class CustomChecker(BaseChecker):
            def check(self, content: str, context=None) -> CheckResult:
                return CheckResult(
                    check_name=self.name,
                    category=self.category,
                    level=CheckLevel.INFO,
                    message="自定义检查",
                    passed=True
                )
        
        checker = CustomChecker("自定义", CheckCategory.COMPLIANCE)
        result = checker.check("内容")
        
        assert result.check_name == "自定义"
        assert result.category == CheckCategory.COMPLIANCE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
