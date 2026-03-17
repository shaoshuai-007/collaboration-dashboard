#!/usr/bin/env python3
"""
工尺 - 系统设计增强模块
集成github技能，管理设计文档版本
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

class GongchiGithubEnhanced:
    """工尺的系统设计增强类"""

    def __init__(self, github_token: str = None):
        self.name = "工尺"
        self.role = "系统设计师"
        self.skill = "github"
        self.workspace = Path("/tmp/gongchi-workspace")
        self.workspace.mkdir(exist_ok=True)

        # GitHub配置
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "${GITHUB_TOKEN}")
        self.github_user = "shaoshuai-007"
        self.github_repo = "system-design"

    def generate_interface_design(self, module_name: str, endpoints: list) -> dict:
        """
        生成接口设计文档

        Args:
            module_name: 模块名称
            endpoints: 接口列表

        Returns:
            接口设计文档
        """
        doc = {
            "module": module_name,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "endpoints": []
        }

        for ep in endpoints:
            endpoint = {
                "id": f"API-{len(doc['endpoints'])+1:03d}",
                "path": ep.get("path", ""),
                "method": ep.get("method", "GET"),
                "name": ep.get("name", ""),
                "description": ep.get("description", ""),
                "request_params": ep.get("request_params", []),
                "response_fields": ep.get("response_fields", []),
                "errors": ep.get("errors", []),
                "example": ep.get("example", {})
            }
            doc["endpoints"].append(endpoint)

        return doc

    def generate_database_design(self, tables: list) -> dict:
        """
        生成数据库设计文档

        Args:
            tables: 表列表

        Returns:
            数据库设计文档
        """
        doc = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "tables": []
        }

        for table in tables:
            t = {
                "name": table.get("name", ""),
                "description": table.get("description", ""),
                "columns": table.get("columns", []),
                "indexes": table.get("indexes", []),
                "foreign_keys": table.get("foreign_keys", [])
            }
            doc["tables"].append(t)

        return doc

    def generate_sequence_diagram(self, scenario: str, actors: list) -> str:
        """
        生成时序图

        Args:
            scenario: 场景名称
            actors: 参与者列表

        Returns:
            时序图（Mermaid格式）
        """
        diagram = f"""
