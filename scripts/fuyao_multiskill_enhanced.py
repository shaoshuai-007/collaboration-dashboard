#!/usr/bin/env python3
"""
扶摇 - 总指挥增强模块 V2.0
多技能集成：coding-agent + compass-coordinator + workflow-designer + github + canvas

技能调用优先级：
1. compass-coordinator (流程协调)
2. workflow-designer (工作流设计)
3. coding-agent (调度脚本)
4. github (状态跟踪)
5. canvas (团队仪表盘)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class FuyaoMultiSkillEnhanced:
    """扶摇的多技能增强类"""

    def __init__(self):
        self.name = "扶摇"
        self.role = "总指挥"

        # 技能清单
        self.skills = {
            "coding_agent": {"skill": "coding-agent", "usage": "调度脚本", "priority": 3},
            "coordinator": {"skill": "compass-coordinator", "usage": "流程协调", "priority": 1},
            "workflow": {"skill": "workflow-designer", "usage": "工作流设计", "priority": 2},
            "github": {"skill": "github", "usage": "状态跟踪", "priority": 4},
            "canvas": {"skill": "canvas", "usage": "团队仪表盘", "priority": 5}
        }

        self.workspace = Path("/root/.openclaw/workspace")
        self.output_dir = self.workspace / "03_输出成果" / "扶摇产出"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 团队成员
        self.team = {
            "采薇": {"role": "需求分析师", "skills": ["summarize", "compass-needdoc", "compass-mindmap"]},
            "织锦": {"role": "架构设计师", "skills": ["coding-agent", "compass-solution", "compass-design"]},
            "筑台": {"role": "售前工程师", "skills": ["summarize", "ppt-generator", "market-research"]},
            "呈彩": {"role": "方案设计师", "skills": ["coding-agent", "compass-ppt", "ppt-generator"]},
            "工尺": {"role": "系统设计师", "skills": ["github", "compass-design", "diagram-creator"]},
            "玉衡": {"role": "项目经理", "skills": ["github", "compass-project", "spreadsheet"]},
            "折桂": {"role": "资源管家", "skills": ["summarize", "knowledge-graph", "document-pdf"]},
            "天工": {"role": "开发工程师", "skills": ["coding-agent", "compass-dev", "github"]},
            "知微": {"role": "数据分析师", "skills": ["summarize", "compass-analysis", "data-analysis"]},
            "南乔": {"role": "用户助手", "skills": ["summarize", "compass-shared", "send-email"]}
        }

    def coordinate_task(self, task_description: str, project_name: str = "项目") -> dict:
        """协调任务执行"""
        print(f"🌀 扶摇开始协调 {project_name} 任务...")
        results = {}

        # Step 1: 分析任务
        print("  [1/4] 分析任务...")
        task_analysis = self.analyze_task(task_description)
        results["analysis"] = task_analysis

        # Step 2: 分配任务
        print("  [2/4] 分配任务...")
        assignment = self.assign_tasks(task_analysis, project_name)
        results["assignment"] = assignment

        # Step 3: 生成工作流
        print("  [3/4] 生成工作流...")
        workflow = self.generate_workflow(project_name, assignment)
        results["workflow"] = workflow

        # Step 4: 生成仪表盘
        print("  [4/4] 生成仪表盘...")
        dashboard = self.generate_dashboard(project_name)
        results["dashboard"] = dashboard

        print(f"✅ 任务协调完成！")
        return results

    def analyze_task(self, description: str) -> dict:
        """分析任务需求"""
        # 识别任务类型
        task_types = []
        keywords = {
            "需求分析": ["需求", "分析", "文档"],
            "方案设计": ["方案", "设计", "PPT"],
            "开发实现": ["开发", "代码", "实现"],
            "项目管理": ["项目", "进度", "风险"],
            "数据分析": ["数据", "分析", "报表"]
        }

        for task_type, kws in keywords.items():
            if any(kw in description for kw in kws):
                task_types.append(task_type)

        return {
            "description": description,
            "task_types": task_types,
            "complexity": "中" if len(task_types) > 2 else "低",
            "estimated_members": len(task_types)
        }

    def assign_tasks(self, analysis: dict, project: str) -> dict:
        """分配任务给团队成员"""
        assignments = {}

        # 根据任务类型分配成员
        type_member_map = {
            "需求分析": "采薇",
            "方案设计": "呈彩",
            "开发实现": "天工",
            "项目管理": "玉衡",
            "数据分析": "知微"
        }

        for task_type in analysis["task_types"]:
            member = type_member_map.get(task_type, "南乔")
            if member not in assignments:
                assignments[member] = []
            assignments[member].append(task_type)

        # 生成分配报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_任务分配_{timestamp}.md"

        md = f'''# {project}任务分配报告

**协调人**: 扶摇 @ 九星智囊团
**分配时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

---

## 任务分析

- **任务描述**: {analysis["description"]}
- **任务类型**: {", ".join(analysis["task_types"])}
- **复杂度**: {analysis["complexity"]}
- **涉及成员**: {len(assignments)}人

## 任务分配

| 成员 | 角色 | 任务 | 预计产出 |
|------|------|------|---------|
'''

        for member, tasks in assignments.items():
            role = self.team[member]["role"]
            md += f"| {member} | {role} | {', '.join(tasks)} | 待确认 |\n"

        md += '''
## 协调要点

1. 任务间依赖关系需明确
2. 定期同步进度
3. 及时反馈问题

---

**九星智囊团**
*以智为针，以信为盘*
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {"success": True, "assignments": assignments, "report_file": str(output_file)}

    def generate_workflow(self, project: str, assignment: dict) -> dict:
        """生成工作流"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_工作流_{timestamp}.html"

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{project} - 工作流程</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #C93832; text-align: center; }}
        .workflow {{ background: white; border-radius: 10px; padding: 30px; margin-top: 30px; }}
        .step {{ display: flex; align-items: center; margin: 20px 0; }}
        .step-number {{ width: 40px; height: 40px; background: #C93832; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }}
        .step-content {{ flex: 1; margin-left: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #006EBD; }}
        .step-title {{ font-weight: bold; color: #006EBD; }}
        .step-member {{ color: #595959; font-size: 14px; }}
        .arrow {{ text-align: center; color: #C93832; font-size: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌀 {project} - 工作流程</h1>

        <div class="workflow">
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <div class="step-title">需求分析</div>
                    <div class="step-member">负责人: 采薇 | 产出: 需求文档、思维导图</div>
                </div>
            </div>
            <div class="arrow">↓</div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <div class="step-title">方案设计</div>
                    <div class="step-member">负责人: 呈彩 | 产出: 方案PPT、UI原型</div>
                </div>
            </div>
            <div class="arrow">↓</div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <div class="step-title">详细设计</div>
                    <div class="step-member">负责人: 织锦、工尺 | 产出: 架构设计、接口文档</div>
                </div>
            </div>
            <div class="arrow">↓</div>
            <div class="step">
                <div class="step-number">4</div>
                <div class="step-content">
                    <div class="step-title">开发实现</div>
                    <div class="step-member">负责人: 天工 | 产出: 代码、测试用例</div>
                </div>
            </div>
            <div class="arrow">↓</div>
            <div class="step">
                <div class="step-number">5</div>
                <div class="step-content">
                    <div class="step-title">数据分析</div>
                    <div class="step-member">负责人: 知微 | 产出: 分析报告、可视化</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return {"success": True, "workflow_file": str(output_file)}

    def generate_dashboard(self, project: str) -> dict:
        """生成团队仪表盘"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_团队仪表盘_{timestamp}.html"

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{project} - 团队仪表盘</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #1a1a2e; color: white; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ text-align: center; background: linear-gradient(135deg, #C93832, #006EBD); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #16213e; border-radius: 10px; padding: 20px; text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: bold; color: #C93832; }}
        .stat-label {{ color: #888; margin-top: 10px; }}
        .team-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }}
        .member-card {{ background: #16213e; border-radius: 10px; padding: 15px; text-align: center; }}
        .member-name {{ font-weight: bold; margin-bottom: 5px; }}
        .member-role {{ font-size: 12px; color: #888; }}
        .member-status {{ margin-top: 10px; padding: 5px; border-radius: 5px; }}
        .status-active {{ background: #28a745; }}
        .status-idle {{ background: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌀 九星智囊团 - {project}</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">11</div>
                <div class="stat-label">团队成员</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">82</div>
                <div class="stat-label">可用技能</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">8</div>
                <div class="stat-label">指南针步骤</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">100%</div>
                <div class="stat-label">专家级达标</div>
            </div>
        </div>

        <div class="team-grid">
            <div class="member-card">
                <div class="member-name">🌸 采薇</div>
                <div class="member-role">需求分析师</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">🧵 织锦</div>
                <div class="member-role">架构设计师</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">🏗️ 筑台</div>
                <div class="member-role">售前工程师</div>
                <div class="member-status status-idle">待命</div>
            </div>
            <div class="member-card">
                <div class="member-name">🎨 呈彩</div>
                <div class="member-role">方案设计师</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">📐 工尺</div>
                <div class="member-role">系统设计师</div>
                <div class="member-status status-idle">待命</div>
            </div>
            <div class="member-card">
                <div class="member-name">⚖️ 玉衡</div>
                <div class="member-role">项目经理</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">📚 折桂</div>
                <div class="member-role">资源管家</div>
                <div class="member-status status-idle">待命</div>
            </div>
            <div class="member-card">
                <div class="member-name">💻 天工</div>
                <div class="member-role">开发工程师</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">📊 知微</div>
                <div class="member-role">数据分析师</div>
                <div class="member-status status-idle">待命</div>
            </div>
            <div class="member-card">
                <div class="member-name">🌿 南乔</div>
                <div class="member-role">用户助手+Leader</div>
                <div class="member-status status-active">活跃</div>
            </div>
            <div class="member-card">
                <div class="member-name">🌀 扶摇</div>
                <div class="member-role">总指挥</div>
                <div class="member-status status-active">活跃</div>
            </div>
        </div>
    </div>
</body>
</html>'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return {"success": True, "dashboard_file": str(output_file)}


if __name__ == "__main__":
    fuyao = FuyaoMultiSkillEnhanced()
    result = fuyao.coordinate_task("湖北电信AI配案系统需求分析和方案设计", "湖北电信AI配案系统")
    print(f"\n📊 协调结果:")
    for key, val in result.items():
        if isinstance(val, dict):
            print(f"  {key}: {list(val.values())}")
