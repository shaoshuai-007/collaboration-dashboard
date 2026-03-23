#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档重要性评估模型 - Document Importance Evaluator
功能：评估文档重要性，决定审核模式（半自动/全自动）
创建时间：2026-03-23
创建者：南乔
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DocumentPurpose(Enum):
    """文档用途"""
    EXTERNAL_REPORT = "对外汇报"      # 客户汇报、领导汇报
    INTERNAL_COLLAB = "内部协作"      # 团队协作、项目沟通
    PERSONAL_DRAFT = "个人草稿"       # 学习笔记、草稿


class DocumentType(Enum):
    """文档类型"""
    PROPOSAL_PPT = "方案PPT"
    DETAILED_DESIGN = "详细设计"
    REQUIREMENT_DOC = "需求文档"
    PROJECT_PLAN = "项目计划"
    MINDMAP = "思维导图"
    SOLUTION_TABLE = "方案举措"
    OTHER = "其他"


class ReviewAudience(Enum):
    """审阅对象"""
    CUSTOMER = "客户"          # 外部客户
    LEADERSHIP = "领导"        # 公司领导
    TEAM = "内部团队"          # 项目团队
    SELF = "自己"              # 个人使用


class BusinessValue(Enum):
    """业务价值"""
    HIGH = "高"      # 百万级项目
    MEDIUM = "中"    # 十万级项目
    LOW = "低"       # 万级以下


class ImpactScope(Enum):
    """影响范围"""
    GLOBAL = "全局"      # 公司层面
    DEPARTMENT = "部门"  # 部门层面
    PROJECT = "项目"     # 项目层面
    PERSONAL = "个人"    # 个人层面


@dataclass
class DocumentImportanceScore:
    """文档重要性评分"""
    purpose_score: float      # 用途得分
    type_score: float         # 类型得分
    audience_score: float     # 审阅对象得分
    value_score: float        # 业务价值得分
    scope_score: float        # 影响范围得分
    total_score: float        # 总分
    level: str                # 重要性等级
    recommended_mode: str     # 推荐审核模式


