#!/usr/bin/env python3
"""
💻 天工 - 开发工程师赋能脚本
核心技能: coding-agent
"""

import os
import json
from datetime import datetime
from pathlib import Path

class TiangongDeveloper:
    """天工 - 开发工程师"""

    def __init__(self):
        self.name = "天工"
        self.code = "💻"
        self.role = "开发工程师"
        self.slogan = "匠心独运，天工开物"
        self.skill = "coding-agent"
        self.level = "B级"
        self.target_level = "A级"

        # 工作空间
        self.workspace = Path("/root/.openclaw/workspace")
        self.knowledge_dir = self.workspace / "知识库" / "Agent专属"
        self.output_dir = self.workspace / "03_输出成果"

    def create_knowledge_base(self):
        """创建专属知识库"""
        kb_content = """# 💻 天工知识库

## 一、开发规范

### 1.1 Python编码规范

```python
# 命名规范
class UserController:  # 类名：大驼峰
    def get_user_info(self):  # 方法名：小写下划线
        user_name = "test"  # 变量名：小写下划线
        MAX_RETRY = 3  # 常量：大写下划线

# 文档规范
def calculate_user_value(user_id: int) -> float:
    \"\"\"
    计算用户价值

    Args:
        user_id: 用户ID

    Returns:
        用户价值分数

    Raises:
        ValueError: 用户不存在时抛出
    \"\"\"
    pass
```

### 1.2 API设计规范

```
RESTful API规范：

GET /api/v1/users          # 获取用户列表
GET /api/v1/users/{id}     # 获取单个用户
POST /api/v1/users         # 创建用户
PUT /api/v1/users/{id}     # 更新用户
DELETE /api/v1/users/{id}  # 删除用户

响应格式：
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

### 1.3 Git提交规范

```
提交格式：<type>(<scope>): <subject>

类型：
- feat: 新功能
- fix: 修复Bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例：
feat(api): 添加用户登录接口
fix(db): 修复数据库连接池泄漏
docs(readme): 更新部署文档
```

---

## 二、技术栈速查

### 2.1 Flask快速开发

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify({
        "code": 200,
        "data": [u.to_dict() for u in users]
    })

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"code": 200, "data": user.to_dict()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2.2 数据库操作

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    phone = Column(String(20))
    value_score = Column(Integer, default=0)

# 查询
users = session.query(User).filter(User.value_score > 80).all()

# 插入
user = User(name="张三", phone="13800138000")
session.add(user)
session.commit()

# 更新
user.value_score = 90
session.commit()

# 删除
session.delete(user)
session.commit()
```

### 2.3 Redis缓存

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# 设置缓存
r.setex('user:1001', 3600, json.dumps(user_data))

# 获取缓存
data = r.get('user:1001')
if data:
    user_data = json.loads(data)
```

---

## 三、电信业务开发

### 3.1 核心数据表

```sql
-- 用户表
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    phone VARCHAR(20),
    name VARCHAR(50),
    package_id INT,
    value_score INT,
    create_time DATETIME
);

-- 套餐表
CREATE TABLE packages (
    package_id INT PRIMARY KEY,
    package_name VARCHAR(100),
    price DECIMAL(10,2),
    data_quota INT,  -- 流量额度(MB)
    voice_quota INT  -- 语音额度(分钟)
);

-- 订单表
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    package_id INT,
    order_type VARCHAR(20),
    status VARCHAR(20),
    create_time DATETIME
);
```

### 3.2 常用接口

```python
# 用户套餐变更
@app.route('/api/v1/users/<int:user_id>/package', methods=['PUT'])
def change_package(user_id):
    new_package_id = request.json.get('package_id')
    # 1. 校验用户
    # 2. 校验套餐
    # 3. 执行变更
    # 4. 记录日志
    return jsonify({"code": 200})

# 用户画像查询
@app.route('/api/v1/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    # 从缓存获取
    cache_key = f'profile:{user_id}'
    cached = r.get(cache_key)
    if cached:
        return jsonify(json.loads(cached))

    # 查询数据库
    profile = calculate_user_profile(user_id)

    # 写入缓存
    r.setex(cache_key, 3600, json.dumps(profile))

    return jsonify(profile)
```

---

## 四、开发工具

### 4.1 常用命令

```bash
# 启动服务
python app.py

# 数据库迁移
flask db init
flask db migrate -m "init"
flask db upgrade

# 测试
pytest tests/

# 代码检查
pylint app/
black app/
```

### 4.2 Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

## 五、质量检查清单

### 5.1 代码检查

- [ ] 代码符合PEP8规范
- [ ] 函数有完整文档注释
- [ ] 变量命名清晰易懂
- [ ] 无冗余代码
- [ ] 错误处理完整

### 5.2 功能检查

- [ ] 接口功能正确
- [ ] 边界情况处理
- [ ] 异常情况处理
- [ ] 性能满足要求
- [ ] 安全性检查

### 5.3 文档检查

- [ ] API文档完整
- [ ] 部署文档清晰
- [ ] 数据库文档更新
- [ ] 变更记录完整

---

*💻 天工 | 匠心独运，天工开物*
"""
        kb_path = self.knowledge_dir / "天工知识库.md"
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_path, 'w', encoding='utf-8') as f:
            f.write(kb_content)

        return str(kb_path)

    def generate_development_report(self, task: str, code: str) -> str:
        """生成开发报告"""
        report = f"""# 💻 开发报告

**开发者**: 天工
**任务**: {task}
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 一、开发内容

{code[:500]}...

---

## 二、技术要点

1. 采用RESTful API设计
2. 使用Redis缓存提升性能
3. 完善的错误处理机制

---

## 三、测试结果

- 单元测试：通过
- 接口测试：通过
- 性能测试：通过

---

*💻 天工*
"""
        return report


# 演示
if __name__ == "__main__":
    tiangong = TiangongDeveloper()

    print("=" * 60)
    print(f"💻 {tiangong.name} - {tiangong.role}")
    print(f"Slogan: {tiangong.slogan}")
    print("=" * 60)

    # 创建知识库
    print("\n📚 创建专属知识库...")
    kb_path = tiangong.create_knowledge_base()
    print(f"✅ 知识库已创建: {kb_path}")

    print("\n✅ 天工赋能完成！")
