#!/usr/bin/env python3
"""
南乔版本管控模块
自动Git提交推送，支持代码版本管理
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class VersionControl:
    """版本管控类"""
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.github_token = "${GITHUB_TOKEN}"
        self.github_user = "shaoshuai-007"
        self.github_repo = "compass-engine"
        
    def run_command(self, cmd, cwd=None):
        """执行命令"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd or self.workspace,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def setup_remote(self):
        """设置远程仓库"""
        # 检查是否已有remote
        success, stdout, _ = self.run_command("git remote -v")
        if stdout and "origin" in stdout:
            print("✅ 远程仓库已配置")
            return True
        
        # 创建远程仓库URL（带token）
        remote_url = f"https://{self.github_token}@github.com/{self.github_user}/{self.github_repo}.git"
        
        # 添加remote
        success, _, stderr = self.run_command(f"git remote add origin {remote_url}")
        if success:
            print("✅ 已添加远程仓库")
            return True
        else:
            print(f"⚠️ 添加远程仓库失败: {stderr}")
            return False
    
    def auto_commit(self, message=None):
        """自动提交"""
        if message is None:
            message = f"🌿 南乔自动提交 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 添加所有文件
        success, _, stderr = self.run_command("git add -A")
        if not success:
            print(f"⚠️ git add 失败: {stderr}")
            return False
        
        # 提交
        success, _, stderr = self.run_command(f'git commit -m "{message}"')
        if not success:
            if "nothing to commit" in stderr:
                print("ℹ️ 没有需要提交的更改")
                return True
            print(f"⚠️ git commit 失败: {stderr}")
            return False
        
        print(f"✅ 提交成功: {message}")
        return True
    
    def auto_push(self):
        """自动推送"""
        # 设置远程仓库
        self.setup_remote()
        
        # 推送
        success, stdout, stderr = self.run_command("git push -u origin master --force")
        if success:
            print("✅ 推送成功！")
            print(f"📍 仓库地址: https://github.com/{self.github_user}/{self.github_repo}")
            return True
        else:
            # 可能需要先pull
            print(f"⚠️ 推送失败，尝试强制推送...")
            success, _, _ = self.run_command("git push -u origin master --force")
            if success:
                print("✅ 强制推送成功！")
                return True
            print(f"❌ 推送失败: {stderr}")
            return False
    
    def full_sync(self, message=None):
        """完整同步：提交+推送"""
        print("=" * 50)
        print("🔄 开始版本同步...")
        print("=" * 50)
        
        # 提交
        if not self.auto_commit(message):
            return False
        
        # 推送
        if not self.auto_push():
            return False
        
        print("=" * 50)
        print("✅ 版本同步完成！")
        print("=" * 50)
        return True


if __name__ == "__main__":
    vc = VersionControl()
    vc.full_sync()
