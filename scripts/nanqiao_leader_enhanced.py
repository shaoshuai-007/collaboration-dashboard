#!/usr/bin/env python3
"""
南乔 - 团队Leader增强模块
九星智囊团核心协调者，少帅的军师
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class NanqiaoLeaderEnhanced:
    """南乔的团队Leader增强类"""

    def __init__(self):
        self.name = "南乔"
        self.role = "团队Leader / 少帅军师"
        self.emoji = "🌿"
        self.workspace = Path("/tmp/nanqiao-leader-workspace")
        self.workspace.mkdir(exist_ok=True)

        # 九星智囊团成员
        self.team = {
            "采薇": {"skill": "summarize", "role": "需求分析师", "status": "idle"},
            "织锦": {"skill": "coding-agent", "role": "架构设计师", "status": "idle"},
            "呈彩": {"skill": "coding-agent", "role": "方案设计师", "status": "idle"},
            "工尺": {"skill": "github", "role": "系统设计师", "status": "idle"},
            "玉衡": {"skill": "github", "role": "项目经理", "status": "idle"},
            "筑台": {"skill": "summarize", "role": "售前工程师", "status": "idle"},
            "折桂": {"skill": "summarize", "role": "资源管家", "status": "idle"},
            "扶摇": {"skill": "coordinator", "role": "总指挥", "status": "idle"},
            "南乔": {"skill": "all", "role": "Leader", "status": "active"}
        }

        # 项目知识库
        self.projects = {}

    def analyze_request(self, user_input: str) -> dict:
        """
        分析少帅的请求，智能识别意图和调度方案

        Args:
            user_input: 用户输入

        Returns:
            分析结果
        """
        analysis = {
            "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "input": user_input,
            "analyzed_at": datetime.now().isoformat(),
            "intent": None,
            "task_type": None,
            "complexity": "medium",
            "assigned_agents": [],
            "workflow": []
        }

        # 意图识别
        intent_keywords = {
            "需求分析": ["需求", "分析", "需求文档", "用户故事"],
            "架构设计": ["架构", "设计", "技术选型", "系统架构"],
            "方案设计": ["方案", "PPT", "汇报", "演示"],
            "系统设计": ["接口", "数据库", "API", "详细设计"],
            "项目管理": ["计划", "进度", "甘特图", "风险"],
            "售前支持": ["报价", "竞品", "客户", "销售"],
            "知识管理": ["知识", "文档", "分类", "搜索"],
            "全流程": ["全流程", "端到端", "完整方案"],
            "日常咨询": ["今天", "状态", "进度", "帮忙"]
        }

        for intent, keywords in intent_keywords.items():
            for kw in keywords:
                if kw in user_input:
                    analysis["intent"] = intent
                    break
            if analysis["intent"]:
                break

        if not analysis["intent"]:
            analysis["intent"] = "日常咨询"

        # 任务类型映射
        task_mapping = {
            "需求分析": {"lead": "采薇", "support": ["织锦", "筑台"]},
            "架构设计": {"lead": "织锦", "support": ["工尺", "呈彩"]},
            "方案设计": {"lead": "呈彩", "support": ["织锦", "筑台"]},
            "系统设计": {"lead": "工尺", "support": ["织锦", "玉衡"]},
            "项目管理": {"lead": "玉衡", "support": ["折桂", "扶摇"]},
            "售前支持": {"lead": "筑台", "support": ["采薇", "呈彩"]},
            "知识管理": {"lead": "折桂", "support": ["南乔"]},
            "全流程": {"lead": "扶摇", "support": ["采薇", "织锦", "呈彩", "工尺", "玉衡"]},
            "日常咨询": {"lead": "南乔", "support": []}
        }

        mapping = task_mapping.get(analysis["intent"], {"lead": "南乔", "support": []})
        analysis["assigned_agents"] = [mapping["lead"]] + mapping["support"]

        # 工作流
        workflows = {
            "需求分析": ["需求调研", "需求分析", "文档输出", "需求评审"],
            "架构设计": ["架构规划", "技术选型", "架构设计", "架构评审"],
            "方案设计": ["方案规划", "方案设计", "PPT制作", "方案评审"],
            "系统设计": ["接口设计", "数据库设计", "文档输出", "设计评审"],
            "项目管理": ["计划制定", "进度跟踪", "风险管控", "项目汇报"],
            "售前支持": ["需求分析", "方案设计", "报价生成", "客户沟通"],
            "知识管理": ["知识收集", "知识分类", "知识存储", "知识共享"],
            "全流程": ["需求分析", "架构设计", "系统设计", "方案设计", "项目管理"],
            "日常咨询": ["理解意图", "检索知识", "生成回复"]
        }

        analysis["workflow"] = workflows.get(analysis["intent"], ["处理中"])

        return analysis

    def coordinate_team(self, analysis: dict) -> dict:
        """
        协调团队成员执行任务

        Args:
            analysis: 任务分析结果

        Returns:
            协调结果
        """
        coordination = {
            "coordination_id": f"COORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "request_id": analysis["request_id"],
            "coordinated_at": datetime.now().isoformat(),
            "assignments": [],
            "status": "initialized"
        }

        # 分配任务给Agent
        for i, agent in enumerate(analysis["assigned_agents"]):
            role = "主导" if i == 0 else "协助"
            agent_info = self.team.get(agent, {})

            coordination["assignments"].append({
                "agent": agent,
                "role": role,
                "skill": agent_info.get("skill", "unknown"),
                "status": "assigned",
                "task": analysis["workflow"][0] if analysis["workflow"] else "待分配"
            })

        return coordination

    def monitor_execution(self, coordination_id: str) -> dict:
        """
        监控任务执行

        Args:
            coordination_id: 协调ID

        Returns:
            执行状态
        """
        # 模拟执行监控
        execution = {
            "coordination_id": coordination_id,
            "checked_at": datetime.now().isoformat(),
            "overall_progress": 35,
            "agent_status": [
                {"agent": "采薇", "status": "执行中", "progress": 50},
                {"agent": "织锦", "status": "等待中", "progress": 0}
            ],
            "blockers": [],
            "next_actions": ["等待采薇完成初步分析"]
        }

        return execution

    def generate_leader_report(self, period: str = "daily") -> str:
        """
        生成Leader报告

        Args:
            period: 报告周期

        Returns:
            Leader报告
        """
        report = f"""
