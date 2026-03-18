#!/usr/bin/env python3
"""
呈彩多技能增强脚本 V4.0
岗位专属：方案设计师
核心技能：compass-ppt + ppt-generator + infographic-creator
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 工作空间设置
WORKSPACE = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE / "03_输出成果" / "呈彩产出"
KNOWLEDGE_DIR = WORKSPACE / "知识库" / "呈彩"

# 创建目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


class ChengcaiAgent:
    """呈彩 - 方案设计师"""
    
    def __init__(self):
        self.name = "呈彩"
        self.role = "方案设计师"
        self.skills = {
            "core": ["compass-ppt", "ppt-generator"],
            "auxiliary": ["infographic-creator"],
            "output": ["document-pdf"],
            "growth": ["self-improving-agent"]
        }
    
    def execute_task(self, task_type: str, input_data: dict) -> dict:
        """执行方案设计任务"""
        
        result = {
            "agent": self.name,
            "role": self.role,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat(),
            "output_files": []
        }
        
        if task_type == "方案PPT":
            output = self._generate_ppt(input_data)
            result["output_files"].append(output)
        
        elif task_type == "信息图表":
            output = self._create_infographic(input_data)
            result["output_files"].append(output)
        
        return result
    
    def _generate_ppt(self, input_data: dict) -> str:
        """生成方案PPT"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = OUTPUT_DIR / f"方案PPT_{timestamp}.html"
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>方案PPT - 呈彩</title>
    <style>
        body {{ font-family: "Microsoft YaHei"; margin: 40px; }}
        .slide {{ border: 2px solid #C93832; padding: 30px; margin: 20px 0; }}
        .title {{ color: #C93832; font-size: 28px; }}
        .subtitle {{ color: #006EBD; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="slide">
        <h1 class="title">{input_data.get('title', '方案PPT')}</h1>
        <p class="subtitle">设计师: 呈彩（方案设计师）</p>
        <p class="subtitle">时间: {datetime.now().strftime('%Y年%m月%d日')}</p>
    </div>
    
    <div class="slide">
        <h2>目录</h2>
        <ol>
            <li>项目背景</li>
            <li>解决方案</li>
            <li>实施计划</li>
            <li>预期效果</li>
        </ol>
    </div>
    
    <div class="slide">
        <h2>项目背景</h2>
        <p>{input_data.get('background', '项目背景说明...')}</p>
    </div>
    
    <div class="slide">
        <h2>解决方案</h2>
        <p>{input_data.get('solution', '解决方案说明...')}</p>
    </div>
</body>
</html>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_file)
    
    def _create_infographic(self, input_data: dict) -> str:
        """创建信息图表"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = OUTPUT_DIR / f"信息图表_{timestamp}.html"
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>信息图表 - 呈彩</title>
</head>
<body>
    <h1>{input_data.get('title', '信息图表')}</h1>
    <p>设计师: 呈彩</p>
    <p>时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    
    <div style="display: flex; justify-content: space-around; margin: 40px 0;">
        <div style="text-align: center;">
            <div style="font-size: 48px; color: #C93832;">85%</div>
            <div>客户满意度</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 48px; color: #006EBD;">30%</div>
            <div>效率提升</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 48px; color: #595959;">92%</div>
            <div>准确率</div>
        </div>
    </div>
</body>
</html>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_file)


if __name__ == "__main__":
    agent = ChengcaiAgent()
    
    # 测试PPT生成
    result = agent.execute_task("方案PPT", {
        "title": "湖北电信AI智能配案系统方案",
        "background": "提升配案效率和准确率",
        "solution": "基于AI的智能配案系统"
    })
    
    print(f"任务类型: {result['task_type']}")
    print(f"输出文件: {result['output_files']}")
    print("\n✅ 呈彩赋能脚本V4.0测试完成")
    print("核心技能: compass-ppt + ppt-generator + infographic-creator")
    print("岗位专属: 方案设计师")
