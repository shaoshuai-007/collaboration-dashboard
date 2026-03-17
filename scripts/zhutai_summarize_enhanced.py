#!/usr/bin/env python3
"""
筑台 - 售前工程师增强模块
集成summarize技能，快速分析客户需求和竞品信息
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ZhutaiSummarizeEnhanced:
    """筑台的售前工程增强类"""

    def __init__(self):
        self.name = "筑台"
        self.role = "售前工程师"
        self.skill = "summarize"
        self.workspace = Path("/tmp/zhutai-workspace")
        self.workspace.mkdir(exist_ok=True)

    def analyze_customer_requirement(self, requirement_text: str) -> dict:
        """
        分析客户需求

        Args:
            requirement_text: 需求文本

        Returns:
            需求分析结果
        """
        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "original_length": len(requirement_text),
            "key_points": [],
            "pain_points": [],
            "budget_hints": [],
            "timeline_hints": [],
            "decision_makers": []
        }

        # 关键点提取
        keywords = ["核心需求", "主要目标", "关键指标", "验收标准"]
        for kw in keywords:
            if kw in requirement_text:
                analysis["key_points"].append(f"发现关键词: {kw}")

        # 痛点识别
        pain_keywords = ["痛点", "问题", "困难", "挑战", "不足"]
        for pk in pain_keywords:
            if pk in requirement_text:
                analysis["pain_points"].append(f"识别到痛点关键词: {pk}")

        # 预算线索
        budget_keywords = ["预算", "投资", "金额", "费用", "成本"]
        for bk in budget_keywords:
            if bk in requirement_text:
                analysis["budget_hints"].append(f"发现预算线索: {bk}")

        # 时间线索
        time_keywords = ["期限", "截止", "上线", "交付", "里程碑"]
        for tk in time_keywords:
            if tk in requirement_text:
                analysis["timeline_hints"].append(f"发现时间线索: {tk}")

        return analysis

    def generate_quotation(self, items: list, discount: float = 1.0) -> dict:
        """
        生成报价单

        Args:
            items: 项目列表
            discount: 折扣系数

        Returns:
            报价单
        """
        quotation = {
            "quote_id": f"QT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "valid_until": "30天",
            "items": [],
            "subtotal": 0,
            "discount": discount,
            "total": 0
        }

        for item in items:
            line_item = {
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("unit_price", 0),
                "amount": item.get("quantity", 1) * item.get("unit_price", 0)
            }
            quotation["items"].append(line_item)
            quotation["subtotal"] += line_item["amount"]

        quotation["total"] = quotation["subtotal"] * discount

        return quotation

    def generate_sales_proposal(self, client: str, requirements: str, solution: str) -> str:
        """
        生成销售建议书

        Args:
            client: 客户名称
            requirements: 需求描述
            solution: 解决方案

        Returns:
            销售建议书
        """
        proposal = f"""
# {client}项目销售建议书

**编制单位**: 九星智囊团
**编制日期**: {datetime.now().strftime('%Y年%m月%d日')}
**售前工程师**: 筑台

---

## 一、客户需求分析

{requirements}

### 1.1 核心需求

- 需求点1：业务效率提升
- 需求点2：成本控制优化
- 需求点3：客户体验改善

### 1.2 关键痛点

| 痛点 | 影响 | 紧急度 |
|------|------|:------:|
| 人工效率低 | 运营成本高 | 高 |
| 服务不精准 | 客户流失 | 高 |
| 数据分散 | 决策困难 | 中 |

## 二、解决方案

{solution}

### 2.1 方案亮点

1. **技术先进**：采用最新AI技术，行业领先
2. **快速落地**：标准产品+定制开发，缩短交付周期
3. **效果显著**：预期效率提升5倍以上

### 2.2 实施路径

```
第一阶段：需求调研（2周）
    ↓
第二阶段：方案设计（2周）
    ↓
第三阶段：开发测试（6周）
    ↓
第四阶段：试运行（2周）
    ↓
第五阶段：正式上线（1周）
```

