"""
单元测试 - 产物生成引擎
V15.2 多智能体协同平台

测试覆盖:
- ProductBlueprintGenerator
- AgentTaskScheduler
- ResultIntegrator
"""

import pytest
from datetime import datetime
from typing import Any

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


class TestProductBlueprint:
    """测试产物蓝图数据类"""
    
    def test_create_blueprint(self):
        """测试创建蓝图"""
        blueprint = ProductBlueprint(
            product_type=ProductType.REQUIREMENT_DOC,
            product_name="测试需求文档"
        )
        
        assert blueprint.product_type == ProductType.REQUIREMENT_DOC
        assert blueprint.product_name == "测试需求文档"
        assert blueprint.blueprint_id != ""
        assert isinstance(blueprint.created_at, datetime)
    
    def test_blueprint_to_dict(self):
        """测试蓝图转换为字典"""
        blueprint = ProductBlueprint(
            product_type=ProductType.ARCHITECTURE_DESIGN,
            product_name="架构设计",
            requirements=["高可用", "高性能"]
        )
        
        result = blueprint.to_dict()
        
        assert result["product_type"] == "architecture_design"
        assert result["product_name"] == "架构设计"
        assert result["requirements"] == ["高可用", "高性能"]
    
    def test_blueprint_to_json(self):
        """测试蓝图转换为JSON"""
        blueprint = ProductBlueprint(
            product_type=ProductType.PROJECT_PLAN,
            product_name="项目计划"
        )
        
        json_str = blueprint.to_json()
        
        assert isinstance(json_str, str)
        assert "project_plan" in json_str
        assert "项目计划" in json_str


class TestAgentTask:
    """测试Agent任务数据类"""
    
    def test_create_task(self):
        """测试创建任务"""
        task = AgentTask(
            task_name="需求分析",
            agent_role=AgentRole.ANALYST,
            description="分析用户需求"
        )
        
        assert task.task_name == "需求分析"
        assert task.agent_role == AgentRole.ANALYST
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0
    
    def test_task_status_transitions(self):
        """测试任务状态转换"""
        task = AgentTask(task_name="测试任务")
        
        # 标记为运行中
        task.mark_running()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None
        
        # 标记为完成
        output = {"result": "success"}
        task.mark_completed(output)
        assert task.status == TaskStatus.COMPLETED
        assert task.output_data == output
        assert task.completed_at is not None
    
    def test_task_failure(self):
        """测试任务失败"""
        task = AgentTask(task_name="测试任务")
        task.mark_running()
        
        task.mark_failed("执行失败")
        
        assert task.status == TaskStatus.FAILED
        assert task.error_message == "执行失败"
        assert task.completed_at is not None
    
    def test_task_retry(self):
        """测试任务重试"""
        task = AgentTask(task_name="测试任务", max_retries=2)
        
        task.mark_failed("第一次失败")
        assert task.can_retry() is True
        
        task.retry_count = 2
        assert task.can_retry() is False


class TestProductBlueprintGenerator:
    """测试产物蓝图生成器"""
    
    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        return ProductBlueprintGenerator()
    
    def test_generate_requirement_blueprint(self, generator):
        """测试生成需求文档蓝图"""
        blueprint = generator.generate(
            product_type=ProductType.REQUIREMENT_DOC,
            product_name="用户管理系统需求文档",
            requirements=["用户注册", "用户登录", "权限管理"],
            description="用户管理系统需求规格说明书"
        )
        
        assert blueprint.product_type == ProductType.REQUIREMENT_DOC
        assert blueprint.product_name == "用户管理系统需求文档"
        assert len(blueprint.requirements) == 3
        assert len(blueprint.task_sequence) == 3  # 分析、用例、评审
    
    def test_generate_architecture_blueprint(self, generator):
        """测试生成架构设计蓝图"""
        blueprint = generator.generate(
            product_type=ProductType.ARCHITECTURE_DESIGN,
            product_name="系统架构设计",
            requirements=["微服务架构", "容器化部署"]
        )
        
        assert blueprint.product_type == ProductType.ARCHITECTURE_DESIGN
        assert len(blueprint.task_sequence) == 4  # 架构、技术选型、接口、评审
    
    def test_generate_with_invalid_params(self, generator):
        """测试无效参数"""
        with pytest.raises(ValueError):
            generator.generate(
                product_type=ProductType.REQUIREMENT_DOC,
                product_name="",  # 空名称
                requirements=["需求1"]
            )
        
        with pytest.raises(ValueError):
            generator.generate(
                product_type=ProductType.REQUIREMENT_DOC,
                product_name="测试",
                requirements=[]  # 空需求
            )
    
    def test_generate_from_template(self, generator):
        """测试从模板生成"""
        blueprint = generator.generate_from_template(
            template_name="software_requirement",
            params={
                "name": "电商系统",
                "requirements": ["商品管理", "订单管理"],
                "description": "电商平台需求文档"
            }
        )
        
        assert blueprint.product_name == "电商系统"
        assert blueprint.product_type == ProductType.REQUIREMENT_DOC
    
    def test_generate_from_invalid_template(self, generator):
        """测试无效模板"""
        with pytest.raises(KeyError):
            generator.generate_from_template(
                template_name="invalid_template",
                params={}
            )


