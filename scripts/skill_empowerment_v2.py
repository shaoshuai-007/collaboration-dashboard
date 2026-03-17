#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团技能赋能工具 V2

功能：
- 为所有成员安装增强技能
- 生成赋能报告

作者：南乔
时间：2026-03-17
"""

import os
from pathlib import Path

OPENCLAW_ROOT = Path.home() / '.openclaw'

# 成员技能配置
MEMBER_SKILLS = {
    'tiangong': {
        'name': '天工',
        'emoji': '💻',
        'skills': ['data-analysis', 'document-pdf', 'spreadsheet'],
        'role': '开发工程师'
    },
    'zhiwei': {
        'name': '知微',
        'emoji': '📊',
        'skills': ['data-analysis', 'infographic-creator', 'spreadsheet'],
        'role': '数据分析师'
    },
    'caiwei': {
        'name': '采薇',
        'emoji': '🌸',
        'skills': ['document-pdf', 'spreadsheet'],
        'role': '需求分析师'
    },
    'zhijin': {
        'name': '织锦',
        'emoji': '🧵',
        'skills': ['document-pdf', 'infographic-creator'],
        'role': '架构设计师'
    },
    'chengcai': {
        'name': '呈彩',
        'emoji': '🎨',
        'skills': ['ppt-generator', 'infographic-creator'],
        'role': '方案设计师'
    },
    'gongchi': {
        'name': '工尺',
        'emoji': '📐',
        'skills': ['document-pdf', 'spreadsheet'],
        'role': '系统设计师'
    },
    'yuheng': {
        'name': '玉衡',
        'emoji': '⚖️',
        'skills': ['spreadsheet', 'document-pdf'],
        'role': '项目经理'
    }
}

def install_skills(member_id, skill_list):
    """为成员安装技能"""
    workspace = OPENCLAW_ROOT / f'workspace-{member_id}'

    if not workspace.exists():
        print(f"❌ workspace不存在：{workspace}")
        return 0

    installed = 0
    for skill in skill_list:
        skill_link = workspace / f'skills-{skill}'
        skill_target = OPENCLAW_ROOT / 'skills' / skill

        if not skill_target.exists():
            print(f"⚠️  技能不存在：{skill}")
            continue

        # 创建软链接
        if skill_link.exists() or skill_link.is_symlink():
            skill_link.unlink()

        skill_link.symlink_to(skill_target)
        installed += 1

    return installed

def main():
    print("="*60)
    print("🌿 九星智囊团技能赋能工具 V2")
    print("="*60)

    report = []
    total_installed = 0

    for member_id, info in MEMBER_SKILLS.items():
        print(f"\n{info['emoji']} {info['name']}（{info['role']}）")
        print(f"   目标技能：{', '.join(info['skills'])}")

        installed = install_skills(member_id, info['skills'])
        total_installed += installed

        status = "✅" if installed == len(info['skills']) else "⚠️"
        print(f"   {status} 已安装：{installed}/{len(info['skills'])}")

        report.append({
            'member': info['name'],
            'role': info['role'],
            'skills': info['skills'],
            'installed': installed
        })

    print("\n" + "="*60)
    print(f"🎉 赋能完成！共安装 {total_installed} 个技能")
    print("="*60)

if __name__ == '__main__':
    main()
