#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码自动同步脚本
- 监控代码变更
- 自动提交到Git
- 自动推送到GitHub

Author: 工尺
Date: 2026-03-17
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 工作区路径
WORKSPACE_PATH = "/root/.openclaw/workspace"

# 需要监控的目录
MONITOR_DIRS = [
    "03_输出成果",  # 成果文件
    "scripts",      # 脚本文件
    "memory",       # 记忆文件
    "知识库",       # 知识库
    "学习计划",     # 学习计划
    "学习日志",     # 学习日志
]

# 排除的文件模式
EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    "*.log",
    ".DS_Store",
    "node_modules",
    ".git",
]


def run_git_command(cmd, cwd=WORKSPACE_PATH, env=None):
    """执行Git命令"""
    try:
        # 合并环境变量
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


def check_changes():
    """检查是否有代码变更"""
    success, stdout, stderr = run_git_command(["git", "status", "--porcelain"])
    if not success:
        print(f"[ERROR] 检查变更失败: {stderr}")
        return False, []
    
    changes = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
    return len(changes) > 0, changes


def get_commit_message(changes):
    """生成提交消息"""
    # 分析变更类型
    added = len([c for c in changes if c.startswith("??") or c.startswith("A ")])
    modified = len([c for c in changes if c.startswith(" M") or c.startswith("M ")])
    deleted = len([c for c in changes if c.startswith(" D") or c.startswith("D ")])
    
    # 构建消息
    parts = []
    if modified > 0:
        parts.append(f"修改{modified}个文件")
    if added > 0:
        parts.append(f"新增{added}个文件")
    if deleted > 0:
        parts.append(f"删除{deleted}个文件")
    
    action = "、".join(parts) if parts else "更新代码"
    
    # 获取当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return f"🌿 {action} - {now}"


def commit_and_push(changes):
    """提交并推送代码"""
    # 1. 添加所有变更
    success, stdout, stderr = run_git_command(["git", "add", "-A"])
    if not success:
        print(f"[ERROR] git add 失败: {stderr}")
        return False
    
    # 2. 生成提交消息
    message = get_commit_message(changes)
    
    # 3. 提交
    success, stdout, stderr = run_git_command(["git", "commit", "-m", message])
    if not success:
        if "nothing to commit" in stderr:
            print("[INFO] 没有需要提交的变更")
            return True
        print(f"[ERROR] git commit 失败: {stderr}")
        return False
    
    print(f"[SUCCESS] 提交成功: {message}")
    
    # 4. 推送（使用环境变量认证，禁用SSL验证）
    # 设置远程URL（使用环境变量中的Token）
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if github_token:
        remote_url = f"https://shaoshuai-007:{github_token}@github.com/shaoshuai-007/collaboration-dashboard.git"
        run_git_command(["git", "remote", "set-url", "origin", remote_url])
    
    # 推送（禁用SSL验证）
    success, stdout, stderr = run_git_command(
        ["git", "push", "origin", "master"],
        env={"GIT_SSL_NO_VERIFY": "1"}
    )
    if not success:
        print(f"[ERROR] git push 失败: {stderr}")
        return False
    
    print(f"[SUCCESS] 推送成功")
    return True


def sync():
    """执行同步"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始同步检查")
    print(f"{'='*50}")
    
    # 1. 检查变更
    has_changes, changes = check_changes()
    
    if not has_changes:
        print("[INFO] 没有检测到代码变更")
        return True
    
    print(f"[INFO] 检测到 {len(changes)} 个变更:")
    for change in changes[:10]:  # 只显示前10个
        print(f"  - {change}")
    if len(changes) > 10:
        print(f"  ... 还有 {len(changes) - 10} 个变更")
    
    # 2. 提交并推送
    return commit_and_push(changes)


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="代码自动同步脚本")
    parser.add_argument("--once", action="store_true", help="执行一次同步后退出")
    parser.add_argument("--interval", type=int, default=60, help="定时同步间隔（分钟）")
    args = parser.parse_args()
    
    if args.once:
        # 执行一次
        success = sync()
        exit(0 if success else 1)
    else:
        # 定时执行
        print(f"[INFO] 启动定时同步，间隔: {args.interval} 分钟")
        while True:
            try:
                sync()
            except Exception as e:
                print(f"[ERROR] 同步异常: {e}")
            
            time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
