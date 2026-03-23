#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闭环质量保证系统 - Quality Fixer
功能：审核 → 诊断 → 修复 → 复审，直到文档达标
创建时间：2026-03-23
创建者：南乔
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 导入审核器
import sys
sys.path.insert(0, str(Path(__file__).parent))
from quality_auditor import QualityAuditor, AUDIT_CHECKLIST, AUDIT_GRADES

# 工作区根目录
WORKSPACE_ROOT = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE_ROOT / "03_输出成果"
AUDIT_LOG_DIR = OUTPUT_DIR / "审核记录"

# 最大迭代次数
MAX_ITERATIONS = 3


class IssueDiagnoser:
    """问题诊断器 - 精准定位缺失内容"""
    
    def __init__(self):
        self.issue_templates = self._load_issue_templates()
    
    def _load_issue_templates(self) -> dict:
        """加载问题模板"""
        return {
            "需求文档": {
                "建设背景": {
                    "required": ["项目背景", "业务痛点", "建设必要性"],
                    "template": """
## 1.1 建设背景

### 项目背景
{项目背景描述}

### 业务痛点
{当前业务存在的问题}

### 建设必要性
{为什么需要建设这个系统}
""",
                    "prompt": "请根据项目实际情况，补充建设背景章节，包括项目背景、业务痛点、建设必要性三部分。"
                },
                "建设目的": {
                    "required": ["解决问题", "预期效果"],
                    "template": """
## 1.2 建设目的

### 解决问题
1. {问题1}
2. {问题2}

### 预期效果
1. {效果1}
2. {效果2}
""",
                    "prompt": "请补充建设目的章节，明确要解决的问题和预期效果。"
                },
                "功能需求": {
                    "required": ["功能模块", "功能描述", "用户故事"],
                    "template": """
## 3. 功能需求

### 3.1 功能结构
{功能模块结构图}

### 3.2 功能清单
| 功能模块 | 功能描述 | 优先级 |
|---------|---------|:------:|
| {模块1} | {描述1} | MUST |
""",
                    "prompt": "请补充功能需求章节，包括功能结构、功能清单、用户故事。"
                },
                "验收标准": {
                    "required": ["功能验收", "性能验收", "业务验收"],
                    "template": """
## 6. 验收标准

### 6.1 功能验收标准
| 需求编号 | 验收标准 | 验收方法 |
|:-------:|---------|:--------:|
| FR-001 | {验收标准1} | 功能测试 |

### 6.2 性能验收标准
| 指标 | 目标值 | 验收方法 |
|-----|:-----:|:--------:|
| 响应时间 | ≤3秒 | 性能测试 |
""",
                    "prompt": "请补充验收标准章节，包括功能验收、性能验收、业务验收标准。"
                },
            },
            "思维导图": {
                "核心主题": {
                    "required": ["中心主题", "主要分支"],
                    "prompt": "请补充核心主题和主要分支结构。"
                },
                "优先级标注": {
                    "required": ["P0", "P1", "P2", "MUST", "SHOULD"],
                    "prompt": "请为各分支标注优先级（P0/P1/P2或MUST/SHOULD）。"
                },
            },
            "方案PPT": {
                "封面页": {
                    "required": ["项目名称", "汇报人", "日期"],
                    "prompt": "请补充封面页，包含项目名称、汇报人、日期。"
                },
                "目录页": {
                    "required": ["目录", "CONTENTS"],
                    "prompt": "请补充目录页，列出主要内容章节。"
                },
            },
            "详细设计": {
                "架构设计": {
                    "required": ["系统架构", "技术架构", "部署架构"],
                    "prompt": "请补充架构设计章节，包括系统架构、技术架构、部署架构。"
                },
                "接口设计": {
                    "required": ["接口名称", "请求参数", "响应参数"],
                    "prompt": "请补充接口设计章节，包括接口清单和详细设计。"
                },
                "数据库设计": {
                    "required": ["表结构", "字段说明", "索引设计"],
                    "prompt": "请补充数据库设计章节，包括表结构、字段说明、索引设计。"
                },
            },
            "项目计划": {
                "WBS分解": {
                    "required": ["任务分解", "工作量估算"],
                    "prompt": "请补充WBS分解，包括任务分解和工作量估算。"
                },
                "RACI矩阵": {
                    "required": ["R", "A", "C", "I"],
                    "prompt": "请补充RACI矩阵，明确各任务的责任人。"
                },
                "风险清单": {
                    "required": ["风险项", "影响程度", "应对措施"],
                    "prompt": "请补充风险清单，包括风险项、影响程度、应对措施。"
                },
            },
        }
    
    def diagnose(self, audit_result: dict) -> dict:
        """诊断问题，生成修复建议"""
        doc_type = audit_result.get("doc_type", "需求文档")
        issues = audit_result.get("issues", [])
        completeness_results = audit_result.get("completeness_results", {})
        
        diagnosis = {
            "doc_type": doc_type,
            "issues": [],
            "fix_prompts": [],
            "missing_sections": [],
        }
        
        # 分析完整性问题
        templates = self.issue_templates.get(doc_type, {})
        
        for item, result in completeness_results.items():
            if result.get("pass") is False:
                template_info = templates.get(item, {})
                
                diagnosis["issues"].append({
                    "type": "completeness",
                    "item": item,
                    "desc": result.get("desc", ""),
                    "required": template_info.get("required", []),
                    "template": template_info.get("template", ""),
                    "prompt": template_info.get("prompt", f"请补充{item}相关内容。"),
                })
                
                diagnosis["missing_sections"].append(item)
                diagnosis["fix_prompts"].append({
                    "section": item,
                    "prompt": template_info.get("prompt", f"请补充{item}相关内容。"),
                    "template": template_info.get("template", ""),
                })
        
        # 分析格式问题
        format_results = audit_result.get("format_results", {})
        for item, result in format_results.items():
            if result.get("pass") is False:
                diagnosis["issues"].append({
                    "type": "format",
                    "item": item,
                    "desc": result.get("desc", ""),
                    "prompt": f"请修正格式问题：{result.get('desc', '')}",
                })
        
        return diagnosis


