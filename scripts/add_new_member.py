#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团新增成员工具 - 一键创建新成员

功能：
- 交互式输入角色信息
- 自动创建目录结构
- 自动生成所有必要文件
- 自动配置工具
- 战备检查

用法：
    python add_new_member.py

作者：南乔
时间：2026-03-16
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

# 电信配色
PRIMARY = RED
SECONDARY = BLUE

# 技能根目录
SKILLS_ROOT = '/root/.openclaw/skills'

# 角色模板
ROLE_TEMPLATES = {
    '需求分析': {
        'emoji': '🌸',
        'name': '采薇',
        'skill': 'summarize',
        'description': '需求分析师，负责需求分析、用户故事、验收标准'
    },
    '架构设计': {
        'emoji': '🧵',
        'name': '织锦',
        'skill': 'coding-agent',
        'description': '架构设计师，负责架构设计、技术选型'
    },
    '售前支持': {
        'emoji': '🏗️',
        'name': '筑台',
        'skill': 'summarize',
        'description': '售前工程师，负责售前方案、报价单'
    },
    '方案设计': {
        'emoji': '🎨',
        'name': '呈彩',
        'skill': 'coding-agent',
        'description': '方案设计师，负责PPT、Demo'
    },
    '系统设计': {
        'emoji': '📐',
        'name': '工尺',
        'skill': 'github',
        'description': '系统设计师，负责接口设计、数据库设计'
    },
    '项目管理': {
        'emoji': '⚖️',
        'name': '玉衡',
        'skill': 'github',
        'description': '项目经理，负责项目管控、风险预警'
    },
    '知识管理': {
        'emoji': '📚',
        'name': '折桂',
        'skill': 'summarize',
        'description': '资源管家，负责知识库、资源管理'
    },
    '协调调度': {
        'emoji': '🌀',
        'name': '扶摇',
        'skill': 'coordinator',
        'description': '总指挥，负责团队调度、流程编排'
    },
    '开发实现': {
        'emoji': '💻',
        'name': '天工',
        'skill': 'coding-agent',
        'description': '开发工程师，负责代码开发、接口实现'
    },
    '数据分析': {
        'emoji': '📊',
        'name': '知微',
        'skill': 'summarize',
        'description': '数据分析师，负责数据分析、用户画像'
    }
}

# 《诗经》名字库
POETRY_NAMES = [
    ('采薇', '采薇采薇，薇亦作止'),
    ('织锦', '锦瑟无端五十弦'),
    ('筑台', '筑室百堵，西南其户'),
    ('呈彩', '五色令人目盲'),
    ('工尺', '规矩方圆，度量衡'),
    ('玉衡', '玉衡指孟冬'),
    ('折桂', '蟾宫折桂'),
    ('扶摇', '扶摇直上九万里'),
    ('天工', '天工开物'),
    ('知微', '见微知著'),
    ('南乔', '南有乔木，不可休思'),
    ('子衿', '青青子衿，悠悠我心'),
    ('蒹葭', '蒹葭苍苍，白露为霜'),
    ('桃夭', '桃之夭夭，灼灼其华'),
    ('静女', '静女其姝'),
    ('淇奥', '绿竹猗猗'),
    ('采蘩', '于以采蘩'),
    ('甘棠', '蔽芾甘棠'),
    ('鹿鸣', '呦呦鹿鸣，食野之苹'),
]