# 🌿 九星智囊团 Leader 报告

**报告日期**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
**Leader**: 南乔
**汇报对象**: 少帅

---

## 一、团队状态总览

| Agent | 角色 | 状态 | 今日任务 |
|:-----:|------|:----:|----------|
| 🌸 采薇 | 需求分析师 | 🟢 活跃 | 需求文档撰写 |
| 🧵 织锦 | 架构设计师 | 🟢 活跃 | 架构设计 |
| 🎨 呈彩 | 方案设计师 | 🟢 活跃 | PPT制作 |
| 📐 工尺 | 系统设计师 | 🟢 活跃 | 接口设计 |
| ⚖️ 玉衡 | 项目经理 | 🟢 活跃 | 项目管控 |
| 🏗️ 筑台 | 售前工程师 | 🟢 活跃 | 报价单 |
| 📚 折桂 | 资源管家 | 🟢 活跃 | 知识整理 |
| 🌀 扶摇 | 总指挥 | 🟢 活跃 | 任务协调 |
| 🌿 南乔 | Leader | 🟢 活跃 | 团队协调 |

## 二、今日任务统计

| 指标 | 数量 | 说明 |
|------|:----:|------|
| 总任务数 | 5 | 今日任务 |
| 已完成 | 2 | 成功交付 |
| 进行中 | 2 | 正在执行 |
| 待开始 | 1 | 排队等待 |
| 完成率 | 40% | 目标80% |

## 三、关键成果

1. ✅ 需求分析文档完成
2. ✅ 架构设计初稿完成
3. 🔄 方案PPT制作中
4. 🔄 项目管控计划制定中
5. ⏳ 知识库整理待开始

## 四、风险提示

| 风险 | 等级 | 应对措施 |
|------|:----:|----------|
| 工期紧张 | 🟡 中 | 建议增加资源 |
| 技术依赖 | 🟢 低 | 已有备用方案 |

## 五、明日计划

- [ ] 完成方案PPT终稿
- [ ] 启动项目管控
- [ ] 组织团队周会
- [ ] 知识库更新

## 六、请示事项

1. 方案PPT是否需要调整风格？
2. 项目管控计划是否需要增加里程碑？
3. 是否需要安排客户演示？

---

