# 多Agent协作框架设计文档

## 一、架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    多Agent协作框架                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  协作调度器 (Scheduler)                   │   │
│  │  • 发言顺序控制  • 冲突处理  • 任务拆解分配              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  通信总线 (Bus)                          │   │
│  │  • 消息路由  • 一对一  • 一对多  • 多对多               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         ▼                  ▼                  ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Agent 1   │    │   Agent 2   │    │   Agent N   │        │
│  │  (角色规则) │    │  (角色规则) │    │  (角色规则) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件

### 2.1 协作调度器 (CollaborationScheduler)

**职责**：
- 协调Agent发言顺序
- 处理并发冲突
- 复杂任务拆解分配

**核心方法**：
```python
class CollaborationScheduler:
    def request_speak(agent_id: str) -> bool      # 请求发言权
    def release_speak(agent_id: str)              # 释放发言权
    def resolve_conflict(agents: List[str])       # 冲突处理
    def decompose_task(task: str) -> List[Task]   # 任务拆解
    def assign_task(task: Task, agent: Agent)     # 任务分配
```

### 2.2 通信总线 (CommunicationBus)

**职责**：
- 消息路由分发
- 支持多种交互模式

**交互模式**：
| 模式 | 说明 | 示例 |
|------|------|------|
| 一对一 | 指定接收者 | 南乔→采薇 |
| 一对多 | 广播给多个 | 扶摇→采薇、织锦、筑台 |
| 多对多 | 群组讨论 | 全体Agent讨论 |
| 广播 | 全员通知 | 系统通知所有Agent |

**核心方法**：
```python
class CommunicationBus:
    def send(from_agent: str, to_agents: List[str], message: Message)
    def broadcast(from_agent: str, message: Message)
    def subscribe(agent_id: str, topics: List[str])
    def publish(topic: str, message: Message)
```

### 2.3 Agent角色规则 (AgentRole)

**角色属性**：
```python
class AgentRole:
    agent_id: str           # Agent标识
    name: str               # 名称
    role: str               # 角色（如：需求分析专家）
    emoji: str              # 表情符号
    
    # 发言规则
    speak_priority: int     # 发言优先级（1-10，10最高）
    speak_cooldown: int     # 发言冷却时间（秒）
    max_speak_duration: int # 最大发言时长（秒）
    
    # 回复风格
    style: str              # 回复风格（专业/简洁/详细）
    tone: str               # 语气（正式/亲切/严谨）
    
    # 能力标签
    capabilities: List[str] # 能力标签（如：需求分析、架构设计）
    expertise: List[str]    # 专业领域
```

---

## 三、发言优先级设计

### 3.1 优先级规则

| 优先级 | Agent | 说明 |
|:------:|-------|------|
| 10 | 扶摇 | 总指挥，全局协调 |
| 9 | 南乔 | 主控Agent，任务分发 |
| 8 | 玉衡 | 项目经理，进度控制 |
| 7 | 采薇 | 需求分析，前置环节 |
| 6 | 织锦 | 架构设计，核心环节 |
| 6 | 工尺 | 详细设计，技术环节 |
| 5 | 筑台 | 售前工程师，成本评估 |
| 5 | 呈彩 | PPT设计，呈现环节 |
| 4 | 折桂 | 资源管家，知识沉淀 |

### 3.2 优先级计算

```python
def calculate_priority(agent: Agent, context: Context) -> int:
    """计算动态优先级"""
    base_priority = agent.speak_priority
    
    # 上下文加权
    if context.current_stage == agent.expertise:
        base_priority += 2  # 当前环节专家加权
    
    if agent.has_pending_task:
        base_priority += 1  # 有待处理任务加权
    
    return min(base_priority, 10)
```

---

## 四、冲突处理策略

### 4.1 冲突类型

| 冲突类型 | 场景 | 处理策略 |
|---------|------|----------|
| 发言冲突 | 多Agent同时请求发言 | 优先级裁决 |
| 任务冲突 | 多Agent争夺同一任务 | 能力匹配+负载均衡 |
| 观点冲突 | Agent之间意见不合 | 投票/扶摇裁决 |
| 资源冲突 | 竞争共享资源 | 排队机制 |