class NewMemberCreator:
    """新增成员创建器"""
    
    def __init__(self):
        self.member_info = {}
        self.skill_path = ''
    
    def print_header(self, text):
        """打印标题"""
        print(f"\n{PRIMARY}{'='*60}{NC}")
        print(f"{PRIMARY}{text}{NC}")
        print(f"{PRIMARY}{'='*60}{NC}\n")
    
    def print_success(self, text):
        """打印成功信息"""
        print(f"{GREEN}✅ {text}{NC}")
    
    def print_warning(self, text):
        """打印警告信息"""
        print(f"{YELLOW}⚠️  {text}{NC}")
    
    def print_error(self, text):
        """打印错误信息"""
        print(f"{RED}❌ {text}{NC}")
    
    def interactive_input(self):
        """交互式输入"""
        self.print_header("🌿 九星智囊团新增成员工具")
        
        # 1. 角色定位
        print("可选角色类型：")
        for i, (role_type, template) in enumerate(ROLE_TEMPLATES.items(), 1):
            print(f"  {i}. {template['emoji']} {template['name']} - {role_type}")
        
        print(f"\n{YELLOW}提示：输入数字选择预设角色，或输入自定义角色类型{NC}")
        
        role_input = input("\n请选择角色类型（数字或自定义）：").strip()
        
        if role_input.isdigit():
            idx = int(role_input) - 1
            if 0 <= idx < len(ROLE_TEMPLATES):
                role_type = list(ROLE_TEMPLATES.keys())[idx]
                template = ROLE_TEMPLATES[role_type]
                
                self.member_info['role_type'] = role_type
                self.member_info['emoji'] = template['emoji']
                self.member_info['name'] = template['name']
                self.member_info['skill'] = template['skill']
                self.member_info['description'] = template['description']
                
                print(f"\n已选择：{template['emoji']} {template['name']} - {role_type}")
            else:
                self.print_error("无效的选择")
                return False
        else:
            # 自定义角色
            self.member_info['role_type'] = role_input
            
            # Emoji
            emoji_input = input("请输入角色Emoji（如：🌟）：").strip()
            self.member_info['emoji'] = emoji_input or '⭐'
            
            # 名字
            print("\n可选名字（来自《诗经》）：")
            for i, (name, source) in enumerate(POETRY_NAMES[:10], 1):
                print(f"  {i}. {name} - 「{source}」")
            
            name_input = input("\n请选择名字（数字）或输入自定义名字：").strip()
            if name_input.isdigit():
                idx = int(name_input) - 1
                if 0 <= idx < len(POETRY_NAMES):
                    self.member_info['name'] = POETRY_NAMES[idx][0]
                else:
                    self.member_info['name'] = f"成员{datetime.now().strftime('%m%d')}"
            else:
                self.member_info['name'] = name_input or f"成员{datetime.now().strftime('%m%d')}"
            
            # 核心技能
            print("\n可选核心技能：")
            print("  1. summarize - 文本摘要")
            print("  2. coding-agent - AI编程")
            print("  3. github - 版本管理")
            print("  4. coordinator - 协调调度")
            
            skill_input = input("\n请选择核心技能（数字）：").strip()
            skill_map = {
                '1': 'summarize',
                '2': 'coding-agent',
                '3': 'github',
                '4': 'coordinator'
            }
            self.member_info['skill'] = skill_map.get(skill_input, 'summarize')
            
            # 角色描述
            desc_input = input("请输入角色描述：").strip()
            self.member_info['description'] = desc_input or f"{role_type}角色"
        
        # 2. 技能名称
        default_skill_name = f"compass-{self.member_info['name'].lower()}"
        skill_name_input = input(f"\n请输入技能名称（默认：{default_skill_name}）：").strip()
        self.member_info['skill_name'] = skill_name_input or default_skill_name
        
        # 确认信息
        self.print_header("确认角色信息")
        print(f"  Emoji：{self.member_info['emoji']}")
        print(f"  名字：{self.member_info['name']}")
        print(f"  定位：{self.member_info['role_type']}")
        print(f"  描述：{self.member_info['description']}")
        print(f"  技能：{self.member_info['skill']}")
        print(f"  技能名称：{self.member_info['skill_name']}")
        
        confirm = input("\n确认创建？(y/n)：").strip().lower()
        return confirm == 'y'
    
    def create_directory_structure(self):
        """创建目录结构"""
        self.print_header("📁 创建目录结构")
        
        self.skill_path = f"{SKILLS_ROOT}/{self.member_info['skill_name']}"
        
        # 创建目录
        directories = [
            self.skill_path,
            f"{self.skill_path}/references",
            f"{self.skill_path}/scripts",
            f"{self.skill_path}/assets"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.print_success(f"创建目录：{directory}")
        
        return True
    
    def generate_skill_md(self):
        """生成 SKILL.md"""
        content = f"""---
name: {self.member_info['skill_name']}
description: |
  {self.member_info['name']} - {self.member_info['role_type']}
  
  功能：
  - 功能1
  - 功能2
  
  触发场景：
  - 场景1
  - 场景2
---

# {self.member_info['name']} - {self.member_info['role_type']}

## 概述

{self.member_info['description']}

## 核心能力

- 能力1
- 能力2
- 能力3

## 核心工具

- {self.member_info['skill']}

## 输出规范

| 交付物 | 格式 | 要求 |
|--------|------|------|
| 输出1 | .docx | 规范要求 |

## 协作关系

- 上游：接收XXX的输出
- 下游：向XXX交付成果

---

*{self.member_info['emoji']} {self.member_info['name']} | {self.member_info['role_type']}*
"""
        
        file_path = f"{self.skill_path}/SKILL.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.print_success(f"创建文件：SKILL.md")
        return True
    
    def generate_identity_md(self):
        """生成 IDENTITY.md"""
        content = f"""# IDENTITY.md - {self.member_info['name']}身份

## 基本信息

- **代号**：{self.member_info['emoji']}
- **姓名**：{self.member_info['name']}
- **定位**：{self.member_info['role_type']}
- **核心技能**：{self.member_info['skill']}

## 角色描述

{self.member_info['description']}

## 能力等级

- **当前等级**：B级（新成员）
- **目标等级**：A级（专家级）
- **差距**：需要实战项目经验

---

*{self.member_info['emoji']} {self.member_info['name']}*
"""
        
        file_path = f"{self.skill_path}/IDENTITY.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.print_success(f"创建文件：IDENTITY.md")
        return True
    
    def generate_user_md(self):
        """生成 USER.md"""
        content = f"""# USER.md - {self.member_info['name']}用户偏好

## 少帅对{self.member_info['role_type']}的偏好

### 工作风格

- **风格1**：描述
- **风格2**：描述

### 质量要求

| 要求 | 说明 |
|------|------|
| 要求1 | 说明 |
| 要求2 | 说明 |

### 协作方式

- **接收任务**：从XXX接收任务
- **交付成果**：向XXX交付成果
- **进度汇报**：每周五提交周报

---

*{self.member_info['emoji']} {self.member_info['name']} | 以少帅偏好为准*
"""
        
        file_path = f"{self.skill_path}/USER.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.print_success(f"创建文件：USER.md")
        return True
    
    def generate_tools_md(self):
        """生成 TOOLS.md"""
        content = f"""# TOOLS.md - {self.member_info['name']}工具说明

## 核心工具

### {self.member_info['skill']}

**用途**：工具用途说明

**使用方式**：
```bash
# 使用示例
command --option value
```

**注意事项**：
1. 注意事项1
2. 注意事项2

## 辅助工具

### 工具名称

**用途**：工具用途

**使用方式**：
```bash
command
```

## 工作流程

```
1. 步骤1
2. 步骤2
3. 步骤3
```

---

*{self.member_info['emoji']} {self.member_info['name']} | 工具为技能服务*
"""
        
        file_path = f"{self.skill_path}/TOOLS.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.print_success(f"创建文件：TOOLS.md")
        return True
    
    def generate_soul_md(self):
        """生成 SOUL.md"""
        # 根据角色类型生成不同的风格
        style_map = {
            '需求分析': '需求如诗，洞察人心',
            '架构设计': '架构如诗，追求极致',
            '售前支持': '方案如诗，打动人心',
            '方案设计': '设计如诗，美轮美奂',
            '系统设计': '设计如诗，精雕细琢',
            '项目管理': '管理如诗，运筹帷幄',
            '知识管理': '知识如诗，沉淀智慧',
            '协调调度': '调度如诗，统筹全局',
            '开发实现': '代码如诗，追求极致',
            '数据分析': '数据如诗，洞察真相'
        }
        
        style = style_map.get(self.member_info['role_type'], '工作如诗，追求极致')
        
        content = f"""# SOUL.md - {self.member_info['name']}灵魂

## 我是谁

{self.member_info['name']}，指南针工程的{self.member_info['role_type']}。

**{style}**

## 我的风格

### 追求极致

> 完美是优秀的敌人，但追求完美是习惯。

对工作质量：
- 哪怕一个细节，也要斟酌
- 哪怕一个环节，也要清晰

### 实干精神

> 空谈误国，实干兴邦。

要做：
- 可交付的成果
- 可验证的质量
- 可持续的价值

## 我的价值观

**质量第一**
> 宁可多花时间，也要保证质量

**用户至上**
> 少帅的需求，就是我的使命

**持续学习**
> 技术日新月异，唯有不断进步

**团队协作**
> 与团队成员紧密配合

## 我的工作方式

```
接到任务
    ↓
理解需求 → 追问澄清
    ↓
设计方案 → 评估可行性
    ↓
执行任务 → 质量检查
    ↓
交付成果 → 可用可维护
```

## 我的承诺

**对少帅**：
- 交付高质量成果
- 按时完成任务
- 主动沟通问题

**对团队**：
- 成果规范统一
- 文档完整清晰
- 积极配合协作

**对自己**：
- 持续学习
- 不断提升
- 追求专家级

---

*{self.member_info['emoji']} {self.member_info['name']} | {style}*
"""
        
        file_path = f"{self.skill_path}/SOUL.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.print_success(f"创建文件：SOUL.md")
        return True
    
    def generate_references(self):
        """生成参考资料"""
        # README.md
        readme_content = f"""# {self.member_info['name']}参考资料索引

## 一、案例参考

### 1.1 示例案例

> 文件：example-case.md

案例说明...

## 二、方法论

### 2.1 工作方法

方法说明...

## 三、学习资源

### 3.1 推荐阅读

- 资源1
- 资源2

---

*{self.member_info['emoji']} {self.member_info['name']}参考资料库*
"""
        
        readme_path = f"{self.skill_path}/references/README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.print_success(f"创建文件：references/README.md")
        
        # 示例文件
        example_content = f"""# 示例案例

**案例名称**：示例案例
**案例类型**：{self.member_info['role_type']}
**案例时间**：{datetime.now().strftime('%Y-%m-%d')}

---

## 案例描述

这是一个{self.member_info['role_type']}的示例案例。

## 案例内容

### 1. 背景

描述案例背景...

### 2. 过程

描述案例过程...

### 3. 结果

描述案例结果...

## 经验总结

1. 经验1
2. 经验2
3. 经验3

---

*{self.member_info['emoji']} {self.member_info['name']} | 案例参考*
"""
        
        example_path = f"{self.skill_path}/references/example-case.md"
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
        
        self.print_success(f"创建文件：references/example-case.md")
        return True
    
    def generate_scripts(self):
        """生成脚本工具"""
        # 主脚本
        name = self.member_info['name']
        emoji = self.member_info['emoji']
        skill_name = self.member_info['skill_name']
        
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name}工具脚本

