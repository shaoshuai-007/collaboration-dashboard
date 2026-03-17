#!/usr/bin/env python3
"""
南乔智能调度系统 V1.0
实现精准Agent调度和任务分解
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class NanqiaoSmartScheduler:
    """南乔的智能调度系统"""

    def __init__(self):
        self.name = "南乔智能调度系统"
        self.version = "1.0.0"
        self.workspace = Path("/root/.openclaw/workspace/调度日志")
        self.workspace.mkdir(exist_ok=True)

        # Agent能力矩阵
        self.agent_capabilities = {
            "采薇": {
                "skills": ["需求分析", "文档撰写", "用户故事"],
                "efficiency": 1800,
                "availability": 0.9,
                "specialization": "需求分析"
            },
            "织锦": {
                "skills": ["架构设计", "代码生成", "API设计"],
                "efficiency": 7200,
                "availability": 0.85,
                "specialization": "架构设计"
            },
            "呈彩": {
                "skills": ["PPT制作", "方案设计", "Demo开发"],
                "efficiency": 10,
                "availability": 0.9,
                "specialization": "方案设计"
            },
            "工尺": {
                "skills": ["接口设计", "数据库设计", "系统设计"],
                "efficiency": 5,
                "availability": 0.9,
                "specialization": "系统设计"
            },
            "玉衡": {
                "skills": ["项目管理", "甘特图", "RACI矩阵"],
                "efficiency": 5,
                "availability": 0.85,
                "specialization": "项目管理"
            },
            "筑台": {
                "skills": ["售前支持", "报价单", "销售话术"],
                "efficiency": 5,
                "availability": 0.9,
                "specialization": "售前支持"
            },
            "折桂": {
                "skills": ["知识管理", "情报采集", "智能摘要"],
                "efficiency": 5,
                "availability": 0.9,
                "specialization": "知识管理"
            },
            "扶摇": {
                "skills": ["任务协调", "团队调度", "进度监控"],
                "efficiency": 3,
                "availability": 0.95,
                "specialization": "任务协调"
            },
            "南乔": {
                "skills": ["信息检索", "文档生成", "任务分解", "决策建议"],
                "efficiency": 2,
                "availability": 0.95,
                "specialization": "用户助手"
            }
        }

        # 任务类型映射
        self.task_mapping = {
            "需求分析": {
                "keywords": ["需求", "分析", "用户故事", "验收标准"],
                "lead": "采薇",
                "support": ["织锦", "筑台"],
                "complexity": "medium"
            },
            "架构设计": {
                "keywords": ["架构", "设计", "技术选型"],
                "lead": "织锦",
                "support": ["工尺", "呈彩"],
                "complexity": "high"
            },
            "方案设计": {
                "keywords": ["方案", "PPT", "汇报", "演示"],
                "lead": "呈彩",
                "support": ["织锦", "筑台"],
                "complexity": "medium"
            },
            "系统设计": {
                "keywords": ["接口", "数据库", "API"],
                "lead": "工尺",
                "support": ["织锦", "玉衡"],
                "complexity": "medium"
            },
            "项目管理": {
                "keywords": ["计划", "进度", "甘特图", "风险"],
                "lead": "玉衡",
                "support": ["折桂", "扶摇"],
                "complexity": "medium"
            },
            "售前支持": {
                "keywords": ["报价", "竞品", "客户", "销售"],
                "lead": "筑台",
                "support": ["采薇", "呈彩"],
                "complexity": "low"
            },
            "知识管理": {
                "keywords": ["知识", "文档", "分类", "搜索"],
                "lead": "折桂",
                "support": ["南乔"],
                "complexity": "low"
            },
            "全流程": {
                "keywords": ["全流程", "端到端", "完整"],
                "lead": "扶摇",
                "support": ["采薇", "织锦", "呈彩", "工尺", "玉衡"],
                "complexity": "high"
            },
            "信息检索": {
                "keywords": ["查找", "搜索", "获取", "检索"],
                "lead": "南乔",
                "support": [],
                "complexity": "low"
            }
        }

    def analyze_intent(self, task_description: str) -> Dict:
        """
        意图识别
        准确率目标：≥95%
        """
        result = {
            "task_id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "input": task_description,
            "analyzed_at": datetime.now().isoformat(),
            "intent": None,
            "confidence": 0.0,
            "keywords_matched": []
        }

        # 关键词匹配
        max_matches = 0
        best_intent = None

        for intent, config in self.task_mapping.items():
            matches = 0
            matched_kw = []

            for kw in config["keywords"]:
                if kw in task_description:
                    matches += 1
                    matched_kw.append(kw)

            if matches > max_matches:
                max_matches = matches
                best_intent = intent
                result["keywords_matched"] = matched_kw

        # 计算置信度
        if max_matches > 0:
            result["intent"] = best_intent
            result["confidence"] = min(0.7 + max_matches * 0.1, 0.98)
        else:
            # 默认意图
            result["intent"] = "信息检索"
            result["confidence"] = 0.5

        return result

    def assess_complexity(self, task_description: str, intent: str) -> str:
        """
        复杂度评估
        """
        # 基础复杂度
        base_complexity = self.task_mapping.get(intent, {}).get("complexity", "medium")

        # 根据关键词调整
        high_indicators = ["复杂", "大型", "企业级", "多个", "全流程"]
        low_indicators = ["简单", "快速", "小型", "单个"]

        for indicator in high_indicators:
            if indicator in task_description:
                return "high"

        for indicator in low_indicators:
            if indicator in task_description:
                return "low"

        return base_complexity

    def assign_agents(self, intent: str, complexity: str) -> Dict:
        """
        Agent分配
        准确率目标：≥90%
        """
        mapping = self.task_mapping.get(intent, {"lead": "南乔", "support": []})

        assignment = {
            "lead": mapping["lead"],
            "support": mapping.get("support", []),
            "assignment_reason": f"根据任务类型【{intent}】和复杂度【{complexity}】自动分配"
        }

        # 根据复杂度调整
        if complexity == "high":
            # 高复杂度任务增加支持Agent
            if assignment["lead"] not in ["扶摇", "南乔"]:
                assignment["support"].append("扶摇")
        elif complexity == "low":
            # 低复杂度任务减少支持Agent
            assignment["support"] = assignment["support"][:1] if assignment["support"] else []

        return assignment

    def generate_workflow(self, intent: str, complexity: str) -> List[Dict]:
        """
        工作流生成
        """
        # 基础工作流
        base_workflows = {
            "需求分析": [
                {"step": 1, "task": "需求调研", "agent": "采薇", "duration": "2天"},
                {"step": 2, "task": "需求分析", "agent": "采薇", "duration": "1天"},
                {"step": 3, "task": "文档撰写", "agent": "采薇", "duration": "1天"},
                {"step": 4, "task": "需求评审", "agent": "全团队", "duration": "0.5天"}
            ],
            "架构设计": [
                {"step": 1, "task": "架构规划", "agent": "织锦", "duration": "1天"},
                {"step": 2, "task": "技术选型", "agent": "织锦", "duration": "1天"},
                {"step": 3, "task": "架构设计", "agent": "织锦", "duration": "2天"},
                {"step": 4, "task": "架构评审", "agent": "全团队", "duration": "0.5天"}
            ],
            "方案设计": [
                {"step": 1, "task": "方案规划", "agent": "呈彩", "duration": "0.5天"},
                {"step": 2, "task": "方案编写", "agent": "呈彩", "duration": "1天"},
                {"step": 3, "task": "PPT制作", "agent": "呈彩", "duration": "1天"},
                {"step": 4, "task": "方案评审", "agent": "全团队", "duration": "0.5天"}
            ],
            "信息检索": [
                {"step": 1, "task": "信息检索", "agent": "南乔", "duration": "5分钟"},
                {"step": 2, "task": "内容整理", "agent": "南乔", "duration": "5分钟"},
                {"step": 3, "task": "文档生成", "agent": "南乔", "duration": "3分钟"}
            ]
        }

        workflow = base_workflows.get(intent, [
            {"step": 1, "task": "任务执行", "agent": "南乔", "duration": "待评估"}
        ])

        # 根据复杂度调整
        if complexity == "high":
            workflow.append({"step": len(workflow) + 1, "task": "深度评审", "agent": "全团队", "duration": "1天"})
            workflow.append({"step": len(workflow) + 1, "task": "多轮迭代", "agent": "相关Agent", "duration": "2天"})

        return workflow

    def smart_schedule(self, task_description: str) -> Dict:
        """
        智能调度主流程
        """
        # 1. 意图识别
        intent_result = self.analyze_intent(task_description)

        # 2. 复杂度评估
        complexity = self.assess_complexity(task_description, intent_result["intent"])

        # 3. Agent分配
        assignment = self.assign_agents(intent_result["intent"], complexity)

        # 4. 工作流生成
        workflow = self.generate_workflow(intent_result["intent"], complexity)

        # 5. 汇总结果
        result = {
            "schedule_id": f"SCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "input": task_description,
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "complexity": complexity,
            "assignment": assignment,
            "workflow": workflow,
            "estimated_duration": self._calculate_duration(workflow)
        }

        # 6. 保存日志
        self._save_schedule_log(result)

        return result

    def _calculate_duration(self, workflow: List[Dict]) -> str:
        """计算预估时长"""
        # 简化计算，实际应根据任务类型更精确
        return f"{len(workflow)} 步骤"

    def _save_schedule_log(self, result: Dict):
        """保存调度日志"""
        log_file = self.workspace / f"{result['schedule_id']}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


# 演示
if __name__ == "__main__":
    scheduler = NanqiaoSmartScheduler()

    print("=" * 60)
    print("🌿 南乔智能调度系统 V1.0 演示")
    print("=" * 60)

    # 测试案例
    test_cases = [
        "帮我完成湖北电信AI智能配案系统的需求分析和架构设计",
        "搜索AI技术趋势并生成报告",
        "制作项目汇报PPT",
        "简单查询用户信息"
    ]

    for task in test_cases:
        print(f"\n📝 任务: {task}")
        result = scheduler.smart_schedule(task)

        print(f"   意图: {result['intent']} (置信度: {result['confidence']:.0%})")
        print(f"   复杂度: {result['complexity']}")
        print(f"   主导: {result['assignment']['lead']}")
        print(f"   协助: {', '.join(result['assignment']['support']) if result['assignment']['support'] else '无'}")
        print(f"   工作流: {len(result['workflow'])} 步骤")
