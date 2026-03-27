# Agent运行增强工具

**版本**：V1.0
**创建时间**：2026-03-26
**执行人**：扶摇

---

## 功能说明

1. **超时重试机制**：Agent响应延迟时自动重试
2. **文件校验机制**：跨Agent文件传递时验证完整性

---

## 超时重试配置

```python
# config.py
AGENT_TIMEOUT = 60  # 超时时间（秒）
MAX_RETRIES = 3     # 最大重试次数
RETRY_DELAY = 5     # 重试间隔（秒）
```

---

## 文件校验机制

```python
import hashlib
import json

def generate_file_hash(filepath):
    """生成文件MD5校验码"""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def verify_file_transfer(source, dest):
    """验证文件传输完整性"""
    source_hash = generate_file_hash(source)
    dest_hash = generate_file_hash(dest)
    return source_hash == dest_hash
```

---

## 文件传递记录表

**位置**：`02_管控体系/文件传递记录.csv`

**格式**：
```
日期,发送方,接收方,文件名,MD5校验码,状态
2026-03-26,采薇,织锦,需求文档.md,abc123,成功
```

---

## 告警机制

文件传递失败时，自动告警到南乔：
- 发送QQ消息
- 记录到《文件传递问题记录.md》

---

## 使用方法

```python
from agent_enhanced import run_with_retry, verify_and_transfer

# 带重试的Agent调用
result = run_with_retry(agent_name="采薇", task="生成需求文档")

# 文件传递校验
success = verify_and_transfer(
    source="/path/to/source.md",
    dest="/path/to/dest.md"
)
```

**产出物**：`scripts/agent_enhanced.py`（待开发）

**说明**：代码增强功能待明日开发，当前已建立管理制度
