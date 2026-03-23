#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整闭环执行器 - Closed Loop Executor
功能：实现全自动闭环质量保证，包括AI生成、文档更新、复审循环
创建时间：2026-03-23
创建者：南乔
版本：V3.0 - 全自动闭环
"""

import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 导入其他模块
import sys
sys.path.insert(0, str(Path(__file__).parent))
from agent_auto_fixer import FullClosedLoopSystem, AgentAutoFixer
from document_importance_evaluator import DocumentImportanceEvaluator

# 工作区根目录
WORKSPACE_ROOT = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE_ROOT / "03_输出成果"
AUDIT_LOG_DIR = OUTPUT_DIR / "审核记录"

# 千帆API配置（从环境变量获取）
QIANFAN_API_URL = os.environ.get("QIANFAN_API_URL", "https://qianfan.baidubce.com/v2/coding/chat/completions")
QIANFAN_API_KEY = os.environ.get("QIANFAN_API_KEY", "")


class AIContentGenerator:
    """AI内容生成器 - 调用千帆API生成补充内容"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or QIANFAN_API_URL
        self.api_key = api_key or QIANFAN_API_KEY
    
    def generate_section_content(self, section_name: str, template: str, 
                                  context: str, doc_type: str) -> str:
        """生成章节内容
        
        Args:
            section_name: 章节名称
            template: 内容模板
            context: 文档上下文
            doc_type: 文档类型
        
        Returns:
            生成的章节内容
        """
        prompt = f"""你是一位专业的{doc_type}撰写专家。请根据以下信息生成完整的章节内容。

## 任务要求
- 章节名称：{section_name}
- 请填充模板中的占位符，生成完整、专业的内容
- 内容要具体、可落地，不要泛泛而谈

## 内容模板
{template}

## 文档上下文
{context[:2000]}

## 输出要求
请直接输出填充后的完整内容，不要输出其他说明。
"""
        
        try:
            # 调用千帆API
            response = self._call_qianfan(prompt)
            return response
        except Exception as e:
            print(f"❌ AI生成失败：{e}")
            return self._fallback_generate(section_name, template)
    
    def _call_qianfan(self, prompt: str) -> str:
        """调用千帆API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        data = {
            "model": "qianfan-code-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=60,
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            raise Exception(f"API调用失败：{response.status_code} - {response.text}")
    
    def _fallback_generate(self, section_name: str, template: str) -> str:
        """降级生成（API不可用时）"""
        # 简单替换模板中的占位符
        content = template
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        for placeholder in placeholders:
            # 用描述性文本替换
            content = content.replace(f"{{{placeholder}}}", f"[待补充：{placeholder}]")
        
        return content


class DocumentUpdater:
    """文档更新器 - 智能插入补充内容"""
    
    def __init__(self):
        self.section_markers = {
            "建设背景": ["## 1.1 建设背景", "# 建设背景", "## 建设背景"],
            "建设目的": ["## 1.2 建设目的", "# 建设目的", "## 建设目的"],
            "功能需求": ["## 3. 功能需求", "# 功能需求", "## 功能需求"],
            "验收标准": ["## 6. 验收标准", "# 验收标准", "## 验收标准"],
            "架构设计": ["## 架构设计", "# 架构设计"],
            "接口设计": ["## 接口设计", "# 接口设计"],
            "数据库设计": ["## 数据库设计", "# 数据库设计"],
            "WBS分解": ["## WBS分解", "# WBS分解"],
            "RACI矩阵": ["## RACI矩阵", "# RACI矩阵"],
            "风险清单": ["## 风险清单", "# 风险清单"],
        }
    
    def find_insert_position(self, content: str, section_name: str) -> int:
        """找到插入位置
        
        Returns:
            插入位置（行号），-1表示未找到
        """
        lines = content.split("\n")
        markers = self.section_markers.get(section_name, [f"## {section_name}", f"# {section_name}"])
        
        for i, line in enumerate(lines):
            for marker in markers:
                if marker in line:
                    return i
        
        return -1
    
    def insert_content(self, file_path: str, section_name: str, 
                       new_content: str, position: str = "after_header") -> bool:
        """插入内容到文档
        
        Args:
            file_path: 文件路径
            section_name: 章节名称
            new_content: 新内容
            position: 插入位置
                - "after_header": 在标题后插入
                - "replace": 替换整个章节
                - "append": 追加到文档末尾
        
        Returns:
            是否成功
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = content.split("\n")
            
            # 查找章节位置
            section_pos = self.find_insert_position(content, section_name)
            
            if section_pos == -1:
                # 章节不存在，追加到合适位置
                # 找到文档结构中的合适位置
                insert_pos = self._find_best_insert_position(lines, section_name)
                
                # 插入新章节
                new_section = f"\n\n## {section_name}\n\n{new_content}\n"
                lines.insert(insert_pos, new_section)
            else:
                # 章节已存在，根据策略处理
                if position == "replace":
                    # 替换整个章节
                    lines = self._replace_section(lines, section_pos, new_content)
                else:
                    # 在章节后追加
                    insert_pos = self._find_section_end(lines, section_pos)
                    lines.insert(insert_pos, f"\n{new_content}\n")
            
            # 写回文件
            new_file_content = "\n".join(lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_file_content)
            
            print(f"✅ 已更新文档：{file_path}")
            return True
        
        except Exception as e:
            print(f"❌ 更新文档失败：{e}")
            return False
    
    def _find_best_insert_position(self, lines: List[str], section_name: str) -> int:
        """找到最佳插入位置"""
        # 简单策略：在文档末尾插入
        return len(lines)
    
    def _find_section_end(self, lines: List[str], section_start: int) -> int:
        """找到章节结束位置"""
        for i in range(section_start + 1, len(lines)):
            if lines[i].startswith("#"):
                return i
        return len(lines)
    
    def _replace_section(self, lines: List[str], section_start: int, 
                         new_content: str) -> List[str]:
        """替换章节内容"""
        section_end = self._find_section_end(lines, section_start)
        
        # 保留章节标题
        title = lines[section_start]
        
        # 替换内容
        new_lines = lines[:section_start + 1]
        new_lines.append(new_content)
        new_lines.extend(lines[section_end:])
        
        return new_lines