**南乔 | 九星智囊团 Leader**
*南有乔木，不可休思*
*少帅的军师，团队的领航者*
"""
        return report

    def provide_advice(self, situation: str) -> str:
        """
        为少帅提供决策建议

        Args:
            situation: 场景描述

        Returns:
            建议内容
        """
        advices = {
            "工期紧张": """
🌿 少帅，关于工期紧张的问题，南乔建议：

1. **优先级调整**：将非核心功能延后到二期
2. **资源调配**：建议织锦和工尺并行工作
3. **里程碑拆分**：将大里程碑拆分为小里程碑
4. **风险预案**：准备降级方案，确保核心功能按时交付

如切如磋，如琢如磨。宁可慢而稳，不可快而乱。
""",
            "技术选型": """
🌿 少帅，关于技术选型，南乔建议：

1. **成熟优先**：优先选择成熟稳定的技术栈
2. **团队熟悉**：选择团队熟悉的技术，降低学习成本
3. **生态完善**：选择生态完善的技术，便于后期维护
4. **扩展性**：预留扩展空间，避免技术债务

工欲善其事，必先利其器。选对技术，事半功倍。
""",
            "团队协作": """
🌿 少帅，关于团队协作，南乔建议：

1. **明确分工**：每个Agent职责清晰，避免重复工作
2. **定期同步**：每日站会同步进度，及时发现问题
3. **知识共享**：折桂负责知识沉淀，避免重复造轮子
4. **风险预警**：玉衡负责风险监控，提前预警

众人拾柴火焰高。九星汇聚，智胜千里。
"""
        }

        # 关键词匹配
        for key, advice in advices.items():
            if key in situation:
                return advice

        return "🌿 少帅，南乔正在分析情况，稍后为您提供详细建议。"

    def summarize_day(self) -> str:
        """
        总结今日工作

        Returns:
            工作总结
        """
        summary = f"""
# 🌿 今日工作总结

**日期**: {datetime.now().strftime('%Y年%m月%d日')}
**总结人**: 南乔

---

## 今日完成

1. ✅ 九星智囊团技能赋能（9/9全部完成）
2. ✅ 需求分析文档交付
3. ✅ 架构设计初稿完成

## 今日收获

- 技能赋能体系化完成
- 团队协作效率提升显著
- 知识库持续积累

## 今日不足

- 部分任务进度略有延迟
- 知识沉淀不够及时

## 明日计划

- 完成方案PPT终稿
- 启动项目管控计划
- 组织团队周会

---

**如切如磋，如琢如磨。**
**南有乔木，不可休思。**
"""
        return summary


# 使用示例
if __name__ == "__main__":
    nanqiao = NanqiaoLeaderEnhanced()

    print("=" * 50)
    print("🌿 南乔 - 团队Leader演示")
    print("=" * 50)

    # 分析请求
    print("\n📋 分析少帅请求...")

    analysis = nanqiao.analyze_request(
        "帮我完成湖北电信AI智能配案系统的需求分析和架构设计"
    )

    print(f"请求ID: {analysis['request_id']}")
    print(f"意图: {analysis['intent']}")
    print(f"分配Agent: {', '.join(analysis['assigned_agents'])}")
    print(f"工作流: {' → '.join(analysis['workflow'])}")

    # 协调团队
    print("\n" + "=" * 50)
    print("🚀 协调团队执行...")

    coordination = nanqiao.coordinate_team(analysis)

    print(f"协调ID: {coordination['coordination_id']}")
    print(f"\n任务分配:")
    for assignment in coordination['assignments']:
        print(f"  {assignment['agent']} ({assignment['role']}): {assignment['skill']}")

    # 监控执行
    print("\n" + "=" * 50)
    print("📊 监控执行进度...")

    execution = nanqiao.monitor_execution(coordination['coordination_id'])

    print(f"整体进度: {execution['overall_progress']}%")
    for agent_status in execution['agent_status']:
        print(f"  {agent_status['agent']}: {agent_status['status']} ({agent_status['progress']}%)")

    # 提供建议
    print("\n" + "=" * 50)
    print("💡 为少帅提供建议...")

    advice = nanqiao.provide_advice("工期紧张，技术选型需要决策")
    print(advice)

    # 生成报告
    print("\n" + "=" * 50)
    print("📄 生成Leader报告...")

    report = nanqiao.generate_leader_report("daily")
    print(report[:500] + "...")

    # 今日总结
    print("\n" + "=" * 50)
    print("📝 今日工作总结...")

    summary = nanqiao.summarize_day()
    print(summary[:400] + "...")
