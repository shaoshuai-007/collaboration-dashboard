"""
V15.2 API路由 - Flask Blueprint
多智能体协同平台API接口层

包含:
- product_bp: 产物生成API
- quality_bp: 质量检查API
- template_bp: 模板管理API
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from flask import Blueprint, abort, jsonify, request, send_file

# 导入核心引擎
from product_engine import (
    ProductBlueprint,
    ProductBlueprintGenerator,
    ProductResult,
    ProductType,
    TaskStatus,
    ResultIntegrator,
)
from quality_engine import (
    CheckCategory,
    CheckLevel,
    CheckResult,
    ExpertReviewer,
    Feedback,
    FeedbackGenerator,
    ReviewReport,
    StandardChecker,
)


# ==================== 通用工具函数 ====================

def generate_task_id() -> str:
    """生成任务ID"""
    return str(uuid4())


def format_datetime(dt: datetime) -> str:
    """格式化时间为ISO格式"""
    return dt.isoformat() + "Z" if dt else None


def create_response(
    success: bool = True,
    data: Optional[Dict[str, Any]] = None,
    message: str = "",
    error_code: Optional[str] = None,
    status_code: int = 200
) -> tuple:
    """
    创建统一格式的API响应
    
    Args:
        success: 是否成功
        data: 响应数据
        message: 消息
        error_code: 错误码
        status_code: HTTP状态码
    
    Returns:
        Flask响应元组
    """
    response_body = {
        "success": success,
        "message": message,
        "timestamp": format_datetime(datetime.now())
    }
    
    if data:
        response_body["data"] = data
    
    if error_code:
        response_body["error_code"] = error_code
    
    return jsonify(response_body), status_code


def error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> tuple:
    """
    创建错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        details: 详细信息
        status_code: HTTP状态码
    
    Returns:
        Flask响应元组
    """
    response_body = {
        "code": code,
        "message": message,
        "request_id": generate_task_id()
    }
    
    if details:
        response_body["details"] = details
    
    return jsonify(response_body), status_code


# ==================== 内存存储（生产环境应替换为数据库/Redis） ====================

# 任务存储
_task_store: Dict[str, Dict[str, Any]] = {}

# 质量检查存储
_quality_check_store: Dict[str, Dict[str, Any]] = {}

# 产物存储
_product_store: Dict[str, ProductResult] = {}

# 报告存储
_report_store: Dict[str, ReviewReport] = {}


def get_task_store() -> Dict[str, Dict[str, Any]]:
    """获取任务存储"""
    return _task_store


def get_quality_check_store() -> Dict[str, Dict[str, Any]]:
    """获取质量检查存储"""
    return _quality_check_store


def get_product_store() -> Dict[str, ProductResult]:
    """获取产物存储"""
    return _product_store


def get_report_store() -> Dict[str, ReviewReport]:
    """获取报告存储"""
    return _report_store


# ==================== 产物类型映射 ====================

PRODUCT_TYPE_MAP = {
    "code": ProductType.CODE_MODULE,
    "document": ProductType.REQUIREMENT_DOC,
    "model": ProductType.ARCHITECTURE_DESIGN,
    "pipeline": ProductType.PROJECT_PLAN,
}

PRODUCT_TYPE_REVERSE_MAP = {v: k for k, v in PRODUCT_TYPE_MAP.items()}


# ==================== 模板数据（示例数据） ====================

TEMPLATES_DATA = [
    {
        "id": "tpl_code_fastapi_auth",
        "name": "FastAPI认证服务模板",
        "description": "包含JWT认证、用户管理、权限控制的FastAPI服务模板",
        "category": "code",
        "tags": ["python", "fastapi", "auth", "jwt"],
        "version": "2.1.0",
        "author": "九星智囊团",
        "rating": 4.8,
        "usage_count": 1256,
        "created_at": "2026-01-15T08:00:00Z",
        "updated_at": "2026-03-10T14:30:00Z",
        "parameters": [
            {"name": "project_name", "type": "string", "required": True, "description": "项目名称"},
            {"name": "author", "type": "string", "required": False, "default": "匿名", "description": "作者"},
            {"name": "version", "type": "string", "required": False, "default": "1.0.0", "description": "版本号"},
        ]
    },
    {
        "id": "tpl_code_nestjs_auth",
        "name": "NestJS认证服务模板",
        "description": "基于NestJS的企业级认证服务模板，支持OAuth2、RBAC",
        "category": "code",
        "tags": ["typescript", "nestjs", "auth", "oauth2"],
        "version": "1.5.0",
        "author": "九星智囊团",
        "rating": 4.6,
        "usage_count": 892,
        "created_at": "2026-02-01T09:00:00Z",
        "updated_at": "2026-03-12T10:00:00Z",
        "parameters": [
            {"name": "project_name", "type": "string", "required": True, "description": "项目名称"},
            {"name": "author", "type": "string", "required": False, "default": "匿名", "description": "作者"},
        ]
    },
    {
        "id": "tpl_document_api",
        "name": "API文档模板",
        "description": "标准API文档模板，符合OpenAPI 3.0规范",
        "category": "document",
        "tags": ["markdown", "api", "documentation"],
        "version": "1.2.0",
        "author": "九星智囊团",
        "rating": 4.5,
        "usage_count": 2341,
        "created_at": "2025-12-01T08:00:00Z",
        "updated_at": "2026-03-05T11:00:00Z",
        "parameters": [
            {"name": "api_name", "type": "string", "required": True, "description": "API名称"},
            {"name": "version", "type": "string", "required": False, "default": "1.0.0", "description": "API版本"},
        ]
    },
    {
        "id": "tpl_model_microservice",
        "name": "微服务架构模板",
        "description": "微服务架构设计模板，包含服务拆分、通信方式、部署方案",
        "category": "model",
        "tags": ["architecture", "microservice", "design"],
        "version": "1.0.0",
        "author": "九星智囊团",
        "rating": 4.7,
        "usage_count": 567,
        "created_at": "2026-02-15T08:00:00Z",
        "updated_at": "2026-03-08T09:00:00Z",
        "parameters": [
            {"name": "system_name", "type": "string", "required": True, "description": "系统名称"},
        ]
    },
    {
        "id": "tpl_pipeline_sprint",
        "name": "Sprint计划模板",
        "description": "敏捷开发Sprint计划模板，包含任务分解、时间规划",
        "category": "pipeline",
        "tags": ["agile", "sprint", "planning"],
        "version": "1.3.0",
        "author": "九星智囊团",
        "rating": 4.4,
        "usage_count": 1567,
        "created_at": "2025-11-20T08:00:00Z",
        "updated_at": "2026-03-01T14:00:00Z",
        "parameters": [
            {"name": "sprint_name", "type": "string", "required": True, "description": "Sprint名称"},
            {"name": "duration_weeks", "type": "integer", "required": False, "default": 2, "description": "持续周数"},
        ]
    },
]


# ==================== 产物生成API Blueprint ====================

product_bp = Blueprint('product', __name__, url_prefix='/api/v15.2/product')


@product_bp.route('/generate', methods=['POST'])
def generate_product():
    """
    触发产物生成
    
    请求体:
        - type: 产物类型 (code/document/model/pipeline)
        - name: 产物名称
        - description: 产物描述（可选）
        - config: 生成配置（可选）
        - input_data: 输入数据（可选）
        - tags: 标签列表（可选）
    
    返回:
        - task_id: 任务ID
        - status: 初始状态
        - message: 消息
        - status_url: 状态查询URL
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response(
                code="INVALID_FORMAT",
                message="请求体必须是有效的JSON格式",
                status_code=400
            )
        
        # 参数验证
        product_type = data.get('type')
        product_name = data.get('name')
        
        if not product_type:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: type",
                details={"field": "type", "reason": "产物类型不能为空"},
                status_code=400
            )
        
        if not product_name:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: name",
                details={"field": "name", "reason": "产物名称不能为空"},
                status_code=400
            )
        
        if product_type not in PRODUCT_TYPE_MAP:
            return error_response(
                code="PRODUCT_TYPE_NOT_SUPPORTED",
                message=f"不支持的产物类型: {product_type}",
                details={
                    "allowed_values": list(PRODUCT_TYPE_MAP.keys()),
                    "provided": product_type
                },
                status_code=400
            )
        
        # 生成任务ID
        task_id = generate_task_id()
        created_at = datetime.now()
        
        # 使用引擎生成蓝图
        generator = ProductBlueprintGenerator()
        
        # 提取需求
        requirements = []
        if data.get('input_data', {}).get('requirements'):
            req = data['input_data']['requirements']
            if isinstance(req, str):
                requirements = [req]
            elif isinstance(req, list):
                requirements = req
        
        if not requirements:
            requirements = [f"生成{product_name}"]
        
        try:
            blueprint = generator.generate(
                product_type=PRODUCT_TYPE_MAP[product_type],
                product_name=product_name,
                requirements=requirements,
                description=data.get('description', ''),
                constraints=data.get('config', {}),
                metadata={
                    "tags": data.get('tags', []),
                    "config": data.get('config', {}),
                    "input_data": data.get('input_data', {})
                }
            )
        except ValueError as e:
            return error_response(
                code="INVALID_PARAMETER",
                message=str(e),
                status_code=400
            )
        
        # 存储任务信息
        task_store = get_task_store()
        task_store[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "stage": "initialized",
            "message": "产物生成任务已提交",
            "created_at": created_at,
            "started_at": None,
            "completed_at": None,
            "blueprint": blueprint,
            "product_type": product_type,
            "product_name": product_name,
            "config": data.get('config', {}),
            "input_data": data.get('input_data', {}),
            "error": None
        }
        
        # 模拟异步处理（实际应使用Celery等任务队列）
        _process_product_generation(task_id)
        
        return create_response(
            success=True,
            data={
                "task_id": task_id,
                "status": "pending",
                "message": "产物生成任务已提交",
                "created_at": format_datetime(created_at),
                "estimated_duration": 900,
                "status_url": f"/api/v15.2/product/status/{task_id}"
            },
            message="产物生成任务已提交",
            status_code=202
        )
        
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"服务器内部错误: {str(e)}",
            status_code=500
        )


