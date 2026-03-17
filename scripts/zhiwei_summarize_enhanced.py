#!/usr/bin/env python3
"""
📊 知微 - 数据分析师赋能脚本
核心技能: summarize + 专属知识库
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ZhiweiDataAnalyst:
    """知微 - 数据分析师"""

    def __init__(self):
        self.name = "知微"
        self.code = "📊"
        self.role = "数据分析师"
        self.slogan = "见微知著，洞察先机"
        self.skill = "summarize"
        self.level = "B级"
        self.target_level = "A级"

        # 工作空间
        self.workspace = Path("/root/.openclaw/workspace")
        self.knowledge_dir = self.workspace / "知识库" / "Agent专属"
        self.output_dir = self.workspace / "03_输出成果"

    def create_knowledge_base(self):
        """创建专属知识库"""
        kb_content = """# 📊 知微知识库

## 一、电信业务指标体系

### 1.1 收入指标

| 指标名称 | 定义 | 计算公式 |
|----------|------|----------|
| ARPU | 户均收入 | 总收入/用户数 |
| 收入增长率 | 收入同比变化 | (本期-上期)/上期×100% |
| 收入构成 | 各业务收入占比 | 业务收入/总收入×100% |

### 1.2 用户指标

| 指标名称 | 定义 | 计算公式 |
|----------|------|----------|
| 用户规模 | 总用户数 | COUNT(user_id) |
| 新增用户 | 新入网用户数 | 新增用户数 |
| 离网率 | 用户流失比例 | 离网用户/总用户×100% |
| 活跃率 | 活跃用户占比 | 活跃用户/总用户×100% |

### 1.3 业务指标

| 指标名称 | 定义 | 计算公式 |
|----------|------|----------|
| DOU | 户均流量 | 总流量/用户数 |
| MOU | 户均通话时长 | 总通话时长/用户数 |
| 套餐渗透率 | 套餐用户占比 | 套餐用户/总用户×100% |
| 增值业务渗透率 | 增值业务用户占比 | 增值业务用户/总用户×100% |

---

## 二、分析方法论

### 2.1 用户分群方法

```
RFM模型：
- R (Recency): 最近一次消费时间
- F (Frequency): 消费频率
- M (Monetary): 消费金额

用户价值分层：
- 高价值用户：R↑ F↑ M↑
- 潜力用户：R↓ F↑ M↑
- 流失预警用户：R↓ F↓ M↓
- 低价值用户：R↓ F↓ M↓
```

### 2.2 流失预测方法

```python
# 流失预测特征
features = [
    '最近登录天数',
    '消费金额变化率',
    '投诉次数',
    '套餐变更次数',
    '通话时长变化率',
    '流量使用变化率'
]

# 预测模型
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

### 2.3 用户画像构建

```
用户画像维度：

基础属性：
- 人口统计：年龄、性别、地域
- 消费能力：ARPU、消费频率

行为特征：
- 通信行为：通话、流量、短信
- 业务偏好：套餐类型、增值业务

兴趣标签：
- 应用偏好：视频、游戏、社交
- 内容偏好：娱乐、新闻、教育

生命周期：
- 新用户、成长期、成熟期、衰退期、流失期
```

---

## 三、数据可视化规范

### 3.1 图表选择

| 分析目的 | 推荐图表 | 说明 |
|----------|----------|------|
| 趋势分析 | 折线图 | 时间序列数据 |
| 对比分析 | 柱状图 | 多个类别对比 |
| 占比分析 | 饼图/环形图 | 各部分占比 |
| 分布分析 | 直方图/箱线图 | 数据分布 |
| 相关分析 | 散点图 | 两变量关系 |

### 3.2 配色规范

```
电信主题配色：

主色：电信红 #C93832
辅色：深蓝 #006EBD
中性色：灰色 #595959

图表配色：
- 数据系列：主色 + 辅色 + 渐变色
- 重点标注：主色
- 背景色：白色或浅灰
```

### 3.3 图表规范

```
图表设计要点：

1. 标题清晰
   - 明确表达图表主题
   - 包含时间范围

2. 数据标注
   - 关键数据点标注数值
   - 使用适当的单位

3. 图例说明
   - 图例位置合理
   - 颜色与数据对应

4. 重点突出
   - 重点数据使用主色
   - 次要数据使用中性色
```

---

## 四、分析报告模板

### 4.1 数据分析报告结构

```markdown
# 数据分析报告

