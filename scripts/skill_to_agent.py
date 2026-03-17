#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能转智能体一键工具

用法：
    python3 skill_to_agent.py --id tiangong --name 天工 --skill compass-dev --vibe "代码如诗，追求极致" --emoji 💻

参数说明：
    --id      Agent ID（小写英文，如 tiangong）
    --name    Agent名称（中文，如 天工）
    --skill   技能ID（如 compass-dev）
    --vibe    性格描述（可选）
    --emoji   Emoji符号（可选）

示例：
    # 创建天工
    python3 skill_to_agent.py --id tiangong --name 天工 --skill compass-dev --vibe "代码如诗，追求极致" --emoji 💻

    # 创建知微
    python3 skill_to_agent.py --id zhiwei --name 知微 --skill compass-analysis --vibe "数据说话，洞察为先" --emoji 📊

作者：南乔
时间：2026-03-17
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

# OpenClaw根目录
OPENCLAW_ROOT = Path.home() / '.openclaw'

# API配置
API_KEY = 'bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19'
BASE_URL = 'https://qianfan.baidubce.com/v2/coding'


def print_header(text):
    """打印标题"""
    print(f"\n{RED}{'='*60}{NC}")
    print(f"{RED}{text}{NC}")
    print(f"{RED}{'='*60}{NC}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{GREEN}✅ {text}{NC}")


def print_warning(text):
    """打印警告信息"""
    print(f"{YELLOW}⚠️  {text}{NC}")


def print_error(text):
    """打印错误信息"""
    print(f"{RED}❌ {text}{NC}")


def check_skill_exists(skill_id):
    """检查技能是否存在"""
    skill_path = OPENCLAW_ROOT / 'skills' / skill_id
    if not skill_path.exists():
        print_error(f"技能不存在：{skill_id}")
        print_warning(f"请先创建技能目录：{skill_path}")
        return False

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        print_warning(f"技能缺少SKILL.md文件")
        return False

    print_success(f"技能检查通过：{skill_id}")
    return True


def create_agent_config(agent_id, agent_name, skill_id, vibe, emoji):
    """创建Agent配置"""

    print_header(f"🌿 开始创建Agent：{agent_name} ({agent_id})")

    # 步骤1：检查技能
    if not check_skill_exists(skill_id):
        return False

    # 步骤2：创建Agent目录
    print(f"\n{BLUE}步骤2：创建Agent目录{NC}")
    agent_dir = OPENCLAW_ROOT / 'agents' / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    (agent_dir / 'agent').mkdir(exist_ok=True)
    (agent_dir / 'sessions').mkdir(exist_ok=True)

    # 创建models.json
    models_config = {
        "providers": {
            "qianfan-ls": {
                "baseUrl": BASE_URL,
                "apiKey": API_KEY,
                "api": "openai-completions",
                "models": [{
                    "id": "qianfan-code-latest",
                    "name": "qianfan-code-latest",
                    "reasoning": False,
                    "input": ["text"],
                    "cost": {
                        "input": 0,
                        "output": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0
                    },
                    "contextWindow": 98304,
                    "maxTokens": 65536
                }]
            }
        }
    }

    models_file = agent_dir / 'agent' / 'models.json'
    with open(models_file, 'w', encoding='utf-8') as f:
        json.dump(models_config, f, indent=2)

    print_success(f"Agent目录创建完成")
    print(f"   路径：{agent_dir}")

    # 步骤3：创建Workspace
    print(f"\n{BLUE}步骤3：创建Workspace{NC}")
    workspace_dir = OPENCLAW_ROOT / f'workspace-{agent_id}'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / 'memory').mkdir(exist_ok=True)

    # 复制基础文件
    template_dir = OPENCLAW_ROOT / 'workspace-caiwei'
    template_files = ['AGENTS.md', 'HEARTBEAT.md', 'USER.md', 'SOUL.md', 'TOOLS.md']

    for file in template_files:
        src = template_dir / file
        dst = workspace_dir / file
        if src.exists():
            import shutil
            shutil.copy(src, dst)

    # 创建IDENTITY.md
    identity_content = f"""# IDENTITY.md - {agent_name}身份

- **Name:** {agent_name} ({agent_id.capitalize()})
- **Creature:** {skill_id.split('-')[-1] if '-' in skill_id else '智能助手'}
- **Vibe:** {vibe if vibe else '专业、高效、贴心'}
- **Emoji:** {emoji if emoji else '🤖'}

---

{get_poetry(agent_name)}
"""

    with open(workspace_dir / 'IDENTITY.md', 'w', encoding='utf-8') as f:
        f.write(identity_content)

    # 创建技能软链接
    skill_link = workspace_dir / f'skills-{skill_id.split("-")[-1] if "-" in skill_id else skill_id}'
    skill_target = OPENCLAW_ROOT / 'skills' / skill_id

    if skill_link.exists() or skill_link.is_symlink():
        skill_link.unlink()

    skill_link.symlink_to(skill_target)

    print_success(f"Workspace创建完成")
    print(f"   路径：{workspace_dir}")

    # 步骤4：更新openclaw.json
    print(f"\n{BLUE}步骤4：更新openclaw.json{NC}")
    config_file = OPENCLAW_ROOT / 'openclaw.json'

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 检查是否已存在
    existing_ids = [a['id'] for a in config['agents']['list']]
    if agent_id in existing_ids:
        print_warning(f"Agent已存在，跳过添加")
    else:
        # 添加Agent
        config['agents']['list'].append({
            "id": agent_id,
            "name": agent_name,
            "workspace": f"/root/.openclaw/workspace-{agent_id}",
            "subagents": {
                "allowAgents": ["*"]
            }
        })

        # 更新agentToAgent
        if agent_id not in config['tools']['agentToAgent']['allow']:
            config['tools']['agentToAgent']['allow'].append(agent_id)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print_success(f"openclaw.json更新完成")

    # 步骤5：重启Gateway
    print(f"\n{BLUE}步骤5：重启Gateway{NC}")
    print_warning("请手动执行以下命令重启Gateway：")
    print(f"   openclaw gateway restart --force")

    # 步骤6：验证
    print(f"\n{BLUE}步骤6：验证Agent{NC}")
    print_warning("重启Gateway后，执行以下命令验证：")
    print(f"   openclaw agents list | grep {agent_id}")

    print_header(f"🎉 Agent创建完成：{agent_name}")
    print(f"Agent ID: {agent_id}")
    print(f"Agent名称: {agent_name}")
    print(f"关联技能: {skill_id}")
    print(f"Workspace: {workspace_dir}")

    return True


