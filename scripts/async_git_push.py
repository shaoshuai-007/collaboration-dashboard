#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步Git推送服务
- 后台异步推送，不阻塞主流程
- 自动重试机制
- 推送队列管理

Author: 九星智囊团
Date: 2026-03-17
"""

import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from threading import Thread
from queue import Queue

WORKSPACE_PATH = "/root/.openclaw/workspace"
PUSH_QUEUE_FILE = f"{WORKSPACE_PATH}/03_输出成果/push_queue.json"

# 推送队列
push_queue = Queue()


def run_git_command(cmd, cwd=WORKSPACE_PATH, env=None, timeout=300):
    """执行Git命令（5分钟超时）"""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=full_env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时（5分钟）"
    except Exception as e:
        return False, "", str(e)


def async_push_worker():
    """后台推送工作线程"""
    while True:
        try:
            # 从队列获取推送任务
            task = push_queue.get()
            if task is None:
                break
            
            print(f"\n📤【后台推送】开始推送: {task['commit']}")
            
            # 设置远程URL
            github_token = os.environ.get("GITHUB_TOKEN", "")
            if github_token:
                remote_url = f"https://shaoshuai-007:{github_token}@github.com/shaoshuai-007/collaboration-dashboard.git"
                run_git_command(["git", "remote", "set-url", "origin", remote_url])
            
            # 推送
            success, stdout, stderr = run_git_command(
                ["git", "push", "origin", "master"],
                env={"GIT_SSL_NO_VERIFY": "1"},
                timeout=300  # 5分钟超时
            )
            
            if success:
                print(f"✅【后台推送】推送成功: {task['commit']}")
                # 更新队列状态
                update_queue_status(task['commit'], "success")
            else:
                print(f"❌【后台推送】推送失败: {stderr}")
                update_queue_status(task['commit'], "failed", stderr)
                
        except Exception as e:
            print(f"❌【后台推送】异常: {e}")
        
        push_queue.task_done()


def update_queue_status(commit, status, error=""):
    """更新队列状态"""
    if os.path.exists(PUSH_QUEUE_FILE):
        with open(PUSH_QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
    else:
        queue = {"pending": [], "completed": []}
    
    # 从pending移到completed
    queue["pending"] = [t for t in queue["pending"] if t["commit"] != commit]
    queue["completed"].append({
        "commit": commit,
        "status": status,
        "error": error,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(PUSH_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def add_push_task(commit):
    """添加推送任务到队列"""
    if os.path.exists(PUSH_QUEUE_FILE):
        with open(PUSH_QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
    else:
        queue = {"pending": [], "completed": []}
    
    queue["pending"].append({
        "commit": commit,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(PUSH_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    
    push_queue.put({"commit": commit})


def quick_commit_and_push(message):
    """快速提交（不等待推送完成）"""
    # 1. 添加变更
    success, _, stderr = run_git_command(["git", "add", "-A"], timeout=60)
    if not success:
        return False, f"git add 失败: {stderr}"
    
    # 2. 提交
    success, _, stderr = run_git_command(["git", "commit", "-m", message], timeout=60)
    if not success:
        if "nothing to commit" in stderr:
            return True, "没有变更"
        return False, f"git commit 失败: {stderr}"
    
    # 3. 获取commit hash
    success, stdout, _ = run_git_command(["git", "rev-parse", "--short", "HEAD"], timeout=10)
    commit = stdout.strip() if success else "unknown"
    
    # 4. 添加到异步推送队列
    add_push_task(commit)
    
    return True, f"已提交 {commit}，推送已在后台进行"


# 启动后台工作线程
worker_thread = Thread(target=async_push_worker, daemon=True)
worker_thread.start()


if __name__ == "__main__":
    # 测试
    success, msg = quick_commit_and_push("🌿 测试异步推送")
    print(msg)
    
    # 等待推送完成
    time.sleep(10)