class TestAgentTaskScheduler:
    """测试Agent任务调度器"""
    
    @pytest.fixture
    def scheduler(self):
        """创建调度器实例"""
        return AgentTaskScheduler(max_concurrent=3)
    
    def test_add_task(self, scheduler):
        """测试添加任务"""
        task = AgentTask(task_name="任务1")
        task_id = scheduler.add_task(task)
        
        assert task_id == task.task_id
        assert task_id in scheduler.tasks
    
    def test_add_duplicate_task(self, scheduler):
        """测试添加重复任务"""
        task = AgentTask(task_name="任务1")
        scheduler.add_task(task)
        
        with pytest.raises(ValueError):
            scheduler.add_task(task)
    
    def test_get_next_task(self, scheduler):
        """测试获取下一个任务"""
        task1 = AgentTask(task_name="任务1", priority=2)
        task2 = AgentTask(task_name="任务2", priority=1)
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        
        # 优先级低的先执行
        next_task = scheduler.get_next_task()
        assert next_task.task_name == "任务2"
        assert next_task.status == TaskStatus.RUNNING
    
    def test_task_dependencies(self, scheduler):
        """测试任务依赖"""
        task1 = AgentTask(task_name="任务1", priority=1)
        task2 = AgentTask(task_name="任务2", priority=2)
        task2.dependencies = [task1.task_id]
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        
        # 任务2依赖任务1，不能先执行
        next_task = scheduler.get_next_task()
        assert next_task.task_name == "任务1"
        
        # 完成任务1后，任务2可以执行
        scheduler.complete_task(task1.task_id, {})
        next_task = scheduler.get_next_task()
        assert next_task.task_name == "任务2"
    
    def test_complete_task(self, scheduler):
        """测试完成任务"""
        task = AgentTask(task_name="任务1")
        scheduler.add_task(task)
        
        scheduler.get_next_task()  # 标记为运行中
        result = scheduler.complete_task(task.task_id, {"output": "success"})
        
        assert result is True
        assert task.status == TaskStatus.COMPLETED
    
    def test_fail_task_with_retry(self, scheduler):
        """测试任务失败重试"""
        task = AgentTask(task_name="任务1", max_retries=2)
        scheduler.add_task(task)
        scheduler.get_next_task()
        
        scheduler.fail_task(task.task_id, "执行失败", retry=True)
        
        assert task.retry_count == 1
        assert task.status == TaskStatus.PENDING
    
    def test_status_summary(self, scheduler):
        """测试状态统计"""
        task1 = AgentTask(task_name="任务1")
        task2 = AgentTask(task_name="任务2")
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        scheduler.get_next_task()
        
        summary = scheduler.get_status_summary()
        
        assert summary["pending"] == 1
        assert summary["running"] == 1
    
    def test_callback_registration(self, scheduler):
        """测试回调注册"""
        events = []
        
        def on_start(task):
            events.append(("start", task.task_name))
        
        def on_complete(task):
            events.append(("complete", task.task_name))
        
        scheduler.register_callback("on_task_start", on_start)
        scheduler.register_callback("on_task_complete", on_complete)
        
        task = AgentTask(task_name="任务1")
        scheduler.add_task(task)
        scheduler.get_next_task()
        scheduler.complete_task(task.task_id, {})
        
        assert len(events) == 2
        assert events[0] == ("start", "任务1")
        assert events[1] == ("complete", "任务1")