@product_bp.route('/status/<task_id>', methods=['GET'])
def get_product_status(task_id: str):
    """
    查询生成状态
    
    路径参数:
        - task_id: 任务ID
    
    返回:
        - task_id: 任务ID
        - status: 任务状态
        - progress: 进度百分比
        - stage: 当前阶段
        - message: 状态消息
    """
    task_store = get_task_store()
    
    if task_id not in task_store:
        return error_response(
            code="TASK_NOT_FOUND",
            message=f"任务不存在: {task_id}",
            details={"task_id": task_id},
            status_code=404
        )
    
    task = task_store[task_id]
    
    response_data = {
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task["progress"],
        "stage": task["stage"],
        "message": task["message"],
        "created_at": format_datetime(task["created_at"]),
        "started_at": format_datetime(task["started_at"]) if task["started_at"] else None,
        "completed_at": format_datetime(task["completed_at"]) if task["completed_at"] else None,
    }
    
    # 如果已完成，添加下载链接
    if task["status"] == "completed":
        product_store = get_product_store()
        if task_id in product_store:
            response_data["result"] = {
                "download_url": f"/api/v15.2/product/download/{task_id}",
                "file_size": len(product_store[task_id].content),
                "checksum": f"sha256:{hashlib.sha256(product_store[task_id].content.encode()).hexdigest()[:16]}"
            }
    
    # 如果失败，添加错误信息
    if task["status"] == "failed" and task.get("error"):
        response_data["error"] = task["error"]
    
    return create_response(
        success=True,
        data=response_data,
        status_code=200
    )


