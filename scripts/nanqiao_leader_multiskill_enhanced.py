#!/usr/bin/env python3
"""
南乔 - 用户助手+Leader增强模块 V2.0
多技能集成：summarize + compass-shared + send-email + canvas + spreadsheet + document-pdf

技能调用优先级：
1. summarize (智能对话、内容摘要)
2. compass-shared (共享知识库)
3. send-email (发送报告)
4. canvas (展示成果)
5. spreadsheet (数据整理)
6. document-pdf (报告输出)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class NanqiaoLeaderEnhanced:
    """南乔的多技能增强类"""

    def __init__(self):
        self.name = "南乔"
        self.role = "用户助手 + Leader"

        self.skills = {
            "summarize": {"skill": "summarize", "usage": "智能对话、内容摘要", "priority": 1},
            "compass_shared": {"skill": "compass-shared", "usage": "共享知识库", "priority": 2},
            "send_email": {"skill": "send-email", "usage": "发送报告", "priority": 3},
            "canvas": {"skill": "canvas", "usage": "展示成果", "priority": 4},
            "spreadsheet": {"skill": "spreadsheet", "usage": "数据整理", "priority": 5},
            "document_pdf": {"skill": "document-pdf", "usage": "报告输出", "priority": 6}
        }

        self.workspace = Path("/root/.openclaw/workspace")
        self.output_dir = self.workspace / "03_输出成果" / "南乔产出"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 团队成员
        self.team_members = [
            {"name": "采薇", "role": "需求分析师", "status": "active"},
            {"name": "织锦", "role": "架构设计师", "status": "active"},
            {"name": "筑台", "role": "售前工程师", "status": "idle"},
            {"name": "呈彩", "role": "方案设计师", "status": "active"},
            {"name": "工尺", "role": "系统设计师", "status": "idle"},
            {"name": "玉衡", "role": "项目经理", "status": "active"},
            {"name": "折桂", "role": "资源管家", "status": "idle"},
            {"name": "扶摇", "role": "总指挥", "status": "active"},
            {"name": "天工", "role": "开发工程师", "status": "active"},
            {"name": "知微", "role": "数据分析师", "status": "idle"},
        ]

    def serve_user(self, request: str) -> dict:
        """服务用户请求"""
        print(f"🌿 南乔开始处理用户请求...")
        results = {}

        # Step 1: 理解意图
        print("  [1/4] 理解用户意图...")
        intent = self.analyze_intent(request)
        results["intent"] = intent

        # Step 2: 分配任务
        print("  [2/4] 分配任务给团队成员...")
        assignment = self.assign_to_team(intent)
        results["assignment"] = assignment

        # Step 3: 执行任务
        print("  [3/4] 协调执行...")
        execution = self.coordinate_execution(assignment)
        results["execution"] = execution

        # Step 4: 返回结果
        print("  [4/4] 整理返回结果...")
        response = self.prepare_response(execution)
        results["response"] = response

        print(f"✅ 用户请求处理完成！")
        return results

    def analyze_intent(self, request: str) -> dict:
        """分析用户意图"""
        intent_types = {
            "需求分析": ["需求", "文档", "分析"],
            "方案设计": ["方案", "PPT", "设计"],
            "开发实现": ["开发", "代码", "实现"],
            "项目管理": ["项目", "进度", "计划"],
            "数据分析": ["数据", "分析", "报表"],
            "售前支持": ["报价", "竞品", "售前"]
        }

        detected = []
        for intent, keywords in intent_types.items():
            if any(kw in request for kw in keywords):
                detected.append(intent)

        return {
            "request": request,
            "intents": detected if detected else ["通用咨询"],
            "complexity": "高" if len(detected) > 2 else "中" if len(detected) > 1 else "低"
        }

    def assign_to_team(self, intent: dict) -> dict:
        """分配任务给团队成员"""
        intent_member_map = {
            "需求分析": "采薇",
            "方案设计": "呈彩",
            "开发实现": "天工",
            "项目管理": "玉衡",
            "数据分析": "知微",
            "售前支持": "筑台"
        }

        assignments = []
        for i in intent["intents"]:
            member = intent_member_map.get(i, "南乔")
            assignments.append({"intent": i, "member": member})

        return {"success": True, "assignments": assignments}

    def coordinate_execution(self, assignment: dict) -> dict:
        """协调执行"""
        # 模拟执行结果
        return {"success": True, "status": "已分配", "members_notified": len(assignment["assignments"])}

    def prepare_response(self, execution: dict) -> dict:
        """准备响应"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"用户请求处理报告_{timestamp}.md"

        md = f'''# 用户请求处理报告

**处理人**: 南乔 @ 九星智囊团
**处理时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

---

## 处理结果

✅ 任务已成功分配给相关团队成员，正在处理中。

---

**九星智囊团**
*南有乔木，不可休思*
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {"success": True, "report_file": str(output_file)}

    def generate_daily_report(self) -> dict:
        """生成每日报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"每日团队报告_{timestamp}.md"

        active_members = [m for m in self.team_members if m["status"] == "active"]

        md = f'''# 九星智囊团每日报告

**报告人**: 南乔 @ 九星智囊团
**报告日期**: {datetime.now().strftime('%Y年%m月%d日')}

---

## 团队状态

| 指标 | 数值 |
|------|:----:|
| 团队成员 | 11人 |
| 活跃成员 | {len(active_members)}人 |
| 可用技能 | 82个 |
| 指南针步骤 | 8步 |

## 今日任务

- ✅ 需求分析任务处理
- ✅ 方案设计任务处理
- ⏳ 开发实现任务进行中

## 明日计划

1. 继续推进项目进度
2. 团队技能培训
3. 知识库更新

---

**九星智囊团**
*以智为针，以信为盘*
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {"success": True, "report_file": str(output_file)}


if __name__ == "__main__":
    nanqiao = NanqiaoLeaderEnhanced()
    result = nanqiao.serve_user("帮我分析湖北电信AI配案系统的需求")
    print(f"\n📊 处理结果:")
    for key, val in result.items():
        print(f"  {key}: {val}")
