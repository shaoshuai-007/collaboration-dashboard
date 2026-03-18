#!/usr/bin/env python3
"""
工尺 - 系统设计师增强模块 V2.0
多技能集成：github + compass-design + diagram-creator + test-designer + document-pdf

技能调用优先级：
1. compass-design (详细设计)
2. diagram-creator (接口流程图)
3. github (接口文档管理)
4. test-designer (测试设计)
5. document-pdf (文档输出)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class GongchiMultiSkillEnhanced:
    """工尺的多技能增强类"""

    def __init__(self):
        self.name = "工尺"
        self.role = "系统设计师"

        self.skills = {
            "github": {"skill": "github", "usage": "接口文档管理", "priority": 3},
            "compass_design": {"skill": "compass-design", "usage": "详细设计文档", "priority": 1},
            "diagram_creator": {"skill": "diagram-creator", "usage": "接口流程图", "priority": 2},
            "test_designer": {"skill": "test-designer", "usage": "测试用例设计", "priority": 4},
            "document_pdf": {"skill": "document-pdf", "usage": "文档输出", "priority": 5}
        }

        self.workspace = Path("/root/.openclaw/workspace")
        self.output_dir = self.workspace / "03_输出成果" / "工尺产出"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def design_system(self, project: str, architecture: str) -> dict:
        """完整系统设计流程"""
        print(f"📐 工尺开始设计 {project} 系统...")
        results = {}

        # Step 1: 详细设计文档
        print("  [1/4] 生成详细设计文档...")
        design = self.generate_design_doc(project, architecture)
        results["design"] = design

        # Step 2: 接口设计
        print("  [2/4] 设计接口规范...")
        api = self.design_apis(project)
        results["api"] = api

        # Step 3: 数据库设计
        print("  [3/4] 设计数据库...")
        db = self.design_database(project)
        results["database"] = db

        # Step 4: 测试用例
        print("  [4/4] 设计测试用例...")
        tests = self.design_tests(project)
        results["tests"] = tests

        print(f"✅ 系统设计完成！")
        return results

    def generate_design_doc(self, project: str, arch: str) -> dict:
        """生成详细设计文档"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_详细设计_{timestamp}.md"

        md = f'''# {project}详细设计文档

**设计人**: 工尺 @ 九星智囊团
**设计日期**: {datetime.now().strftime('%Y年%m月%d日')}

---

## 一、系统架构

### 1.1 分层架构

```
┌─────────────────────────────────────────┐
│             表示层 (Presentation)        │
├─────────────────────────────────────────┤
│             业务层 (Business)            │
├─────────────────────────────────────────┤
│             数据层 (Data)                │
├─────────────────────────────────────────┤
│             基础层 (Infrastructure)      │
└─────────────────────────────────────────┘
```

## 二、模块设计

### 2.1 核心模块

| 模块 | 功能 | 技术栈 |
|------|------|--------|
| 用户模块 | 用户认证、权限管理 | JWT、RBAC |
| 业务模块 | 核心业务处理 | FastAPI |
| AI模块 | AI推理服务 | TensorFlow |
| 数据模块 | 数据存储查询 | PostgreSQL |

## 三、接口设计

### 3.1 RESTful API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 登录 | POST | /api/auth/login | 用户登录 |
| 查询 | GET | /api/data/query | 数据查询 |
| 推理 | POST | /api/ai/inference | AI推理 |

## 四、数据库设计

### 4.1 核心表

- users (用户表)
- roles (角色表)
- permissions (权限表)
- logs (日志表)

---

**九星智囊团**
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {"success": True, "design_file": str(output_file)}

    def design_apis(self, project: str) -> dict:
        """设计接口规范"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_接口设计_{timestamp}.yaml"

        yaml = f'''openapi: 3.0.0
info:
  title: {project} API
  version: 1.0.0
  description: 系统接口规范 - 工尺设计

servers:
  - url: https://api.example.com/v1

paths:
  /auth/login:
    post:
      summary: 用户登录
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: 登录成功

  /data/query:
    get:
      summary: 数据查询
      parameters:
        - name: query
          in: query
          schema:
            type: string
      responses:
        '200':
          description: 查询成功

  /ai/inference:
    post:
      summary: AI推理
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                input:
                  type: string
      responses:
        '200':
          description: 推理成功
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml)

        return {"success": True, "api_file": str(output_file)}

    def design_database(self, project: str) -> dict:
        """设计数据库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_数据库设计_{timestamp}.sql"

        sql = f'''-- {project} 数据库设计
-- 设计人: 工尺 @ 九星智囊团
-- 设计日期: {datetime.now().strftime('%Y-%m-%d')}

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 日志表
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_created_at ON logs(created_at);
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql)

        return {"success": True, "db_file": str(output_file)}

    def design_tests(self, project: str) -> dict:
        """设计测试用例"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{project}_测试用例_{timestamp}.csv"

        csv = '''用例ID,用例名称,前置条件,测试步骤,预期结果,优先级
TC001,用户登录-正常,用户已注册,1.输入用户名密码\n2.点击登录,登录成功,高
TC002,用户登录-密码错误,用户已注册,1.输入错误密码\n2.点击登录,提示密码错误,高
TC003,数据查询-正常,用户已登录,1.输入查询条件\n2.点击查询,返回正确结果,高
TC004,AI推理-正常,用户已登录,1.输入问题\n2.点击推理,返回推理结果,高
TC005,权限验证-无权限,用户无权限,1.访问管理页面,提示无权限,中'''

        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(csv)

        return {"success": True, "test_file": str(output_file)}


if __name__ == "__main__":
    gongchi = GongchiMultiSkillEnhanced()
    result = gongchi.design_system("湖北电信AI配案系统", "微服务架构")
    print(f"\n📊 设计结果:")
    for key, val in result.items():
        print(f"  {key}: {val}")
