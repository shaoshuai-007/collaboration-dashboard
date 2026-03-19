"""
产物生成引擎 - Product Generation Engine
V15.2 多智能体协同平台核心模块

包含:
- ProductBlueprintGenerator: 产物蓝图生成器
- AgentTaskScheduler: Agent任务调度器
- ResultIntegrator: 结果整合器
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class ProductType(Enum):
    """产物类型枚举"""
    REQUIREMENT_DOC = "requirement_doc"
    ARCHITECTURE_DESIGN = "architecture_design"
    SOLUTION_PPT = "solution_ppt"
    PROJECT_PLAN = "project_plan"
    CODE_MODULE = "code_module"
    TEST_REPORT = "test_report"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(Enum):
    """Agent角色枚举"""
    ANALYST = "analyst"           # 需求分析师
    ARCHITECT = "architect"       # 架构师
    DEVELOPER = "developer"       # 开发工程师
    TESTER = "tester"             # 测试工程师
    REVIEWER = "reviewer"         # 评审专家
    PROJECT_MANAGER = "pm"        # 项目经理


@dataclass
class ProductBlueprint:
    """
    产物蓝图
    
    描述一个产物的完整生成计划，包括所需的Agent任务和依赖关系。
    """
    blueprint_id: str = field(default_factory=lambda: str(uuid4()))
    product_type: ProductType = ProductType.REQUIREMENT_DOC
    product_name: str = ""
    description: str = ""
    requirements: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    task_sequence: list[AgentTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "blueprint_id": self.blueprint_id,
            "product_type": self.product_type.value,
            "product_name": self.product_name,
            "description": self.description,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "task_count": len(self.task_sequence),
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class AgentTask:
    """
    Agent任务
    
    表示单个Agent需要执行的任务单元。
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_name: str = ""
    agent_role: AgentRole = AgentRole.DEVELOPER
    description: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)  # 依赖的任务ID列表
    priority: int = 0
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def mark_running(self) -> None:
        """标记任务为运行中"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self, output: dict[str, Any]) -> None:
        """标记任务为已完成"""
        self.status = TaskStatus.COMPLETED
        self.output_data = output
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str) -> None:
        """标记任务为失败"""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()
    
    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "agent_role": self.agent_role.value,
            "description": self.description,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }


@dataclass
class ProductResult:
    """
    产物结果
    
    表示最终生成的产物内容。
    """
    result_id: str = field(default_factory=lambda: str(uuid4()))
    blueprint_id: str = ""
    product_type: ProductType = ProductType.REQUIREMENT_DOC
    content: str = ""
    format: str = "markdown"  # markdown, json, html, pptx
    quality_score: float = 0.0
    review_comments: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "result_id": self.result_id,
            "blueprint_id": self.blueprint_id,
            "product_type": self.product_type.value,
            "content_length": len(self.content),
            "format": self.format,
            "quality_score": self.quality_score,
            "review_comments": self.review_comments,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class ProductBlueprintGenerator:
    """
    产物蓝图生成器
    
    根据需求自动生成产物蓝图，规划Agent任务序列。
    
    使用示例:
        generator = ProductBlueprintGenerator()
        blueprint = generator.generate(
            product_type=ProductType.REQUIREMENT_DOC,
            product_name="用户管理系统需求文档",
            requirements=["支持用户注册登录", "支持权限管理"],
            constraints={"format": "markdown", "language": "zh-CN"}
        )
    """
    
    # 产物类型到任务序列的映射
    TASK_TEMPLATES: dict[ProductType, list[dict[str, Any]]] = {
        ProductType.REQUIREMENT_DOC: [
            {"role": AgentRole.ANALYST, "task": "需求收集与分析", "priority": 1},
            {"role": AgentRole.ANALYST, "task": "用例设计", "priority": 2},
            {"role": AgentRole.REVIEWER, "task": "需求评审", "priority": 3},
        ],
        ProductType.ARCHITECTURE_DESIGN: [
            {"role": AgentRole.ARCHITECT, "task": "架构方案设计", "priority": 1},
            {"role": AgentRole.ARCHITECT, "task": "技术选型", "priority": 2},
            {"role": AgentRole.ARCHITECT, "task": "接口设计", "priority": 3},
            {"role": AgentRole.REVIEWER, "task": "架构评审", "priority": 4},
        ],
        ProductType.SOLUTION_PPT: [
            {"role": AgentRole.ANALYST, "task": "需求提炼", "priority": 1},
            {"role": AgentRole.ARCHITECT, "task": "方案设计", "priority": 2},
            {"role": AgentRole.PROJECT_MANAGER, "task": "PPT内容编排", "priority": 3},
        ],
        ProductType.PROJECT_PLAN: [
            {"role": AgentRole.PROJECT_MANAGER, "task": "需求分解", "priority": 1},
            {"role": AgentRole.PROJECT_MANAGER, "task": "进度规划", "priority": 2},
            {"role": AgentRole.PROJECT_MANAGER, "task": "资源分配", "priority": 3},
            {"role": AgentRole.REVIEWER, "task": "计划评审", "priority": 4},
        ],
        ProductType.CODE_MODULE: [
            {"role": AgentRole.DEVELOPER, "task": "代码实现", "priority": 1},
            {"role": AgentRole.TESTER, "task": "单元测试", "priority": 2},
            {"role": AgentRole.REVIEWER, "task": "代码审查", "priority": 3},
        ],
        ProductType.TEST_REPORT: [
            {"role": AgentRole.TESTER, "task": "测试执行", "priority": 1},
            {"role": AgentRole.TESTER, "task": "结果分析", "priority": 2},
            {"role": AgentRole.REVIEWER, "task": "报告审核", "priority": 3},
        ],
    }
    
    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        初始化蓝图生成器
        
        Args:
            config: 配置参数，可包含自定义任务模板等
        """
        self.config = config or {}
        if "task_templates" in self.config:
            self.TASK_TEMPLATES.update(self.config["task_templates"])
    
    def generate(
        self,
        product_type: ProductType,
        product_name: str,
        requirements: list[str],
        description: str = "",
        constraints: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> ProductBlueprint:
        """
        生成产物蓝图
        
        Args:
            product_type: 产物类型
            product_name: 产物名称
            requirements: 需求列表
            description: 产物描述
            constraints: 约束条件
            metadata: 元数据
        
        Returns:
            生成的产物蓝图
        
        Raises:
            ValueError: 当参数无效时
        """
        if not product_name:
            raise ValueError("product_name 不能为空")
        if not requirements:
            raise ValueError("requirements 不能为空")
        
        # 创建蓝图
        blueprint = ProductBlueprint(
            product_type=product_type,
            product_name=product_name,
            description=description or f"{product_name} - {product_type.value}",
            requirements=requirements,
            constraints=constraints or {},
            metadata=metadata or {}
        )
        
        # 生成任务序列
        task_template = self.TASK_TEMPLATES.get(product_type, [])
        task_ids: list[str] = []
        
        for idx, template in enumerate(task_template):
            task = AgentTask(
                task_name=f"{product_name} - {template['task']}",
                agent_role=template["role"],
                description=f"执行 {template['task']} 任务",
                input_data={
                    "requirements": requirements,
                    "constraints": constraints or {}
                },
                priority=template["priority"],
                dependencies=task_ids.copy() if idx > 0 else []
            )
            blueprint.task_sequence.append(task)
            task_ids.append(task.task_id)
        
        return blueprint
    
    def generate_from_template(
        self,
        template_name: str,
        params: dict[str, Any]
    ) -> ProductBlueprint:
        """
        从模板生成蓝图
        
        Args:
            template_name: 模板名称
            params: 模板参数
        
        Returns:
            生成的产物蓝图
        
        Raises:
            KeyError: 模板不存在时
        """
        templates = {
            "software_requirement": {
                "product_type": ProductType.REQUIREMENT_DOC,
                "constraints": {"format": "markdown", "language": "zh-CN"}
            },
            "system_architecture": {
                "product_type": ProductType.ARCHITECTURE_DESIGN,
                "constraints": {"format": "markdown", "include_diagrams": True}
            },
            "project_proposal": {
                "product_type": ProductType.SOLUTION_PPT,
                "constraints": {"format": "pptx", "slide_count": "10-15"}
            },
            "sprint_plan": {
                "product_type": ProductType.PROJECT_PLAN,
                "constraints": {"format": "markdown", "duration_weeks": 2}
            }
        }
        
        if template_name not in templates:
            raise KeyError(f"模板 '{template_name}' 不存在，可用模板: {list(templates.keys())}")
        
        template = templates[template_name]
        return self.generate(
            product_type=template["product_type"],
            product_name=params.get("name", template_name),
            requirements=params.get("requirements", []),
            description=params.get("description", ""),
            constraints={**template.get("constraints", {}), **params.get("constraints", {})},
            metadata=params.get("metadata", {})
        )


class AgentTaskScheduler:
    """
    Agent任务调度器
    
    管理和调度Agent任务的执行顺序，处理任务依赖关系。
    
    使用示例:
        scheduler = AgentTaskScheduler()
        scheduler.add_task(task1)
        scheduler.add_task(task2, dependencies=[task1.task_id])
        
        while scheduler.has_pending_tasks():
            task = scheduler.get_next_task()
            # 执行任务...
            scheduler.complete_task(task.task_id, result)
    """
    
    def __init__(self, max_concurrent: int = 5):
        """
        初始化任务调度器
        
        Args:
            max_concurrent: 最大并发任务数
        """
        self.max_concurrent = max_concurrent
        self.tasks: dict[str, AgentTask] = {}
        self.running_count = 0
        self._callbacks: dict[str, list[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_task_fail": []
        }
    
    def add_task(self, task: AgentTask) -> str:
        """
        添加任务到调度器
        
        Args:
            task: 要添加的任务
        
        Returns:
            任务ID
        
        Raises:
            ValueError: 任务ID已存在时
        """
        if task.task_id in self.tasks:
            raise ValueError(f"任务ID '{task.task_id}' 已存在")
        
        self.tasks[task.task_id] = task
        return task.task_id
    
    def add_blueprint_tasks(self, blueprint: ProductBlueprint) -> list[str]:
        """
        添加蓝图中的所有任务
        
        Args:
            blueprint: 产物蓝图
        
        Returns:
            任务ID列表
        """
        task_ids = []
        for task in blueprint.task_sequence:
            task_ids.append(self.add_task(task))
        return task_ids
    
    def get_next_task(self) -> Optional[AgentTask]:
        """
        获取下一个可执行的任务
        
        Returns:
            下一个可执行的任务，如果没有则返回None
        """
        if self.running_count >= self.max_concurrent:
            return None
        
        # 按优先级排序，获取所有pending且依赖已满足的任务
        pending_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING and self._check_dependencies(task)
        ]
        
        if not pending_tasks:
            return None
        
        # 按优先级排序（数字小的优先）
        pending_tasks.sort(key=lambda t: t.priority)
        next_task = pending_tasks[0]
        
        next_task.mark_running()
        self.running_count += 1
        self._trigger_callback("on_task_start", next_task)
        
        return next_task
    
    def _check_dependencies(self, task: AgentTask) -> bool:
        """
        检查任务的依赖是否都已满足
        
        Args:
            task: 要检查的任务
        
        Returns:
            依赖是否都已满足
        """
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def complete_task(self, task_id: str, output: dict[str, Any]) -> bool:
        """
        标记任务完成
        
        Args:
            task_id: 任务ID
            output: 任务输出
        
        Returns:
            是否成功完成
        
        Raises:
            KeyError: 任务不存在时
        """
        if task_id not in self.tasks:
            raise KeyError(f"任务 '{task_id}' 不存在")
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.RUNNING:
            return False
        
        task.mark_completed(output)
        self.running_count -= 1
        self._trigger_callback("on_task_complete", task)
        
        return True
    
    def fail_task(self, task_id: str, error: str, retry: bool = True) -> bool:
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error: 错误信息
            retry: 是否尝试重试
        
        Returns:
            是否成功标记失败
        
        Raises:
            KeyError: 任务不存在时
        """
        if task_id not in self.tasks:
            raise KeyError(f"任务 '{task_id}' 不存在")
        
        task = self.tasks[task_id]
        
        if retry and task.can_retry():
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            task.error_message = error
            return True
        
        task.mark_failed(error)
        if task.status == TaskStatus.RUNNING:
            self.running_count -= 1
        self._trigger_callback("on_task_fail", task)
        
        return True
    
    def has_pending_tasks(self) -> bool:
        """检查是否还有待执行的任务"""
        return any(
            task.status in (TaskStatus.PENDING, TaskStatus.RUNNING)
            for task in self.tasks.values()
        )
    
    def get_status_summary(self) -> dict[str, int]:
        """
        获取任务状态统计
        
        Returns:
            各状态的任务数量
        """
        summary = {status.value: 0 for status in TaskStatus}
        for task in self.tasks.values():
            summary[task.status.value] += 1
        return summary
    
    def register_callback(self, event: str, callback: Callable[[AgentTask], None]) -> None:
        """
        注册事件回调
        
        Args:
            event: 事件名称 (on_task_start, on_task_complete, on_task_fail)
            callback: 回调函数
        
        Raises:
            ValueError: 事件名称无效时
        """
        if event not in self._callbacks:
            raise ValueError(f"无效的事件 '{event}'，可用事件: {list(self._callbacks.keys())}")
        self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, task: AgentTask) -> None:
        """触发事件回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(task)
            except Exception:
                pass  # 回调失败不影响主流程
    
    def cancel_all(self) -> int:
        """
        取消所有待执行任务
        
        Returns:
            取消的任务数量
        """
        cancelled = 0
        for task in self.tasks.values():
            if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                task.status = TaskStatus.CANCELLED
                cancelled += 1
        return cancelled


class ResultIntegrator:
    """
    结果整合器
    
    将多个Agent任务的输出结果整合为最终产物。
    
    使用示例:
        integrator = ResultIntegrator()
        integrator.add_task_result(task1.task_id, task1.output_data)
        integrator.add_task_result(task2.task_id, task2.output_data)
        
        result = integrator.integrate(blueprint, format="markdown")
    """
    
    def __init__(self, template_loader: Optional[Callable[[str], str]] = None):
        """
        初始化结果整合器
        
        Args:
            template_loader: 模板加载函数，用于加载产物模板
        """
        self.task_results: dict[str, dict[str, Any]] = {}
        self.template_loader = template_loader
    
    def add_task_result(self, task_id: str, result: dict[str, Any]) -> None:
        """
        添加任务结果
        
        Args:
            task_id: 任务ID
            result: 任务结果数据
        """
        self.task_results[task_id] = result
    
    def integrate(
        self,
        blueprint: ProductBlueprint,
        format: str = "markdown"
    ) -> ProductResult:
        """
        整合结果生成最终产物
        
        Args:
            blueprint: 产物蓝图
            format: 输出格式 (markdown, json, html)
        
        Returns:
            整合后的产物结果
        """
        # 收集所有任务结果
        all_results = []
        for task in blueprint.task_sequence:
            if task.task_id in self.task_results:
                all_results.append({
                    "task_name": task.task_name,
                    "agent_role": task.agent_role.value,
                    "data": self.task_results[task.task_id]
                })
        
        # 根据产物类型选择整合策略
        content = self._integrate_by_type(
            product_type=blueprint.product_type,
            blueprint=blueprint,
            results=all_results,
            format=format
        )
        
        # 创建产物结果
        result = ProductResult(
            blueprint_id=blueprint.blueprint_id,
            product_type=blueprint.product_type,
            content=content,
            format=format,
            metadata={
                "task_count": len(blueprint.task_sequence),
                "completed_count": len(all_results),
                "product_name": blueprint.product_name
            }
        )
        
        return result
    
    def _integrate_by_type(
        self,
        product_type: ProductType,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """
        根据产物类型整合结果
        
        Args:
            product_type: 产物类型
            blueprint: 产物蓝图
            results: 所有任务结果
            format: 输出格式
        
        Returns:
            整合后的内容字符串
        """
        integrators = {
            ProductType.REQUIREMENT_DOC: self._integrate_requirement,
            ProductType.ARCHITECTURE_DESIGN: self._integrate_architecture,
            ProductType.SOLUTION_PPT: self._integrate_ppt,
            ProductType.PROJECT_PLAN: self._integrate_project_plan,
            ProductType.CODE_MODULE: self._integrate_code,
            ProductType.TEST_REPORT: self._integrate_test_report,
        }
        
        integrator = integrators.get(product_type, self._integrate_default)
        return integrator(blueprint, results, format)
    
    def _integrate_requirement(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合需求文档"""
        sections = [
            f"# {blueprint.product_name}\n",
            f"\n## 概述\n{blueprint.description}\n",
            f"\n## 需求列表\n"
        ]
        
        for idx, req in enumerate(blueprint.requirements, 1):
            sections.append(f"\n### 需求{idx}\n{req}\n")
        
        for result in results:
            if "content" in result["data"]:
                sections.append(f"\n### {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(sections)
    
    def _integrate_architecture(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合架构设计文档"""
        sections = [
            f"# {blueprint.product_name} - 架构设计\n",
            f"\n## 设计概述\n{blueprint.description}\n",
            f"\n## 架构方案\n"
        ]
        
        for result in results:
            if "content" in result["data"]:
                sections.append(f"\n### {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(sections)
    
    def _integrate_ppt(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合PPT内容"""
        slides = [f"# {blueprint.product_name}\n"]
        
        for idx, result in enumerate(results, 1):
            if "content" in result["data"]:
                slides.append(f"\n## 第{idx}页: {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(slides)
    
    def _integrate_project_plan(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合项目计划"""
        sections = [
            f"# {blueprint.product_name} - 项目计划\n",
            f"\n## 项目概述\n{blueprint.description}\n",
            f"\n## 需求分解\n"
        ]
        
        for idx, req in enumerate(blueprint.requirements, 1):
            sections.append(f"- {req}\n")
        
        for result in results:
            if "content" in result["data"]:
                sections.append(f"\n## {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(sections)
    
    def _integrate_code(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合代码模块"""
        code_sections = [f"# {blueprint.product_name}\n"]
        
        for result in results:
            if "code" in result["data"]:
                code_sections.append(f"\n## {result['task_name']}\n```\n{result['data']['code']}\n```\n")
            elif "content" in result["data"]:
                code_sections.append(f"\n## {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(code_sections)
    
    def _integrate_test_report(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """整合测试报告"""
        sections = [
            f"# {blueprint.product_name} - 测试报告\n",
            f"\n## 测试概述\n{blueprint.description}\n"
        ]
        
        for result in results:
            if "content" in result["data"]:
                sections.append(f"\n## {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(sections)
    
    def _integrate_default(
        self,
        blueprint: ProductBlueprint,
        results: list[dict[str, Any]],
        format: str
    ) -> str:
        """默认整合方法"""
        sections = [f"# {blueprint.product_name}\n"]
        
        for result in results:
            if "content" in result["data"]:
                sections.append(f"\n## {result['task_name']}\n{result['data']['content']}\n")
        
        return "\n".join(sections)
    
    def clear(self) -> None:
        """清空所有任务结果"""
        self.task_results.clear()


# 导出所有公共类
__all__ = [
    "ProductType",
    "TaskStatus",
    "AgentRole",
    "ProductBlueprint",
    "AgentTask",
    "ProductResult",
    "ProductBlueprintGenerator",
    "AgentTaskScheduler",
    "ResultIntegrator",
]
