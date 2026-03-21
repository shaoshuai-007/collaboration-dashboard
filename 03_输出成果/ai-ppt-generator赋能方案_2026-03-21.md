# AI-PPT-Generator 技能赋能方案

**创建时间**：2026-03-21 23:38
**创建人**：南乔
**技能名称**：ai-ppt-generator

---

## 📑 技能概述

### 核心功能

| 功能 | 说明 |
|------|------|
| **智能PPT生成** | 使用百度AI自动生成PPT |
| **模板智能选择** | 根据主题内容自动选择合适的模板风格 |
| **多种风格支持** | 企业商务、未来科技、卡通手绘、创意趣味、中国风等 |
| **流式输出** | 实时监控生成进度，等待最终PPT URL |

### 技术要求

| 项目 | 要求 |
|------|------|
| Python | ≥ 3.x |
| API密钥 | BAIDU_API_KEY |
| 生成时间 | 2-5分钟 |
| 超时设置 | 300秒 |

---

## 🎯 赋能对象

### 核心赋能（优先级最高）

| Agent | 岗位 | 赋能理由 | 使用场景 |
|-------|------|----------|----------|
| 🎨 呈彩 | 方案设计师 | 主要负责PPT制作 | 方案PPT、汇报PPT、演示PPT |
| 🏗️ 筑台 | 售前工程师 | 需要做售前PPT | 售前方案PPT、客户汇报PPT |

### 扩展赋能

| Agent | 岗位 | 赋能理由 | 使用场景 |
|-------|------|----------|----------|
| ⚖️ 玉衡 | 项目经理 | 需要做项目汇报PPT | 项目进度汇报、里程碑汇报 |
| 🌸 采薇 | 需求分析师 | 可能需要做需求PPT | 需求分析汇报、用户故事展示 |

---

## 🔧 赋能方式

### 方式1：直接使用技能

```bash
# 智能自动选择模板（推荐）
python3 /root/.openclaw/workspace/skills/ai-ppt-generator/scripts/random_ppt_theme.py --query "人工智能发展趋势报告"

# 查看所有可用模板
python3 /root/.openclaw/workspace/skills/ai-ppt-generator/scripts/ppt_theme_list.py

# 指定模板生成
python3 /root/.openclaw/workspace/skills/ai-ppt-generator/scripts/generate_ppt.py --query "儿童英语课件" --tpl_id 106
```

### 方式2：Agent调用示例

```python
# 呈彩生成方案PPT
import subprocess
import json

def generate_proposal_ppt(topic, style=None):
    """生成方案PPT"""
    script_path = "/root/.openclaw/workspace/skills/ai-ppt-generator/scripts/random_ppt_theme.py"
    
    cmd = ["python3", script_path, "--query", topic]
    if style:
        cmd.extend(["--category", style])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.stdout

# 使用示例
ppt_output = generate_proposal_ppt("湖北电信AI智能配案系统建设方案", "企业商务")
```

---

## 📋 模板风格对照表

| 主题类型 | 推荐风格 | 说明 |
|---------|---------|------|
| 商业方案 | 企业商务 | 专业、稳重、商务感 |
| 技术方案 | 未来科技 | 科技感、现代、创新 |
| 教育培训 | 卡通手绘 | 活泼、有趣、易懂 |
| 创意方案 | 创意趣味 | 新颖、独特、吸引人 |
| 文化主题 | 中国风/文化艺术 | 传统、典雅、文化感 |
| 年度汇报 | 年终总结 | 数据展示、成果总结 |
| 简约风格 | 扁平简约 | 简洁、清晰、现代 |
| 文艺主题 | 文艺清新 | 优雅、清新、文艺感 |

---

## 🔄 与其他PPT技能的关系

| 技能 | 定位 | 适用场景 |
|------|------|----------|
| **ai-ppt-generator** | AI智能生成 | 快速生成、智能选择 |
| compass-ppt | 电信专属 | 电信方案汇报、规范严格 |
| ppt-generator | 通用灵活 | 自定义模板、灵活需求 |

### 使用建议

```
需要PPT
    ↓
是电信方案汇报？ → 是 → compass-ppt
    ↓ 否
需要快速生成？ → 是 → ai-ppt-generator ⭐
    ↓ 否
需要自定义模板？ → 是 → ppt-generator
```

---

## ⚠️ 注意事项

1. **API密钥**：需要配置BAIDU_API_KEY
2. **生成时间**：2-5分钟，需要设置足够超时时间
3. **输出格式**：等待`is_end: true`获取最终PPT URL
4. **模板选择**：推荐使用智能选择（random_ppt_theme.py）

---

## 📊 赋能效果预期

| 指标 | 预期效果 |
|------|----------|
| PPT生成效率 | 提升10倍+ |
| 模板选择时间 | 从10分钟→即时 |
| PPT质量 | 专业、美观、符合主题 |
| 团队协作 | 呈彩、筑台快速响应PPT需求 |

---

## ✅ 下一步行动

1. 测试ai-ppt-generator技能
2. 呈彩、筑台开始使用
3. 收集使用反馈
4. 优化赋能方案

---

*南有乔木，不可休思*
*赋能团队，持续进化*