class TestResultIntegrator:
    """测试结果整合器"""
    
    @pytest.fixture
    def integrator(self):
        """创建整合器实例"""
        return ResultIntegrator()
    
    @pytest.fixture
    def sample_blueprint(self):
        """创建示例蓝图"""
        blueprint = ProductBlueprint(
            product_type=ProductType.REQUIREMENT_DOC,
            product_name="测试需求文档",
            requirements=["需求1", "需求2"]
        )
        task1 = AgentTask(task_name="需求分析")
        task2 = AgentTask(task_name="用例设计")
        blueprint.task_sequence = [task1, task2]
        return blueprint
    
    def test_add_task_result(self, integrator):
        """测试添加任务结果"""
        integrator.add_task_result("task-1", {"content": "分析结果"})
        
        assert "task-1" in integrator.task_results
        assert integrator.task_results["task-1"]["content"] == "分析结果"
    
    def test_integrate_requirement_doc(self, integrator, sample_blueprint):
        """测试整合需求文档"""
        task1 = sample_blueprint.task_sequence[0]
        task2 = sample_blueprint.task_sequence[1]
        
        integrator.add_task_result(task1.task_id, {"content": "需求分析内容"})
        integrator.add_task_result(task2.task_id, {"content": "用例设计内容"})
        
        result = integrator.integrate(sample_blueprint, format="markdown")
        
        assert result.product_type == ProductType.REQUIREMENT_DOC
        assert "测试需求文档" in result.content
        assert "需求分析内容" in result.content
        assert result.format == "markdown"
    
    def test_integrate_partial_results(self, integrator, sample_blueprint):
        """测试部分结果整合"""
        task1 = sample_blueprint.task_sequence[0]
        # 只添加第一个任务的结果
        
        integrator.add_task_result(task1.task_id, {"content": "部分内容"})
        
        result = integrator.integrate(sample_blueprint)
        
        assert "部分内容" in result.content
        assert result.metadata["completed_count"] == 1
    
    def test_integrate_architecture(self, integrator):
        """测试整合架构设计"""
        blueprint = ProductBlueprint(
            product_type=ProductType.ARCHITECTURE_DESIGN,
            product_name="系统架构",
            requirements=["高可用", "高性能"]
        )
        task = AgentTask(task_name="架构设计")
        blueprint.task_sequence = [task]
        
        integrator.add_task_result(task.task_id, {"content": "架构方案"})
        
        result = integrator.integrate(blueprint)
        
        assert "系统架构" in result.content
        assert "架构方案" in result.content
    
    def test_clear_results(self, integrator):
        """测试清空结果"""
        integrator.add_task_result("task-1", {"content": "内容"})
        integrator.clear()
        
        assert len(integrator.task_results) == 0


class TestProductResult:
    """测试产物结果数据类"""
    
    def test_create_result(self):
        """测试创建产物结果"""
        result = ProductResult(
            blueprint_id="bp-001",
            product_type=ProductType.REQUIREMENT_DOC,
            content="# 需求文档\n\n内容...",
            format="markdown"
        )
        
        assert result.blueprint_id == "bp-001"
        assert result.format == "markdown"
        assert "需求文档" in result.content
    
    def test_result_to_dict(self):
        """测试结果转换为字典"""
        result = ProductResult(
            blueprint_id="bp-001",
            product_type=ProductType.SOLUTION_PPT,
            content="PPT内容",
            quality_score=0.85
        )
        
        data = result.to_dict()
        
        assert data["blueprint_id"] == "bp-001"
        assert data["product_type"] == "solution_ppt"
        assert data["quality_score"] == 0.85


class TestEnums:
    """测试枚举类"""
    
    def test_product_type_values(self):
        """测试产物类型枚举值"""
        assert ProductType.REQUIREMENT_DOC.value == "requirement_doc"
        assert ProductType.ARCHITECTURE_DESIGN.value == "architecture_design"
        assert ProductType.SOLUTION_PPT.value == "solution_ppt"
        assert ProductType.PROJECT_PLAN.value == "project_plan"
    
    def test_task_status_values(self):
        """测试任务状态枚举值"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
    
    def test_agent_role_values(self):
        """测试Agent角色枚举值"""
        assert AgentRole.ANALYST.value == "analyst"
        assert AgentRole.ARCHITECT.value == "architect"
        assert AgentRole.DEVELOPER.value == "developer"
        assert AgentRole.TESTER.value == "tester"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
