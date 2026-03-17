# API接口设计规范完整指南

**来源**: RESTful API最佳实践
**整理人**: 🌿 南乔
**更新时间**: 2026-03-16

---

## 一、URL设计规范

### 1.1 基本原则

- 使用 **名词** 而非动词
- 使用 **复数形式**
- 使用 **小写字母** 和 **连字符**
- 版本号放在URL中

```python
# ✅ 正确
GET    /api/v1/users           # 获取用户列表
GET    /api/v1/users/1001      # 获取单个用户
POST   /api/v1/users           # 创建用户
PUT    /api/v1/users/1001      # 更新用户
DELETE /api/v1/users/1001      # 删除用户

# ❌ 错误
GET    /api/v1/getUsers        # 不要用动词
GET    /api/v1/user            # 不要用单数
GET    /api/v1/Users           # 不要大写
```

### 1.2 资源嵌套

```python
# ✅ 正确：层级不超过3层
GET /api/v1/users/1001/orders                    # 用户的订单列表
GET /api/v1/users/1001/orders/2024001            # 用户的单个订单
GET /api/v1/users/1001/orders/2024001/items      # 订单明细

# ❌ 错误：层级过深
GET /api/v1/users/1001/orders/2024001/items/1/products/...
```

### 1.3 查询参数

```python
# 分页
GET /api/v1/users?page=1&page_size=20

# 排序
GET /api/v1/users?sort=create_time&order=desc

# 过滤
GET /api/v1/users?status=1&gender=1

# 字段选择
GET /api/v1/users?fields=id,name,phone

# 搜索
GET /api/v1/users?keyword=张三
```

---

## 二、HTTP方法规范

### 2.1 方法语义

| 方法 | 语义 | 幂等性 | 安全性 |
|------|------|:------:|:------:|
| GET | 查询资源 | ✅ | ✅ |
| POST | 创建资源 | ❌ | ❌ |
| PUT | 全量更新 | ✅ | ❌ |
| PATCH | 部分更新 | ❌ | ❌ |
| DELETE | 删除资源 | ✅ | ❌ |

### 2.2 使用示例

```python
# GET - 查询
GET /api/v1/users/1001
Response: {
    "code": 200,
    "data": {"id": 1001, "name": "张三"}
}

# POST - 创建
POST /api/v1/users
Request: {"name": "张三", "phone": "13800138000"}
Response: {
    "code": 201,
    "data": {"id": 1002, "name": "张三"}
}

# PUT - 全量更新
PUT /api/v1/users/1001
Request: {"name": "李四", "phone": "13900139000", "gender": 1}
Response: {"code": 200, "data": {"id": 1001, "name": "李四"}}

# PATCH - 部分更新
PATCH /api/v1/users/1001
Request: {"name": "王五"}
Response: {"code": 200, "data": {"id": 1001, "name": "王五"}}

# DELETE - 删除
DELETE /api/v1/users/1001
Response: {"code": 200, "message": "删除成功"}
```

---

## 三、请求响应规范

### 3.1 请求头

```python
# 必要请求头
{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer <token>",
    "X-Request-ID": "uuid-12345"  # 请求追踪ID
}
```

### 3.2 响应格式

```python
# 成功响应
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1001,
        "name": "张三",
        "phone": "13800138000"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}

# 列表响应
{
    "code": 200,
    "message": "success",
    "data": {
        "list": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}

# 错误响应
{
    "code": 400,
    "message": "参数错误",
    "error": {
        "field": "phone",
        "reason": "手机号格式不正确"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 四、HTTP状态码规范

### 4.1 状态码分类

| 范围 | 类别 | 说明 |
|------|------|------|
| 1xx | 信息 | 请求已接收，继续处理 |
| 2xx | 成功 | 请求已成功处理 |
| 3xx | 重定向 | 需要进一步操作 |
| 4xx | 客户端错误 | 请求参数或语法错误 |
| 5xx | 服务端错误 | 服务器处理失败 |

### 4.2 常用状态码

| 状态码 | 说明 | 使用场景 |
|:------:|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功（无返回体） |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未登录 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 业务校验失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |

---

## 五、错误码设计

### 5.1 错误码格式

```
格式：{模块}{业务}{错误类型}