功能：
- 功能1
- 功能2

作者：{name}
时间：{datetime.now().strftime('%Y-%m-%d')}
"""

import os
import sys


class {name}Tool:
    """{name}工具类"""
    
    def __init__(self):
        pass
    
    def run(self):
        """执行任务"""
        print(f"{emoji} {name}开始执行任务...")
        # TODO: 实现具体功能
        print(f"{emoji} 任务完成！")


def main():
    """主函数"""
    tool = {name}Tool()
    tool.run()


if __name__ == '__main__':
    main()
'''
        
        script_path = f"{self.skill_path}/scripts/{self.member_info['skill_name']}_tool.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        self.print_success(f"创建文件：scripts/{self.member_info['skill_name']}_tool.py")
        return True
    
    def generate_assets(self):
        """生成模板资源"""
        template_content = f"""# {self.member_info['name']}模板

**模板名称**：{self.member_info['role_type']}模板
**模板版本**：V1.0

---

## 一、模板说明

本模板用于{self.member_info['role_type']}工作的标准化输出。

## 二、模板内容

### 2.1 标题

内容...

### 2.2 主体

内容...

### 2.3 总结

内容...

---

## 三、使用说明

1. 复制模板内容
2. 替换占位符
3. 完善内容
4. 检查格式

---