class DocumentImportanceEvaluator:
    """文档重要性评估器"""
    
    # 权重配置
    WEIGHTS = {
        "purpose": 0.25,
        "type": 0.20,
        "audience": 0.25,
        "value": 0.20,
        "scope": 0.10,
    }
    
    # 用途得分映射
    PURPOSE_SCORES = {
        DocumentPurpose.EXTERNAL_REPORT: 90,
        DocumentPurpose.INTERNAL_COLLAB: 60,
        DocumentPurpose.PERSONAL_DRAFT: 30,
    }
    
    # 类型得分映射
    TYPE_SCORES = {
        DocumentType.PROPOSAL_PPT: 95,      # 对外汇报，最重要
        DocumentType.DETAILED_DESIGN: 85,   # 技术决策，重要
        DocumentType.REQUIREMENT_DOC: 80,   # 业务基础，重要
        DocumentType.PROJECT_PLAN: 75,      # 资源分配，较重要
        DocumentType.MINDMAP: 50,           # 中间产物，一般
        DocumentType.SOLUTION_TABLE: 55,    # 中间产物，一般
        DocumentType.OTHER: 40,             # 其他，普通
    }
    
    # 审阅对象得分映射
    AUDIENCE_SCORES = {
        ReviewAudience.CUSTOMER: 95,
        ReviewAudience.LEADERSHIP: 90,
        ReviewAudience.TEAM: 60,
        ReviewAudience.SELF: 30,
    }
    
    # 业务价值得分映射
    VALUE_SCORES = {
        BusinessValue.HIGH: 90,
        BusinessValue.MEDIUM: 70,
        BusinessValue.LOW: 50,
    }
    
    # 影响范围得分映射
    SCOPE_SCORES = {
        ImpactScope.GLOBAL: 90,
        ImpactScope.DEPARTMENT: 70,
        ImpactScope.PROJECT: 50,
        ImpactScope.PERSONAL: 30,
    }
    
    def __init__(self):
        self.tag_patterns = self._build_tag_patterns()
        self.keyword_indicators = self._build_keyword_indicators()
    
    def _build_tag_patterns(self) -> dict:
        """构建标签识别模式"""
        return {
            # 用途标签
            "purpose": {
                r"\[对外汇报\]|\[客户汇报\]|\[领导汇报\]": DocumentPurpose.EXTERNAL_REPORT,
                r"\[内部协作\]|\[团队协作\]|\[项目沟通\]": DocumentPurpose.INTERNAL_COLLAB,
                r"\[草稿\]|\[笔记\]|\[个人\]": DocumentPurpose.PERSONAL_DRAFT,
            },
            # 审阅对象标签
            "audience": {
                r"\[客户\]|\[甲方\]|\[外部\]": ReviewAudience.CUSTOMER,
                r"\[领导\]|\[高层\]|\[汇报\]": ReviewAudience.LEADERSHIP,
                r"\[团队\]|\[项目组\]|\[内部\]": ReviewAudience.TEAM,
                r"\[个人\]|\[自己\]|\[私\]": ReviewAudience.SELF,
            },
            # 业务价值标签
            "value": {
                r"\[高价值\]|\[百万\]|\[重要\]": BusinessValue.HIGH,
                r"\[中价值\]|\[十万\]|\[一般\]": BusinessValue.MEDIUM,
                r"\[低价值\]|\[万级\]|\[普通\]": BusinessValue.LOW,
            },
            # 影响范围标签
            "scope": {
                r"\[全局\]|\[公司\]|\[集团\]": ImpactScope.GLOBAL,
                r"\[部门\]|\[中心\]|\[团队\]": ImpactScope.DEPARTMENT,
                r"\[项目\]|\[产品\]|\[系统\]": ImpactScope.PROJECT,
                r"\[个人\]|\[自己\]|\[私\]": ImpactScope.PERSONAL,
            },
        }
    
    def _build_keyword_indicators(self) -> dict:
        """构建关键词指示器"""
        return {
            # 用途关键词
            "purpose": {
                "external_keywords": ["客户", "甲方", "汇报", "答辩", "投标", "方案"],
                "internal_keywords": ["团队", "项目组", "协作", "评审", "讨论"],
                "draft_keywords": ["草稿", "笔记", "学习", "测试", "demo"],
            },
            # 审阅对象关键词
            "audience": {
                "customer_keywords": ["电信", "移动", "联通", "银行", "政府", "企业"],
                "leadership_keywords": ["总经理", "总监", "领导", "高层", "决策"],
                "team_keywords": ["开发", "测试", "产品", "运营", "团队"],
            },
            # 业务价值关键词
            "value": {
                "high_keywords": ["百万", "千万", "核心", "战略", "重点"],
                "medium_keywords": ["十万", "项目", "产品", "系统"],
                "low_keywords": ["万级", "测试", "学习", "实验"],
            },
        }
    
    def detect_document_type(self, file_path: str, content: str = None) -> DocumentType:
        """检测文档类型"""
        file_name = Path(file_path).name.lower()
        
        # 从文件名判断
        if "ppt" in file_name or "方案" in file_name:
            return DocumentType.PROPOSAL_PPT
        if "设计" in file_name or "详细" in file_name:
            return DocumentType.DETAILED_DESIGN
        if "需求" in file_name or "srs" in file_name:
            return DocumentType.REQUIREMENT_DOC
        if "项目" in file_name and "计划" in file_name:
            return DocumentType.PROJECT_PLAN
        if "思维导图" in file_name or "mindmap" in file_name:
            return DocumentType.MINDMAP
        if "方案举措" in file_name or "solution" in file_name:
            return DocumentType.SOLUTION_TABLE
        
        # 从内容判断
        if content:
            if "方案" in content and ("PPT" in content or "汇报" in content):
                return DocumentType.PROPOSAL_PPT
            if "设计" in content and ("架构" in content or "接口" in content):
                return DocumentType.DETAILED_DESIGN
            if "需求" in content and ("功能" in content or "验收" in content):
                return DocumentType.REQUIREMENT_DOC
            if "项目" in content and ("甘特图" in content or "RACI" in content):
                return DocumentType.PROJECT_PLAN
        
        return DocumentType.OTHER
    
    def extract_tags_from_content(self, content: str) -> dict:
        """从内容中提取标签"""
        tags = {
            "purpose": None,
            "audience": None,
            "value": None,
            "scope": None,
        }
        
        for category, patterns in self.tag_patterns.items():
            for pattern, value in patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    tags[category] = value
                    break
        
        return tags
    
    def infer_from_keywords(self, content: str, file_name: str) -> dict:
        """从关键词推断属性"""
        combined = f"{file_name} {content[:2000]}"  # 结合文件名和内容前2000字
        
        inferred = {
            "purpose": None,
            "audience": None,
            "value": None,
        }
        
        # 推断用途
        purpose_indicators = self.keyword_indicators["purpose"]
        external_count = sum(1 for kw in purpose_indicators["external_keywords"] if kw in combined)
        internal_count = sum(1 for kw in purpose_indicators["internal_keywords"] if kw in combined)
        draft_count = sum(1 for kw in purpose_indicators["draft_keywords"] if kw in combined)
        
        if external_count > internal_count and external_count > draft_count:
            inferred["purpose"] = DocumentPurpose.EXTERNAL_REPORT
        elif internal_count > draft_count:
            inferred["purpose"] = DocumentPurpose.INTERNAL_COLLAB
        else:
            inferred["purpose"] = DocumentPurpose.PERSONAL_DRAFT
        
        # 推断审阅对象
        audience_indicators = self.keyword_indicators["audience"]
        customer_count = sum(1 for kw in audience_indicators["customer_keywords"] if kw in combined)
        leadership_count = sum(1 for kw in audience_indicators["leadership_keywords"] if kw in combined)
        team_count = sum(1 for kw in audience_indicators["team_keywords"] if kw in combined)
        
        if customer_count >= leadership_count and customer_count >= team_count:
            inferred["audience"] = ReviewAudience.CUSTOMER
        elif leadership_count >= team_count:
            inferred["audience"] = ReviewAudience.LEADERSHIP
        else:
            inferred["audience"] = ReviewAudience.TEAM
        
        # 推断业务价值
        value_indicators = self.keyword_indicators["value"]
        high_count = sum(1 for kw in value_indicators["high_keywords"] if kw in combined)
        medium_count = sum(1 for kw in value_indicators["medium_keywords"] if kw in combined)
        low_count = sum(1 for kw in value_indicators["low_keywords"] if kw in combined)
        
        if high_count >= medium_count and high_count >= low_count:
            inferred["value"] = BusinessValue.HIGH
        elif medium_count >= low_count:
            inferred["value"] = BusinessValue.MEDIUM
        else:
            inferred["value"] = BusinessValue.LOW
        
        return inferred
    
    def evaluate(self, file_path: str, content: str = None,
                 purpose: DocumentPurpose = None,
                 doc_type: DocumentType = None,
                 audience: ReviewAudience = None,
                 value: BusinessValue = None,
                 scope: ImpactScope = None) -> DocumentImportanceScore:
        """评估文档重要性"""
        
        # 读取内容（如果未提供）
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except:
                content = ""
        
        file_name = Path(file_path).name
        
        # 1. 检测文档类型
        if doc_type is None:
            doc_type = self.detect_document_type(file_path, content)
        
        # 2. 提取显式标签
        tags = self.extract_tags_from_content(content)
        
        # 3. 推断隐含属性
        inferred = self.infer_from_keywords(content, file_name)
        
        # 4. 确定最终属性（显式标签 > 用户指定 > 关键词推断）
        final_purpose = purpose or tags["purpose"] or inferred["purpose"] or DocumentPurpose.INTERNAL_COLLAB
        final_audience = audience or tags["audience"] or inferred["audience"] or ReviewAudience.TEAM
        final_value = value or tags["value"] or inferred["value"] or BusinessValue.MEDIUM
        final_scope = scope or tags["scope"] or ImpactScope.PROJECT
        
        # 5. 计算得分
        purpose_score = self.PURPOSE_SCORES[final_purpose]
        type_score = self.TYPE_SCORES[doc_type]
        audience_score = self.AUDIENCE_SCORES[final_audience]
        value_score = self.VALUE_SCORES[final_value]
        scope_score = self.SCOPE_SCORES[final_scope]
        
        # 6. 计算加权总分
        total_score = (
            purpose_score * self.WEIGHTS["purpose"] +
            type_score * self.WEIGHTS["type"] +
            audience_score * self.WEIGHTS["audience"] +
            value_score * self.WEIGHTS["value"] +
            scope_score * self.WEIGHTS["scope"]
        )
        
        # 7. 确定重要性等级
        if total_score >= 80:
            level = "重要"
            recommended_mode = "semi"  # 半自动
        elif total_score >= 60:
            level = "较重要"
            recommended_mode = "semi"  # 半自动
        else:
            level = "普通"
            recommended_mode = "auto"  # 全自动
        
        return DocumentImportanceScore(
            purpose_score=purpose_score,
            type_score=type_score,
            audience_score=audience_score,
            value_score=value_score,
            scope_score=scope_score,
            total_score=round(total_score, 1),
            level=level,
            recommended_mode=recommended_mode,
        )
    
    def generate_report(self, file_path: str, score: DocumentImportanceScore) -> str:
        """生成评估报告"""
        lines = [
            "# 文档重要性评估报告",
            "",
            f"**文件**：{file_path}",
            f"**评估时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 评估结果",
            "",
            f"| 维度 | 得分 | 权重 | 加权得分 |",
            f"|------|:----:|:----:|:--------:|",
            f"| 用途 | {score.purpose_score} | 25% | {score.purpose_score * 0.25:.1f} |",
            f"| 类型 | {score.type_score} | 20% | {score.type_score * 0.20:.1f} |",
            f"| 审阅对象 | {score.audience_score} | 25% | {score.audience_score * 0.25:.1f} |",
            f"| 业务价值 | {score.value_score} | 20% | {score.value_score * 0.20:.1f} |",
            f"| 影响范围 | {score.scope_score} | 10% | {score.scope_score * 0.10:.1f} |",
            f"| **总分** | - | - | **{score.total_score}** |",
            "",
            "---",
            "",
            "## 评估结论",
            "",
            f"- **重要性等级**：{score.level}",
            f"- **推荐审核模式**：{'半自动（人工确认）' if score.recommended_mode == 'semi' else '全自动'}",
            "",
        ]
        
        if score.recommended_mode == "semi":
            lines.extend([
                "**理由**：文档重要性较高，建议采用半自动模式，南乔在关键节点人工确认，确保质量。",
            ])
        else:
            lines.extend([
                "**理由**：文档为普通级别，可采用全自动模式，提高处理效率。",
            ])
        
        return "\n".join(lines)


def main():
    """测试入口"""
    print("\n" + "="*70)
    print("📄 文档重要性评估器 - 测试")
    print("="*70)
    
    evaluator = DocumentImportanceEvaluator()
    
    # 测试用例
    test_cases = [
        {
            "name": "方案PPT（对外汇报）",
            "file": "知识库/方法论/需求文档模板_九星智囊团专属版.md",
            "expected": "重要",
        },
        {
            "name": "内部学习笔记",
            "file": "知识库/方法论/提示词工程框架.md",
            "expected": "普通/较重要",
        },
        {
            "name": "项目管控计划",
            "file": "03_输出成果/九星智囊团计划管控表.xlsx",
            "expected": "较重要",
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"测试 {i}：{case['name']}")
        print(f"{'─'*70}")
        
        file_path = Path(case["file"])
        if file_path.exists():
            score = evaluator.evaluate(str(file_path))
            
            print(f"总分：{score.total_score}")
            print(f"等级：{score.level}")
            print(f"推荐模式：{'半自动' if score.recommended_mode == 'semi' else '全自动'}")
            print(f"预期：{case['expected']}")
        else:
            print(f"文件不存在：{file_path}")


if __name__ == "__main__":
    main()