class ClosedLoopExecutor:
    """完整闭环执行器"""
    
    def __init__(self):
        self.system = FullClosedLoopSystem()
        self.ai_generator = AIContentGenerator()
        self.doc_updater = DocumentUpdater()
        self.max_iterations = 3
    
    def execute(self, file_path: str, mode: str = "smart") -> dict:
        """执行完整闭环
        
        Args:
            file_path: 文件路径
            mode: 审核模式
                - "smart": 智能判断
                - "semi": 半自动（需人工确认）
                - "auto": 全自动
        
        Returns:
            执行结果
        """
        print(f"\n{'='*70}")
        print(f"🔄 完整闭环执行器 V3.0")
        print(f"{'='*70}")
        print(f"📄 文件：{file_path}")
        print(f"📌 模式：{mode}")
        
        # 读取文档内容
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        iteration = 0
        all_results = []
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'─'*70}")
            print(f"第 {iteration} 轮")
            print(f"{'─'*70}")
            
            # 1. 审核文档
            result = self.system.process(file_path, mode=mode)
            all_results.append(result)
            
            # 2. 判断是否通过
            if result["status"] == "passed":
                print(f"\n✅ 审核通过！等级：{result['final_grade']}")
                return self._build_success_result(result, iteration, all_results)
            
            # 3. 需要修复
            if result["status"] in ["waiting_confirmation", "ready_for_fix"]:
                
                # 如果是半自动模式，等待人工确认
                if mode == "semi" or result.get("review_mode") == "semi":
                    print(f"\n⏸️ 半自动模式，等待人工确认...")
                    print(f"   {result.get('message', '')}")
                    return result
                
                # 全自动模式，自动执行修复
                print(f"\n🔧 全自动模式，开始修复...")
                
                fix_result = result.get("fix_result", {})
                diagnosis = result.get("diagnosis", {})
                missing_sections = diagnosis.get("missing_sections", [])
                
                if not missing_sections:
                    print(f"⚠️ 无明确缺失章节，无法自动修复")
                    return result
                
                # 4. AI生成补充内容
                print(f"\n🤖 AI生成补充内容...")
                
                for section in missing_sections:
                    print(f"   生成：{section}")
                    
                    # 获取模板
                    prompts = fix_result.get("instruction", {}).get("prompts", {})
                    section_prompt = prompts.get(section, {})
                    template = section_prompt.get("template", f"## {section}\n\n{{待补充内容}}")
                    
                    # 调用AI生成
                    new_content = self.ai_generator.generate_section_content(
                        section_name=section,
                        template=template,
                        context=original_content,
                        doc_type=result.get("importance_score", {}).get("level", "需求文档"),
                    )
                    
                    print(f"   生成内容：{new_content[:100]}...")
                    
                    # 5. 更新文档
                    print(f"   更新文档...")
                    success = self.doc_updater.insert_content(
                        file_path=file_path,
                        section_name=section,
                        new_content=new_content,
                        position="after_header",
                    )
                    
                    if success:
                        print(f"   ✅ {section} 已补充")
                    else:
                        print(f"   ❌ {section} 补充失败")
                
                # 6. 继续下一轮审核
                print(f"\n🔄 重新审核...")
                continue
            
            # 其他状态
            if result["status"] == "need_manual_intervention":
                print(f"\n⚠️ 需要人工介入")
                return result
        
        # 达到最大迭代次数
        print(f"\n⚠️ 达到最大迭代次数（{self.max_iterations}次）")
        return {
            "status": "max_iterations_reached",
            "iterations": iteration,
            "all_results": all_results,
        }
    
    def _build_success_result(self, result: dict, iteration: int, 
                               all_results: list) -> dict:
        """构建成功结果"""
        return {
            "status": "passed",
            "final_grade": result.get("final_grade", "A"),
            "final_score": result.get("final_score", 0),
            "iterations": iteration,
            "all_results": all_results,
            "message": f"审核通过！最终等级：{result.get('final_grade', 'A')}，得分：{result.get('final_score', 0)}",
        }


def main():
    """测试入口"""
    print("\n" + "="*70)
    print("🧪 完整闭环执行器 - 测试")
    print("="*70)
    
    executor = ClosedLoopExecutor()
    
    # 测试文件
    test_file = WORKSPACE_ROOT / "知识库" / "方法论" / "提示词工程框架.md"
    
    if test_file.exists():
        # 先备份
        import shutil
        backup_file = test_file.with_suffix(".md.backup")
        shutil.copy(test_file, backup_file)
        print(f"📦 已备份：{backup_file}")
        
        # 执行闭环
        result = executor.execute(str(test_file), mode="auto")
        
        print(f"\n{'='*70}")
        print(f"📊 执行结果")
        print(f"{'='*70}")
        print(f"状态：{result['status']}")
        if result['status'] == 'passed':
            print(f"最终等级：{result['final_grade']}")
            print(f"最终得分：{result['final_score']}")
            print(f"迭代次数：{result['iterations']}")
    else:
        print(f"\n❌ 测试文件不存在：{test_file}")


if __name__ == "__main__":
    main()
