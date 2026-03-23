#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent自动修复执行器 - Agent Auto Fixer
功能：调用对应的Agent自动修复文档缺失内容
创建时间：2026-03-23
创建者：南乔
版本：V2.0 - 集成文档重要性评估
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 导入闭环质量系统
import sys
sys.path.insert(0, str(Path(__file__).parent))
from quality_fixer import ClosedLoopQualitySystem, IssueDiagnoser, ContentFixer, IterationController

# 导入文档重要性评估器
from document_importance_evaluator import (
    DocumentImportanceEvaluator,
    DocumentImportanceScore,
    DocumentPurpose,
    DocumentType,
    ReviewAudience,
    BusinessValue,
    ImpactScope,
)

# 工作区根目录
WORKSPACE_ROOT = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE_ROOT / "03_输出成果"
AUDIT_LOG_DIR = OUTPUT_DIR / "审核记录"


class AgentAutoFixer:
    """Agent自动修复执行器"""
    
    def __init__(self):
        # Agent分配规则
        self.agent_mapping = {
            "需求文档": {
                "agent": "采薇",
                "agent_id": "caiwei",
                "emoji": "🌸",
                "skill": "compass-needdoc",
            },
            "思维导图": {
                "agent": "织锦",
                "agent_id": "zhijin",
                "emoji": "🧵",
                "skill": "compass-mindmap",
            },
            "方案PPT": {
                "agent": "呈彩",
                "agent_id": "chengcai",
                "emoji": "🎨",
                "skill": "compass-ppt",
            },
            "详细设计": {
                "agent": "工尺",
                "agent_id": "gongchi",
                "emoji": "📐",
                "skill": "compass-design",
            },
            "项目计划": {
                "agent": "玉衡",
                "agent_id": "yuheng",
                "emoji": "⚖️",
                "skill": "compass-project",
            },
        }
        
        # 章节修复模板
        self.section_templates = {
            "建设背景": self._template_background,
            "建设目的": self._template_purpose,
            "功能需求": self._template_functional,
            "验收标准": self._template_acceptance,
            "核心主题": self._template_core_topic,
            "优先级标注": self._template_priority,
            "封面页": self._template_cover,
            "目录页": self._template_toc,
            "架构设计": self._template_architecture,
            "接口设计": self._template_interface,
            "数据库设计": self._template_database,
            "WBS分解": self._template_wbs,
            "RACI矩阵": self._template_raci,
            "风险清单": self._template_risk,
        }
    
    def _template_background(self, context: dict) -> str:
        """建设背景模板"""
        return """
## 1.1 建设背景

### 项目背景
本项目源于{客户名称}{部门}的{业务需求}。

### 业务痛点
当前存在以下问题：
1. {痛点1}
2. {痛点2}
3. {痛点3}

### 建设必要性
为解决上述问题，亟需通过{解决方案}实现{目标}。
"""
    
    def _template_purpose(self, context: dict) -> str:
        """建设目的模板"""
        return """
## 1.2 建设目的

### 解决问题
1. {问题1}
2. {问题2}

### 预期效果
1. 指标一：{效果1}
2. 指标二：{效果2}
3. 效率提升：{效果3}
"""
    
    def _template_functional(self, context: dict) -> str:
        """功能需求模板"""
        return """
## 3. 功能需求

### 3.1 功能结构
```
{系统名称}
├── {模块1}
│   ├── {子模块1-1}
│   └── {子模块1-2}
├── {模块2}
│   ├── {子模块2-1}
│   └── {子模块2-2}
└── 系统管理
    ├── 用户管理
    └── 权限管理
```

### 3.2 功能清单
| 功能模块 | 功能描述 | 优先级 |
|---------|---------|:------:|
| {模块1} | {描述1} | MUST |
| {模块2} | {描述2} | MUST |
"""
    
    def _template_acceptance(self, context: dict) -> str:
        """验收标准模板"""
        return """
## 6. 验收标准

### 6.1 功能验收标准
| 需求编号 | 验收标准 | 验收方法 |
|:-------:|---------|:--------:|
| FR-001 | {验收标准1} | 功能测试 |
| FR-002 | {验收标准2} | 功能测试 |

### 6.2 性能验收标准
| 指标 | 目标值 | 验收方法 |
|-----|:-----:|:--------:|
| 响应时间 | ≤3秒 | 性能测试 |
| 并发用户 | ≥100 | 性能测试 |

### 6.3 业务验收标准
- {业务指标1}：{目标值1}
- {业务指标2}：{目标值2}
"""
    
    def _template_core_topic(self, context: dict) -> str:
        """核心主题模板"""
        return """
# {主题名称}

## 核心问题
{核心问题描述}

## 主要分支
1. {分支1}
2. {分支2}
3. {分支3}
"""
    
    def _template_priority(self, context: dict) -> str:
        """优先级标注模板"""
        return """
## 优先级说明

| 优先级 | 说明 | 标注 |
|:------:|------|:----:|
| P0 | 必须完成，核心功能 | 🔴 |
| P1 | 重要功能，优先实现 | 🟡 |
| P2 | 可选功能，后续迭代 | 🟢 |

## 功能优先级
- {功能1}：P0 🔴
- {功能2}：P1 🟡
- {功能3}：P2 🟢
"""
    
    def _template_cover(self, context: dict) -> str:
        """封面页模板"""
        return """
# 封面页设计

---
项目名称：{项目名称}
汇报人：{汇报人}
日期：{日期}
---

【PPT封面】
- 主标题：{项目名称}
- 副标题：{副标题}
- 汇报单位：{单位名称}
- 汇报日期：{日期}
"""
    
    def _template_toc(self, context: dict) -> str:
        """目录页模板"""
        return """
# 目录

1. 项目背景
2. 需求分析
3. 解决方案
4. 实施计划
5. 预期效果
6. 总结展望
"""
    
    def _template_architecture(self, context: dict) -> str:
        """架构设计模板"""
        return """
## 架构设计

### 系统架构
```
┌─────────────────────────────────────┐
│           展现层                     │
│   Web前端 / 移动端 / 小程序          │
├─────────────────────────────────────┤
│           应用层                     │
│   API网关 / 业务服务 / 认证服务       │
├─────────────────────────────────────┤
│           数据层                     │
│   MySQL / Redis / Elasticsearch      │
├─────────────────────────────────────┤
│           基础设施层                  │
│   云服务器 / 对象存储 / 消息队列       │
└─────────────────────────────────────┘
```

### 技术架构
- 前端：Vue.js / React
- 后端：Spring Boot / Python Flask
- 数据库：MySQL / Redis
- 部署：Docker / Kubernetes
"""
    
    def _template_interface(self, context: dict) -> str:
        """接口设计模板"""
        return """
## 接口设计

### 接口清单
| 接口编号 | 接口名称 | 请求方式 | 说明 |
|:-------:|---------|:-------:|------|
| API-001 | {接口1} | POST | {说明1} |
| API-002 | {接口2} | GET | {说明2} |

### API-001 {接口名称}

**请求参数**：
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|:----:|------|
| param1 | String | 是 | {说明} |

**响应参数**：
| 参数名 | 类型 | 说明 |
|-------|------|------|
| code | Int | 状态码 |
| message | String | 消息 |
| data | Object | 数据 |
"""
    
    def _template_database(self, context: dict) -> str:
        """数据库设计模板"""
        return """
## 数据库设计

### 数据表清单
| 表名 | 说明 | 备注 |
|-----|------|------|
| t_user | 用户表 | |
| t_order | 订单表 | |

### t_user 用户表
| 字段 | 名称 | 类型 | 说明 |
|-----|------|------|------|
| id | 主键 | BIGINT | 自增 |
| username | 用户名 | VARCHAR(50) | 唯一 |
| created_at | 创建时间 | DATETIME | |
"""
    
    def _template_wbs(self, context: dict) -> str:
        """WBS分解模板"""
        return """
## WBS分解

### 工作分解结构
```
1. 项目管理
   1.1 项目启动
   1.2 项目规划
   1.3 项目监控
   1.4 项目收尾

2. 需求分析
   2.1 需求调研
   2.2 需求文档
   2.3 需求评审

3. 系统设计
   3.1 架构设计
   3.2 详细设计
   3.3 数据库设计

4. 开发实现
   4.1 前端开发
   4.2 后端开发
   4.3 接口联调

5. 测试验收
   5.1 单元测试
   5.2 集成测试
   5.3 验收测试
```
"""
    
    def _template_raci(self, context: dict) -> str:
        """RACI矩阵模板"""
        return """
## RACI矩阵

| 任务 | 项目经理 | 需求分析师 | 开发工程师 | 测试工程师 |
|-----|:-------:|:---------:|:---------:|:---------:|
| 需求调研 | A | R | C | I |
| 架构设计 | A | C | R | I |
| 编码实现 | A | I | R | C |
| 测试验收 | A | I | C | R |

**说明**：R-执行 | A-负责 | C-咨询 | I-知情
"""
    
    def _template_risk(self, context: dict) -> str:
        """风险清单模板"""
        return """
## 风险清单

| 风险编号 | 风险描述 | 影响程度 | 发生概率 | 应对措施 |
|:-------:|---------|:-------:|:-------:|---------|
| R001 | 需求变更频繁 | 高 | 中 | 需求冻结机制 |
| R002 | 技术难点攻关 | 中 | 高 | 预研验证 |
| R003 | 人员变动 | 中 | 低 | 文档完善 |
"""
    
    def get_agent_info(self, doc_type: str) -> dict:
        """获取负责Agent信息"""
        return self.agent_mapping.get(doc_type, self.agent_mapping["需求文档"])
    
    def build_fix_prompt(self, doc_type: str, missing_sections: List[str], 
                          original_content: str = "") -> str:
        """构建修复提示词"""
        agent_info = self.get_agent_info(doc_type)
        agent_name = agent_info["agent"]
        agent_emoji = agent_info["emoji"]
        
        prompt_lines = [
            f"# {agent_emoji} {agent_name} - 文档修复任务",
            "",
            f"**文档类型**：{doc_type}",
            f"**缺失章节**：{', '.join(missing_sections)}",
            "",
            "---",
            "",
            "## 需要补充的内容",
            "",
        ]
        
        for section in missing_sections:
            template_func = self.section_templates.get(section)
            if template_func:
                template_content = template_func({})
                prompt_lines.append(f"### {section}")
                prompt_lines.append("")
                prompt_lines.append("**内容模板**：")
                prompt_lines.append("```markdown")
                prompt_lines.append(template_content.strip())
                prompt_lines.append("```")
                prompt_lines.append("")
                
                # 添加AI生成提示
                prompt_lines.append(f"**生成要求**：请根据项目实际情况，填充上述模板中的占位符，生成完整内容。")
                prompt_lines.append("")
            else:
                prompt_lines.append(f"### {section}")
                prompt_lines.append("")
                prompt_lines.append(f"请补充{section}相关内容。")
                prompt_lines.append("")
        
        return "\n".join(prompt_lines)
    
    def generate_fix_content_with_ai(self, doc_type: str, missing_sections: List[str],
                                      context: dict = None) -> dict:
        """使用AI生成修复内容（返回可供南乔调用的提示词）"""
        agent_info = self.get_agent_info(doc_type)
        agent_name = agent_info["agent"]
        agent_emoji = agent_info["emoji"]
        skill = agent_info["skill"]
        
        # 构建给南乔的调用指令
        instruction = {
            "task": "auto_fix_document",
            "agent": agent_name,
            "agent_id": agent_info["agent_id"],
            "skill": skill,
            "doc_type": doc_type,
            "missing_sections": missing_sections,
            "action": f"请{agent_emoji} {agent_name}补充{doc_type}的以下缺失章节：{', '.join(missing_sections)}",
            "prompts": {},
        }
        
        # 为每个缺失章节生成具体提示
        for section in missing_sections:
            template_func = self.section_templates.get(section)
            if template_func:
                instruction["prompts"][section] = {
                    "template": template_func(context or {}),
                    "requirement": f"请根据项目上下文，填充模板中的占位符，生成完整的{section}内容",
                }
        
        return instruction
    
    def fix_document(self, file_path: str, diagnosis: dict, 
                     auto_mode: bool = False) -> dict:
        """执行文档修复"""
        doc_type = diagnosis.get("doc_type", "需求文档")
        missing_sections = diagnosis.get("missing_sections", [])
        
        print(f"\n{'='*60}")
        print(f"🔧 Agent自动修复执行器")
        print(f"{'='*60}")
        print(f"📄 文件：{file_path}")
        print(f"📂 类型：{doc_type}")
        print(f"📝 缺失章节：{', '.join(missing_sections)}")
        print(f"{'='*60}\n")
        
        # 获取负责Agent
        agent_info = self.get_agent_info(doc_type)
        print(f"👤 负责Agent：{agent_info['emoji']} {agent_info['agent']}")
        print(f"📌 关联技能：{agent_info['skill']}")
        
        # 生成修复指令
        instruction = self.generate_fix_content_with_ai(doc_type, missing_sections)
        
        print(f"\n📋 修复指令：")
        print(f"   {instruction['action']}")
        
        for section, prompt in instruction.get("prompts", {}).items():
            print(f"\n   【{section}】")
            print(f"   要求：{prompt['requirement']}")
        
        # 如果自动模式，返回可执行的指令
        if auto_mode:
            return {
                "status": "ready_for_agent",
                "instruction": instruction,
                "agent_info": agent_info,
                "file_path": file_path,
            }
        
        # 否则返回修复建议供人工确认
        return {
            "status": "need_confirmation",
            "instruction": instruction,
            "agent_info": agent_info,
            "file_path": file_path,
            "message": f"请确认是否调用 {agent_info['emoji']} {agent_info['agent']} 执行修复？",
        }


