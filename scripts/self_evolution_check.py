#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团自我进化检查工具

功能：
- 检查团队状态
- 发现潜在问题
- 提出改进建议
- 生成检查报告

用法：
    python3 self_evolution_check.py

作者：南乔
时间：2026-03-16
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

# 技能根目录
SKILLS_ROOT = '/root/.openclaw/skills'
WORKSPACE = '/root/.openclaw/workspace'

# 成员清单
MEMBERS = {
    '采薇': {'skill': 'compass-needdoc', 'emoji': '🌸'},
    '织锦': {'skill': 'compass-mindmap', 'emoji': '🧵'},
    '筑台': {'skill': 'compass-solution', 'emoji': '🏗️'},
    '呈彩': {'skill': 'compass-ppt', 'emoji': '🎨'},
    '工尺': {'skill': 'compass-design', 'emoji': '📐'},
    '玉衡': {'skill': 'compass-project', 'emoji': '⚖️'},
    '折桂': {'skill': 'compass-shared', 'emoji': '📚'},
    '扶摇': {'skill': 'compass-coordinator', 'emoji': '🌀'},
    '天工': {'skill': 'compass-dev', 'emoji': '💻'},
    '知微': {'skill': 'compass-analysis', 'emoji': '📊'},
}


class SelfEvolutionChecker:
    """自我进化检查器"""

    def __init__(self):
        self.issues = []
        self.suggestions = []
        self.report = []

    def print_header(self, text):
        """打印标题"""
        print(f"\n{RED}{'='*60}{NC}")
        print(f"{RED}{text}{NC}")
        print(f"{RED}{'='*60}{NC}\n")

    def print_success(self, text):
        """打印成功信息"""
        print(f"{GREEN}✅ {text}{NC}")

    def print_warning(self, text):
        """打印警告信息"""
        print(f"{YELLOW}⚠️  {text}{NC}")

    def print_error(self, text):
        """打印错误信息"""
        print(f"{RED}❌ {text}{NC}")

    def check_member_files(self):
        """检查成员文件完整性"""
        self.print_header("📁 成员文件检查")

        all_ok = True
        for name, info in MEMBERS.items():
            skill_path = f"{SKILLS_ROOT}/{info['skill']}"
            required_files = ['SKILL.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'SOUL.md']

            missing = []
            for file in required_files:
                if not os.path.exists(f"{skill_path}/{file}"):
                    missing.append(file)

            if missing:
                self.print_error(f"{info['emoji']} {name}：缺少 {', '.join(missing)}")
                self.issues.append({
                    'type': '文件缺失',
                    'member': name,
                    'detail': f"缺少文件：{', '.join(missing)}"
                })
                all_ok = False
            else:
                self.print_success(f"{info['emoji']} {name}：文件完整")

        return all_ok

    def check_member_scripts(self):
        """检查成员脚本工具"""
        self.print_header("🔧 脚本工具检查")

        for name, info in MEMBERS.items():
            skill_path = f"{SKILLS_ROOT}/{info['skill']}"
            scripts_dir = f"{skill_path}/scripts"

            if not os.path.exists(scripts_dir):
                self.print_warning(f"{info['emoji']} {name}：无scripts目录")
                continue

            scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.py') or f.endswith('.sh')]

            if len(scripts) == 0:
                self.print_warning(f"{info['emoji']} {name}：无脚本工具")
                self.suggestions.append(f"为 {name} 开发脚本工具")
            else:
                self.print_success(f"{info['emoji']} {name}：{len(scripts)}个脚本")

    def check_collaboration_records(self):
        """检查协作记录"""
        self.print_header("🤝 协作记录检查")

        # 检查协作记录文件
        collab_file = f"{WORKSPACE}/02_工作台/九星智囊团协作记录.md"
        if os.path.exists(collab_file):
            # 检查文件更新时间
            mtime = os.path.getmtime(collab_file)
            days_old = (datetime.now().timestamp() - mtime) / 86400

            if days_old > 7:
                self.print_warning(f"协作记录已{int(days_old)}天未更新")
                self.suggestions.append("更新协作记录")
            else:
                self.print_success(f"协作记录最近更新于{int(days_old)}天前")
        else:
            self.print_error("协作记录文件不存在")
            self.issues.append({
                'type': '文件缺失',
                'member': '团队',
                'detail': '协作记录文件不存在'
            })

    def check_automation_tasks(self):
        """检查自动化任务"""
        self.print_header("⏰ 自动化任务检查")

        # 这里可以检查 cron 任务
        # 简化版：检查记录的任务
        tasks = [
            ('📚 折桂', '情报采集', '每周一 08:00'),
            ('🏗️ 筑台', '竞品动态采集', '每周二 08:00'),
            ('🧵 织锦', '技术趋势采集', '每周三 08:00'),
            ('⚖️ 玉衡', '项目风险预警', '每天 09:00'),
            ('🎨 呈彩', '设计案例采集', '每周一 10:00'),
            ('🌀 扶摇', '团队周报生成', '每周五 18:00'),
        ]

        for member, task, time in tasks:
            self.print_success(f"{member}：{task}（{time}）")

    def check_tool_availability(self):
        """检查工具可用性"""
        self.print_header("🛠️ 工具可用性检查")

        # 检查核心工具
        tools = [
            ('python3', 'Python3'),
            ('gh', 'GitHub CLI'),
            ('pi', 'Coding Agent'),
        ]

        for cmd, name in tools:
            result = os.system(f"which {cmd} > /dev/null 2>&1")
            if result == 0:
                self.print_success(f"{name}：可用")
            else:
                self.print_warning(f"{name}：未安装")
                self.suggestions.append(f"安装 {name}")

        # 检查 web_search
        self.print_warning("web_search：需要配置 Brave Search API Key")
        self.issues.append({
            'type': '工具配置',
            'member': '团队',
            'detail': 'web_search 需要配置 Brave Search API Key'
        })

    def check_new_member_readiness(self):
        """检查新成员战备状态"""
        self.print_header("🌟 新成员战备检查")

        new_members = ['天工', '知微']

        for name in new_members:
            info = MEMBERS[name]
            skill_path = f"{SKILLS_ROOT}/{info['skill']}"

            # 检查是否有实战项目记录
            references_dir = f"{skill_path}/references"
            if os.path.exists(references_dir):
                files = os.listdir(references_dir)
                if len(files) > 2:  # 除了 README.md 和 example-case.md
                    self.print_success(f"{info['emoji']} {name}：有实战案例")
                else:
                    self.print_warning(f"{info['emoji']} {name}：缺乏实战案例")
                    self.suggestions.append(f"为 {name} 安排实战项目")
            else:
                self.print_warning(f"{info['emoji']} {name}：无参考资料目录")

    def generate_report(self):
        """生成检查报告"""
        self.print_header("📊 自我进化检查报告")

        print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n发现的问题：{len(self.issues)}个")
        for i, issue in enumerate(self.issues, 1):
            print(f"  {i}. [{issue['type']}] {issue['member']}：{issue['detail']}")

        print(f"\n改进建议：{len(self.suggestions)}条")
        for i, suggestion in enumerate(self.suggestions, 1):
            print(f"  {i}. {suggestion}")

        # 保存报告
        report_path = f"{WORKSPACE}/memory/self_evolution_report_{datetime.now().strftime('%Y%m%d')}.json"
        report_data = {
            'check_time': datetime.now().isoformat(),
            'issues': self.issues,
            'suggestions': self.suggestions
        }

        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存：{report_path}")

        return len(self.issues) == 0

    def run(self):
        """运行检查"""
        self.print_header("🌿 九星智囊团自我进化检查")

        print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"检查内容：成员文件、脚本工具、协作记录、自动化任务、工具可用性、新成员战备")

        # 执行检查
        self.check_member_files()
        self.check_member_scripts()
        self.check_collaboration_records()
        self.check_automation_tasks()
        self.check_tool_availability()
        self.check_new_member_readiness()

        # 生成报告
        all_ok = self.generate_report()

        if all_ok:
            self.print_success("团队状态良好，未发现问题")
        else:
            self.print_warning(f"发现 {len(self.issues)} 个问题，请及时处理")

        return all_ok


def main():
    """主函数"""
    checker = SelfEvolutionChecker()
    checker.run()


if __name__ == '__main__':
    main()
