#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent产出物审核包装器 - Agent Output Auditor
功能：拦截Agent产出物，自动触发审核，确保质量达标
创建时间：2026-03-23
创建者：南乔
版本：V1.0

使用方法：
    # 在调用Agent技能后，使用包装器审核
    from scripts.agent_output_auditor import AgentOutputAuditor
    
    auditor = AgentOutputAuditor()
    result = auditor.audit_agent_output(
        agent_name="采薇",
        output_path="03_输出成果/需求文档.md",
        auto_notify=True
    )
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from closed_loop_executor import ClosedLoopExecutor


class AgentOutputAuditor:
    """Agent产出物审核包装器"""
    
    # Agent信息
    AGENTS = {
        "采薇": {"emoji": "🌸", "skill": "compass-needdoc", "output_type": "需求文档"},
        "织锦": {"emoji": "🧵", "skill": "compass-solution", "output_type": "方案举措"},
        "呈彩": {"emoji": "🎨", "skill": "compass-ppt", "output_type": "方案PPT"},
        "工尺": {"emoji": "📐", "skill": "compass-design", "output_type": "详细设计"},
        "玉衡": {"emoji": "⚖️", "skill": "compass-project", "output_type": "项目管控"},
        "筑台": {"emoji": "🏗️", "skill": "compass-solution", "output_type": "售前方案"},
        "折桂": {"emoji": "📚", "skill": "compass-resource", "output_type": "知识文档"},
        "扶摇": {"emoji": "🌀", "skill": "compass-coordinator", "output_type": "协调报告"},
        "天工": {"emoji": "💻", "skill": "compass-dev", "output_type": "代码/接口"},
        "知微": {"emoji": "📊", "skill": "compass-analysis", "output_type": "分析报告"},
    }
    
    # 审核结果通知配置
    NOTIFY_CONFIG = {
        "channel": "qqbot",
        "to": "8236C3DA8CF6F5DF6FEE66D42ADAAE97",  # 少帅QQ
        "email": "szideaf7@163.com",  # 重要文件发送邮箱
    }
    
    def __init__(self):
        self.executor = ClosedLoopExecutor()
        self.workspace_root = Path("/root/.openclaw/workspace")
        self.audit_log_dir = self.workspace_root / "03_输出成果" / "审核记录"
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)
    
    def audit_agent_output(self, agent_name: str, output_path: str, 
                            auto_notify: bool = True,
                            mode: str = "smart") -> dict:
        """审核Agent产出物
        
        Args:
            agent_name: Agent名称（采薇/织锦/呈彩/工尺/玉衡/筑台/折桂/扶摇/天工/知微）
            output_path: 产出物路径
            auto_notify: 是否自动通知少帅
            mode: 审核模式（smart/semi/auto）
        
        Returns:
            审核结果
        """
        # 获取Agent信息
        agent_info = self.AGENTS.get(agent_name, {
            "emoji": "❓", 
            "skill": "unknown", 
            "output_type": "未知"
        })
        
        print(f"\n{'='*70}")
        print(f"🔍 Agent产出物审核包装器")
        print(f"{'='*70}")
        print(f"Agent：{agent_info['emoji']} {agent_name}")
        print(f"技能：{agent_info['skill']}")
        print(f"产出类型：{agent_info['output_type']}")
        print(f"产出物：{output_path}")
        print(f"{'='*70}")
        
        # 检查文件是否存在
        file_path = Path(output_path)
        if not file_path.is_absolute():
            file_path = self.workspace_root / output_path
        
        if not file_path.exists():
            print(f"❌ 文件不存在：{file_path}")
            return {
                "status": "error",
                "message": f"文件不存在：{file_path}",
            }
        
        # 执行审核
        print(f"\n📋 开始审核...")
        result = self.executor.execute(str(file_path), mode=mode)
        
        # 保存审核记录
        self._save_audit_log(agent_name, output_path, result)
        
        # 通知少帅
        if auto_notify:
            self._notify_shaoshuai(agent_name, agent_info, output_path, result)
        
        return result
    
    def _save_audit_log(self, agent_name: str, output_path: str, result: dict):
        """保存审核记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.audit_log_dir / f"audit_{agent_name}_{timestamp}.md"
        
        lines = [
            f"# Agent产出物审核记录",
            f"",
            f"**时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent**：{agent_name}",
            f"**产出物**：{output_path}",
            f"**状态**：{result.get('status', 'unknown')}",
            f"",
            f"---",
            f"",
        ]
        
        if result.get("status") == "passed":
            lines.extend([
                f"## 审核结果：通过 ✅",
                f"",
                f"- **最终等级**：{result.get('final_grade', '?')}级",
                f"- **最终得分**：{result.get('final_score', 0)}分",
                f"- **迭代次数**：{result.get('iterations', 0)}轮",
            ])
        else:
            lines.extend([
                f"## 审核结果：未通过 ⚠️",
                f"",
                f"- **状态**：{result.get('status', 'unknown')}",
            ])
            
            if result.get("message"):
                lines.append(f"- **消息**：{result.get('message')}")
        
        # 写入文件
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"📄 审核记录已保存：{log_file}")
    
    def _notify_shaoshuai(self, agent_name: str, agent_info: dict, 
                          output_path: str, result: dict):
        """通知少帅审核结果
        
        这里生成通知消息，实际发送由调用方（南乔）执行
        """
        emoji = agent_info["emoji"]
        output_type = agent_info["output_type"]
        
        if result.get("status") == "passed":
            # 审核通过
            grade = result.get("final_grade", "?")
            score = result.get("final_score", 0)
            
            message = f"""✅ {emoji} {agent_name}产出物审核通过