@product_bp.route('/download/<task_id>', methods=['GET'])
def download_product(task_id: str):
    """
    下载产物
    
    路径参数:
        - task_id: 任务ID
    
    查询参数:
        - format: 输出格式 (zip/tar.gz/raw)
        - include_metadata: 是否包含元数据文件
    
    返回:
        产物文件（二进制流）
    """
    task_store = get_task_store()
    
    if task_id not in task_store:
        return error_response(
            code="TASK_NOT_FOUND",
            message=f"任务不存在: {task_id}",
            status_code=404
        )
    
    task = task_store[task_id]
    
    if task["status"] != "completed":
        return error_response(
            code="TASK_NOT_COMPLETED",
            message=f"产物生成任务尚未完成，当前状态: {task['status']}",
            details={
                "task_id": task_id,
                "current_status": task["status"]
            },
            status_code=409
        )
    
    product_store = get_product_store()
    if task_id not in product_store:
        return error_response(
            code="NOT_FOUND",
            message="产物文件不存在",
            status_code=404
        )
    
    product = product_store[task_id]
    output_format = request.args.get('format', 'zip')
    include_metadata = request.args.get('include_metadata', 'true').lower() == 'true'
    
    try:
        if output_format == 'raw':
            # 返回原始内容
            return product.content, 200, {
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition': f'attachment; filename="{task["product_name"]}.md"'
            }
        
        elif output_format in ('zip', 'tar.gz'):
            # 创建ZIP文件
            buffer = io.BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 添加主产物文件
                zf.writestr(
                    f"{task['product_name']}/content.md",
                    product.content
                )
                
                # 添加元数据
                if include_metadata:
                    metadata = {
                        "product_id": product.result_id,
                        "product_name": task["product_name"],
                        "product_type": task["product_type"],
                        "quality_score": product.quality_score,
                        "created_at": format_datetime(product.created_at),
                        "task_id": task_id
                    }
                    zf.writestr(
                        f"{task['product_name']}/metadata.json",
                        json.dumps(metadata, ensure_ascii=False, indent=2)
                    )
            
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f"product_{task_id}.zip"
            )
        
        else:
            return error_response(
                code="INVALID_PARAMETER",
                message=f"不支持的格式: {output_format}",
                details={"allowed_values": ["zip", "tar.gz", "raw"]},
                status_code=400
            )
            
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"下载失败: {str(e)}",
            status_code=500
        )