## 一、分析背景
- 分析目的
- 数据来源
- 分析时间范围

## 二、数据概览
- 数据量统计
- 数据质量评估
- 关键指标摘要

## 三、分析内容
### 3.1 趋势分析
### 3.2 对比分析
### 3.3 细分分析

## 四、关键发现
1. 发现一
2. 发现二
3. 发现三

## 五、策略建议
1. 建议一
2. 建议二

## 六、附录
- 数据明细
- 计算过程
```

### 4.2 用户画像报告结构

```markdown
# 用户画像报告

## 一、画像概述
- 用户群体定义
- 数据来源

## 二、基础画像
- 人口统计特征
- 消费特征

## 三、行为画像
- 通信行为
- 业务偏好

## 四、价值画像
- RFM分群
- 价值分层

## 五、标签体系
- 标签列表
- 标签规则

## 六、应用建议
- 精准营销建议
- 产品优化建议
```

---

## 五、分析工具

### 5.1 SQL常用查询

```sql
-- 用户ARPU分布
SELECT
    CASE
        WHEN arpu < 50 THEN '0-50'
        WHEN arpu < 100 THEN '50-100'
        WHEN arpu < 200 THEN '100-200'
        ELSE '200+'
    END as arpu_range,
    COUNT(*) as user_count
FROM users
GROUP BY arpu_range
ORDER BY arpu_range;

-- 用户流失预警
SELECT
    user_id,
    last_login_days,
    consumption_change,
    complaint_count
FROM users
WHERE last_login_days > 30
    OR consumption_change < -0.3
    OR complaint_count > 2;

-- 套餐渗透率
SELECT
    package_name,
    COUNT(*) as user_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users) as penetration_rate
FROM users u
JOIN packages p ON u.package_id = p.package_id
GROUP BY package_name;
```

### 5.2 Python分析示例

```python
import pandas as pd
import matplotlib.pyplot as plt

# 数据加载
df = pd.read_sql(sql, engine)

# 数据清洗
df = df.dropna()
df['date'] = pd.to_datetime(df['date'])

# 分组统计
monthly_stats = df.groupby(df['date'].dt.month).agg({
    'revenue': 'sum',
    'users': 'count'
})

# 可视化
plt.figure(figsize=(12, 6))
plt.plot(monthly_stats.index, monthly_stats['revenue'], marker='o')
plt.title('月度收入趋势')
plt.xlabel('月份')
plt.ylabel('收入（万元）')
plt.grid(True)
plt.savefig('revenue_trend.png')
```

---

## 六、质量检查清单

### 6.1 数据质量检查

- [ ] 数据来源可靠
- [ ] 数据完整无缺失
- [ ] 数据准确性验证
- [ ] 异常值处理

### 6.2 分析质量检查

- [ ] 分析方法合理
- [ ] 结论有数据支撑
- [ ] 建议可落地执行
- [ ] 报告逻辑清晰

### 6.3 可视化质量检查

- [ ] 图表选择正确
- [ ] 配色规范统一
- [ ] 标题标注清晰
- [ ] 重点突出明显

---

*📊 知微 | 见微知著，洞察先机*
"""
        kb_path = self.knowledge_dir / "知微知识库.md"
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_path, 'w', encoding='utf-8') as f:
            f.write(kb_content)

        return str(kb_path)

    def generate_analysis_report(self, title: str, findings: list) -> str:
        """生成分析报告"""
        report = f"""# 📊 {title}

**分析师**: 知微
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 一、分析概述

本报告针对{title}进行深入分析。

---

## 二、关键发现

"""
        for i, finding in enumerate(findings, 1):
            report += f"### 发现{i}: {finding}\n\n"

        report += """
---

## 三、策略建议

1. 针对高价值用户，制定差异化服务策略
2. 针对流失预警用户，及时干预挽留
3. 针对潜力用户，提供增值业务推荐

---

*📊 知微*
"""
        return report


# 演示
if __name__ == "__main__":
    zhiwei = ZhiweiDataAnalyst()

    print("=" * 60)
    print(f"📊 {zhiwei.name} - {zhiwei.role}")
    print(f"Slogan: {zhiwei.slogan}")
    print("=" * 60)

    # 创建知识库
    print("\n📚 创建专属知识库...")
    kb_path = zhiwei.create_knowledge_base()
    print(f"✅ 知识库已创建: {kb_path}")

    print("\n✅ 知微赋能完成！")
