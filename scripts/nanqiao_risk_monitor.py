#!/usr/bin/env python3
"""
南乔风险预警系统 V1.0
智能风险识别与预警
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class NanqiaoRiskMonitor:
    """南乔的风险预警系统"""

    def __init__(self):
        self.name = "南乔风险预警系统"
        self.version = "1.0.0"
        self.workspace = Path("/root/.openclaw/workspace/风险日志")
        self.workspace.mkdir(exist_ok=True)

        # 风险关键词库
        self.risk_keywords = {
            "进度风险": {
                "关键词": ["延期", "延迟", "进度落后", "来不及", "赶工"],
                "概率": 0.7,
                "影响": 0.8,
                "应对": ["调整计划", "增加资源", "拆分任务"]
            },
            "技术风险": {
                "关键词": ["技术障碍", "不会", "搞不定", "bug", "错误"],
                "概率": 0.6,
                "影响": 0.9,
                "应对": ["技术攻关", "寻求支持", "方案调整"]
            },
            "资源风险": {
                "关键词": ["人手不足", "资源不够", "没人", "忙不过来"],
                "概率": 0.5,
                "影响": 0.7,
                "应对": ["资源调配", "外部支持", "优先级调整"]
            },
            "需求风险": {
                "关键词": ["需求变更", "需求不明确", "改需求", "新增需求"],
                "概率": 0.8,
                "影响": 0.6,
                "应对": ["需求冻结", "变更流程", "影响评估"]
            },
            "干系人风险": {
                "关键词": ["联系不上", "找不到人", "不回复", "失联"],
                "概率": 0.6,
                "影响": 0.5,
                "应对": ["多渠道联系", "向上汇报", "备选方案"]
            }
        }

        # 风险事件记录
        self.risk_events = []

    def identify_risks(self, text: str, context: Dict = None) -> List[Dict]:
        """
        风险识别
        """
        risks = []

        for risk_type, config in self.risk_keywords.items():
            for keyword in config["关键词"]:
                if keyword in text:
                    risk = {
                        "risk_id": f"RISK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(risks)+1}",
                        "type": risk_type,
                        "keyword": keyword,
                        "probability": config["概率"],
                        "impact": config["影响"],
                        "risk_score": config["概率"] * config["影响"],
                        "risk_level": self._calculate_risk_level(config["概率"] * config["影响"]),
                        "suggestions": config["应对"],
                        "detected_at": datetime.now().isoformat(),
                        "source_text": text
                    }
                    risks.append(risk)
                    break  # 每种风险类型只记录一次

        return risks

    def _calculate_risk_level(self, risk_score: float) -> str:
        """
        计算风险等级
        """
        if risk_score >= 0.6:
            return "🔴 高"
        elif risk_score >= 0.4:
            return "🟡 中"
        else:
            return "🟢 低"

    def check_stakeholder_status(self, stakeholder: str, last_contact_date: str) -> Dict:
        """
        干系人状态检查
        """
        last_contact = datetime.strptime(last_contact_date, "%Y-%m-%d")
        days_since_contact = (datetime.now() - last_contact).days

        if days_since_contact >= 15:
            risk_level = "🔴 高"
            message = f"【风险预警】{stakeholder}已{days_since_contact}天未联系，请尽快安排沟通"
            action = "立即安排电话或当面沟通"
        elif days_since_contact >= 10:
            risk_level = "🟡 中"
            message = f"【提醒】{stakeholder}已{days_since_contact}天未联系，建议近期安排沟通"
            action = "本周内安排沟通"
        else:
            risk_level = "🟢 低"
            message = f"{stakeholder}联系状态正常"
            action = "保持定期沟通"

        return {
            "stakeholder": stakeholder,
            "last_contact": last_contact_date,
            "days_since_contact": days_since_contact,
            "risk_level": risk_level,
            "message": message,
            "suggested_action": action
        }

    def generate_risk_report(self, risks: List[Dict] = None) -> str:
        """
        生成风险报告
        """
        if risks is None:
            risks = self.risk_events

        report = f"""
# 🌿 风险预警报告

**报告时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
**报告人**: 南乔

---

## 一、风险概览

| 风险等级 | 数量 | 占比 |
|:--------:|:----:|:----:|
| 🔴 高 | {len([r for r in risks if '高' in r.get('risk_level', '')])} | {len([r for r in risks if '高' in r.get('risk_level', '')]) / max(len(risks), 1) * 100:.0f}% |
| 🟡 中 | {len([r for r in risks if '中' in r.get('risk_level', '')])} | {len([r for r in risks if '中' in r.get('risk_level', '')]) / max(len(risks), 1) * 100:.0f}% |
| 🟢 低 | {len([r for r in risks if '低' in r.get('risk_level', '')])} | {len([r for r in risks if '低' in r.get('risk_level', '')]) / max(len(risks), 1) * 100:.0f}% |

## 二、风险详情

"""
        for i, risk in enumerate(risks, 1):
            report += f"""
### 风险 {i}: {risk.get('type', '未知')}

- **风险等级**: {risk.get('risk_level', '未知')}
- **风险评分**: {risk.get('risk_score', 0):.2f}
- **触发关键词**: {risk.get('keyword', '未知')}
- **应对建议**: {', '.join(risk.get('suggestions', []))}

"""

        report += f"""
---

**🌿 南乔 | 九星智囊团**
*南有乔木，不可休思*
"""
        return report


# 演示
if __name__ == "__main__":
    monitor = NanqiaoRiskMonitor()

    print("=" * 60)
    print("🌿 南乔风险预警系统 V1.0 演示")
    print("=" * 60)

    # 测试案例1：风险识别
    print("\n📋 风险识别演示...")

    test_texts = [
        "项目进度有点延期，可能来不及完成",
        "这个技术问题我们搞不定，需要寻求支持",
        "万必波已经15天没有联系了",
        "客户又改需求了，需要重新评估"
    ]

    all_risks = []
    for text in test_texts:
        risks = monitor.identify_risks(text)
        if risks:
            all_risks.extend(risks)
            for risk in risks:
                print(f"\n   ⚠️ {risk['type']}: {risk['risk_level']}")
                print(f"      关键词: {risk['keyword']}")
                print(f"      应对: {', '.join(risk['suggestions'])}")

    # 测试案例2：干系人状态检查
    print("\n" + "=" * 60)
    print("👥 干系人状态检查...")

    stakeholders = [
        ("万必波", "2026-03-01"),
        ("万海波", "2026-03-01"),
        ("关主任", "2026-03-10")
    ]

    for name, last_contact in stakeholders:
        result = monitor.check_stakeholder_status(name, last_contact)
        print(f"\n   {result['stakeholder']}: {result['risk_level']}")
        print(f"      {result['message']}")
        print(f"      建议: {result['suggested_action']}")

    # 生成报告
    print("\n" + "=" * 60)
    print("📄 生成风险报告...")

    report = monitor.generate_risk_report(all_risks)
    print(report[:600] + "...")