def _process_product_generation(task_id: str) -> None:
    """
    处理产物生成（模拟异步处理）
    
    在实际应用中，这应该是一个异步任务（如Celery任务）
    这里简化为同步处理
    """
    task_store = get_task_store()
    product_store = get_product_store()
    
    if task_id not in task_store:
        return
    
    task = task_store[task_id]
    blueprint = task["blueprint"]
    
    try:
        # 更新状态为处理中
        task["status"] = "processing"
        task["started_at"] = datetime.now()
        task["stage"] = "generating_blueprint"
        task["message"] = "正在生成产物蓝图..."
        task["progress"] = 20
        
        # 创建结果整合器
        integrator = ResultIntegrator()
        
        # 模拟Agent任务执行
        task["stage"] = "executing_agents"
        task["message"] = "正在执行Agent任务..."
        task["progress"] = 40
        
        for agent_task in blueprint.task_sequence:
            # 模拟任务完成
            integrator.add_task_result(
                agent_task.task_id,
                {"content": f"## {agent_task.task_name}\n\n已完成任务执行，生成内容如下：\n\n这是一个模拟的产物内容。"}
            )
        
        # 整合结果
        task["stage"] = "integrating_results"
        task["message"] = "正在整合结果..."
        task["progress"] = 80
        
        result = integrator.integrate(blueprint, format="markdown")
        
        # 存储产物
        product_store[task_id] = result
        
        # 更新任务状态
        task["status"] = "completed"
        task["stage"] = "completed"
        task["message"] = "产物生成完成"
        task["progress"] = 100
        task["completed_at"] = datetime.now()
        
    except Exception as e:
        task["status"] = "failed"
        task["stage"] = "failed"
        task["message"] = f"产物生成失败: {str(e)}"
        task["error"] = {
            "code": "PRODUCT_GENERATION_FAILED",
            "message": str(e)
        }
        task["completed_at"] = datetime.now()


