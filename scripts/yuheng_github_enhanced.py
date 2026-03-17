#!/usr/bin/env python3
"""
玉衡 - 项目管理增强模块
集成github技能，管理项目任务和进度
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class YuhengGithubEnhanced:
    """玉衡的项目管理增强类"""

    def __init__(self, github_token: str = None):
        self.name = "玉衡"
        self.role = "项目经理"
        self.skill = "github"
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "${GITHUB_TOKEN}")
        self.github_user = "shaoshuai-007"
        self.github_repo = "project-management"

    def create_project_board(self, project_name: str, columns: list) -> dict:
        """
        创建项目看板

        Args:
            project_name: 项目名称
            columns: 列列表

        Returns:
            项目看板
        """
        board = {
            "name": project_name,
            "created_at": datetime.now().isoformat(),
            "columns": []
        }

        for col in columns:
            column = {
                "name": col,
                "tasks": []
            }
            board["columns"].append(column)

        return board

    def create_task(self, title: str, description: str, assignee: str, priority: str, due_date: str) -> dict:
        """
        创建任务

        Args:
            title: 标题
            description: 描述
            assignee: 负责人
            priority: 优先级
            due_date: 截止日期

        Returns:
            任务对象
        """
        task = {
            "id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "assignee": assignee,
            "priority": priority,
            "status": "待开始",
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "subtasks": [],
            "comments": []
        }

        return task

    def generate_gantt_chart(self, tasks: list) -> str:
        """
        生成甘特图

        Args:
            tasks: 任务列表

        Returns:
            甘特图（ASCII格式）
        """
        chart = """
## 项目甘特图

```
任务          | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 |
--------------|--------|--------|--------|--------|--------|
需求分析      |████████|        |        |        |        |
架构设计      |        |████████|        |        |        |
开发实现      |        |        |████████|████████|████████|
测试验收      |        |        |        |        |████████|
上线部署      |        |        |        |        |    ████|
```
"""
        return chart

    def generate_raci_matrix(self, tasks: list, team: list) -> dict:
        """
        生成RACI矩阵

        Args:
            tasks: 任务列表
            team: 团队成员列表

        Returns:
            RACI矩阵
        """
        matrix = {
            "title": "RACI责任矩阵",
            "created_at": datetime.now().isoformat(),
            "legend": {
                "R": "负责执行（Responsible）",
                "A": "最终批准（Accountable）",
                "C": "提供咨询（Consulted）",
                "I": "被告知（Informed）"
            },
            "matrix": []
        }

        for task in tasks:
            row = {
                "task": task,
                "assignments": {}
            }
            for member in team:
                # 简单的分配逻辑
                if "经理" in member["role"] or "PM" in member["role"]:
                    row["assignments"][member["name"]] = "A"
                elif "开发" in member["role"] or "工程师" in member["role"]:
                    row["assignments"][member["name"]] = "R"
                else:
                    row["assignments"][member["name"]] = "C"

            matrix["matrix"].append(row)

        return matrix

    def create_github_issue(self, title: str, body: str, labels: list = None) -> dict:
        """
        创建GitHub Issue

        Args:
            title: 标题
            body: 内容
            labels: 标签列表

        Returns:
            操作结果
        """
        try:
            cmd = [
                "gh", "issue", "create",
                "--repo", f"{self.github_user}/{self.github_repo}",
                "--title", title,
                "--body", body
            ]

            if labels:
                cmd.extend(["--labels", ",".join(labels)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "GH_TOKEN": self.github_token}
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "issue_url": result.stdout.strip()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_weekly_report(self, completed_tasks: list, pending_tasks: list, risks: list) -> str:
        """
        生成周报

        Args:
            completed_tasks: 已完成任务
            pending_tasks: 待完成任务
            risks: 风险列表

        Returns:
            周报内容
        """
        report = f"""
# 项目周报

**报告日期**: {datetime.now().strftime('%Y-%m-%d')}

## 一、本周完成情况

已完成任务: {len(completed_tasks)}项

"""
        for task in completed_tasks:
            report += f"- ✅ {task}\n"

        report += f"""

## 二、下周计划

待完成任务: {len(pending_tasks)}项

"""
        for task in pending_tasks:
            report += f"- ⏳ {task}\n"

        report += f"""

## 三、风险提示

风险数量: {len(risks)}项

"""
        for risk in risks:
            report += f"- ⚠️ {risk}\n"

        report += """

---

**项目经理**: 玉衡
**生成时间**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return report


# 使用示例
if __name__ == "__main__":
    yuheng = YuhengGithubEnhanced()

    print("=" * 50)
    print("⚖️ 玉衡 - 项目管理演示")
    print("=" * 50)

    # 创建项目看板
    print("\n📋 创建项目看板...")

    board = yuheng.create_project_board(
        project_name="AI智能配案系统",
        columns=["待开始", "进行中", "待验收", "已完成"]
    )

    print(f"项目: {board['name']}")
    print(f"列数: {len(board['columns'])}")
    for col in board['columns']:
        print(f"  - {col['name']}")

    # 创建任务
    print("\n" + "=" * 50)
    print("📝 创建任务...")

    tasks = [
        yuheng.create_task(
            title="需求分析",
            description="完成用户需求分析文档",
            assignee="采薇",
            priority="高",
            due_date="2026-03-20"
        ),
        yuheng.create_task(
            title="架构设计",
            description="完成系统架构设计文档",
            assignee="织锦",
            priority="高",
            due_date="2026-03-25"
        ),
        yuheng.create_task(
            title="接口开发",
            description="完成用户模块API开发",
            assignee="工尺",
            priority="中",
            due_date="2026-04-01"
        )
    ]

    for task in tasks:
        print(f"\n任务ID: {task['id']}")
        print(f"标题: {task['title']}")
        print(f"负责人: {task['assignee']}")
        print(f"优先级: {task['priority']}")
        print(f"截止日期: {task['due_date']}")

    # 生成甘特图
    print("\n" + "=" * 50)
    print("📊 生成甘特图...")

    gantt = yuheng.generate_gantt_chart(tasks)
    print(gantt)

    # 生成RACI矩阵
    print("=" * 50)
    print("👥 生成RACI矩阵...")

    team = [
        {"name": "采薇", "role": "需求分析师"},
        {"name": "织锦", "role": "架构设计师"},
        {"name": "工尺", "role": "开发工程师"},
        {"name": "玉衡", "role": "项目经理"}
    ]

    raci = yuheng.generate_raci_matrix(
        tasks=["需求分析", "架构设计", "接口开发", "测试验收"],
        team=team
    )

    print(f"\n{raci['title']}")
    print("\n图例:")
    for k, v in raci['legend'].items():
        print(f"  {k}: {v}")

    print("\n矩阵:")
    for row in raci['matrix']:
        print(f"\n  {row['task']}:")
        for name, role in row['assignments'].items():
            print(f"    {name}: {role}")

    # 生成周报
    print("\n" + "=" * 50)
    print("📄 生成周报...")

    report = yuheng.generate_weekly_report(
        completed_tasks=["需求分析文档完成", "架构设计评审通过"],
        pending_tasks=["接口开发", "单元测试"],
        risks=["开发工期紧张", "第三方接口联调延迟"]
    )

    print(report[:500] + "...")
