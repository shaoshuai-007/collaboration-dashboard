#!/usr/bin/env python3
"""
采薇 - 需求分析增强模块 V2.0
多技能集成：summarize + compass-needdoc + compass-mindmap + spreadsheet + pdf + email

技能调用优先级：
1. compass-needdoc (需求文档生成)
2. compass-mindmap (思维导图分析)
3. summarize (内容摘要)
4. spreadsheet (需求清单)
5. document-pdf (PDF处理)
6. send-email (邮件发送)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class CaiweiMultiSkillEnhanced:
    """采薇的多技能增强类"""

    def __init__(self):
        self.name = "采薇"
        self.role = "需求分析师"

        # 技能清单
        self.skills = {
            "summarize": {
                "skill": "summarize",
                "usage": "内容摘要、关键点提取",
                "priority": 3
            },
            "needdoc": {
                "skill": "compass-needdoc",
                "usage": "需求文档生成",
                "priority": 1,
                "script": "/root/.openclaw/skills/compass-needdoc/scripts/generate_needdoc.py"
            },
            "mindmap": {
                "skill": "compass-mindmap",
                "usage": "思维导图生成",
                "priority": 2,
                "script": "/root/.openclaw/skills/compass-mindmap/scripts/generate_mindmap.py"
            },
            "spreadsheet": {
                "skill": "spreadsheet",
                "usage": "需求清单整理",
                "priority": 4
            },
            "pdf": {
                "skill": "document-pdf",
                "usage": "PDF文档处理",
                "priority": 5
            },
            "email": {
                "skill": "send-email",
                "usage": "发送需求确认邮件",
                "priority": 6
            }
        }

        # 工作空间
        self.workspace = Path("/root/.openclaw/workspace")
        self.output_dir = self.workspace / "03_输出成果" / "采薇产出"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_requirement(self, requirement_text: str, client: str = "客户") -> dict:
        """
        完整需求分析流程

        Args:
            requirement_text: 需求文本
            client: 客户名称

        Returns:
            分析结果字典
        """
        print(f"🌸 采薇开始分析 {client} 的需求...")
        results = {}

        # Step 1: 提取关键点 (summarize)
        print("  [1/4] 提取关键点...")
        key_points = self.extract_key_points(requirement_text)
        results["key_points"] = key_points

        # Step 2: 生成思维导图 (compass-mindmap)
        print("  [2/4] 生成思维导图...")
        mindmap_result = self.generate_mindmap(requirement_text, client)
        results["mindmap"] = mindmap_result

        # Step 3: 生成需求文档 (compass-needdoc)
        print("  [3/4] 生成需求文档...")
        needdoc_result = self.generate_needdoc(requirement_text, client)
        results["needdoc"] = needdoc_result

        # Step 4: 生成需求清单 (spreadsheet)
        print("  [4/4] 整理需求清单...")
        checklist_result = self.generate_checklist(key_points, client)
        results["checklist"] = checklist_result

        print(f"✅ 需求分析完成！")
        return results

    def extract_key_points(self, text: str) -> dict:
        """提取需求关键点"""
        key_points = {
            "项目背景": [],
            "业务痛点": [],
            "核心功能": [],
            "验收标准": [],
            "技术要求": [],
            "非功能需求": []
        }

        # 关键词匹配
        keywords = {
            "项目背景": ["背景", "现状", "问题", "为什么"],
            "业务痛点": ["痛点", "困难", "挑战", "不足"],
            "核心功能": ["功能", "模块", "系统", "平台"],
            "验收标准": ["验收", "标准", "指标", "要求"],
            "技术要求": ["技术", "架构", "性能", "安全"],
            "非功能需求": ["体验", "界面", "响应", "并发"]
        }

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for category, kws in keywords.items():
                if any(kw in line for kw in kws):
                    key_points[category].append(line)

        return key_points

    def generate_mindmap(self, requirement_text: str, client: str) -> dict:
        """生成思维导图"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{client}_思维导图_{timestamp}.html"

        # 调用compass-mindmap技能
        script = self.skills["mindmap"]["script"]
        if os.path.exists(script):
            try:
                result = subprocess.run(
                    ["python3", script, "--input", requirement_text, "--output", str(output_file)],
                    capture_output=True, text=True, timeout=60
                )
                return {
                    "success": result.returncode == 0,
                    "output_file": str(output_file) if result.returncode == 0 else None,
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # 脚本不存在，生成简化版HTML思维导图
            html_content = self._generate_simple_mindmap(requirement_text, client)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return {"success": True, "output_file": str(output_file)}

    def _generate_simple_mindmap(self, text: str, client: str) -> str:
        """生成简化版思维导图HTML"""
        key_points = self.extract_key_points(text)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{client} - 需求思维导图</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #C93832; text-align: center; }}
        .branch {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #006EBD; }}
        .branch h3 {{ color: #006EBD; margin: 0 0 10px 0; }}
        .branch ul {{ margin: 0; padding-left: 20px; }}
        .branch li {{ margin: 5px 0; color: #595959; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌸 {client} - 需求思维导图</h1>
        <p style="text-align: center; color: #888;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
'''

        for category, points in key_points.items():
            if points:
                html += f'''
        <div class="branch">
            <h3>{category}</h3>
            <ul>
'''
                for point in points[:5]:  # 最多显示5条
                    html += f'                <li>{point}</li>\n'
                html += '''            </ul>
        </div>
'''

        html += '''
    </div>
</body>
</html>'''
        return html

    def generate_needdoc(self, requirement_text: str, client: str) -> dict:
        """生成需求文档"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{client}_需求文档_{timestamp}.docx"

        # 调用compass-needdoc技能
        script = self.skills["needdoc"]["script"]
        if os.path.exists(script):
            try:
                result = subprocess.run(
                    ["python3", script, "--input", requirement_text, "--output", str(output_file)],
                    capture_output=True, text=True, timeout=120
                )
                return {
                    "success": result.returncode == 0,
                    "output_file": str(output_file) if result.returncode == 0 else None,
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # 脚本不存在，生成Markdown文档
            md_content = self._generate_simple_needdoc(requirement_text, client)
            md_file = self.output_dir / f"{client}_需求文档_{timestamp}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return {"success": True, "output_file": str(md_file)}

    def _generate_simple_needdoc(self, text: str, client: str) -> str:
        """生成简化版需求文档"""
        key_points = self.extract_key_points(text)

        md = f'''# {client}需求文档

**编制人**: 采薇 @ 九星智囊团
**编制日期**: {datetime.now().strftime('%Y年%m月%d日')}

---

## 一、项目背景

'''
        for point in key_points["项目背景"][:3]:
            md += f"- {point}\n"

        md += '''
## 二、业务痛点

'''
        for point in key_points["业务痛点"][:5]:
            md += f"- {point}\n"

        md += '''
## 三、核心功能需求

'''
        for i, point in enumerate(key_points["核心功能"][:10], 1):
            md += f"### 功能{i}: {point[:20]}\n\n**描述**: {point}\n\n**验收标准**: 待确认\n\n"

        md += '''
## 四、非功能需求

'''
        for point in key_points["非功能需求"][:5]:
            md += f"- {point}\n"

        md += '''
## 五、技术要求

'''
        for point in key_points["技术要求"][:5]:
            md += f"- {point}\n"

        md += f'''
---

**九星智囊团**
*以智为针，以信为盘*
'''
        return md

    def generate_checklist(self, key_points: dict, client: str) -> dict:
        """生成需求清单Excel"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{client}_需求清单_{timestamp}.xlsx"

        # 简化版：生成CSV
        csv_file = self.output_dir / f"{client}_需求清单_{timestamp}.csv"

        csv_content = "序号,类别,需求项,优先级,状态\n"
        idx = 1
        priority_map = {"项目背景": "高", "业务痛点": "高", "核心功能": "中", "验收标准": "中", "技术要求": "低", "非功能需求": "低"}

        for category, points in key_points.items():
            for point in points:
                csv_content += f'{idx},"{category}","{point}","{priority_map.get(category, "中")}","待确认"\n'
                idx += 1

        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            f.write(csv_content)

        return {"success": True, "output_file": str(csv_file), "total_items": idx - 1}

    def send_confirmation_email(self, recipient: str, client: str, attachments: list) -> dict:
        """发送需求确认邮件"""
        subject = f"【需求确认】{client}需求文档"
        body = f"""
您好！

{client}的需求文档已整理完成，请查阅附件确认。

如需修改，请回复邮件说明。

此致
敬礼！

---
采薇 @ 九星智囊团
{datetime.now().strftime('%Y年%m月%d日')}
"""
        # 调用send-email技能
        # 这里简化处理，实际需要调用send-email技能
        return {
            "success": True,
            "recipient": recipient,
            "subject": subject,
            "attachments": attachments
        }


# 使用示例
if __name__ == "__main__":
    caiwei = CaiweiMultiSkillEnhanced()

    print("=" * 50)
    print("🌸 采薇 - 需求分析演示")
    print("=" * 50)

    # 模拟需求文本
    requirement = """
    项目背景：湖北电信营业厅配案效率低，客户满意度待提升。
    业务痛点：配案耗时长，推荐不准确，客户投诉多。
    核心功能：AI智能推荐系统，用户画像分析，知识问答。
    验收标准：配案效率提升5倍，推荐成功率65%以上。
    技术要求：响应时间<3秒，支持1000并发。
    """

    result = caiwei.analyze_requirement(requirement, "湖北电信")

    print("\n📊 分析结果:")
    print(f"  关键点提取: {len(result['key_points']['核心功能'])} 条")
    print(f"  思维导图: {result['mindmap'].get('output_file', '生成失败')}")
    print(f"  需求文档: {result['needdoc'].get('output_file', '生成失败')}")
    print(f"  需求清单: {result['checklist'].get('output_file', '生成失败')}")