class ContentFixer:
    """内容修复器 - 生成针对性修复内容"""
    
    def __init__(self):
        self.doc_type_templates = self._load_doc_templates()
    
    def _load_doc_templates(self) -> dict:
        """加载文档模板"""
        return {
            "需求文档": """
# 需求规格说明书

## 第1章 简介
### 1.1 建设背景
{建设背景内容}

### 1.2 建设目的
{建设目的内容}

## 第2章 业务需求
### 2.1 业务场景
{业务场景内容}

## 第3章 功能需求
### 3.1 功能结构
{功能结构内容}

### 3.2 功能清单
{功能清单内容}

## 第4章 接口需求
{接口需求内容}

## 第5章 非功能需求
### 5.1 性能需求
{性能需求内容}

### 5.2 安全性需求
{安全性需求内容}

## 第6章 验收标准
{验收标准内容}
""",
        }
    
    def generate_fix_content(self, diagnosis: dict, original_content: str = "") -> str:
        """生成修复内容"""
        doc_type = diagnosis.get("doc_type", "需求文档")
        fix_prompts = diagnosis.get("fix_prompts", [])
        
        fix_content_parts = []
        fix_content_parts.append("# 修复建议\n")
        fix_content_parts.append(f"**文档类型**：{doc_type}\n")
        fix_content_parts.append(f"**缺失章节**：{', '.join(diagnosis.get('missing_sections', []))}\n")
        fix_content_parts.append("\n---\n\n")
        fix_content_parts.append("## 需要补充的内容\n\n")
        
        for i, fix in enumerate(fix_prompts, 1):
            section = fix.get("section", "")
            prompt = fix.get("prompt", "")
            template = fix.get("template", "")
            
            fix_content_parts.append(f"### {i}. {section}\n\n")
            fix_content_parts.append(f"**修复提示**：{prompt}\n\n")
            
            if template:
                fix_content_parts.append("**内容模板**：\n\n```markdown\n")
                fix_content_parts.append(template)
                fix_content_parts.append("\n```\n\n")
            
            fix_content_parts.append("---\n\n")
        
        return "".join(fix_content_parts)


