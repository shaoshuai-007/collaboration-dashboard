#!/usr/bin/env python3
"""
代码自动同步服务
监控工作区变更，自动同步到GitHub
"""

import os
import time
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

# 配置
CONFIG = {
    "watch_dirs": [
        "/root/.openclaw/workspace/03_输出成果",
        "/root/.openclaw/skills"
    ],
    "github_repo": "/tmp/github-push",
    "sync_interval": 300,  # 5分钟检查一次
    "file_extensions": [".py", ".md", ".html", ".js", ".css", ".json"],
    "github_token": "${GITHUB_TOKEN}",
    "github_user": "shaoshuai-007",
    "github_repo_name": "collaboration-dashboard"
}

def get_file_hash(filepath):
    """计算文件MD5"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def scan_files():
    """扫描所有监控文件"""
    files = {}
    for watch_dir in CONFIG["watch_dirs"]:
        path = Path(watch_dir)
        if not path.exists():
            continue
        for ext in CONFIG["file_extensions"]:
            for file in path.rglob(f"*{ext}"):
                file_hash = get_file_hash(file)
                if file_hash:
                    files[str(file)] = file_hash
    return files

def check_changes(previous_files):
    """检查文件变更"""
    current_files = scan_files()
    
    added = set(current_files.keys()) - set(previous_files.keys())
    removed = set(previous_files.keys()) - set(current_files.keys())
    modified = set()
    
    for filepath in set(current_files.keys()) & set(previous_files.keys()):
        if current_files[filepath] != previous_files[filepath]:
            modified.add(filepath)
    
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "current_files": current_files
    }

def sync_to_github(changes):
    """同步变更到GitHub"""
    if not any([changes["added"], changes["removed"], changes["modified"]]):
        return False
    
    # 复制新文件和修改的文件
    for filepath in changes["added"] | changes["modified"]:
        try:
            subprocess.run(["cp", filepath, CONFIG["github_repo"] + "/"], check=True)
        except:
            pass
    
    # 生成提交信息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_parts = []
    if changes["added"]:
        commit_parts.append(f"+{len(changes['added'])} files")
    if changes["modified"]:
        commit_parts.append(f"~{len(changes['modified'])} files")
    if changes["removed"]:
        commit_parts.append(f"-{len(changes['removed'])} files")
    
    commit_msg = f"auto: {', '.join(commit_parts)} ({timestamp})"
    
    # Git操作
    os.chdir(CONFIG["github_repo"])
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    env = os.environ.copy()
    env["GIT_SSL_NO_VERIFY"] = "1"
    subprocess.run(["git", "push", "origin", "main"], env=env, check=True)
    
    print(f"✅ Synced: {commit_msg}")
    return True

def main():
    """主循环"""
    print("🚀 Code Auto-Sync Service Started")
    print(f"   Watching: {CONFIG['watch_dirs']}")
    print(f"   Interval: {CONFIG['sync_interval']}s")
    print(f"   Repo: {CONFIG['github_repo_name']}")
    
    previous_files = scan_files()
    
    while True:
        time.sleep(CONFIG["sync_interval"])
        
        changes = check_changes(previous_files)
        
        if any([changes["added"], changes["removed"], changes["modified"]]):
            print(f"📝 Changes detected:")
            if changes["added"]:
                print(f"   Added: {len(changes['added'])} files")
            if changes["modified"]:
                print(f"   Modified: {len(changes['modified'])} files")
            if changes["removed"]:
                print(f"   Removed: {len(changes['removed'])} files")
            
            sync_to_github(changes)
            previous_files = changes["current_files"]

if __name__ == "__main__":
    main()
