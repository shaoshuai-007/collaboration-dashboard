#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量审核执行器 - Quality Auditor
功能：自动检查产出物质量 + 生成审核报告
创建时间：2026-03-23
创建者：南乔
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# 工作区根目录
WORKSPACE_ROOT = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE_ROOT / "03_输出成果"
AUDIT_LOG_DIR = OUTPUT_DIR / "审核记录"

# 审核检查清单
AUDIT_CHECKLIST = {
    "需求文档": {
        "format": {
            "文件格式": "检查是否为 .md 或 .docx 格式",
            "命名规范": "检查文件名是否包含日期和版本",
        },
        "completeness": {
            "建设背景": "检查是否包含建设背景章节",
            "建设目的": "检查是否包含建设目的章节",
            "功能需求": "检查是否包含功能需求章节",
            "验收标准": "检查是否包含验收标准章节",
        },
        "consistency": {
            "术语统一": "检查关键术语是否一致",
            "编号规范": "检查需求编号是否规范（如 FR-001）",
        },
        "weights": {
            "format": 20,
            "completeness": 40,
            "consistency": 20,
            "content": 20,
        }
    },
    "思维导图": {
        "format": {
            "文件格式": "检查是否为 .html 或 .xmind 格式",
        },
        "completeness": {
            "核心主题": "检查是否有明确的中心主题",
            "分支结构": "检查是否有清晰的分支结构",
            "优先级标注": "检查是否标注优先级",
        },
        "consistency": {
            "层级清晰": "检查层级是否清晰（不超过4层）",
        },
        "weights": {
            "format": 20,
            "completeness": 40,
            "consistency": 20,
            "content": 20,
        }
    },
    "方案PPT": {
        "format": {
            "文件格式": "检查是否为 .pptx 格式",
            "配色规范": "检查配色是否符合三原色定理（可选，需人工）",
        },
        "completeness": {
            "封面页": "检查是否有封面页",
            "目录页": "检查是否有目录页",
            "内容页": "检查内容页数量（建议≥10页）",
            "结束页": "检查是否有结束页",
        },
        "consistency": {
            "版式统一": "检查版式是否统一（需人工）",
        },
        "weights": {
            "format": 20,
            "completeness": 40,
            "consistency": 20,
            "content": 20,
        }
    },
    "详细设计": {
        "format": {
            "文件格式": "检查是否为 .md 或 .docx 格式",
        },
        "completeness": {
            "架构设计": "检查是否包含架构设计章节",
            "接口设计": "检查是否包含接口设计章节",
            "数据库设计": "检查是否包含数据库设计章节",
        },
        "consistency": {
            "接口编号": "检查接口编号是否规范",
            "表命名": "检查数据库表命名是否规范",
        },
        "weights": {
            "format": 20,
            "completeness": 40,
            "consistency": 20,
            "content": 20,
        }
    },
    "项目计划": {
        "format": {
            "文件格式": "检查是否为 .xlsx 或 .md 格式",
        },
        "completeness": {
            "WBS分解": "检查是否包含WBS分解",
            "甘特图": "检查是否包含甘特图或时间计划",
            "RACI矩阵": "检查是否包含RACI矩阵",
            "风险清单": "检查是否包含风险清单",
        },
        "consistency": {
            "时间合理性": "检查工期是否合理（需人工）",
        },
        "weights": {
            "format": 20,
            "completeness": 40,
            "consistency": 20,
            "content": 20,
        }
    }
}

# 审核等级
AUDIT_GRADES = {
    "A": {"min": 90, "max": 100, "desc": "直接通过"},
    "B": {"min": 80, "max": 89, "desc": "小幅优化后通过"},
    "C": {"min": 70, "max": 79, "desc": "优化后重新审核"},
    "D": {"min": 0, "max": 69, "desc": "重新编写"},
}


