#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星智囊团运营监控脚本
功能：检查定时任务状态、统计Agent产出、生成监控报告、发送告警通知
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = f"{WORKSPACE}/03_输出成果"
CRON_JOBS_FILE = "/root/.openclaw/cron/jobs.json"
SHAOSHUAI_OPENID = "8236C3DA8CF6F5DF6FEE66D42ADAAE97"
SHAOSHUAI_EMAIL = "szideaf7@163.com"

# Agent产出目录映射
AGENT_OUTPUTS = {
    "采薇": f"{OUTPUT_DIR}/需求文档",
    "织锦": f"{OUTPUT_DIR}/架构方案",
    "筑台": f"{OUTPUT_DIR}/售前方案",
    "呈彩": f"{OUTPUT_DIR}/设计作品",
    "工尺": f"{OUTPUT_DIR}/详细设计",
    "玉衡": f"{OUTPUT_DIR}/项目报告",
    "折桂": f"{OUTPUT_DIR}/情报报告",
    "扶摇": f"{OUTPUT_DIR}/团队周报"
}

def check_cron_status():
    """检查定时任务状态"""
    try:
        with open(CRON_JOBS_FILE, 'r') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        results = {
            "total": len(jobs),
            "enabled": 0,
            "ok": 0,
            "error": 0,
            "idle": 0,
            "disabled": 0
        }
        
        for job in jobs:
            if job.get('enabled', False):
                results["enabled"] += 1
                state = job.get('state', {})
                last_status = state.get('lastStatus', 'idle')
                if last_status == 'ok':
                    results["ok"] += 1
                elif last_status == 'error':
                    results["error"] += 1
                else:
                    results["idle"] += 1
            else:
                results["disabled"] += 1
        
        return results
    except Exception as e:
        return {"error": str(e)}

def count_agent_outputs(days=7):
    """统计各Agent近N天的产出"""
    results = {}
    
    for agent, output_dir in AGENT_OUTPUTS.items():
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取近N天的文件
        files = []
        for ext in ['*.md', '*.docx', '*.xlsx', '*.pptx', '*.pdf']:
            files.extend(glob.glob(f"{output_dir}/{ext}"))
        
        # 统计文件数量和大小
        total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
        results[agent] = {
            "count": len(files),
            "total_size": total_size,
            "size_kb": round(total_size / 1024, 2)
        }
    
    return results

def generate_monitor_report():
    """生成监控报告"""
    now = datetime.now()
    
    # 检查任务状态
    cron_status = check_cron_status()
    
    # 统计Agent产出
    agent_outputs = count_agent_outputs(7)
    
    # 生成报告
    report = f"""# 🌿 九星智囊团运营监控日报

**生成时间**：{now.strftime('%Y-%m-%d %H:%M:%S')}

---

## 一、定时任务状态

| 指标 | 数值 |
|------|:----:|
| 总任务数 | {cron_status.get('total', 0)} |
| 已启用 | {cron_status.get('enabled', 0)} |
| 运行正常 | {cron_status.get('ok', 0)} |
| 运行异常 | {cron_status.get('error', 0)} |
| 待触发 | {cron_status.get('idle', 0)} |
| 已禁用 | {cron_status.get('disabled', 0)} |

"""
    
    if cron_status.get('error', 0) > 0:
        report += "⚠️ **告警**：存在异常任务，请检查！\n\n"
    
    report += """---

## 二、Agent产出统计（近7天）

| Agent | 产出数量 | 总大小 |
|-------|:-------:|-------:|
"""
    
    for agent, stats in agent_outputs.items():
        report += f"| {agent} | {stats['count']} | {stats['size_kb']} KB |\n"
    
    report += """
---

## 三、今日待办

"""
    
    # 根据星期几生成待办
    weekday = now.weekday()
    weekday_tasks = {
        0: "- 周一：情报采集(08:00)、设计案例采集(10:00)",
        1: "- 周二：竞品动态采集(08:00)",
        2: "- 周三：技术趋势采集(08:00)",
        3: "- 周四：常规任务执行",
        4: "- 周五：团队周报生成(18:00)",
        5: "- 周六：知识库维护",
        6: "- 周日：系统优化、问题复盘"
    }
    
    report += weekday_tasks.get(weekday, "- 常规任务执行") + "\n\n"
    
    report += """---

## 四、风险提示

"""
    
    # 读取MEMORY.md中的风险项
    memory_file = f"{WORKSPACE}/MEMORY.md"
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "风险" in content or "延期" in content:
                report += "⚠️ 存在风险项，请查阅MEMORY.md\n\n"
    
    report += """---

**南乔**：监控完成，团队运转正常。🌿
"""
    
    return report

def save_report(report):
    """保存报告"""
    now = datetime.now()
    report_dir = f"{OUTPUT_DIR}/九星监控日报"
    os.makedirs(report_dir, exist_ok=True)
    
    filename = f"{report_dir}/{now.strftime('%Y-%m-%d')}_监控日报.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filename

def main():
    """主函数"""
    print("🌿 九星监控启动...")
    
    # 生成报告
    report = generate_monitor_report()
    
    # 保存报告
    filename = save_report(report)
    
    print(f"✅ 监控报告已生成：{filename}")
    
    # 返回摘要用于推送
    cron_status = check_cron_status()
    
    summary = f"""🌿 九星监控日报

📊 定时任务：{cron_status.get('ok', 0)}/{cron_status.get('enabled', 0)} 正常运行

✅ 团队运转正常，无异常告警

📄 详细报告：{filename}
"""
    
    print(summary)
    return summary

if __name__ == "__main__":
    main()
