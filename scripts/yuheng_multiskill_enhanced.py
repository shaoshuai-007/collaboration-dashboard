#!/usr/bin/env python3
"""
玉衡 - 项目管理增强模块 V2.0
多技能集成：github + compass-project + spreadsheet + risk-monitor + send-email

技能调用优先级：
1. compass-project (项目管控计划)
2. github (项目看板)
3. spreadsheet (项目报表)
4. risk-monitor (风险监控)
5. send-email (邮件周报)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class YuhengMultiSkillEnhanced:
    """玉衡的多技能增强类"""

    def __init__(self):
        self.name = "玉衡"
        self.role = "项目经理"

        # 技能清单
        self.skills = {
            "github": {"skill": "github", "usage": "项目看板管理", "priority": 2},
            "compass_project": {"skill": "compass-project", "usage": "项目管控计划", "priority": 1},
            "spreadsheet": {"skill": "spreadsheet", "usage": "项目报表", "priority": 3},
            "risk_monitor": {"skill": "risk-monitor", "usage": "风险监控", "priority": 4},
            "send_email": {"skill": "send-email", "usage": "邮件周报", "priority": 5}
        }

        # 工作空间
        self.workspace = Path("/root/.openclaw/workspace")
        self.output_dir = self.workspace / "03_输出成果" / "玉衡产出"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def manage_project(self, project_name: str, duration_weeks: int = 12) -> dict:
        """完整项目管理流程"""
        print(f"⚖️ 玉衡开始管理 {project_name} 项目...")
        results = {}

        # Step 1: 生成项目管控计划
        print("  [1/4] 生成项目管控计划...")
        plan_result = self.generate_project_plan(project_name, duration_weeks)
        results["plan"] = plan_result

        # Step 2: 生成甘特图
        print("  [2/4] 生成甘特图...")
        gantt_result = self.generate_gantt(project_name, duration_weeks)
        results["gantt"] = gantt_result

        # Step 3: 生成RACI矩阵
        print("  [3/4] 生成RACI矩阵...")
        raci_result = self.generate_raci(project_name)
        results["raci"] = raci_result

        # Step 4: 生成风险清单
        print("  [4/4] 生成风险清单...")
        risk_result = self.generate_risk_register(project_name)
        results["risk"] = risk_result

        print(f"✅ 项目管理完成！")
        return results

    def generate_project_plan(self, project: str, weeks: int) -> dict:
        """生成项目管控计划"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_管控计划_{timestamp}.md"

        # 生成里程碑
        milestones = []
        for i in range(1, 5):
            week = i * (weeks // 4)
            milestones.append(f"Week {week}: 里程碑{i}")

        md = f'''# {project}项目管控计划

**项目经理**: 玉衡 @ 九星智囊团
**编制日期**: {datetime.now().strftime('%Y年%m月%d日')}
**项目周期**: {weeks}周

---

## 一、项目里程碑

| 里程碑 | 时间节点 | 交付物 | 负责人 |
|--------|---------|--------|--------|
| 项目启动 | Week 1 | 项目章程 | 项目经理 |
| 需求确认 | Week 3 | 需求规格说明书 | 需求分析师 |
| 设计完成 | Week 6 | 详细设计文档 | 架构设计师 |
| 开发完成 | Week 10 | 可运行系统 | 开发团队 |
| 项目验收 | Week {weeks} | 验收报告 | 项目经理 |

## 二、工作分解结构(WBS)

1. 项目管理
   - 项目启动
   - 进度跟踪
   - 风险管理
2. 需求分析
   - 需求调研
   - 需求文档
3. 系统设计
   - 架构设计
   - 详细设计
4. 开发测试
   - 编码实现
   - 单元测试
   - 集成测试
5. 部署上线
   - 环境准备
   - 系统部署
   - 用户培训

## 三、干系人列表

| 干系人 | 角色 | 职责 | 沟通频率 |
|--------|------|------|---------|
| 项目经理 | 项目管理 | 统筹协调 | 每日 |
| 产品经理 | 需求管理 | 需求确认 | 每周 |
| 技术负责人 | 技术决策 | 架构设计 | 每周 |
| 开发团队 | 开发实施 | 代码开发 | 每日 |

---

**九星智囊团**
*以智为针，以信为盘*
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {"success": True, "plan_file": str(output_file)}

    def generate_gantt(self, project: str, weeks: int) -> dict:
        """生成甘特图HTML"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_甘特图_{timestamp}.html"

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{project} - 甘特图</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #C93832; text-align: center; }}
        .gantt {{ margin-top: 30px; }}
        .task {{ display: flex; margin: 10px 0; align-items: center; }}
        .task-name {{ width: 150px; font-weight: bold; }}
        .task-bar {{ flex: 1; height: 30px; position: relative; background: #f0f0f0; border-radius: 4px; }}
        .bar {{ position: absolute; height: 100%; border-radius: 4px; }}
        .bar.design {{ background: #006EBD; }}
        .bar.dev {{ background: #C93832; }}
        .bar.test {{ background: #595959; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚖️ {project} - 甘特图</h1>
        <p style="text-align: center; color: #888;">项目周期: {weeks}周</p>
        <div class="gantt">
            <div class="task">
                <div class="task-name">需求分析</div>
                <div class="task-bar"><div class="bar design" style="left: 0%; width: 25%;"></div></div>
            </div>
            <div class="task">
                <div class="task-name">架构设计</div>
                <div class="task-bar"><div class="bar design" style="left: 20%; width: 20%;"></div></div>
            </div>
            <div class="task">
                <div class="task-name">开发实现</div>
                <div class="task-bar"><div class="bar dev" style="left: 35%; width: 45%;"></div></div>
            </div>
            <div class="task">
                <div class="task-name">测试验收</div>
                <div class="task-bar"><div class="bar test" style="left: 75%; width: 25%;"></div></div>
            </div>
        </div>
    </div>
</body>
</html>'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return {"success": True, "gantt_file": str(output_file)}

    def generate_raci(self, project: str) -> dict:
        """生成RACI矩阵CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_RACI矩阵_{timestamp}.csv"

        csv = '''任务,项目经理,需求分析师,架构设计师,开发工程师,测试工程师
需求调研,A,R,C,I,I
需求文档,A,R,I,I,I
架构设计,C,I,R,I,I
详细设计,C,I,R,C,I
编码实现,I,I,C,R,C
单元测试,I,I,I,R,R
集成测试,A,I,I,C,R
系统部署,A,I,I,R,I
验收测试,A,C,I,I,R'''

        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(csv)

        return {"success": True, "raci_file": str(output_file)}

    def generate_risk_register(self, project: str) -> dict:
        """生成风险清单"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_风险清单_{timestamp}.csv"

        csv = '''风险ID,风险描述,风险类别,概率,影响,风险等级,应对措施,负责人
R001,需求变更频繁,需求风险,高,高,高,建立变更控制流程,项目经理
R002,技术方案不成熟,技术风险,中,高,高,技术预研,PoC验证,技术负责人
R003,人员流动,资源风险,中,中,中,知识文档化,AB角机制,项目经理
R004,进度延期,进度风险,高,中,中,预留缓冲时间,周报跟踪,项目经理
R005,质量不达标,质量风险,中,高,高,加强测试,代码审查,测试负责人'''

        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(csv)

        return {"success": True, "risk_file": str(output_file)}


if __name__ == "__main__":
    yuheng = YuhengMultiSkillEnhanced()
    result = yuheng.manage_project("湖北电信AI配案系统", 12)
    print(f"\n📊 管理结果:")
    for key, val in result.items():
        if isinstance(val, dict):
            print(f"  {key}: {val.get(list(val.keys())[1], '生成失败')}")