class QualityAuditor:
    """质量审核执行器"""
    
    def __init__(self):
        self.audit_results = []
        self.ensure_audit_log_dir()
    
    def ensure_audit_log_dir(self):
        """确保审核日志目录存在"""
        AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def detect_document_type(self, file_path: str) -> str:
        """检测文档类型"""
        file_path = str(file_path).lower()
        
        if "需求" in file_path or "requirement" in file_path or "srs" in file_path:
            return "需求文档"
        elif "思维导图" in file_path or "mindmap" in file_path or "分析" in file_path:
            return "思维导图"
        elif "ppt" in file_path or "方案" in file_path:
            return "方案PPT"
        elif "设计" in file_path or "design" in file_path:
            return "详细设计"
        elif "计划" in file_path or "项目" in file_path or "甘特图" in file_path:
            return "项目计划"
        else:
            return "需求文档"  # 默认
    
    def check_format(self, file_path: str, doc_type: str) -> dict:
        """检查格式"""
        results = {}
        checklist = AUDIT_CHECKLIST.get(doc_type, {}).get("format", {})
        file_path_str = str(file_path).lower()
        
        for item, desc in checklist.items():
            if item == "文件格式":
                if file_path_str.endswith(".md") or file_path_str.endswith(".docx") or \
                   file_path_str.endswith(".html") or file_path_str.endswith(".xmind") or \
                   file_path_str.endswith(".pptx") or file_path_str.endswith(".xlsx"):
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": False, "desc": f"{desc} - 当前格式不符合要求"}
            
            elif item == "命名规范":
                # 检查文件名是否包含日期（如2026-03-23）或版本（V1.0）
                if re.search(r"\d{4}-\d{2}-\d{2}", file_path) or re.search(r"V\d+", file_path, re.I):
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": False, "desc": f"{desc} - 建议在文件名中包含日期或版本"}
            
            else:
                results[item] = {"pass": None, "desc": f"{desc} - 需人工检查"}
        
        return results
    
    def check_completeness(self, file_path: str, doc_type: str) -> dict:
        """检查完整性"""
        results = {}
        checklist = AUDIT_CHECKLIST.get(doc_type, {}).get("completeness", {})
        
        # 读取文件内容
        content = ""
        try:
            if str(file_path).endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
        except Exception as e:
            for item, desc in checklist.items():
                results[item] = {"pass": None, "desc": f"{desc} - 无法读取文件内容"}
            return results
        
        for item, desc in checklist.items():
            # 检查是否包含关键词
            keywords = self.get_keywords_for_item(item)
            if any(kw in content for kw in keywords):
                results[item] = {"pass": True, "desc": desc}
            else:
                results[item] = {"pass": False, "desc": f"{desc} - 未找到相关内容"}
        
        return results
    
    def get_keywords_for_item(self, item: str) -> list:
        """获取检查项的关键词"""
        keyword_map = {
            "建设背景": ["建设背景", "项目背景", "业务背景"],
            "建设目的": ["建设目的", "项目目标", "建设目标"],
            "功能需求": ["功能需求", "功能描述", "功能模块"],
            "验收标准": ["验收标准", "验收条件", "验收要求"],
            "核心主题": ["主题", "核心", "中心"],
            "分支结构": ["分支", "模块", "章节"],
            "优先级标注": ["优先级", "P0", "P1", "MUST", "SHOULD"],
            "封面页": ["封面", "标题页"],
            "目录页": ["目录", "CONTENTS"],
            "内容页": ["第", "章", "节"],
            "结束页": ["谢谢", "THANKS", "结束"],
            "架构设计": ["架构", "系统架构", "技术架构"],
            "接口设计": ["接口", "API", "请求", "响应"],
            "数据库设计": ["数据库", "表", "字段", "TABLE"],
            "WBS分解": ["WBS", "任务分解", "工作分解"],
            "甘特图": ["甘特图", "时间计划", "进度计划"],
            "RACI矩阵": ["RACI", "责任矩阵"],
            "风险清单": ["风险", "风险清单", "风险识别"],
        }
        return keyword_map.get(item, [item])
    
    def check_consistency(self, file_path: str, doc_type: str) -> dict:
        """检查一致性"""
        results = {}
        checklist = AUDIT_CHECKLIST.get(doc_type, {}).get("consistency", {})
        
        # 读取文件内容
        content = ""
        try:
            if str(file_path).endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
        except Exception as e:
            for item, desc in checklist.items():
                results[item] = {"pass": None, "desc": f"{desc} - 无法读取文件内容"}
            return results
        
        for item, desc in checklist.items():
            if item == "术语统一":
                # 检查是否有重复定义的术语
                results[item] = {"pass": None, "desc": f"{desc} - 需人工检查"}
            
            elif item == "编号规范":
                # 检查是否有规范的编号（如 FR-001, FR-002）
                if re.search(r"FR-\d{3}", content) or re.search(r"BR-\d{3}", content):
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": None, "desc": f"{desc} - 未发现规范编号，需人工确认"}
            
            elif item == "层级清晰":
                # 检查层级（通过#号数量判断）
                max_level = content.count("####")
                if max_level <= 3:
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": None, "desc": f"{desc} - 层级较深，建议简化"}
            
            elif item == "接口编号":
                if re.search(r"API-\d{3}", content) or re.search(r"接口\d+", content):
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": None, "desc": f"{desc} - 需人工检查"}
            
            elif item == "表命名":
                if re.search(r"CREATE TABLE", content, re.I) or re.search(r"\|.*\|.*\|", content):
                    results[item] = {"pass": True, "desc": desc}
                else:
                    results[item] = {"pass": None, "desc": f"{desc} - 需人工检查"}
            
            else:
                results[item] = {"pass": None, "desc": f"{desc} - 需人工检查"}
        
        return results
    
    def calculate_score(self, format_results: dict, completeness_results: dict, 
                        consistency_results: dict, doc_type: str) -> dict:
        """计算总分"""
        weights = AUDIT_CHECKLIST.get(doc_type, {}).get("weights", {
            "format": 20, "completeness": 40, "consistency": 20, "content": 20
        })
        
        # 计算各项得分
        def get_pass_rate(results: dict) -> float:
            if not results:
                return 0.5  # 无检查项，默认50%
            passed = sum(1 for r in results.values() if r.get("pass") is True)
            total = len(results)
            if total == 0:
                return 0.5
            # None视为需要人工检查，计50%
            none_count = sum(1 for r in results.values() if r.get("pass") is None)
            return (passed + none_count * 0.5) / total
        
        format_score = get_pass_rate(format_results) * weights["format"]
        completeness_score = get_pass_rate(completeness_results) * weights["completeness"]
        consistency_score = get_pass_rate(consistency_results) * weights["consistency"]
        content_score = weights["content"] * 0.7  # 内容审核需人工，默认给70%
        
        total_score = format_score + completeness_score + consistency_score + content_score
        
        return {
            "format_score": round(format_score, 1),
            "completeness_score": round(completeness_score, 1),
            "consistency_score": round(consistency_score, 1),
            "content_score": round(content_score, 1),
            "total_score": round(total_score, 1),
        }
    
    def get_grade(self, score: float) -> dict:
        """获取等级"""
        for grade, info in AUDIT_GRADES.items():
            if info["min"] <= score <= info["max"]:
                return {"grade": grade, "desc": info["desc"]}
        return {"grade": "D", "desc": "重新编写"}
    
    def generate_audit_report(self, file_path: str, doc_type: str, 
                              format_results: dict, completeness_results: dict,
                              consistency_results: dict, score_info: dict,
                              grade_info: dict, issues: list = None) -> str:
        """生成审核报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_lines = [
            f"# 质量审核报告",
            f"",
            f"**审核时间**：{timestamp}",
            f"**审核对象**：{file_path}",
            f"**文档类型**：{doc_type}",
            f"",
            f"---",
            f"",
            f"## 审核结果",
            f"",
            f"| 检查项 | 得分 | 权重 |",
            f"|:------:|:----:|:----:|",
            f"| 格式检查 | {score_info['format_score']} | 20% |",
            f"| 完整性检查 | {score_info['completeness_score']} | 40% |",
            f"| 一致性检查 | {score_info['consistency_score']} | 20% |",
            f"| 内容质量 | {score_info['content_score']} | 20% |",
            f"| **总分** | **{score_info['total_score']}** | **100%** |",
            f"",
            f"### 审核等级：**{grade_info['grade']}级**（{grade_info['desc']}）",
            f"",
            f"---",
            f"",
            f"## 详细检查结果",
            f"",
            f"### 格式检查",
            f"",
        ]
        
        for item, result in format_results.items():
            status = "✅" if result.get("pass") is True else ("❌" if result.get("pass") is False else "⚠️")
            report_lines.append(f"- {status} **{item}**：{result.get('desc', '')}")
        
        report_lines.extend([
            f"",
            f"### 完整性检查",
            f"",
        ])
        
        for item, result in completeness_results.items():
            status = "✅" if result.get("pass") is True else ("❌" if result.get("pass") is False else "⚠️")
            report_lines.append(f"- {status} **{item}**：{result.get('desc', '')}")
        
        report_lines.extend([
            f"",
            f"### 一致性检查",
            f"",
        ])
        
        for item, result in consistency_results.items():
            status = "✅" if result.get("pass") is True else ("❌" if result.get("pass") is False else "⚠️")
            report_lines.append(f"- {status} **{item}**：{result.get('desc', '')}")
        
        if issues:
            report_lines.extend([
                f"",
                f"---",
                f"",
                f"## 问题清单",
                f"",
            ])
            for i, issue in enumerate(issues, 1):
                report_lines.append(f"{i}. {issue}")
        
        report_lines.extend([
            f"",
            f"---",
            f"",
            f"## 改进建议",
            f"",
            f"1. 请人工审核内容质量和业务正确性",
            f"2. 针对未通过的检查项进行修改",
        ])
        
        return "\n".join(report_lines)
    
    def audit(self, file_path: str, doc_type: str = None) -> dict:
        """执行审核"""
        # 检测文档类型
        if not doc_type:
            doc_type = self.detect_document_type(file_path)
        
        # 执行检查
        format_results = self.check_format(file_path, doc_type)
        completeness_results = self.check_completeness(file_path, doc_type)
        consistency_results = self.check_consistency(file_path, doc_type)
        
        # 计算得分
        score_info = self.calculate_score(format_results, completeness_results, 
                                          consistency_results, doc_type)
        
        # 获取等级
        grade_info = self.get_grade(score_info["total_score"])
        
        # 收集问题
        issues = []
        for item, result in {**format_results, **completeness_results, **consistency_results}.items():
            if result.get("pass") is False:
                issues.append(f"{item}：{result.get('desc', '')}")
        
        # 生成报告
        report = self.generate_audit_report(
            file_path, doc_type, format_results, completeness_results,
            consistency_results, score_info, grade_info, issues
        )
        
        # 保存报告
        report_file = AUDIT_LOG_DIR / f"审核报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        return {
            "file_path": str(file_path),
            "doc_type": doc_type,
            "score": score_info["total_score"],
            "grade": grade_info["grade"],
            "grade_desc": grade_info["desc"],
            "issues": issues,
            "report_file": str(report_file),
            "report": report,
            # 新增：返回详细检查结果，供诊断器使用
            "format_results": format_results,
            "completeness_results": completeness_results,
            "consistency_results": consistency_results,
            "score_info": score_info,
        }


def main():
    """测试入口"""
    print("=" * 60)
    print("质量审核执行器 - Quality Auditor")
    print("=" * 60)
    
    # 创建审核器
    auditor = QualityAuditor()
    
    # 测试：审核需求文档模板
    test_file = WORKSPACE_ROOT / "知识库" / "方法论" / "需求文档模板_九星智囊团专属版.md"
    
    if test_file.exists():
        print(f"\n📝 测试文件：{test_file}")
        print("-" * 60)
        
        result = auditor.audit(str(test_file))
        
        print(f"\n📊 审核结果：")
        print(f"  - 文档类型：{result['doc_type']}")
        print(f"  - 总分：{result['score']}分")
        print(f"  - 等级：{result['grade']}级（{result['grade_desc']}）")
        
        if result['issues']:
            print(f"\n⚠️ 问题清单：")
            for issue in result['issues']:
                print(f"  - {issue}")
        
        print(f"\n📄 审核报告已保存：{result['report_file']}")
    else:
        print(f"\n❌ 测试文件不存在：{test_file}")
    
    print("\n" + "=" * 60)
    print("审核完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