## 三、投资回报分析

### 3.1 投资估算

| 项目 | 金额（万元） | 占比 |
|------|:-----------:|:----:|
| 软件许可 | 30 | 20% |
| 开发实施 | 80 | 53% |
| 数据服务 | 20 | 13% |
| 培训服务 | 10 | 7% |
| 运维支持 | 10 | 7% |
| **合计** | **150** | 100% |

### 3.2 收益预测

| 指标 | 当前值 | 预期值 | 年化收益 |
|------|:------:|:------:|:--------:|
| 人工成本 | 100万/年 | 60万/年 | 节省40万 |
| 业务收入 | 500万/年 | 600万/年 | 增加100万 |
| 客户满意度 | 70% | 90% | 品牌价值提升 |

### 3.3 投资回报

- **投资回收期**：1.5年
- **投资回报率**：93%
- **净现值（3年）**：150万元

## 四、竞争优势

| 对比项 | 九星方案 | 竞品A | 竞品B |
|--------|---------|-------|-------|
| 技术架构 | 微服务+AI | 传统单体 | 混合架构 |
| 实施周期 | 10周 | 16周 | 12周 |
| 总投资 | 150万 | 200万 | 180万 |
| 定制能力 | 强 | 弱 | 中 |

## 五、风险提示

1. **技术风险**：AI模型需要持续优化，建议预留调优时间
2. **数据风险**：数据质量影响效果，建议提前进行数据治理
3. **变革风险**：业务流程变化需要组织变革管理

## 六、下一步行动

1. 安排技术交流会（本周）
2. 提供POC演示环境（下周）
3. 签订合作框架协议（两周内）

---

**联系方式**

售前工程师：筑台
电话：400-XXX-XXXX
邮箱：zhutai@ninestars.com

---