# ==================== 质量检查API Blueprint ====================

quality_bp = Blueprint('quality', __name__, url_prefix='/api/v15.2/quality')


@quality_bp.route('/check', methods=['POST'])
def run_quality_check():
    """
    执行质量检查
    
    请求体:
        - target_type: 目标类型 (product/file/directory)
        - target_id: 目标ID或路径
        - check_types: 检查类型列表
        - options: 检查选项（可选）
    
    返回:
        - check_id: 检查任务ID
        - status: 状态
        - message: 消息
        - report_url: 报告URL
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response(
                code="INVALID_FORMAT",
                message="请求体必须是有效的JSON格式",
                status_code=400
            )
        
        # 参数验证
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        check_types = data.get('check_types', [])
        
        if not target_type:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: target_type",
                status_code=400
            )
        
        if not target_id:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: target_id",
                status_code=400
            )
        
        if not check_types:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: check_types",
                status_code=400
            )
        
        valid_check_types = ['code_quality', 'security', 'performance', 'compliance', 'full']
        for ct in check_types:
            if ct not in valid_check_types:
                return error_response(
                    code="CHECK_TYPE_NOT_SUPPORTED",
                    message=f"不支持的检查类型: {ct}",
                    details={"allowed_values": valid_check_types},
                    status_code=400
                )
        
        # 生成检查ID
        check_id = generate_task_id()
        created_at = datetime.now()
        
        # 获取目标内容
        content = ""
        product_name = target_id
        
        product_store = get_product_store()
        if target_id in product_store:
            content = product_store[target_id].content
            product_name = product_store[target_id].metadata.get("product_name", target_id)
        else:
            # 尝试从任务存储获取
            task_store = get_task_store()
            if target_id in task_store:
                # 模拟内容
                content = f"# {task_store[target_id]['product_name']}\n\n这是一个模拟的产物内容用于质量检查。"
                product_name = task_store[target_id]['product_name']
        
        # 存储检查任务
        quality_check_store = get_quality_check_store()
        quality_check_store[check_id] = {
            "check_id": check_id,
            "status": "pending",
            "target_id": target_id,
            "target_type": target_type,
            "check_types": check_types,
            "options": data.get('options', {}),
            "created_at": created_at,
            "started_at": None,
            "completed_at": None,
            "content": content,
            "product_name": product_name
        }
        
        # 执行质量检查
        _process_quality_check(check_id)
        
        return create_response(
            success=True,
            data={
                "check_id": check_id,
                "status": "pending",
                "message": "质量检查任务已提交",
                "created_at": format_datetime(created_at),
                "estimated_duration": 300,
                "report_url": f"/api/v15.2/quality/report/{check_id}"
            },
            message="质量检查任务已提交",
            status_code=202
        )
        
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"服务器内部错误: {str(e)}",
            status_code=500
        )


@quality_bp.route('/report/<check_id>', methods=['GET'])
def get_quality_report(check_id: str):
    """
    获取质量报告
    
    路径参数:
        - check_id: 检查任务ID
    
    查询参数:
        - format: 报告格式 (json/html/pdf/markdown)
        - include_details: 是否包含详细问题描述
    
    返回:
        质量报告详情
    """
    quality_check_store = get_quality_check_store()
    
    if check_id not in quality_check_store:
        return error_response(
            code="NOT_FOUND",
            message=f"检查任务不存在: {check_id}",
            status_code=404
        )
    
    check_task = quality_check_store[check_id]
    
    if check_task["status"] != "completed":
        return error_response(
            code="REPORT_NOT_READY",
            message=f"报告尚未生成，当前状态: {check_task['status']}",
            details={
                "check_id": check_id,
                "current_status": check_task["status"]
            },
            status_code=409
        )
    
    report_store = get_report_store()
    if check_id not in report_store:
        return error_response(
            code="NOT_FOUND",
            message="质量报告不存在",
            status_code=404
        )
    
    report = report_store[check_id]
    output_format = request.args.get('format', 'json')
    include_details = request.args.get('include_details', 'true').lower() == 'true'
    
    try:
        if output_format == 'json':
            response_data = {
                "check_id": check_id,
                "target_id": check_task["target_id"],
                "status": "completed",
                "summary": {
                    "total_issues": len(report.check_results),
                    "critical": len([r for r in report.check_results if r.level == CheckLevel.ERROR and not r.passed]),
                    "error": len([r for r in report.check_results if r.level == CheckLevel.ERROR]),
                    "warning": len([r for r in report.check_results if r.level == CheckLevel.WARNING]),
                    "info": len([r for r in report.check_results if r.level == CheckLevel.INFO]),
                    "score": round(report.overall_score * 100, 1)
                },
                "passed": report.passed,
                "reviewed_at": format_datetime(report.reviewed_at),
                "recommendations": report.recommendations
            }
            
            if include_details:
                response_data["issues"] = [
                    {
                        "id": r.check_id,
                        "type": r.check_name,
                        "severity": r.level.value,
                        "category": r.category.value,
                        "title": r.message,
                        "description": r.message,
                        "location": r.location,
                        "suggestion": r.suggestion,
                        "passed": r.passed
                    }
                    for r in report.check_results
                ]
            
            return create_response(
                success=True,
                data=response_data,
                status_code=200
            )
        
        elif output_format == 'markdown':
            feedback_gen = FeedbackGenerator()
            feedback = feedback_gen.generate(report)
            return feedback.to_markdown(), 200, {
                'Content-Type': 'text/markdown; charset=utf-8'
            }
        
        else:
            return error_response(
                code="INVALID_PARAMETER",
                message=f"不支持的报告格式: {output_format}",
                details={"allowed_values": ["json", "html", "pdf", "markdown"]},
                status_code=400
            )
            
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"获取报告失败: {str(e)}",
            status_code=500
        )


def _process_quality_check(check_id: str) -> None:
    """
    处理质量检查（模拟异步处理）
    """
    quality_check_store = get_quality_check_store()
    report_store = get_report_store()
    
    if check_id not in quality_check_store:
        return
    
    check_task = quality_check_store[check_id]
    
    try:
        # 更新状态
        check_task["status"] = "processing"
        check_task["started_at"] = datetime.now()
        
        # 执行标准检查
        checker = StandardChecker(strict_mode=False)
        report = checker.check(
            content=check_task["content"],
            context={
                "product_id": check_task["target_id"],
                "product_name": check_task["product_name"],
                "product_type": check_task["target_type"]
            }
        )
        
        # 如果包含full或security，执行专家评审
        if "full" in check_task["check_types"] or "security" in check_task["check_types"]:
            expert_reviewer = ExpertReviewer(domain="软件工程")
            expert_report = expert_reviewer.review(
                content=check_task["content"],
                context={
                    "product_id": check_task["target_id"],
                    "product_name": check_task["product_name"]
                }
            )
            
            # 合并结果
            for result in expert_report.check_results:
                report.add_result(result)
            
            report.calculate_overall_score()
        
        # 存储报告
        report_store[check_id] = report
        
        # 更新任务状态
        check_task["status"] = "completed"
        check_task["completed_at"] = datetime.now()
        
    except Exception as e:
        check_task["status"] = "failed"
        check_task["completed_at"] = datetime.now()
        check_task["error"] = str(e)


# ==================== 模板管理API Blueprint ====================

template_bp = Blueprint('template', __name__, url_prefix='/api/v15.2/templates')


@template_bp.route('', methods=['GET'])
def list_templates():
    """
    获取模板列表
    
    查询参数:
        - category: 模板分类 (code/document/model/pipeline/all)
        - search: 搜索关键词
        - tags: 标签过滤（逗号分隔）
        - page: 页码
        - page_size: 每页数量
        - sort: 排序字段
        - order: 排序方向
    
    返回:
        模板列表
    """
    try:
        # 获取查询参数
        category = request.args.get('category', 'all')
        search = request.args.get('search', '').lower()
        tags = request.args.get('tags', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        sort = request.args.get('sort', 'usage_count')
        order = request.args.get('order', 'desc')
        
        # 过滤模板
        filtered_templates = TEMPLATES_DATA.copy()
        
        # 按分类过滤
        if category and category != 'all':
            filtered_templates = [
                t for t in filtered_templates
                if t['category'] == category
            ]
        
        # 按关键词搜索
        if search:
            filtered_templates = [
                t for t in filtered_templates
                if search in t['name'].lower() or search in t['description'].lower()
            ]
        
        # 按标签过滤
        if tags:
            tag_list = [tag.strip().lower() for tag in tags.split(',')]
            filtered_templates = [
                t for t in filtered_templates
                if any(tag in [t.lower() for t in t['tags']] for tag in tag_list)
            ]
        
        # 排序
        reverse = order == 'desc'
        if sort in ['name', 'created_at', 'usage_count', 'rating']:
            filtered_templates.sort(key=lambda x: x.get(sort, 0), reverse=reverse)
        
        # 分页
        total = len(filtered_templates)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        paginated_templates = filtered_templates[start:end]
        
        return create_response(
            success=True,
            data={
                "templates": paginated_templates,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages
                }
            },
            status_code=200
        )
        
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"服务器内部错误: {str(e)}",
            status_code=500
        )


@template_bp.route('/apply', methods=['POST'])
def apply_template():
    """
    应用模板
    
    请求体:
        - template_id: 模板ID
        - mode: 应用模式 (create/merge/override)
        - target_product_id: 目标产物ID（merge/override模式必填）
        - parameters: 模板参数
        - options: 应用选项
    
    返回:
        任务信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response(
                code="INVALID_FORMAT",
                message="请求体必须是有效的JSON格式",
                status_code=400
            )
        
        # 参数验证
        template_id = data.get('template_id')
        mode = data.get('mode')
        parameters = data.get('parameters', {})
        options = data.get('options', {})
        
        if not template_id:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: template_id",
                status_code=400
            )
        
        if not mode:
            return error_response(
                code="MISSING_PARAMETER",
                message="缺少必填参数: mode",
                status_code=400
            )
        
        if mode not in ['create', 'merge', 'override']:
            return error_response(
                code="INVALID_PARAMETER",
                message=f"不支持的应用模式: {mode}",
                details={"allowed_values": ["create", "merge", "override"]},
                status_code=400
            )
        
        # 查找模板
        template = None
        for t in TEMPLATES_DATA:
            if t['id'] == template_id:
                template = t
                break
        
        if not template:
            return error_response(
                code="TEMPLATE_NOT_FOUND",
                message=f"模板不存在: {template_id}",
                status_code=404
            )
        
        # merge/override模式需要target_product_id
        if mode in ['merge', 'override']:
            target_product_id = data.get('target_product_id')
            if not target_product_id:
                return error_response(
                    code="MISSING_PARAMETER",
                    message=f"{mode}模式需要提供target_product_id",
                    status_code=400
                )
            
            # 验证目标产物存在
            product_store = get_product_store()
            task_store = get_task_store()
            
            if target_product_id not in product_store and target_product_id not in task_store:
                return error_response(
                    code="NOT_FOUND",
                    message=f"目标产物不存在: {target_product_id}",
                    status_code=404
                )
        
        # 生成任务ID
        task_id = generate_task_id()
        created_at = datetime.now()
        
        # 存储任务
        task_store = get_task_store()
        task_store[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "template_id": template_id,
            "template_name": template['name'],
            "mode": mode,
            "parameters": parameters,
            "options": options,
            "created_at": created_at,
            "completed_at": None
        }
        
        # 模拟处理
        result_product_id = None
        if mode == 'create':
            # 创建新产物
            result_product_id = generate_task_id()
            product_store = get_product_store()
            product_store[result_product_id] = ProductResult(
                result_id=result_product_id,
                product_type=PRODUCT_TYPE_MAP.get(template['category'], ProductType.CODE_MODULE),
                content=f"# {parameters.get('project_name', template['name'])}\n\n基于模板 {template['name']} 生成的产物。\n\n参数：\n```json\n{json.dumps(parameters, ensure_ascii=False, indent=2)}\n```",
                format="markdown",
                metadata={
                    "template_id": template_id,
                    "template_name": template['name']
                }
            )
            task_store[task_id]["result_product_id"] = result_product_id
        
        # 更新任务状态
        task_store[task_id]["status"] = "completed"
        task_store[task_id]["completed_at"] = datetime.now()
        
        # 更新模板使用次数
        for t in TEMPLATES_DATA:
            if t['id'] == template_id:
                t['usage_count'] += 1
                break
        
        return create_response(
            success=True,
            data={
                "task_id": task_id,
                "status": "completed",
                "message": "模板应用完成",
                "created_at": format_datetime(created_at),
                "result_product_id": result_product_id,
                "status_url": f"/api/v15.2/product/status/{task_id}"
            },
            message="模板应用完成",
            status_code=202
        )
        
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"服务器内部错误: {str(e)}",
            status_code=500
        )