def get_poetry(name):
    """获取角色诗意描述"""
    poetries = {
        '天工': '天工开物，巧夺天工。我是天工，九星智囊团的开发工程师。',
        '知微': '见微知著，洞察先机。我是知微，九星智囊团的数据分析师。',
        '采薇': '采薇采薇，薇亦作止。我是采薇，九星智囊团的需求分析师。',
        '织锦': '织锦织锦，锦上添花。我是织锦，九星智囊团的架构设计师。',
        '筑台': '筑台筑台，高筑登台。我是筑台，九星智囊团的售前工程师。',
        '呈彩': '呈彩呈彩，异彩纷呈。我是呈彩，九星智囊团的方案设计师。',
        '工尺': '工尺工尺，规矩方圆。我是工尺，九星智囊团的系统设计师。',
        '玉衡': '玉衡玉衡，衡平天下。我是玉衡，九星智囊团的项目经理。',
        '折桂': '折桂折桂，蟾宫折桂。我是折桂，九星智囊团的资源管家。',
        '扶摇': '扶摇扶摇，扶摇直上。我是扶摇，九星智囊团的总指挥。',
        '南乔': '南有乔木，不可休思。我是南乔，你的私人小助手。',
    }
    return poetries.get(name, f'{name}，九星智囊团成员。')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='技能转智能体一键工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 创建天工
  python3 skill_to_agent.py --id tiangong --name 天工 --skill compass-dev --vibe "代码如诗，追求极致" --emoji 💻

  # 创建知微
  python3 skill_to_agent.py --id zhiwei --name 知微 --skill compass-analysis --vibe "数据说话，洞察为先" --emoji 📊
        """
    )

    parser.add_argument('--id', required=True, help='Agent ID（小写英文）')
    parser.add_argument('--name', required=True, help='Agent名称（中文）')
    parser.add_argument('--skill', required=True, help='技能ID')
    parser.add_argument('--vibe', default='专业、高效、贴心', help='性格描述')
    parser.add_argument('--emoji', default='🤖', help='Emoji符号')

    args = parser.parse_args()

    # 执行创建
    create_agent_config(args.id, args.name, args.skill, args.vibe, args.emoji)


if __name__ == '__main__':
    main()
