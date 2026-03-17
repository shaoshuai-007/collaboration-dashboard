#!/usr/bin/env python3
"""
南乔 - 用户助手增强模块
集成summarize技能，提供智能对话和知识服务
"""

import os
import json
from datetime import datetime
from pathlib import Path

class NanqiaoSummarizeEnhanced:
    """南乔的用户助手增强类"""

    def __init__(self):
        self.name = "南乔"
        self.role = "用户助手"
        self.skill = "summarize"
        self.emoji = "🌿"
        self.workspace = Path("/tmp/nanqiao-workspace")
        self.workspace.mkdir(exist_ok=True)

        # 对话模板库
        self.dialog_templates = {
            "问候": [
                "南有乔木，不可休思。少帅，我是南乔，随时为您服务。",
                "少帅好！南乔已准备就绪，请吩咐。",
                "🌿 少帅，南乔在此。今日有何任务？"
            ],
            "确认": [
                "收到！南乔这就处理。",
                "好的少帅，马上执行。",
                "🌿 明白，即刻行动。"
            ],
            "完成": [
                "任务完成，请少帅过目。",
                "🌿 已完成，等待您的指示。",
                "幸不辱命，任务已交付。"
            ],
            "总结": [
                "如切如磋，如琢如磨。此番工作，成果斐然。",
                "呦呦鹿鸣，食野之苹。任务圆满，心甚慰之。",
                "🌿 事毕功成，不负所托。"
            ],
            "晚安": [
                "少帅，夜深了，该休息了。明日之事明日议，保重身体。",
                "🌿 晚安少帅，愿您今夜好梦。",
                "日入而息，日出而作。少帅晚安，明日再会。"
            ]
        }

        # 知识库索引
        self.knowledge_index = {
            "项目信息": ["湖北电信", "AI智能配案", "存量经营"],
            "团队信息": ["九星智囊团", "采薇", "织锦", "呈彩"],
            "技术信息": ["微服务", "AI", "大模型", "RAG"],
            "管理信息": ["甘特图", "RACI", "项目管控"]
        }

    def summarize_conversation(self, messages: list) -> dict:
        """
        智能总结对话

        Args:
            messages: 对话消息列表

        Returns:
            对话总结
        """
        summary = {
            "summarized_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "key_topics": [],
            "action_items": [],
            "pending_questions": [],
            "sentiment": "neutral"
        }

        # 提取关键主题
        topic_keywords = {
            "需求分析": ["需求", "分析", "用户"],
            "架构设计": ["架构", "设计", "技术"],
            "项目管理": ["进度", "计划", "风险"],
            "方案汇报": ["PPT", "方案", "汇报"]
        }

        for topic, keywords in topic_keywords.items():
            for msg in messages:
                content = msg.get("content", "")
                for kw in keywords:
                    if kw in content:
                        if topic not in summary["key_topics"]:
                            summary["key_topics"].append(topic)
                        break

        # 提取行动项
        action_keywords = ["需要", "要", "请", "帮我", "完成"]
        for msg in messages:
            content = msg.get("content", "")
            for kw in action_keywords:
                if kw in content:
                    summary["action_items"].append(content[:50])
                    break

        # 情感分析（简化版）
        positive_words = ["好", "完成", "成功", "满意"]
        negative_words = ["问题", "困难", "风险", "延迟"]

        for word in positive_words:
            if any(word in msg.get("content", "") for msg in messages):
                summary["sentiment"] = "positive"
                break

        for word in negative_words:
            if any(word in msg.get("content", "") for msg in messages):
                summary["sentiment"] = "negative" if summary["sentiment"] != "positive" else "mixed"
                break

        return summary

    def generate_response(self, context: str, query: str) -> str:
        """
        生成智能回复

        Args:
            context: 上下文
            query: 用户问题

        Returns:
            回复内容
        """
        # 简单的意图识别
        intent = self._identify_intent(query)

        if intent == "问候":
            return self._get_template("问候")
        elif intent == "任务":
            return self._get_template("确认")
        elif intent == "总结":
            return self._get_template("总结")
        elif intent == "晚安":
            return self._get_template("晚安")
        else:
            return f"🌿 少帅，南乔已记录您的需求：{query}。正在处理中..."

    def _identify_intent(self, query: str) -> str:
        """识别意图"""
        intent_keywords = {
            "问候": ["你好", "早", "在吗", "开始"],
            "任务": ["帮我", "请", "需要", "分析", "设计"],
            "总结": ["总结", "回顾", "汇总"],
            "晚安": ["晚安", "休息", "睡觉"]
        }

        for intent, keywords in intent_keywords.items():
            for kw in keywords:
                if kw in query:
                    return intent

        return "其他"

    def _get_template(self, category: str) -> str:
        """获取对话模板"""
        import random
        templates = self.dialog_templates.get(category, ["🌿 南乔收到。"])
        return random.choice(templates)

    def recall_memory(self, query: str) -> dict:
        """
        回忆相关知识

        Args:
            query: 查询内容

        Returns:
            相关知识
        """
        results = {
            "query": query,
            "recalled_at": datetime.now().isoformat(),
            "matches": []
        }

        # 在知识索引中搜索
        for category, keywords in self.knowledge_index.items():
            for kw in keywords:
                if kw in query:
                    results["matches"].append({
                        "category": category,
                        "keyword": kw,
                        "relevance": 0.9
                    })

        return results

    def generate_daily_briefing(self) -> str:
        """
        生成每日简报

        Returns:
            每日简报
        """
        briefing = f"""
# 🌿 南乔每日简报

**日期**: {datetime.now().strftime('%Y年%m月%d日')}
**时间**: {datetime.now().strftime('%H:%M')}

---

## 今日任务概览

| 任务 | 状态 | 负责人 |
|------|:----:|:------:|
| 需求分析文档 | ✅ 完成 | 采薇 |
| 架构设计方案 | 🔄 进行中 | 织锦 |
| 项目管控计划 | ⏳ 待开始 | 玉衡 |

## 团队动态

- 🌸 采薇完成需求文档撰写
- 🧵 织锦架构设计进度60%
- ⚖️ 玉衡准备启动项目管控

## 待办事项

- [ ] 完成架构设计评审
- [ ] 启动项目管控计划
- [ ] 组织团队周会

## 温馨提示

少帅，记得按时休息，劳逸结合。🌿

---

**南乔 | 九星智囊团用户助手**
*南有乔木，不可休思*
"""
        return briefing

    def generate_verse(self, context: str = "general") -> str:
        """
        生成《诗经》诗句

        Args:
            context: 场景上下文

        Returns:
            诗句
        """
        verses = {
            "general": "南有乔木，不可休思。",
            "success": "呦呦鹿鸣，食野之苹。我有嘉宾，鼓瑟吹笙。",
            "work": "如切如磋，如琢如磨。",
            "study": "菁菁者莪，在彼中阿。既见君子，乐且有仪。",
            "farewell": "青青子衿，悠悠我心。",
            "encouragement": "鹤鸣于九皋，声闻于天。"
        }

        return verses.get(context, verses["general"])