class FullClosedLoopSystem:
    """完整闭环质量保证系统（含Agent自动修复 + 智能模式判断）"""
    
    def __init__(self):
        self.quality_system = ClosedLoopQualitySystem()
        self.auto_fixer = AgentAutoFixer()
        self.importance_evaluator = DocumentImportanceEvaluator()
    
    def determine_review_mode(self, file_path: str, content: str = None,
                               mode: str = "smart") -> Tuple[str, DocumentImportanceScore]:
        """确定审核模式
        
        Args:
            file_path: 文件路径
            content: 文档内容（可选）
            mode: 模式选择
                - "smart": 智能判断（根据文档重要性自动选择）
                - "semi": 强制半自动
                - "auto": 强制全自动
        
        Returns:
            (审核模式, 重要性评分)
        """
        if mode == "semi":
            # 强制半自动，但仍计算重要性
            score = self.importance_evaluator.evaluate(file_path, content)
            return "semi", score
        
        if mode == "auto":
            # 强制全自动，但仍计算重要性
            score = self.importance_evaluator.evaluate(file_path, content)
            return "auto", score
        
        # 智能模式：根据重要性自动选择
        score = self.importance_evaluator.evaluate(file_path, content)
        return score.recommended_mode, score
    
    def process(self, file_path: str, doc_type: str = None, 
                auto_fix: bool = False, max_iterations: int = 3,
                mode: str = "smart") -> dict:
        """完整闭环处理
        
        Args:
            file_path: 文件路径
            doc_type: 文档类型（可选）
            auto_fix: 是否自动修复（已废弃，由mode决定）
            max_iterations: 最大迭代次数
            mode: 审核模式
                - "smart": 智能判断（推荐）
                - "semi": 半自动（人工确认每步）
                - "auto": 全自动（一键完成）
        """
        print(f"\n{'='*70}")
        print(f"🔄 完整闭环质量保证系统 V2.0（智能模式）")
        print(f"{'='*70}")
        
        # 1. 评估文档重要性，确定审核模式
        print(f"\n📊 正在评估文档重要性...")
        review_mode, importance_score = self.determine_review_mode(file_path, mode=mode)
        
        print(f"\n{'─'*70}")
        print(f"📋 文档重要性评估")
        print(f"{'─'*70}")
        print(f"  用途得分：{importance_score.purpose_score}")
        print(f"  类型得分：{importance_score.type_score}")
        print(f"  审阅对象得分：{importance_score.audience_score}")
        print(f"  业务价值得分：{importance_score.value_score}")
        print(f"  影响范围得分：{importance_score.scope_score}")
        print(f"  总分：{importance_score.total_score}")
        print(f"  等级：{importance_score.level}")
        print(f"  审核模式：{'半自动（人工确认）' if review_mode == 'semi' else '全自动'}")
        print(f"{'─'*70}")
        
        # 2. 开始闭环处理
        iteration = 0
        all_results = []
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'─'*70}")
            print(f"第 {iteration} 轮处理")
            print(f"{'─'*70}")
            
            # 2.1 审核
            audit_result = self.quality_system.auditor.audit(file_path, doc_type)
            grade = audit_result["grade"]
            score = audit_result["score"]
            
            print(f"\n📊 审核结果：{score}分 | {grade}级")
            
            # 记录结果
            all_results.append({
                "iteration": iteration,
                "grade": grade,
                "score": score,
                "audit_result": audit_result,
            })
            
            # 2.2 判断是否通过
            if grade == "A":
                print(f"\n✅ 审核通过！等级：A级")
                return {
                    "status": "passed",
                    "final_grade": "A",
                    "final_score": score,
                    "iterations": iteration,
                    "all_results": all_results,
                    "importance_score": importance_score,
                    "review_mode": review_mode,
                }
            
            if grade == "B":
                print(f"\n✅ 审核通过！等级：B级（小幅优化后通过）")
                return {
                    "status": "passed",
                    "final_grade": "B",
                    "final_score": score,
                    "iterations": iteration,
                    "all_results": all_results,
                    "importance_score": importance_score,
                    "review_mode": review_mode,
                }
            
            # 2.3 C/D级需要修复
            if iteration >= max_iterations:
                print(f"\n⚠️ 达到最大迭代次数（{max_iterations}次），需要人工介入")
                return {
                    "status": "need_manual_intervention",
                    "final_grade": grade,
                    "final_score": score,
                    "iterations": iteration,
                    "all_results": all_results,
                    "importance_score": importance_score,
                    "review_mode": review_mode,
                }
            
            # 2.4 诊断问题
            print(f"\n🔍 诊断问题...")
            diagnosis = self.quality_system.diagnoser.diagnose(audit_result)
            missing = diagnosis.get("missing_sections", [])
            
            if missing:
                print(f"📝 缺失章节：{', '.join(missing)}")
            else:
                print(f"📝 问题已记录，但无明确缺失章节")
            
            # 2.5 调用Agent修复
            print(f"\n🔧 准备调用Agent修复...")
            fix_result = self.auto_fixer.fix_document(file_path, diagnosis, auto_mode=True)
            
            # 2.6 根据审核模式决定是否需要人工确认
            if review_mode == "semi":
                # 半自动模式：需要人工确认
                print(f"\n{'='*70}")
                print(f"📋 修复建议（需人工确认）")
                print(f"{'='*70}")
                print(f"Agent：{fix_result['agent_info']['emoji']} {fix_result['agent_info']['agent']}")
                print(f"动作：{fix_result['instruction']['action']}")
                
                return {
                    "status": "waiting_confirmation",
                    "iteration": iteration,
                    "diagnosis": diagnosis,
                    "fix_result": fix_result,
                    "all_results": all_results,
                    "importance_score": importance_score,
                    "review_mode": review_mode,
                    "message": f"请确认是否调用 {fix_result['agent_info']['emoji']} {fix_result['agent_info']['agent']} 执行修复？",
                }
            
            # 全自动模式：返回修复指令，等待南乔执行
            print(f"\n🔄 执行修复...")
            print(f"   注意：实际修复需要南乔调用对应Agent执行")
            print(f"   指令：{fix_result['instruction']['action']}")
            
            return {
                "status": "ready_for_fix",
                "iteration": iteration,
                "diagnosis": diagnosis,
                "fix_result": fix_result,
                "all_results": all_results,
                "importance_score": importance_score,
                "review_mode": review_mode,
                "message": f"请南乔调用 {fix_result['agent_info']['emoji']} {fix_result['agent_info']['agent']} 执行修复",
            }
        
        return {
            "status": "max_iterations_reached",
            "iterations": iteration,
            "all_results": all_results,
            "importance_score": importance_score,
            "review_mode": review_mode,
        }


def main():
    """测试入口"""
    print("\n" + "="*70)
    print("Agent自动修复执行器 - 测试")
    print("="*70)
    
    # 创建系统
    system = FullClosedLoopSystem()
    
    # 测试
    test_file = WORKSPACE_ROOT / "知识库" / "方法论" / "提示词工程框架.md"
    
    if test_file.exists():
        result = system.process(str(test_file), auto_fix=False)
        
        print(f"\n{'='*70}")
        print(f"处理结果")
        print(f"{'='*70}")
        print(f"状态：{result['status']}")
        
        if result['status'] == 'ready_for_fix':
            print(f"迭代次数：{result['iteration']}")
            print(f"缺失章节：{result['diagnosis'].get('missing_sections', [])}")
            print(f"负责Agent：{result['fix_result']['agent_info']['emoji']} {result['fix_result']['agent_info']['agent']}")
            print(f"\n修复指令：{result['fix_result']['instruction']['action']}")
    else:
        print(f"\n❌ 测试文件不存在：{test_file}")


if __name__ == "__main__":
    main()