示例：
- 10001: 用户模块-通用-参数错误
- 10002: 用户模块-通用-未登录
- 10101: 用户模块-用户-不存在
- 10102: 用户模块-用户-已存在
- 10201: 用户模块-权限-无权限
```

### 5.2 错误码表

```python
# 用户模块错误码（1xxxx）
USER_ERRORS = {
    10001: {"message": "参数错误", "http_code": 400},
    10002: {"message": "未登录", "http_code": 401},
    10003: {"message": "登录已过期", "http_code": 401},
    10101: {"message": "用户不存在", "http_code": 404},
    10102: {"message": "用户已存在", "http_code": 409},
    10103: {"message": "密码错误", "http_code": 400},
    10201: {"message": "无权限访问", "http_code": 403},
}

# 订单模块错误码（2xxxx）
ORDER_ERRORS = {
    20001: {"message": "订单不存在", "http_code": 404},
    20002: {"message": "订单已取消", "http_code": 400},
    20003: {"message": "订单已支付", "http_code": 400},
    20101: {"message": "库存不足", "http_code": 400},
}
```

### 5.3 错误响应示例

```python
# 参数错误
{
    "code": 10001,
    "message": "参数错误",
    "error": {
        "field": "phone",
        "reason": "手机号格式不正确",
        "expected": "11位数字"
    }
}

# 业务错误
{
    "code": 10101,
    "message": "用户不存在",
    "error": {
        "user_id": 9999
    }
}
```

---

## 六、接口文档规范

### 6.1 文档结构

```markdown
# 接口名称

## 基本信息
- 接口路径: /api/v1/users
- 请求方法: POST
- 接口描述: 创建新用户

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|:----:|------|
| name | string | 是 | 用户名，2-20字符 |
| phone | string | 是 | 手机号，11位数字 |
| email | string | 否 | 邮箱地址 |

## 请求示例

POST /api/v1/users
Content-Type: application/json

{
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com"
}

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | int | 状态码 |
| message | string | 提示信息 |
| data.id | int | 用户ID |
| data.name | string | 用户名 |
| data.phone | string | 手机号 |

## 响应示例

{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1001,
        "name": "张三",
        "phone": "13800138000"
    }
}

## 错误码

| 错误码 | 说明 |
|:------:|------|
| 10001 | 参数错误 |
| 10102 | 用户已存在 |
```

### 6.2 Swagger/OpenAPI示例

```python
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='用户API', description='用户管理接口')

ns = api.namespace('users', description='用户操作')

user_model = api.model('User', {
    'id': fields.Integer(description='用户ID'),
    'name': fields.String(description='用户名'),
    'phone': fields.String(description='手机号')
})

user_create = api.model('UserCreate', {
    'name': fields.String(required=True, description='用户名'),
    'phone': fields.String(required=True, description='手机号')
})

@ns.route('')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    def get(self):
        """获取用户列表"""
        return []

    @ns.doc('create_user')
    @ns.expect(user_create)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """创建用户"""
        return {'id': 1001, 'name': '张三', 'phone': '13800138000'}, 201
```

---

## 七、版本管理

### 7.1 版本策略

```python
# URL版本（推荐）
GET /api/v1/users
GET /api/v2/users

# Header版本
GET /api/users
Header: Accept: application/vnd.myapi.v1+json
```

### 7.2 版本变更规则

- **大版本（v1 → v2）**：不兼容变更
- **小版本（v1.0 → v1.1）**：向后兼容的功能增加
- **修订版（v1.0.0 → v1.0.1）**：Bug修复

---

## 八、安全规范

### 8.1 认证授权

```python
# JWT认证
Header: Authorization: Bearer <jwt_token>

# API Key认证
Header: X-API-Key: <api_key>

# 验证逻辑
@app.before_request
def verify_token():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"code": 10002, "message": "未登录"}), 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        g.user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 10003, "message": "登录已过期"}), 401
```

### 8.2 请求限流

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/v1/users')
@limiter.limit("10 per minute")
def get_users():
    return jsonify({"code": 200, "data": []})
```

---

## 九、检查清单

- [ ] URL使用名词复数
- [ ] HTTP方法语义正确
- [ ] 响应格式统一
- [ ] 状态码使用正确
- [ ] 错误码定义清晰
- [ ] 接口文档完整
- [ ] 版本管理规范
- [ ] 认证授权完整
- [ ] 请求限流配置

---

*整理人: 🌿 南乔*
*参考: RESTful API设计指南、Swagger官方文档*