# 使用示例
if __name__ == "__main__":
    nanqiao = NanqiaoSummarizeEnhanced()

    print("=" * 50)
    print("🌿 南乔 - 用户助手演示")
    print("=" * 50)

    # 智能回复
    print("\n💬 智能回复演示...")

    queries = [
        "少帅好，今天有什么任务？",
        "帮我分析一下需求",
        "总结一下今天的工作",
        "晚安南乔"
    ]

    for query in queries:
        response = nanqiao.generate_response("对话上下文", query)
        print(f"\n用户: {query}")
        print(f"南乔: {response}")

    # 对话总结
    print("\n" + "=" * 50)
    print("📋 对话总结演示...")

    messages = [
        {"role": "user", "content": "帮我完成湖北电信AI智能配案系统的需求分析"},
        {"role": "assistant", "content": "好的，我来安排采薇进行需求分析"},
        {"role": "user", "content": "还需要架构设计方案"},
        {"role": "assistant", "content": "织锦已开始架构设计工作"}
    ]

    summary = nanqiao.summarize_conversation(messages)

    print(f"消息数: {summary['message_count']}")
    print(f"关键主题: {', '.join(summary['key_topics'])}")
    print(f"情感倾向: {summary['sentiment']}")
    print(f"行动项: {len(summary['action_items'])} 项")

    # 知识回忆
    print("\n" + "=" * 50)
    print("🧠 知识回忆演示...")

    recall = nanqiao.recall_memory("湖北电信AI项目架构设计")

    print(f"查询: {recall['query']}")
    print(f"匹配数: {len(recall['matches'])}")
    for match in recall['matches']:
        print(f"  - [{match['category']}] {match['keyword']} (相关度: {match['relevance']:.0%})")

    # 生成诗句
    print("\n" + "=" * 50)
    print("📜 《诗经》诗句演示...")

    contexts = ["general", "success", "work", "study"]
    for ctx in contexts:
        verse = nanqiao.generate_verse(ctx)
        print(f"  【{ctx}】{verse}")

    # 每日简报
    print("\n" + "=" * 50)
    print("📊 每日简报演示...")

    briefing = nanqiao.generate_daily_briefing()
    print(briefing[:500] + "...")