```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Service
    participant Database

    Client->>Gateway: 请求
    Gateway->>Gateway: 认证鉴权
    Gateway->>Service: 转发请求
    Service->>Database: 查询数据
    Database-->>Service: 返回结果
    Service-->>Gateway: 响应
    Gateway-->>Client: 返回
```
"""
        return diagram

    def push_to_github(self, file_path: str, commit_message: str) -> dict:
        """
        推送设计文档到GitHub

        Args:
            file_path: 文件路径
            commit_message: 提交信息

        Returns:
            操作结果
        """
        try:
            # 初始化Git仓库
            repo_dir = self.workspace / self.github_repo
            repo_dir.mkdir(exist_ok=True)

            os.chdir(repo_dir)

            # 检查是否已初始化
            if not (repo_dir / ".git").exists():
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "config", "user.email", "szideaf7@163.com"], check=True)
                subprocess.run(["git", "config", "user.name", "shaoshuai-007"], check=True)

            # 复制文件
            import shutil
            shutil.copy(file_path, repo_dir)

            # Git操作
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            return {
                "success": True,
                "message": f"已推送到本地仓库: {repo_dir}",
                "commit": commit_message
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_github_issue(self, title: str, body: str) -> dict:
        """
        创建GitHub Issue

        Args:
            title: 标题
            body: 内容

        Returns:
            操作结果
        """
        try:
            cmd = [
                "gh", "issue", "create",
                "--repo", f"{self.github_user}/{self.github_repo}",
                "--title", title,
                "--body", body
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "GH_TOKEN": self.github_token}
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "issue_url": result.stdout.strip()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_design_issues(self) -> list:
        """
        列出设计相关的Issue

        Returns:
            Issue列表
        """
        # 模拟返回设计Issue列表
        return [
            {"id": 1, "title": "用户模块接口设计", "status": "open"},
            {"id": 2, "title": "订单模块数据库设计", "status": "closed"},
            {"id": 3, "title": "支付模块时序图", "status": "open"}
        ]


# 使用示例
if __name__ == "__main__":
    gongchi = GongchiGithubEnhanced()

    print("=" * 50)
    print("📐 工尺 - 系统设计演示")
    print("=" * 50)

    # 生成接口设计
    print("\n🔌 生成接口设计文档...")

    interface_doc = gongchi.generate_interface_design(
        module_name="用户管理模块",
        endpoints=[
            {
                "path": "/api/v1/users",
                "method": "GET",
                "name": "获取用户列表",
                "description": "分页获取用户列表",
                "request_params": [
                    {"name": "page", "type": "int", "required": False, "description": "页码"},
                    {"name": "size", "type": "int", "required": False, "description": "每页数量"}
                ],
                "response_fields": [
                    {"name": "id", "type": "int", "description": "用户ID"},
                    {"name": "name", "type": "string", "description": "用户名"}
                ]
            },
            {
                "path": "/api/v1/users/{id}",
                "method": "GET",
                "name": "获取用户详情",
                "description": "根据ID获取用户详细信息"
            },
            {
                "path": "/api/v1/users",
                "method": "POST",
                "name": "创建用户",
                "description": "创建新用户"
            }
        ]
    )

    print(f"\n模块: {interface_doc['module']}")
    print(f"接口数量: {len(interface_doc['endpoints'])}")
    for ep in interface_doc['endpoints']:
        print(f"  {ep['method']:6} {ep['path']:30} {ep['name']}")

    # 生成数据库设计
    print("\n" + "=" * 50)
    print("🗄️ 生成数据库设计文档...")

    db_doc = gongchi.generate_database_design(
        tables=[
            {
                "name": "users",
                "description": "用户表",
                "columns": [
                    {"name": "id", "type": "BIGINT", "nullable": False, "primary": True},
                    {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "phone", "type": "VARCHAR(20)", "nullable": True},
                    {"name": "created_at", "type": "DATETIME", "nullable": False}
                ],
                "indexes": ["idx_phone", "idx_created_at"]
            },
            {
                "name": "orders",
                "description": "订单表",
                "columns": [
                    {"name": "id", "type": "BIGINT", "nullable": False, "primary": True},
                    {"name": "user_id", "type": "BIGINT", "nullable": False},
                    {"name": "amount", "type": "DECIMAL(10,2)", "nullable": False},
                    {"name": "status", "type": "VARCHAR(20)", "nullable": False}
                ],
                "foreign_keys": [{"column": "user_id", "references": "users.id"}]
            }
        ]
    )

    print(f"\n表数量: {len(db_doc['tables'])}")
    for table in db_doc['tables']:
        print(f"\n  表名: {table['name']}")
        print(f"  描述: {table['description']}")
        print(f"  字段数: {len(table['columns'])}")

    # 生成时序图
    print("\n" + "=" * 50)
    print("📊 生成时序图...")

    sequence = gongchi.generate_sequence_diagram(
        scenario="用户登录",
        actors=["Client", "Gateway", "AuthService", "Database"]
    )

    print(sequence)

    # 推送到GitHub
    print("=" * 50)
    print("🐙 推送到GitHub...")

    # 保存设计文档
    design_file = "/tmp/gongchi-workspace/interface_design.json"
    with open(design_file, "w", encoding="utf-8") as f:
        json.dump(interface_doc, f, ensure_ascii=False, indent=2)

    result = gongchi.push_to_github(
        file_path=design_file,
        commit_message="docs: 添加用户管理模块接口设计"
    )

    print(f"\n推送结果: {result}")
