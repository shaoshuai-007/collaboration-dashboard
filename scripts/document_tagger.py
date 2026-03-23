#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档打标工具 - Document Tagger
功能：为文档添加重要性标签，支持审核模式自动判断
创建时间：2026-03-23
创建者：南乔
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# 标准标签定义
STANDARD_TAGS = {
    # 用途标签（权重25%）
    "用途": {
        "[对外汇报]": "客户汇报、领导汇报、投标答辩",
        "[内部协作]": "团队协作、项目沟通、内部评审",
        "[个人草稿]": "学习笔记、草稿、测试文档",
    },
    
    # 审阅对象标签（权重25%）
    "审阅对象": {
        "[客户]": "外部客户、甲方",
        "[领导]": "公司领导、高层决策",
        "[团队]": "项目团队、内部团队",
        "[自己]": "个人使用",
    },
    
    # 业务价值标签（权重20%）
    "业务价值": {
        "[高价值]": "百万级项目、战略重点",
        "[中价值]": "十万级项目、常规项目",
        "[低价值]": "万级以下、测试学习",
    },
    
    # 影响范围标签（权重10%）
    "影响范围": {
        "[全局]": "公司层面、集团层面",
        "[部门]": "部门层面、中心层面",
        "[项目]": "项目层面、产品层面",
        "[个人]": "个人层面",
    },
    
    # 审核模式标签（手动指定）
    "审核模式": {
        "[半自动审核]": "重要文档，需人工确认每步",
        "[全自动审核]": "普通文档，自动完成审核",
    },
}


@dataclass
class DocumentTag:
    """文档标签"""
    category: str       # 类别
    tag: str           # 标签
    description: str   # 描述


