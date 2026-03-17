#!/usr/bin/env python3
"""
九星智囊团训练管理系统 V1.0
实现团队训练任务的分配、执行、评估、反馈
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class TeamTrainingManager:
    """团队训练管理系统"""

    def __init__(self):
        self.name = "九星智囊团训练管理系统"
        self.version = "1.0.0"
        self.workspace = Path("/root/.openclaw/workspace/训练记录")
        self.workspace.mkdir(exist_ok=True)

        # 团队成员
        self.agents = {
            "采薇": {"role": "需求分析师", "level": "A级", "score": 90},
            "织锦": {"role": "架构设计师", "level": "A级", "score": 90},
            "呈彩": {"role": "方案设计师", "level": "A级", "score": 90},
            "工尺": {"role": "系统设计师", "level": "A级", "score": 90},
            "玉衡": {"role": "项目经理", "level": "A级", "score": 90},
            "筑台": {"role": "售前工程师", "level": "A级", "score": 90},
            "折桂": {"role": "资源管家", "level": "A级", "score": 90},
            "扶摇": {"role": "总指挥", "level": "A级", "score": 90},
            "南乔": {"role": "用户助手", "level": "A级", "score": 90}
        }

        # 训练任务库
        self.training_tasks = {
            "采薇": [
                {"task": "电信业务流程需求分析", "difficulty": 1, "duration": "1天"},
                {"task": "AI系统需求文档编写", "difficulty": 2, "duration": "1天"},
                {"task": "复杂业务需求分析", "difficulty": 3, "duration": "2天"}
            ],
            "织锦": [
                {"task": "微服务架构设计", "difficulty": 1, "duration": "1天"},
                {"task": "AI系统架构设计", "difficulty": 2, "duration": "2天"},
                {"task": "分布式系统架构设计", "difficulty": 3, "duration": "3天"}
            ],
            "呈彩": [
                {"task": "产品方案PPT制作", "difficulty": 1, "duration": "0.5天"},
                {"task": "技术方案PPT制作", "difficulty": 2, "duration": "1天"},
                {"task": "大型汇报PPT制作", "difficulty": 3, "duration": "2天"}
            ],
            "工尺": [
                {"task": "RESTful API设计", "difficulty": 1, "duration": "0.5天"},
                {"task": "数据库表设计", "difficulty": 2, "duration": "1天"},
                {"task": "系统集成设计", "difficulty": 3, "duration": "2天"}
            ],
            "玉衡": [
                {"task": "项目计划制定", "difficulty": 1, "duration": "0.5天"},
                {"task": "风险识别与管理", "difficulty": 2, "duration": "1天"},
                {"task": "复杂项目管控", "difficulty": 3, "duration": "2天"}
            ],
            "筑台": [
                {"task": "产品报价单制作", "difficulty": 1, "duration": "0.5天"},
                {"task": "售前方案编写", "difficulty": 2, "duration": "1天"},
                {"task": "投标文件准备", "difficulty": 3, "duration": "2天"}
            ],
            "折桂": [
                {"task": "知识分类整理", "difficulty": 1, "duration": "0.5天"},
                {"task": "知识图谱构建", "difficulty": 2, "duration": "1天"},
                {"task": "智能检索系统设计", "difficulty": 3, "duration": "2天"}
            ],
            "扶摇": [
                {"task": "团队协调模拟", "difficulty": 1, "duration": "1天"},
                {"task": "多项目调度", "difficulty": 2, "duration": "1天"},
                {"task": "复杂项目协调", "difficulty": 3, "duration": "2天"}
            ]
        }

        # 训练记录
        self.training_records = []

    def assign_training_task(self, agent: str, week: int) -> Dict:
        """分配训练任务"""
        if agent not in self.training_tasks:
            return {"error": f"Agent {agent} 不存在"}

        tasks = self.training_tasks[agent]

        # 根据周次选择任务难度
        if week <= 1:
            difficulty = 1
        elif week <= 2:
            difficulty = 2
        else:
            difficulty = 3

        # 选择对应难度的任务
        task = [t for t in tasks if t["difficulty"] == difficulty][0]

        assignment = {
            "assignment_id": f"TRAIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "agent": agent,
            "task": task["task"],
            "difficulty": task["difficulty"],
            "duration": task["duration"],
            "assigned_at": datetime.now().isoformat(),
            "status": "pending"
        }

        self.training_records.append(assignment)
        self._save_training_record(assignment)

        return assignment

    def evaluate_training_result(self, assignment_id: str, result: Dict) -> Dict:
        """评估训练结果"""
        # 查找对应任务
        assignment = None
        for record in self.training_records:
            if record["assignment_id"] == assignment_id:
                assignment = record
                break

        if not assignment:
            return {"error": "任务不存在"}

        # 评分
        score = self._calculate_score(result)

        # 更新记录
        assignment["status"] = "completed"
        assignment["score"] = score
        assignment["completed_at"] = datetime.now().isoformat()
        assignment["feedback"] = self._generate_feedback(score)

        # 更新Agent能力
        agent = assignment["agent"]
        if agent in self.agents:
            old_score = self.agents[agent]["score"]
            new_score = round((old_score * 0.8 + score * 0.2), 1)
            self.agents[agent]["score"] = new_score

            # 更新等级
            if new_score >= 95:
                self.agents[agent]["level"] = "A+级"
            elif new_score >= 90:
                self.agents[agent]["level"] = "A级"

        self._save_training_record(assignment)

        return {
            "assignment_id": assignment_id,
            "score": score,
            "level": self._get_score_level(score),
            "feedback": assignment["feedback"]
        }

    def _calculate_score(self, result: Dict) -> float:
        """计算训练得分"""
        # 基础分
        base_score = 80

        # 完整性（10分）
        if result.get("完整性"):
            base_score += 10

        # 正确性（5分）
        if result.get("正确性"):
            base_score += 5

        # 专业性（5分）
        if result.get("专业性"):
            base_score += 5

        return min(base_score, 100)

    def _get_score_level(self, score: float) -> str:
        """获取分数等级"""
        if score >= 95:
            return "A+级"
        elif score >= 90:
            return "A级"
        elif score >= 80:
            return "B级"
        else:
            return "C级"

    def _generate_feedback(self, score: float) -> str:
        """生成反馈意见"""
        if score >= 95:
            return "优秀！继续保持！"
        elif score >= 90:
            return "良好，有提升空间"
        elif score >= 80:
            return "合格，需要加强"
        else:
            return "不合格，需要重新训练"

    def _save_training_record(self, record: Dict):
        """保存训练记录"""
        record_file = self.workspace / f"{record['assignment_id']}.json"
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    def generate_training_report(self, week: int) -> str:
        """生成训练报告"""
        report = f"""
