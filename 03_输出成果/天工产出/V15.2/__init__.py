"""
V15.2 多智能体协同平台核心模块

包含:
- product_engine: 产物生成引擎
- quality_engine: 质量审核引擎
- templates: 产物模板库
"""

__version__ = "15.2.0"
__author__ = "天工"

from product_engine import (
    ProductType,
    TaskStatus,
    AgentRole,
    ProductBlueprint,
    AgentTask,
    ProductResult,
    ProductBlueprintGenerator,
    AgentTaskScheduler,
    ResultIntegrator,
)

from quality_engine import (
    CheckLevel,
    CheckCategory,
    CheckResult,
    ReviewReport,
    StandardChecker,
    ExpertReviewer,
    FeedbackGenerator,
    Feedback,
)

__all__ = [
    # 产物生成引擎
    "ProductType",
    "TaskStatus",
    "AgentRole",
    "ProductBlueprint",
    "AgentTask",
    "ProductResult",
    "ProductBlueprintGenerator",
    "AgentTaskScheduler",
    "ResultIntegrator",
    # 质量审核引擎
    "CheckLevel",
    "CheckCategory",
    "CheckResult",
    "ReviewReport",
    "StandardChecker",
    "ExpertReviewer",
    "FeedbackGenerator",
    "Feedback",
]