class DocumentTagger:
    """文档打标工具"""
    
    def __init__(self):
        self.standard_tags = STANDARD_TAGS
    
    def list_all_tags(self) -> str:
        """列出所有标准标签"""
        lines = ["# 标准标签列表", "", "---", ""]
        
        for category, tags in self.standard_tags.items():
            lines.append(f"## {category}")
            lines.append("")
            lines.append("| 标签 | 适用场景 |")
            lines.append("|------|----------|")
            for tag, desc in tags.items():
                lines.append(f"| {tag} | {desc} |")
            lines.append("")
        
        return "\n".join(lines)
    
    def add_tags_to_document(self, file_path: str, tags: List[str], 
                              position: str = "header") -> str:
        """为文档添加标签
        
        Args:
            file_path: 文档路径
            tags: 标签列表，如 ["[对外汇报]", "[客户]", "[高价值]"]
            position: 标签位置，"header"（文件头部）或 "footer"（文件尾部）
        
        Returns:
            处理结果消息
        """
        try:
            # 读取文档
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 构建标签行
            tag_line = " ".join(tags)
            
            # 检查是否已有标签
            existing_tags = self.extract_existing_tags(content)
            if existing_tags:
                # 替换现有标签
                old_tag_line = " ".join(existing_tags)
                content = content.replace(old_tag_line, tag_line, 1)
            else:
                # 添加新标签
                if position == "header":
                    # 在标题后添加
                    lines = content.split("\n")
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith("#"):
                            insert_pos = i + 1
                            break
                    lines.insert(insert_pos, "")
                    lines.insert(insert_pos + 1, f"**标签**：{tag_line}")
                    lines.insert(insert_pos + 2, "")
                    content = "\n".join(lines)
                else:
                    # 在尾部添加
                    content += f"\n\n---\n\n**标签**：{tag_line}\n"
            
            # 写回文档
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return f"✅ 已为文档添加标签：{tag_line}"
        
        except Exception as e:
            return f"❌ 添加标签失败：{str(e)}"
    
    def extract_existing_tags(self, content: str) -> List[str]:
        """提取文档中已有的标签"""
        tags = []
        for category, tag_dict in self.standard_tags.items():
            for tag in tag_dict.keys():
                if tag in content:
                    tags.append(tag)
        return tags
    
    def suggest_tags(self, file_path: str, content: str = None) -> Dict[str, List[str]]:
        """推荐标签
        
        根据文档内容，推荐合适的标签
        """
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except:
                content = ""
        
        suggestions = {
            "用途": [],
            "审阅对象": [],
            "业务价值": [],
            "影响范围": [],
        }
        
        # 用途推荐
        if any(kw in content for kw in ["客户", "甲方", "汇报", "投标", "答辩"]):
            suggestions["用途"].append("[对外汇报]")
        elif any(kw in content for kw in ["团队", "项目组", "协作"]):
            suggestions["用途"].append("[内部协作]")
        else:
            suggestions["用途"].append("[个人草稿]")
        
        # 审阅对象推荐
        if any(kw in content for kw in ["电信", "移动", "联通", "银行"]):
            suggestions["审阅对象"].append("[客户]")
        elif any(kw in content for kw in ["领导", "高层", "决策"]):
            suggestions["审阅对象"].append("[领导]")
        else:
            suggestions["审阅对象"].append("[团队]")
        
        # 业务价值推荐
        if any(kw in content for kw in ["百万", "千万", "战略", "重点"]):
            suggestions["业务价值"].append("[高价值]")
        elif any(kw in content for kw in ["项目", "系统", "产品"]):
            suggestions["业务价值"].append("[中价值]")
        else:
            suggestions["业务价值"].append("[低价值]")
        
        # 影响范围推荐
        if any(kw in content for kw in ["公司", "集团", "全局"]):
            suggestions["影响范围"].append("[全局]")
        elif any(kw in content for kw in ["部门", "中心"]):
            suggestions["影响范围"].append("[部门]")
        else:
            suggestions["影响范围"].append("[项目]")
        
        return suggestions
    
    def generate_tagging_guide(self) -> str:
        """生成打标指南"""
        return """
# 文档打标指南

## 一、为什么需要打标？

文档打标可以帮助系统自动判断文档重要性，从而选择合适的审核模式：
- **重要文档** → 半自动审核，人工把关质量
- **普通文档** → 全自动审核，提高处理效率

## 二、如何打标？

在文档标题下方添加标签行：

```markdown
# 文档标题

**标签**：[对外汇报] [客户] [高价值] [全局]

正文内容...
```

## 三、标准标签体系

### 1. 用途标签（权重25%）

| 标签 | 得分 | 适用场景 |
|------|:----:|----------|
| [对外汇报] | 90 | 客户汇报、领导汇报、投标答辩 |
| [内部协作] | 60 | 团队协作、项目沟通、内部评审 |
| [个人草稿] | 30 | 学习笔记、草稿、测试文档 |

### 2. 审阅对象标签（权重25%）

| 标签 | 得分 | 适用场景 |
|------|:----:|----------|
| [客户] | 95 | 外部客户、甲方 |
| [领导] | 90 | 公司领导、高层决策 |
| [团队] | 60 | 项目团队、内部团队 |
| [自己] | 30 | 个人使用 |

### 3. 业务价值标签（权重20%）

| 标签 | 得分 | 适用场景 |
|------|:----:|----------|
| [高价值] | 90 | 百万级项目、战略重点 |
| [中价值] | 70 | 十万级项目、常规项目 |
| [低价值] | 50 | 万级以下、测试学习 |

### 4. 影响范围标签（权重10%）

| 标签 | 得分 | 适用场景 |
|------|:----:|----------|
| [全局] | 90 | 公司层面、集团层面 |
| [部门] | 70 | 部门层面、中心层面 |
| [项目] | 50 | 项目层面、产品层面 |
| [个人] | 30 | 个人层面 |

## 四、评分规则

**总分 = 用途×25% + 类型×20% + 审阅对象×25% + 业务价值×20% + 影响范围×10%**

**等级判断**：
- 总分 ≥ 80：重要文档 → 半自动审核
- 总分 60-79：较重要文档 → 半自动审核
- 总分 < 60：普通文档 → 全自动审核

## 五、打标示例

### 示例1：重要文档

```markdown
# 湖北电信AI智能配案系统方案PPT

**标签**：[对外汇报] [客户] [高价值] [项目]

## 1. 项目背景
...
```

**评估结果**：
- 用途：[对外汇报] = 90分
- 类型：方案PPT = 95分
- 审阅对象：[客户] = 95分
- 业务价值：[高价值] = 90分
- 影响范围：[项目] = 50分
- **总分**：90×25% + 95×20% + 95×25% + 90×20% + 50×10% = **87.5分**
- **等级**：重要 → 半自动审核

### 示例2：普通文档

```markdown
# 提示词工程学习笔记

**标签**：[个人草稿] [自己] [低价值] [个人]

## 一、提示词基础
...
```

**评估结果**：
- 用途：[个人草稿] = 30分
- 类型：其他 = 40分
- 审阅对象：[自己] = 30分
- 业务价值：[低价值] = 50分
- 影响范围：[个人] = 30分
- **总分**：30×25% + 40×20% + 30×25% + 50×20% + 30×10% = **36分**
- **等级**：普通 → 全自动审核

---

*打标让系统更智能，审核更精准！*
"""


def main():
    """测试入口"""
    print("\n" + "="*70)
    print("🏷️ 文档打标工具 - 测试")
    print("="*70)
    
    tagger = DocumentTagger()
    
    # 打印标签列表
    print("\n" + tagger.list_all_tags())
    
    # 测试标签推荐
    print("\n" + "="*70)
    print("📋 标签推荐测试")
    print("="*70)
    
    test_file = "知识库/方法论/需求文档模板_九星智囊团专属版.md"
    suggestions = tagger.suggest_tags(test_file)
    
    print(f"\n文档：{test_file}")
    print("\n推荐标签：")
    for category, tags in suggestions.items():
        print(f"  {category}：{tags[0] if tags else '无'}")


if __name__ == "__main__":
    main()
