#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent调用包装器 - Agent Wrapper with Auto Audit
功能：调用Agent技能后自动触发审核，确保产出质量
创建时间：2026-03-23
创建者：南乔
版本：V1.0

使用方法：
    from scripts.agent_wrapper import run_agent_with_audit
    
    result = run_agent_with_audit(
        agent_name="采薇",
        skill_id="compass-needdoc",
        task="生成湖北电信AI配案需求文档",
        output_file="03_输出成果/需求文档.md"
    )
    
    # 自动执行：调用Agent → 审核产出 → 通知少帅
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_output_auditor import AgentOutputAuditor


class AgentWrapper:
    """Agent调用包装器（含自动审核）"""
    
    # Agent与技能映射
    AGENT_SKILL_MAP = {
        "采薇": "compass-needdoc",
        "织锦": "compass-solution",
        "呈彩": "compass-ppt",
        "工尺": "compass-design",
        "玉衡": "compass-project",
        "筑台": "compass-solution",
        "折桂": "compass-resource",
        "扶摇": "compass-coordinator",
        "天工": "compass-dev",
        "知微": "compass-analysis",
    }
    
    def __init__(self):
        self.auditor = AgentOutputAuditor()
        self.workspace_root = Path("/root/.openclaw/workspace")
    
    def run_agent_with_audit(self, agent_name: str, task: str,
                              output_file: str,
                              skill_id: str = None,
                              auto_notify: bool = True,
                              audit_mode: str = "smart") -> dict:
        """调用Agent并自动审核
        
        Args:
            agent_name: Agent名称
            task: 任务描述
            output_file: 输出文件路径
            skill_id: 技能ID（可选，自动从映射表获取）
            auto_notify: 是否自动通知少帅
            audit_mode: 审核模式（smart/semi/auto）
        
        Returns:
            包含Agent执行结果和审核结果的字典
        """
        # 获取技能ID
        if skill_id is None:
            skill_id = self.AGENT_SKILL_MAP.get(agent_name)
        
        print(f"\n{'='*70}")
        print(f"🚀 Agent调用包装器（含自动审核）")
        print(f"{'='*70}")
        print(f"Agent：{agent_name}")
        print(f"技能：{skill_id}")
        print(f"任务：{task}")
        print(f"输出：{output_file}")
        print(f"{'='*70}")
        
        result = {
            "agent_name": agent_name,
            "skill_id": skill_id,
            "task": task,
            "output_file": output_file,
            "agent_status": "pending",
            "audit_status": "pending",
        }
        
        # 提示：实际Agent调用需要通过sessions_spawn或其他方式
        # 这里是包装器框架，实际调用由南乔在会话中执行
        
        print(f"\n📋 步骤1：调用Agent执行任务")
        print(f"   提示：使用 sessions_spawn 调用 {skill_id}")
        print(f"   任务：{task}")
        print(f"   ⏳ 等待Agent完成...")
        
        # 实际调用时，南乔会使用sessions_spawn
        # agent_result = sessions_spawn(agentId=skill_id, task=task)
        # result["agent_result"] = agent_result
        # result["agent_status"] = "completed"
        
        print(f"\n📋 步骤2：自动触发审核")
        print(f"   文件：{output_file}")
        print(f"   模式：{audit_mode}")
        
        # 检查文件是否存在
        file_path = Path(output_file)
        if not file_path.is_absolute():
            file_path = self.workspace_root / output_file
        
        if file_path.exists():
            audit_result = self.auditor.audit_agent_output(
                agent_name=agent_name,
                output_path=str(file_path),
                auto_notify=auto_notify,
                mode=audit_mode
            )
            result["audit_result"] = audit_result
            result["audit_status"] = audit_result.get("status", "unknown")
        else:
            print(f"   ⚠️ 文件尚未生成，等待Agent完成")
            result["audit_status"] = "waiting_file"
        
        return result


def run_agent_with_audit(agent_name: str, task: str, output_file: str,
                          skill_id: str = None, auto_notify: bool = True,
                          audit_mode: str = "smart") -> dict:
    """便捷函数：调用Agent并自动审核
    
    Args:
        agent_name: Agent名称（采薇/织锦/呈彩/工尺/玉衡/筑台/折桂/扶摇/天工/知微）
        task: 任务描述
        output_file: 输出文件路径
        skill_id: 技能ID（可选）
        auto_notify: 是否自动通知少帅（默认True）
        audit_mode: 审核模式（默认smart）
    
    Returns:
        包含执行结果和审核结果的字典
    
    示例：
        result = run_agent_with_audit(
            agent_name="采薇",
            task="生成湖北电信AI配案需求文档",
            output_file="03_输出成果/需求文档.md"
        )
        
        if result["audit_status"] == "passed":
            print("✅ 审核通过")
        else:
            print("⚠️ 需要修复")
    """
    wrapper = AgentWrapper()
    return wrapper.run_agent_with_audit(
        agent_name=agent_name,
        task=task,
        output_file=output_file,
        skill_id=skill_id,
        auto_notify=auto_notify,
        audit_mode=audit_mode
    )


# 测试
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Agent调用包装器 - 测试")
    print("="*70)
    
    print("\n模拟场景：调用采薇生成需求文档，并自动审核")
    print("-"*70)
    
    # 模拟调用（使用已存在的测试文件）
    result = run_agent_with_audit(
        agent_name="采薇",
        task="生成提示词工程框架需求文档",
        output_file="知识库/方法论/提示词工程框架.md",
        audit_mode="smart"
    )
    
    print(f"\n{'='*70}")
    print(f"📊 执行结果")
    print(f"{'='*70}")
    print(f"Agent：{result['agent_name']}")
    print(f"技能：{result['skill_id']}")
    print(f"审核状态：{result['audit_status']}")
