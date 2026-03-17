#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能调度API服务
- 提供HTTP接口供测试
- 端口：8765

Author: 南乔
Date: 2026-03-14
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import sys
import os

# 添加路径
sys.path.insert(0, '/root/.openclaw/workspace/03_输出成果')

from smart_scheduler import smart_execute, SmartScheduler

# 创建应用
app = FastAPI(
    title="智能调度API",
    description="意图识别 → 技能调度 → 文档生成",
    version="13.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局调度器
scheduler = SmartScheduler()


# ==================== 请求模型 ====================
class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    full_workflow: bool = False
    discussion_data: Optional[Dict] = None


class BatchRequest(BaseModel):
    """批量任务请求"""
    tasks: List[str]


# ==================== API端点 ====================
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "智能调度API",
        "version": "13.0",
        "status": "running",
        "endpoints": {
            "/execute": "智能执行（自动识别意图）",
            "/recognize": "仅识别意图（不执行）",
            "/batch": "批量执行",
            "/skills": "查看技能列表",
            "/task-types": "查看任务类型"
        }
    }


@app.post("/execute")
async def execute_task(request: TaskRequest):
    """
    智能执行任务
    
    - 自动识别意图
    - 自动选择技能组合
    - 自动生成文档
    """
    try:
        result = smart_execute(
            task_input=request.task,
            discussion_data=request.discussion_data,
            full_workflow=request.full_workflow
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/recognize")
async def recognize_intent(request: TaskRequest):
    """
    仅识别意图（不执行）
    
    返回：
    - 任务类型
    - 置信度
    - 推荐技能
    """
    try:
        result = scheduler.scheduler.process(request.task)
        
        # 获取技能组合
        task_code = result['task_code']
        from smart_scheduler import TASK_SKILL_MAPPING
        skill_config = TASK_SKILL_MAPPING.get(task_code, {})
        
        return {
            "success": True,
            "data": {
                "task_code": result['task_code'],
                "task_name": result['task_name'],
                "category": result['category'],
                "confidence": result['confidence'],
                "complexity": result['complexity'],
                "need_confirm": result['need_confirm'],
                "recommended_skills": skill_config.get('skills', []),
                "description": skill_config.get('description', '')
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/batch")
async def batch_execute(request: BatchRequest):
    """
    批量执行任务
    """
    results = []
    for task in request.tasks:
        try:
            result = smart_execute(task)
            results.append({
                "task": task,
                "success": True,
                "data": result
            })
        except Exception as e:
            results.append({
                "task": task,
                "success": False,
                "error": str(e)
            })
    
    return {
        "total": len(results),
        "results": results
    }


@app.get("/skills")
async def list_skills():
    """查看技能列表"""
    return {
        "skills": [
            {"id": "caiwei", "name": "采薇", "description": "需求文档生成", "output": ".docx"},
            {"id": "zhijin", "name": "织锦", "description": "思维导图生成", "output": ".html"},
            {"id": "zhutai", "name": "筑台", "description": "方案举措生成", "output": ".xlsx"},
            {"id": "chengcai", "name": "呈彩", "description": "方案PPT生成", "output": ".pptx"},
            {"id": "gongchi", "name": "工尺", "description": "详细设计生成", "output": ".docx"},
            {"id": "yuheng", "name": "玉衡", "description": "项目管控生成", "output": ".xlsx"}
        ]
    }


@app.get("/task-types")
async def list_task_types():
    """查看任务类型"""
    from intent_scheduler import TASK_TYPES
    
    task_list = []
    for code, task in TASK_TYPES.items():
        task_list.append({
            "code": code,
            "name": task.name,
            "category": task.category.value,
            "description": task.description
        })
    
    return {
        "total": len(task_list),
        "task_types": task_list
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": str(os.popen('date').read().strip())}


# ==================== 启动 ====================
if __name__ == "__main__":
    print("=" * 70)
    print("智能调度API服务")
    print("=" * 70)
    print(f"服务地址：http://localhost:8765")
    print(f"API文档：http://localhost:8765/docs")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8765)