class IterationController:
    """迭代控制器 - 控制修复次数"""
    
    def __init__(self, max_iterations: int = MAX_ITERATIONS):
        self.max_iterations = max_iterations
        self.iteration_history = []
    
    def should_continue(self, current_iteration: int, grade: str) -> bool:
        """判断是否继续迭代"""
        if grade == "A":
            return False  # A级通过，不需要继续
        
        if grade == "B":
            return False  # B级小幅优化后通过，不需要继续
        
        if current_iteration >= self.max_iterations:
            return False  # 达到最大迭代次数，停止
        
        return True  # 继续修复
    
    def record_iteration(self, iteration: int, score: float, grade: str, issues: list):
        """记录迭代历史"""
        self.iteration_history.append({
            "iteration": iteration,
            "score": score,
            "grade": grade,
            "issues": issues,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    def get_summary(self) -> dict:
        """获取迭代总结"""
        if not self.iteration_history:
            return {"total_iterations": 0, "improved": False}
        
        first_score = self.iteration_history[0]["score"]
        last_score = self.iteration_history[-1]["score"]
        
        return {
            "total_iterations": len(self.iteration_history),
            "first_score": first_score,
            "last_score": last_score,
            "improved": last_score > first_score,
            "improvement": round(last_score - first_score, 1),
            "history": self.iteration_history,
        }


class ClosedLoopQualitySystem:
    """闭环质量保证系统"""
    
    def __init__(self):
        self.auditor = QualityAuditor()
        self.diagnoser = IssueDiagnoser()
        self.fixer = ContentFixer()
        self.controller = IterationController()
    
    def process(self, file_path: str, doc_type: str = None, auto_fix: bool = False) -> dict:
        """处理文档，闭环质量保证"""
        print(f"\n{'='*60}")
        print(f"闭环质量保证系统 - 处理文档")
        print(f"{'='*60}")
        print(f"📄 文件：{file_path}")
        print(f"📂 类型：{doc_type or '自动检测'}")
        print(f"🔧 自动修复：{'开启' if auto_fix else '关闭'}")
        print(f"{'='*60}\n")
        
        iteration = 0
        all_results = []
        
        while True:
            iteration += 1
            print(f"\n--- 第 {iteration} 次审核 ---\n")
            
            # 1. 审核
            audit_result = self.auditor.audit(file_path, doc_type)
            grade = audit_result["grade"]
            score = audit_result["score"]
            issues = audit_result["issues"]
            
            print(f"📊 审核结果：{score}分 | {grade}级")
            if issues:
                print(f"⚠️ 问题清单：{len(issues)}项")
                for issue in issues:
                    print(f"   - {issue}")
            
            # 记录迭代
            self.controller.record_iteration(iteration, score, grade, issues)
            all_results.append(audit_result)
            
            # 2. 判断是否继续
            if not self.controller.should_continue(iteration, grade):
                print(f"\n✅ 审核通过！等级：{grade}级")
                break
            
            # 3. 诊断问题
            print(f"\n🔍 诊断问题...")
            diagnosis = self.diagnoser.diagnose(audit_result)
            
            missing = diagnosis.get("missing_sections", [])
            if missing:
                print(f"📝 缺失章节：{', '.join(missing)}")
            
            # 4. 生成修复建议
            fix_content = self.fixer.generate_fix_content(diagnosis)
            fix_file = AUDIT_LOG_DIR / f"修复建议_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(fix_file, "w", encoding="utf-8") as f:
                f.write(fix_content)
            
            print(f"📄 修复建议已生成：{fix_file}")
            
            # 5. 如果自动修复关闭，返回诊断结果
            if not auto_fix:
                print(f"\n⚠️ 自动修复未开启，请根据修复建议手动修改文档")
                return {
                    "status": "need_fix",
                    "audit_result": audit_result,
                    "diagnosis": diagnosis,
                    "fix_content": fix_content,
                    "fix_file": str(fix_file),
                }
            
            # 6. 自动修复（需要调用Agent补充内容）
            # 这里先打印提示，实际需要集成Agent调用
            print(f"\n🔧 自动修复功能待集成Agent调用...")
            print(f"   请根据修复建议手动补充内容后，重新运行审核")
            
            # 暂停，等待人工处理
            return {
                "status": "need_manual_fix",
                "audit_result": audit_result,
                "diagnosis": diagnosis,
                "fix_content": fix_content,
                "fix_file": str(fix_file),
            }
        
        # 返回最终结果
        summary = self.controller.get_summary()
        
        return {
            "status": "passed",
            "final_grade": grade,
            "final_score": score,
            "iteration_summary": summary,
            "all_results": all_results,
        }
    
    def generate_final_report(self, result: dict) -> str:
        """生成最终报告"""
        lines = [
            "# 闭环质量保证报告",
            "",
            f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 处理结果",
            "",
        ]
        
        if result["status"] == "passed":
            lines.extend([
                f"### ✅ 审核通过",
                "",
                f"- **最终等级**：{result['final_grade']}级",
                f"- **最终得分**：{result['final_score']}分",
                "",
            ])
            
            summary = result.get("iteration_summary", {})
            if summary.get("total_iterations", 0) > 1:
                lines.extend([
                    "### 迭代过程",
                    "",
                    f"- **迭代次数**：{summary['total_iterations']}",
                    f"- **初始得分**：{summary['first_score']}分",
                    f"- **最终得分**：{summary['last_score']}分",
                    f"- **得分提升**：{summary['improvement']}分",
                    "",
                ])
        else:
            lines.extend([
                f"### ⚠️ 需要修复",
                "",
                f"- **当前等级**：{result['audit_result']['grade']}级",
                f"- **当前得分**：{result['audit_result']['score']}分",
                f"- **问题数量**：{len(result['audit_result']['issues'])}项",
                "",
                "### 缺失章节",
                "",
            ])
            
            for section in result['diagnosis'].get('missing_sections', []):
                lines.append(f"- {section}")
            
            lines.extend([
                "",
                f"### 修复建议文件",
                "",
                f"- {result['fix_file']}",
                "",
            ])
        
        return "\n".join(lines)


def main():
    """测试入口"""
    print("\n" + "="*60)
    print("闭环质量保证系统 - Closed Loop Quality System")
    print("="*60)
    
    # 创建系统
    system = ClosedLoopQualitySystem()
    
    # 测试：处理需求文档模板
    test_file = WORKSPACE_ROOT / "知识库" / "方法论" / "需求文档模板_九星智囊团专属版.md"
    
    if test_file.exists():
        result = system.process(str(test_file), auto_fix=False)
        
        # 生成最终报告
        report = system.generate_final_report(result)
        report_file = AUDIT_LOG_DIR / f"闭环质量报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 最终报告已生成：{report_file}")
    else:
        print(f"\n❌ 测试文件不存在：{test_file}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
