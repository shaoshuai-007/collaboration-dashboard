#!/usr/bin/env python3
"""
采薇 - 需求分析增强模块
集成summarize技能，快速理解客户需求
"""

import subprocess
import json
from pathlib import Path

class CaiweiSummarizeEnhanced:
    """采薇的需求分析增强类"""

    def __init__(self):
        self.name = "采薇"
        self.role = "需求分析师"
        self.skill = "summarize"

    def analyze_requirement(self, file_path: str, length: str = "medium") -> dict:
        """
        分析需求文档

        Args:
            file_path: 需求文档路径
            length: 摘要长度 (short/medium/long/xl)

        Returns:
            分析结果字典
        """
        # 使用summarize技能
        cmd = f'summarize "{file_path}" --length {length} --json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            try:
                summary = json.loads(result.stdout)
                return {
                    "success": True,
                    "summary": summary,
                    "file": file_path,
                    "length": length
                }
            except:
                return {
                    "success": False,
                    "error": "JSON解析失败",
                    "raw_output": result.stdout
                }
        else:
            return {
                "success": False,
                "error": result.stderr
            }

    def extract_key_points(self, requirement_text: str) -> dict:
        """
        从需求文本中提取关键点

        Args:
            requirement_text: 需求文本

        Returns:
            关键点字典
        """
        # 关键点提取逻辑
        key_points = {
            "项目背景": self._extract_section(requirement_text, "项目背景"),
            "业务痛点": self._extract_section(requirement_text, "业务痛点"),
            "核心功能": self._extract_section(requirement_text, "核心功能"),
            "验收标准": self._extract_section(requirement_text, "验收标准"),
            "技术要求": self._extract_section(requirement_text, "技术")
        }
        return key_points

    def _extract_section(self, text: str, keyword: str) -> list:
        """提取包含关键词的段落"""
        lines = text.split('\n')
        results = []
        for i, line in enumerate(lines):
            if keyword in line:
                # 提取该段落
                paragraph = [line]
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        paragraph.append(lines[j])
                    else:
                        break
                results.append('\n'.join(paragraph))
        return results

    def generate_user_stories(self, requirement_text: str) -> list:
        """
        从需求文本生成用户故事

        Args:
            requirement_text: 需求文本

        Returns:
            用户故事列表
        """
        user_stories = []

        # 简单的用户故事生成逻辑
        story_templates = [
            "作为一个{角色}，我希望{功能}，以便{价值}",
            "作为一个{角色}，我需要{功能}，这样{原因}"
        ]

        # 提取功能点
        functions = self._extract_functions(requirement_text)

        for func in functions:
            story = {
                "id": f"US-{len(user_stories)+1}",
                "role": "营业员",  # 默认角色
                "feature": func,
                "value": "提高工作效率",
                "format": f"作为一个营业员，我希望{func}，以便提高工作效率"
            }
            user_stories.append(story)

        return user_stories

    def _extract_functions(self, text: str) -> list:
        """从文本中提取功能点"""
        functions = []
        lines = text.split('\n')

        for line in lines:
            if '功能' in line and '：' in line:
                func = line.split('：')[-1].strip()
                if func:
                    functions.append(func)

        return functions[:5]  # 返回前5个

# 使用示例
if __name__ == "__main__":
    caiwei = CaiweiSummarizeEnhanced()

    # 分析需求文档
    result = caiwei.analyze_requirement("/tmp/sample_requirement.md")
    print(f"分析结果: {result}")

    # 提取关键点
    with open("/tmp/sample_requirement.md", "r") as f:
        text = f.read()

    key_points = caiwei.extract_key_points(text)
    print(f"\n关键点: {json.dumps(key_points, ensure_ascii=False, indent=2)}")

    # 生成用户故事
    stories = caiwei.generate_user_stories(text)
    print(f"\n用户故事: {json.dumps(stories, ensure_ascii=False, indent=2)}")