*九星智囊团 - 以智为针，以信为盘*
"""
        return proposal

    def generate_competitor_analysis(self, competitors: list) -> dict:
        """
        生成竞品分析

        Args:
            competitors: 竞品列表

        Returns:
            竞品分析报告
        """
        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "competitors": []
        }

        for comp in competitors:
            competitor = {
                "name": comp.get("name", ""),
                "strengths": comp.get("strengths", []),
                "weaknesses": comp.get("weaknesses", []),
                "pricing": comp.get("pricing", "未知"),
                "market_share": comp.get("market_share", "未知"),
                "our_advantage": comp.get("our_advantage", [])
            }
            analysis["competitors"].append(competitor)

        return analysis

    def generate_talking_points(self, scenario: str) -> list:
        """
        生成销售话术

        Args:
            scenario: 场景

        Returns:
            话术列表
        """
        talking_points = {
            "开场白": [
                "您好，我是九星智囊团的售前工程师筑台，我们专注于电信行业智能化转型。",
                "感谢您抽出时间，我今天想向您介绍我们的AI智能配案解决方案。",
                "在开始之前，能了解一下您当前在业务办理方面遇到的主要挑战吗？"
            ],
            "需求确认": [
                "您提到的这个痛点，我们在其他客户那里也经常听到。",
                "能具体说说，这个问题对您的业务影响有多大吗？",
                "除了这个，还有其他让您头疼的问题吗？"
            ],
            "方案介绍": [
                "我们的解决方案正是针对您提到的这个问题设计的。",
                "通过AI技术，我们可以帮助您将配案效率提升5倍。",
                "让我给您演示一下具体效果。"
            ],
            "异议处理": [
                "我理解您的顾虑，这个投资确实不小，但您看，投资回报期只有1.5年。",
                "关于实施风险，我们有成熟的交付方法论，成功率100%。",
                "数据安全方面，我们符合等保三级要求，您完全不用担心。"
            ],
            "促成成交": [
                "我们可以在本周安排一次技术交流，您看周二还是周四方便？",
                "我可以为您申请一个POC演示环境，您可以先体验一下效果。",
                "如果您现在能确定合作意向，我可以为您争取特别优惠。"
            ]
        }

        return talking_points.get(scenario, [])


# 使用示例
if __name__ == "__main__":
    zhutai = ZhutaiSummarizeEnhanced()

    print("=" * 50)
    print("🏗️ 筑台 - 售前工程演示")
    print("=" * 50)

    # 分析客户需求
    print("\n📋 分析客户需求...")

    requirement = """
    湖北电信希望提升营业厅配案效率，当前人工配案耗时15分钟，
    客户等待时间长，投诉率高达8%。核心痛点是缺乏智能化工具，
    营业员需要手动查询多个系统。预算约200万，要求3个月内上线。
    """

    analysis = zhutai.analyze_customer_requirement(requirement)

    print(f"原文长度: {analysis['original_length']} 字符")
    print(f"关键点: {len(analysis['key_points'])} 个")
    print(f"痛点: {len(analysis['pain_points'])} 个")
    print(f"预算线索: {len(analysis['budget_hints'])} 个")
    print(f"时间线索: {len(analysis['timeline_hints'])} 个")

    # 生成报价单
    print("\n" + "=" * 50)
    print("💰 生成报价单...")

    quotation = zhutai.generate_quotation(
        items=[
            {"name": "软件许可费", "description": "AI智能配案系统", "quantity": 1, "unit_price": 300000},
            {"name": "实施服务费", "description": "需求分析+开发+测试", "quantity": 1, "unit_price": 800000},
            {"name": "数据服务费", "description": "数据接入+清洗", "quantity": 1, "unit_price": 200000},
            {"name": "培训服务费", "description": "用户培训", "quantity": 1, "unit_price": 100000},
            {"name": "运维服务费", "description": "一年运维支持", "quantity": 1, "unit_price": 100000}
        ],
        discount=0.95
    )

    print(f"报价单号: {quotation['quote_id']}")
    print(f"项目数量: {len(quotation['items'])}")
    print(f"小计: {quotation['subtotal']:,.0f} 元")
    print(f"折扣: {quotation['discount']*100:.0f}%")
    print(f"总计: {quotation['total']:,.0f} 元")

    # 生成销售话术
    print("\n" + "=" * 50)
    print("💬 生成销售话术...")

    scenarios = ["开场白", "需求确认", "方案介绍", "异议处理", "促成成交"]

    for scenario in scenarios:
        points = zhutai.generate_talking_points(scenario)
        print(f"\n【{scenario}】")
        for i, point in enumerate(points, 1):
            print(f"  {i}. {point}")

    # 生成竞品分析
    print("\n" + "=" * 50)
    print("🔍 生成竞品分析...")

    competitor_analysis = zhutai.generate_competitor_analysis(
        competitors=[
            {
                "name": "竞品A",
                "strengths": ["品牌知名度高", "功能全面"],
                "weaknesses": ["价格昂贵", "定制能力弱"],
                "pricing": "200万",
                "market_share": "30%",
                "our_advantage": ["性价比高", "定制能力强", "实施周期短"]
            },
            {
                "name": "竞品B",
                "strengths": ["价格适中", "本地化服务"],
                "weaknesses": ["技术落后", "功能单一"],
                "pricing": "180万",
                "market_share": "20%",
                "our_advantage": ["技术领先", "功能丰富", "AI能力"]
            }
        ]
    )

    print(f"\n分析时间: {competitor_analysis['analyzed_at']}")
    print(f"竞品数量: {len(competitor_analysis['competitors'])}")
    for comp in competitor_analysis['competitors']:
        print(f"\n  {comp['name']}:")
        print(f"    优势: {', '.join(comp['strengths'])}")
        print(f"    劣势: {', '.join(comp['weaknesses'])}")
        print(f"    我们的优势: {', '.join(comp['our_advantage'])}")