### 4.2 冲突处理流程

```
冲突检测 → 类型判断 → 策略选择 → 执行处理 → 记录日志

发言冲突：
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Agent A │───▶│ Agent B │───▶│ 冲突！  │
│ 优先级:8│    │ 优先级:7│    │         │
└─────────┘    └─────────┘    └─────────┘
                                   │
                                   ▼
                           ┌─────────────┐
                           │ A优先发言   │
                           │ B进入等待   │
                           └─────────────┘
```

---

## 五、任务拆解与分配

### 5.1 任务拆解策略

```python
def decompose_task(task: str) -> List[Task]:
    """任务拆解"""
    subtasks = []
    
    # 按环节拆解
    if task.contains("需求分析"):
        subtasks.append(Task("需求调研", assignee="采薇"))
        subtasks.append(Task("需求文档", assignee="采薇"))
    
    if task.contains("架构设计"):
        subtasks.append(Task("架构方案", assignee="织锦"))
        subtasks.append(Task("技术选型", assignee="筑台"))
    
    if task.contains("项目管理"):
        subtasks.append(Task("进度规划", assignee="玉衡"))
        subtasks.append(Task("资源协调", assignee="扶摇"))
    
    return subtasks
```

### 5.2 任务分配原则

| 原则 | 说明 |
|------|------|
| 能力匹配 | 任务分配给能力最匹配的Agent |
| 负载均衡 | 避免某个Agent过载 |
| 依赖优先 | 有依赖关系的任务按顺序分配 |
| 并行执行 | 无依赖的任务可并行分配 |

---

## 六、消息格式设计

### 6.1 标准消息格式

```python
class Message:
    id: str                    # 消息ID
    from_agent: str            # 发送者
    to_agents: List[str]       # 接收者列表
    content: str               # 消息内容
    msg_type: MessageType      # 消息类型
    priority: int              # 消息优先级
    timestamp: datetime        # 时间戳
    reply_to: str              # 回复的消息ID
    metadata: dict             # 元数据
    
class MessageType(Enum):
    TASK = "task"              # 任务消息
    QUESTION = "question"      # 提问
    ANSWER = "answer"          # 回答
    FEEDBACK = "feedback"      # 反馈
    BROADCAST = "broadcast"    # 广播
    SYSTEM = "system"          # 系统消息
```

### 6.2 消息示例

```json
{
    "id": "msg_001",
    "from_agent": "nanqiao",
    "to_agents": ["caiwei", "zhijin"],
    "content": "请完成需求分析和架构设计",
    "msg_type": "task",
    "priority": 8,
    "timestamp": "2026-03-13T22:05:00+08:00",
    "reply_to": null,
    "metadata": {
        "project": "湖北电渠AI智能配案系统",
        "stage": "需求分析"
    }
}
```

---

## 七、实现文件清单

| 文件 | 说明 |
|------|------|
| `collaboration_scheduler.py` | 协作调度器 |
| `communication_bus.py` | 通信总线 |
| `agent_role.py` | Agent角色定义 |
| `message.py` | 消息结构 |
| `conflict_resolver.py` | 冲突处理器 |
| `task_decomposer.py` | 任务拆解器 |
| `collaboration_framework.py` | 整体框架集成 |

---

## 八、使用示例

```python
# 初始化框架
framework = CollaborationFramework()

# 注册Agent
framework.register_agent(AgentRole(
    agent_id="caiwei",
    name="采薇",
    role="需求分析专家",
    emoji="🌸",
    speak_priority=7,
    style="专业",
    capabilities=["需求分析", "文档编写"]
))

# 发送消息
framework.send(
    from_agent="nanqiao",
    to_agents=["caiwei"],
    message="请完成需求分析文档"
)

# 广播消息
framework.broadcast(
    from_agent="fuyao",
    message="项目启动，请各位准备"
)

# 任务拆解
tasks = framework.decompose_task("完成湖北电渠AI智能配案系统升级")
framework.assign_tasks(tasks)
```

---

**设计人**：南乔  
**设计时间**：2026-03-13 22:05  
**版本**：V1.0

---

*南有乔木，不可休思。*