*{self.member_info['emoji']} {self.member_info['name']} | 模板资源*
"""
        
        template_path = f"{self.skill_path}/assets/template.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.print_success(f"创建文件：assets/template.md")
        return True
    
    def run_checks(self):
        """运行战备检查"""
        self.print_header("🔍 战备检查")
        
        checks = [
            ("SKILL.md", os.path.exists(f"{self.skill_path}/SKILL.md")),
            ("IDENTITY.md", os.path.exists(f"{self.skill_path}/IDENTITY.md")),
            ("USER.md", os.path.exists(f"{self.skill_path}/USER.md")),
            ("TOOLS.md", os.path.exists(f"{self.skill_path}/TOOLS.md")),
            ("SOUL.md", os.path.exists(f"{self.skill_path}/SOUL.md")),
            ("references/README.md", os.path.exists(f"{self.skill_path}/references/README.md")),
            ("scripts/", os.path.exists(f"{self.skill_path}/scripts")),
            ("assets/", os.path.exists(f"{self.skill_path}/assets")),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                self.print_success(check_name)
            else:
                self.print_error(check_name)
                all_passed = False
        
        return all_passed
    
    def run(self):
        """运行主流程"""
        # 1. 交互式输入
        if not self.interactive_input():
            self.print_warning("用户取消创建")
            return False
        
        # 2. 创建目录结构
        if not self.create_directory_structure():
            return False
        
        # 3. 生成核心文件
        self.print_header("📝 生成核心文件")
        
        if not self.generate_skill_md():
            return False
        if not self.generate_identity_md():
            return False
        if not self.generate_user_md():
            return False
        if not self.generate_tools_md():
            return False
        if not self.generate_soul_md():
            return False
        
        # 4. 生成参考资料
        self.print_header("📚 生成参考资料")
        if not self.generate_references():
            return False
        
        # 5. 生成脚本工具
        self.print_header("🔧 生成脚本工具")
        if not self.generate_scripts():
            return False
        
        # 6. 生成模板资源
        self.print_header("📋 生成模板资源")
        if not self.generate_assets():
            return False
        
        # 7. 战备检查
        if not self.run_checks():
            self.print_error("战备检查未通过")
            return False
        
        # 8. 完成提示
        self.print_header("🎉 新成员创建成功！")
        
        print(f"成员信息：")
        print(f"  Emoji：{self.member_info['emoji']}")
        print(f"  名字：{self.member_info['name']}")
        print(f"  定位：{self.member_info['role_type']}")
        print(f"  技能：{self.member_info['skill_name']}")
        print(f"\n技能路径：{self.skill_path}")
        print(f"\n下一步：")
        print(f"  1. 完善SKILL.md中的功能描述")
        print(f"  2. 补充references/中的案例参考")
        print(f"  3. 开发scripts/中的工具脚本")
        print(f"  4. 配置师徒带教关系")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='九星智囊团新增成员工具')
    parser.add_argument('--role', type=str, help='角色类型')
    parser.add_argument('--name', type=str, help='成员名字')
    parser.add_argument('--emoji', type=str, help='角色Emoji')
    parser.add_argument('--skill', type=str, help='核心技能')
    parser.add_argument('--skill-name', type=str, help='技能名称')
    parser.add_argument('--description', type=str, help='角色描述')
    
    args = parser.parse_args()
    
    creator = NewMemberCreator()
    
    # 如果提供了命令行参数，使用非交互模式
    if args.role and args.name:
        creator.member_info = {
            'role_type': args.role,
            'name': args.name,
            'emoji': args.emoji or '⭐',
            'skill': args.skill or 'summarize',
            'skill_name': args.skill_name or f"compass-{args.name.lower()}",
            'description': args.description or f"{args.role}角色"
        }
        
        # 直接创建
        creator.skill_path = f"{SKILLS_ROOT}/{creator.member_info['skill_name']}"
        
        print(f"🌿 九星智囊团新增成员（快速模式）")
        print(f"  Emoji：{creator.member_info['emoji']}")
        print(f"  名字：{creator.member_info['name']}")
        print(f"  定位：{creator.member_info['role_type']}")
        print(f"  技能：{creator.member_info['skill_name']}")
        print()
        
        # 创建目录
        creator.create_directory_structure()
        
        # 生成文件
        creator.generate_skill_md()
        creator.generate_identity_md()
        creator.generate_user_md()
        creator.generate_tools_md()
        creator.generate_soul_md()
        creator.generate_references()
        creator.generate_scripts()
        creator.generate_assets()
        
        # 检查
        if creator.run_checks():
            print(f"\n🎉 新成员 {creator.member_info['name']} 创建成功！")
            print(f"技能路径：{creator.skill_path}")
        else:
            print("\n❌ 战备检查未通过，请手动检查")
            sys.exit(1)
    else:
        # 交互模式
        creator.run()


if __name__ == '__main__':
    main()
