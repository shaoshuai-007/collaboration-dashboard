# 智汇工程 - 情报采集SOP

> **版本**：v1.0
> **创建时间**：2026-03-16
> **创建人**：南乔 🌿

---

## 一、核心工具

### ✅ 可用工具：web_fetch

**无需配置，直接可用！**

| 工具 | 状态 | 说明 |
|------|:----:|------|
| **web_fetch** | ✅ 可用 | 直接获取网页内容，无需API Key |
| web_search | ❌ | 需配置Brave API Key |
| browser | ❌ | 需连接Chrome扩展 |

---

## 二、信息源URL清单

### 中国电信官网

| 栏目 | URL | 更新频率 |
|------|-----|---------|
| **首页新闻** | https://www.chinatelecom.com.cn/ | 每日 |
| **公司新闻** | https://www.chinatelecom.com.cn/ct/news/gdxw/ | 每日 |
| **人工智能** | https://www.chinatelecom.com.cn/ct/news/rgzn/ | 每周 |
| **云计算算力** | https://www.chinatelecom.com.cn/ct/news/yunjisuanjisuanli/ | 每周 |
| **集团成就** | https://www.chinatelecom.com.cn/ct/news/jctj/ | 每周 |

### 行业媒体

| 媒体 | URL | 说明 |
|------|-----|------|
| **C114通信网** | https://www.c114.com.cn/news/16.html | 通信行业新闻 |
| **工信部官网** | https://www.miit.gov.cn/ | 政策法规 |

### 竞品动态

| 竞品 | URL | 说明 |
|------|-----|------|
| **中国移动** | https://www.chinamobileltd.com/ | 移动官网 |
| **中国联通** | https://www.chinaunicom.com/ | 联通官网 |
| **天翼云** | https://www.ctyun.cn/ | 天翼云产品动态 |

---

## 三、采集流程

### Step 1：获取网页内容

```
web_fetch(
  url="https://www.chinatelecom.com.cn/",
  extractMode="markdown"
)
```

### Step 2：提取关键信息

从返回内容中提取：
- 新闻标题
- 发布时间
- 核心内容
- 关键数据

### Step 3：五维评估

| 维度 | 权重 | 评分标准 |
|------|:----:|---------|
| **准确性** | 25% | 信息来源权威性 |
| **价值度** | 25% | 对湖北业务的相关性 |
| **可用性** | 30% | 是否可直接应用 |
| **时效衰减** | 10% | 发布时间新鲜度 |
| **稀缺性** | 10% | 信息独特性 |

### Step 4：分级入库

| 等级 | 分数 | 处理方式 |
|:----:|:----:|---------|
| **S级** | ≥80 | 精华库 + QQ推送 |
| **A级** | 70-79 | 精华库 |
| **B级** | 60-69 | 原始库 |
| **C级** | 50-59 | 原始库 |
| **D级** | <50 | 舍弃 |

### Step 5：写入知识库

**精华库路径**：
```
/root/.openclaw/workspace/01_知识库/00_信息源知识库/精华知识库/S-XXX_标题_日期.md
```

**文件格式**：
```markdown
# S-XXX：情报标题

**采集时间**：YYYY-MM-DD
**发布时间**：YYYY-MM-DD
**信息源**：来源
**情报等级**：S/A/B/C级（分数）
**新鲜度**：✅ X天内

---

## 📋 基本信息
...

## 🔧 核心内容
...

## 💡 湖北推广价值
...

## 📌 行动建议
...

**来源**：URL
```

---

## 四、自动化触发

### Cron任务配置

```bash
openclaw cron add \
  --name "智汇工程-每周情报采集" \
  --cron "0 8 * * 1" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "📚 折桂情报采集任务触发：请使用web_fetch工具采集中国电信官网、C114通信网最新情报，按五维模型评估，S级入精华库并QQ推送。"
```

---

## 五、快速采集模板

### 中国电信官网首页

```
web_fetch(url="https://www.chinatelecom.com.cn/", extractMode="markdown")
```

### C114通信网

```
web_fetch(url="https://www.c114.com.cn/news/16.html", extractMode="markdown")
```

### 具体新闻页面

```
web_fetch(url="https://www.chinatelecom.com.cn/ct/news/gdxw/XXXXXX.html", extractMode="markdown")
```

---

## 六、常见问题

### Q1：web_fetch返回乱码怎么办？

**原因**：网页编码问题
**解决**：尝试不同的extractMode（markdown/text）

### Q2：如何判断情报价值？

**判断标准**：
1. 是否与湖北业务相关？
2. 是否有具体数据/案例？
3. 是否可用于售前支撑？
4. 是否有推广价值？

### Q3：S级情报如何推送？

**方式**：通过message工具推送到QQ
```
message action=send channel=qqbot to="8236C3DA8CF6F5DF6FEE66D42ADAAE97" message="情报摘要"
```

---

## 七、质量检查清单

- [ ] 信息来源是否权威？
- [ ] 发布时间是否在14天内？
- [ ] 是否有具体数据/案例？
- [ ] 是否与湖北业务相关？
- [ ] 是否已写入知识库？
- [ ] S级情报是否已推送？

---

**南乔心法**：

> 情报采集是AI的眼睛，让知识体系持续进化。
> 
> 不依赖外部工具，web_fetch已足够强大。
> 
> 先武装头脑，再用实践出真知。

---

*本SOP将随实践持续迭代更新。*