# 九星智囊团训练周报 - 第{week}周

**报告时间**: {datetime.now().strftime('%Y年%m月%d日')}
**报告人**: 🌿 南乔

---

## 一、训练概览

| Agent | 角色 | 当前等级 | 当前分数 |
|:-----:|------|:--------:|:--------:|
"""
        for agent, info in self.agents.items():
            report += f"| {agent} | {info['role']} | {info['level']} | {info['score']} |\n"

        report += f"""
---

## 二、本周训练任务

"""
        for agent in self.agents.keys():
            # 直接从任务库选择任务，不保存记录
            if agent in self.training_tasks:
                tasks = self.training_tasks[agent]
                if week <= 1:
                    difficulty = 1
                elif week <= 2:
                    difficulty = 2
                else:
                    difficulty = 3
                task = [t for t in tasks if t["difficulty"] == difficulty][0]
                report += f"### {agent}\n"
                report += f"- 任务：{task['task']}\n"
                report += f"- 难度：{'⭐' * task['difficulty']}\n"
                report += f"- 时长：{task['duration']}\n\n"

        report += f"""
---

## 三、下周计划

- 继续知识武装
- 提升训练难度
- 加强协作演练

---

*🌿 南乔 | 九星智囊团*
"""
        return report


# 演示
if __name__ == "__main__":
    manager = TeamTrainingManager()

    print("=" * 60)
    print("🎯 九星智囊团训练管理系统 V1.0 演示")
    print("=" * 60)

    # 分配训练任务
    print("\n📋 分配训练任务...")
    for agent in ["采薇", "织锦", "呈彩"]:
        assignment = manager.assign_training_task(agent, 1)
        print(f"\n   {agent}: {assignment['task']}")
        print(f"   难度: {'⭐' * assignment['difficulty']}")
        print(f"   时长: {assignment['duration']}")

    # 评估训练结果
    print("\n" + "=" * 60)
    print("📊 评估训练结果...")

    result = {
        "完整性": True,
        "正确性": True,
        "专业性": True
    }

    for record in manager.training_records[:1]:
        evaluation = manager.evaluate_training_result(record["assignment_id"], result)
        print(f"\n   任务ID: {evaluation['assignment_id']}")
        print(f"   得分: {evaluation['score']}分")
        print(f"   等级: {evaluation['level']}")
        print(f"   反馈: {evaluation['feedback']}")

    # 生成报告
    print("\n" + "=" * 60)
    print("📄 生成训练报告...")
    report = manager.generate_training_report(1)
    print(report[:800] + "...")
