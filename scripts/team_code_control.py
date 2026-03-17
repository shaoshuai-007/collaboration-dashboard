#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队代码管控机制
- 工尺：代码变更监控
- 玉衡：自动提交和推送
- 折桂：变更日志记录

Author: 九星智囊团
Date: 2026-03-17
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

WORKSPACE_PATH = "/root/.openclaw/workspace"
CHANGELOG_PATH = f"{WORKSPACE_PATH}/03_输出成果/变更日志"
CONTROL_LOG = f"{WORKSPACE_PATH}/03_输出成果/代码管控日志.json"


def run_git_command(cmd, cwd=WORKSPACE_PATH, env=None):
    """执行Git命令"""
    try:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            env=full_env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"
    except Exception as e:
        return False, "", str(e)


# ============================================
# 工尺：代码变更监控
# ============================================

def gongchi_monitor_changes():
    """工尺：监控代码变更"""
    print("📐【工尺】开始监控代码变更...")
    
    # 检查Git状态
    success, stdout, stderr = run_git_command(["git", "status", "--porcelain"])
    if not success:
        print(f"  ❌ 监控失败: {stderr}")
        return None
    
    changes = []
    for line in stdout.strip().split("\n"):
        if line.strip():
            status = line[:2].strip()
            file_path = line[3:].strip()
            changes.append({
                "status": status,
                "file": file_path,
                "type": _get_change_type(status)
            })
    
    if changes:
        print(f"  ✅ 检测到 {len(changes)} 个变更")
        for c in changes[:5]:
            print(f"     [{c['type']}] {c['file']}")
        if len(changes) > 5:
            print(f"     ... 还有 {len(changes) - 5} 个变更")
    else:
        print("  ✅ 没有检测到变更")
    
    return changes


def _get_change_type(status):
    """获取变更类型"""
    if status in ["A", "??"]:
        return "新增"
    elif status in ["M", " M", "MM"]:
        return "修改"
    elif status in ["D", " D"]:
        return "删除"
    elif status in ["R", "C"]:
        return "重命名"
    return "未知"


# ============================================
# 玉衡：自动提交和推送
# ============================================

def yuheng_commit_push(changes):
    """玉衡：自动提交和推送"""
    if not changes:
        print("⚖️【玉衡】没有需要提交的变更")
        return True
    
    print("⚖️【玉衡】开始提交和推送...")
    
    # 1. 添加所有变更
    success, _, stderr = run_git_command(["git", "add", "-A"])
    if not success:
        print(f"  ❌ git add 失败: {stderr}")
        return False
    
    # 2. 生成提交消息
    added = len([c for c in changes if c['type'] == "新增"])
    modified = len([c for c in changes if c['type'] == "修改"])
    deleted = len([c for c in changes if c['type'] == "删除"])
    
    parts = []
    if modified > 0:
        parts.append(f"修改{modified}个")
    if added > 0:
        parts.append(f"新增{added}个")
    if deleted > 0:
        parts.append(f"删除{deleted}个")
    
    action = "、".join(parts) if parts else "更新"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"🌿 {action}文件 - {now}"
    
    # 3. 提交
    success, _, stderr = run_git_command(["git", "commit", "-m", message])
    if not success:
        if "nothing to commit" in stderr:
            print("  ✅ 没有需要提交的变更")
            return True
        print(f"  ❌ git commit 失败: {stderr}")
        return False
    
    print(f"  ✅ 提交成功: {message}")
    
    # 4. 推送
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if github_token:
        remote_url = f"https://shaoshuai-007:{github_token}@github.com/shaoshuai-007/collaboration-dashboard.git"
        run_git_command(["git", "remote", "set-url", "origin", remote_url])
    
    success, _, stderr = run_git_command(
        ["git", "push", "origin", "master"],
        env={"GIT_SSL_NO_VERIFY": "1"}
    )
    if not success:
        print(f"  ❌ git push 失败: {stderr}")
        return False
    
    print("  ✅ 推送成功")
    return True


# ============================================
# 折桂：变更日志记录
# ============================================

def zhegui_log_changes(changes, commit_success):
    """折桂：记录变更日志"""
    print("📚【折桂】开始记录变更日志...")
    
    # 创建日志目录
    os.makedirs(CHANGELOG_PATH, exist_ok=True)
    
    # 生成日志条目
    log_entry = {
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "变更数量": len(changes) if changes else 0,
        "提交状态": "成功" if commit_success else "失败",
        "变更详情": changes if changes else []
    }
    
    # 追加到JSON日志
    if os.path.exists(CONTROL_LOG):
        with open(CONTROL_LOG, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(CONTROL_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown日志
    today = datetime.now().strftime("%Y-%m-%d")
    md_path = f"{CHANGELOG_PATH}/{today}.md"
    
    with open(md_path, "a", encoding="utf-8") as f:
        if commit_success and changes:
            f.write(f"\n## {datetime.now().strftime('%H:%M:%S')} 变更记录\n\n")
            for c in changes:
                f.write(f"- [{c['type']}] {c['file']}\n")
            f.write("\n")
    
    print(f"  ✅ 日志已记录到 {CONTROL_LOG}")
    print(f"  ✅ Markdown日志: {md_path}")
    
    return True


# ============================================
# 主流程
# ============================================

def run_control_cycle():
    """执行一个完整的管控周期"""
    print(f"\n{'='*60}")
    print(f"🔄 团队代码管控周期 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 1. 工尺：监控变更
    changes = gongchi_monitor_changes()
    
    # 2. 玉衡：提交推送
    commit_success = yuheng_commit_push(changes)
    
    # 3. 折桂：记录日志
    zhegui_log_changes(changes, commit_success)
    
    print(f"\n{'='*60}")
    print(f"✅ 管控周期完成")
    print(f"{'='*60}\n")
    
    return commit_success


def main():
    import argparse
    parser = argparse.ArgumentParser(description="团队代码管控机制")
    parser.add_argument("--once", action="store_true", help="执行一次后退出")
    parser.add_argument("--interval", type=int, default=60, help="定时执行间隔（分钟）")
    args = parser.parse_args()
    
    if args.once:
        success = run_control_cycle()
        exit(0 if success else 1)
    else:
        import time
        print(f"[INFO] 启动定时管控，间隔: {args.interval} 分钟")
        while True:
            try:
                run_control_cycle()
            except Exception as e:
                print(f"[ERROR] 管控异常: {e}")
            time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