# ==================== 注册Blueprints到应用 ====================

def register_api_routes(app):
    """
    注册API路由到Flask应用
    
    Args:
        app: Flask应用实例
    
    使用示例:
        from flask import Flask
        from api_routes import register_api_routes
        
        app = Flask(__name__)
        register_api_routes(app)
    """
    app.register_blueprint(product_bp)
    app.register_blueprint(quality_bp)
    app.register_blueprint(template_bp)


# ==================== 错误处理器 ====================

def register_error_handlers(app):
    """
    注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response(
            code="BAD_REQUEST",
            message="请求格式错误",
            status_code=400
        )
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response(
            code="NOT_FOUND",
            message="请求的资源不存在",
            status_code=404
        )
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response(
            code="INTERNAL_ERROR",
            message="服务器内部错误",
            status_code=500
        )


# ==================== 主程序入口 ====================

if __name__ == '__main__':
    from flask import Flask
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 注册API路由
    register_api_routes(app)
    register_error_handlers(app)
    
    # 添加根路由
    @app.route('/')
    def index():
        return create_response(
            success=True,
            data={
                "name": "多智能体协同平台 V15.2 API",
                "version": "15.2.0",
                "endpoints": [
                    "/api/v15.2/product/generate",
                    "/api/v15.2/product/status/<task_id>",
                    "/api/v15.2/product/download/<task_id>",
                    "/api/v15.2/quality/check",
                    "/api/v15.2/quality/report/<check_id>",
                    "/api/v15.2/templates",
                    "/api/v15.2/templates/apply"
                ]
            },
            message="多智能体协同平台 V15.2 API 服务运行中"
        )
    
    # 启动服务
    print("=" * 60)
    print("多智能体协同平台 V15.2 API")
    print("=" * 60)
    print("服务启动中...")
    print("API文档: http://localhost:5000/")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