📁 文件：{output_path}
📊 类型：{output_type}
🏆 等级：{grade}级
📈 得分：{score}分

审核记录：03_输出成果/审核记录/
"""
            print(f"\n📱 通知消息（QQ）：")
            print(message)
            
        else:
            # 审核未通过
            status = result.get("status", "unknown")
            msg = result.get("message", "")
            
            message = f"""⚠️ {emoji} {agent_name}产出物审核未通过

📁 文件：{output_path}
📊 类型：{output_type}
❌ 状态：{status}
💬 消息：{msg}

请指示后续操作。
"""
            print(f"\n📱 通知消息（QQ）：")
            print(message)
        
        # 如果是重要文档，提示发送邮箱
        importance_score = result.get("importance_score")
        if importance_score and importance_score.total_score >= 80:
            print(f"\n📧 重要文档（得分{importance_score.total_score}），建议发送到邮箱：{self.NOTIFY_CONFIG['email']}")
        
        return message


def audit_after_agent_task(agent_name: str, output_path: str, 
                           task_description: str = "") -> dict:
    """Agent任务后自动审核（便捷函数）
    
    Args:
        agent_name: Agent名称
        output_path: 产出物路径
        task_description: 任务描述（可选）
    
    Returns:
        审核结果
    """
    auditor = AgentOutputAuditor()
    return auditor.audit_agent_output(agent_name, output_path, auto_notify=True)


# 示例用法
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 Agent产出物审核包装器 - 测试")
    print("="*70)
    
    # 模拟Agent产出
    print("\n模拟场景：采薇完成需求文档后，自动审核")
    print("-"*70)
    
    # 模拟调用（使用已存在的测试文件）
    test_file = "知识库/方法论/提示词工程框架.md"
    
    auditor = AgentOutputAuditor()
    result = auditor.audit_agent_output(
        agent_name="采薇",
        output_path=test_file,
        auto_notify=True,
        mode="smart"
    )
    
    print(f"\n{'='*70}")
    print(f"📊 审核结果")
    print(f"{'='*70}")
    print(f"状态：{result.get('status', 'unknown')}")
    
    if result.get("status") == "passed":
        print(f"等级：{result.get('final_grade', '?')}级")
        print(f"得分：{result.get('final_score', 0)}分")
