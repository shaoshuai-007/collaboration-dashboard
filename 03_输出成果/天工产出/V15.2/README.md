# V15.2 QQ任务调度功能 - 后端模块

## 模块概述

任务调度核心模块，提供任务生命周期管理、Agent调度、实时日志等功能。

## 文件结构

```
V15.2/
├── __init__.py          # 模块入口
├── task_store.py        # 内存数据存储
├── task_scheduler.py    # 任务调度引擎
├── task_api.py          # Flask Blueprint API
├── test_task_api.py     # 单元测试
└── README.md            # 本文档
```

## API端点

### 任务管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v15.2/tasks` | 创建任务 |
| GET | `/api/v15.2/tasks` | 任务列表 |
| GET | `/api/v15.2/tasks/<task_id>` | 查询任务 |
| POST | `/api/v15.2/tasks/<task_id>/assign` | 分配Agent |
| POST | `/api/v15.2/tasks/<task_id>/start` | 启动任务 |
| PUT | `/api/v15.2/tasks/<task_id>/progress` | 更新进度 |
| POST | `/api/v15.2/tasks/<task_id>/complete` | 完成任务 |
| POST | `/api/v15.2/tasks/<task_id>/fail` | 标记失败 |
| POST | `/api/v15.2/tasks/<task_id>/cancel` | 取消任务 |
| GET | `/api/v15.2/tasks/<task_id>/output` | 获取产出 |
| GET | `/api/v15.2/tasks/<task_id>/logs` | 获取日志 |
| GET | `/api/v15.2/tasks/<task_id>/logs/stream` | SSE实时日志 |

### Agent管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v15.2/agents` | Agent列表 |
| POST | `/api/v15.2/agents` | 注册Agent |
| GET | `/api/v15.2/agents/<agent_id>` | Agent详情 |
| POST | `/api/v15.2/agents/<agent_id>/heartbeat` | Agent心跳 |
| DELETE | `/api/v15.2/agents/<agent_id>` | 注销Agent |

### 统计

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v15.2/stats` | 统计信息 |

## 使用示例

### 1. 集成到Flask应用

```python
from flask import Flask
from task_api import register_task_api

app = Flask(__name__)
register_task_api(app)

app.run(port=5001)
```

### 2. 创建任务

```bash
curl -X POST http://localhost:5001/api/v15.2/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "测试任务", "description": "描述"}'
```

### 3. SSE日志流

```javascript
const eventSource = new EventSource('/api/v15.2/tasks/task_xxx/logs/stream');

eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data);
    console.log(`[${log.level}] ${log.message}`);
};

eventSource.addEventListener('done', (event) => {
    console.log('任务完成:', event.data);
    eventSource.close();
});
```

## 数据模型

### Task

```python
{
    "task_id": "task_xxx",
    "title": "任务标题",
    "description": "任务描述",
    "status": "pending|assigned|running|completed|failed|cancelled",
    "agent": "agent_id",
    "progress": 0-100,
    "output": {...},
    "created_at": "2026-03-19T11:00:00",
    "updated_at": "2026-03-19T11:00:00",
    "error_message": null,
    "metadata": {...}
}
```

### Agent

```python
{
    "agent_id": "agent_xxx",
    "name": "Agent名称",
    "status": "online|busy|offline|error",
    "current_task": "task_id",
    "capabilities": [...],
    "last_heartbeat": "2026-03-19T11:00:00",
    "metadata": {...}
}
```

## 特性

- ✅ Flask Blueprint 架构
- ✅ 完整类型注解
- ✅ 线程安全存储
- ✅ SSE实时日志流
- ✅ 完整错误处理
- ✅ 自动Agent分配

---

**开发工程师**: 天工（💻）
**版本**: V15.2.0
**日期**: 2026-03-19
