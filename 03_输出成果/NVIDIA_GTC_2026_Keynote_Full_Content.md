# NVIDIA GTC 2026 黄仁勋主题演讲完整内容

## 视频信息

| 项目 | 内容 |
|------|------|
| **标题** | NVIDIA GTC 2026 Keynote |
| **演讲者** | Jensen Huang (黄仁勋), NVIDIA CEO |
| **日期** | 2026年3月16日 |
| **地点** | 美国加州圣何塞 SAP Center |
| **时长** | 约2小时 |
| **来源** | Tom's Hardware Live Blog, Atlan分析报告 |

---

## 演讲概述

NVIDIA GTC (GPU Technology Conference) 2026 大会于2026年3月16日在圣何塞SAP中心举行，NVIDIA创始人兼CEO黄仁勋发表主题演讲。这是CUDA 20周年纪念，演讲涵盖内容之广创历史之最。

---

## 一、开场：CUDA 20年

### 1.1 CUDA的历史意义

黄仁勋以CUDA 20周年开篇。CUDA是NVIDIA今天地位的核心原因之一。

> "The single hardest thing is to have built up our install base, we're in every cloud and computer company in every single industry."
> 
> "最难的事情是建立我们的安装基数，我们现在遍布每个云和每个行业的每一家计算机公司。"

### 1.2 GeForce是最大的营销活动

> "GeForce is Nvidia's greatest marketing campaign."
> 
> "GeForce是Nvidia最大的营销活动。"

黄仁勋描绘了NVIDIA 25年前创建第一个可编程着色器的历程，这最终导致了CUDA的诞生，并使用GeForce作为推动采用率的载体。

---

## 二、DLSS 5：下一代计算机图形

### 2.1 什么是DLSS 5？

NVIDIA发布了下一代图形技术DLSS 5，结合可控3D图形和结构化数据与生成世界。

> "This concept of fusing structured data with generative AI will repeat itself in one industry after another industry after another industry."
> 
> "这种将结构化数据与生成式AI融合的概念将在一个又一个行业中重复出现。"

### 2.2 结构化数据作为AI基础

黄仁勋展示了一张关键幻灯片，表示这是他"最好的幻灯片"。结构化数据是企业计算的"基础真值"(ground truth)。

---

## 三、Moore定律与加速计算

### 3.1 Moore定律已死

> "Moore's Law has run out of steam, accelerated computing allows us to take giant leaps forward."
> 
> "Moore定律已经力竭，加速计算让我们能够取得巨大飞跃。"

黄仁勋以Google Cloud为例，展示NVIDIA的加速如何在各公司和行业间复制。

### 3.2 垂直整合但水平开放

> "Vertically integrated but horizontally open."
> 
> "垂直整合但水平开放。"

黄仁勋这样描述NVIDIA的定位，表示这是实现加速计算目标的唯一方式。

---

## 四、cuDNN与AI大爆炸

### 4.1 cuDNN的重要性

NVIDIA表示cuDNN（CUDA深度神经网络）是公司有史以来最重要的库之一，它导致了现代AI的"大爆炸"。

### 4.2 cuDNN视频展示

NVIDIA展示了关于其各种CUDA-X库的短视频，包括一个完全模拟的逼真视频。

---

## 五、AI发展时间线

### 5.1 AI的快速演进

黄仁勋展示了过去几年AI的快速发展：

- **2023年**：ChatGPT
- **2024年**：推理模型如o1
- **2025年**：具有大上下文窗口的巨大模型如Claude Code
- **2026年**：推理拐点

### 5.2 第一个"代理模型"

> "It's the first 'agentic model'."
> 
> "这是第一个'代理模型'。"

黄仁勋表示NVIDIA 100%在使用Claude Code和其他模型。

---

## 六、1万亿美元需求预测

### 6.1 需求翻倍

> "Last year, Nvidia said it saw about $500 billion of high confidence demand and purchase orders for Blackwell and Rubin through 2026. I see through 2027 at least $1 trillion."
> 
> "去年，NVIDIA表示到2026年Blackwell和Rubin的高置信度需求和采购订单约为5000亿美元。我看到到2027年至少1万亿美元。"

### 6.2 AI计算需求的百万倍增长

黄仁勋解释这个预测背后的逻辑：

- 单个AI工作负载的计算需求在过去两年增长了约10,000倍（推理模型取代检索系统）
- 使用量同时增长约100倍
- **结论：AI计算总需求在过去两年增长了约100万倍**

---

## 七、Vera Rubin：下一代AI计算平台

### 7.1 Vera Rubin NVL72

Vera Rubin NVL72是"为代理AI时代增压的引擎"。

**关键规格**：
- 3.6 exaflops算力
- 260 TB/s全对全NVLink带宽
- 7种芯片类型封装成5个机架级计算机
- 100%液冷（45°C热水冷却）
- 安装时间从2天缩短到2小时

### 7.2 性能提升

- 相比Hopper H200：约50倍的每瓦token数
- 相比x86和Hopper：从每秒200万token提升到每秒7亿token

### 7.3 Vera CPU设计

Vera CPU专为高单线程性能设计，与机架配合用于代理处理。

---

## 八、Groq 3 LPU：NVIDIA为何收购Groq

### 8.1 Groq 3 LPX芯片

NVIDIA在2025年底收购了Groq团队和技术。Groq 3 LPX芯片专为推理设计：确定性、静态编译、大量片上SRAM。

### 8.2 推理分解架构

通过NVIDIA Dynamo软件层，两个处理器紧密耦合：

- **Prefill** → Vera Rubin
- **Decode** → Groq芯片

**结果**：相比单独使用Blackwell，每兆瓦吞吐量提高35倍。

### 8.3 解决延迟与吞吐量矛盾

> "Low latency and high throughput are 'enemies of each other'."
> 
> "低延迟和高吞吐量是'敌人'。"

NVIDIA用一个芯片处理高吞吐量，另一个处理低延迟，通过分解推理实现。

---

## 九、Feynman路线图（2028年）

### 9.1 Feynman家族

- 新GPU
- LP40 LPU（与Groq团队联合开发）
- Rosa CPU
- BlueField 5
- Kyber-CPO扩展（使用共封装光学）

### 9.2 Vera Rubin Space-1

NVIDIA正在开发轨道数据中心系统Vera Rubin Space-1，热管理通过辐射工作。

---

## 十、OpenClaw与NemoClaw：企业代理OS时刻

### 10.1 什么是OpenClaw？

OpenClaw是Peter Steinberger开发的开源代理AI框架。黄仁勋将其与Linux和HTTP的发布直接比较。

> "OpenClaw has open-sourced essentially the operating system of agentic computers."
> 
> "OpenClaw已经开源了代理计算机的操作系统。"

**OpenClaw原语**：
- 资源管理
- 工具访问
- 文件系统访问
- LLM连接
- 调度
- 子代理生成

### 10.2 企业安全挑战

黄仁勋直言：

> "An agent with full OpenClaw capabilities can access employee records, supply chain data, and financial information, and send it outside the organization."
> 
> "具有完整OpenClaw能力的代理可以访问员工记录、供应链数据和财务信息，并将其发送到组织外部。"

### 10.3 NemoClaw：企业参考设计

NVIDIA的答案是NemoClaw，在OpenClaw之上构建三层安全：

1. **OpenShell**：运行时沙箱
2. **隐私路由器**
3. **网络护栏**

**关键特性**：
- 硬件无关
- 开源
- 可配置代理行为而无需重写代理

### 10.4 两个命令启动AI代理

> "Type two lines of shell commands, and you're off to the races with an AI agent."
> 
> "输入两行shell命令，你就可以开始使用AI代理了。"

---

## 十一、Token经济：AI作为新商品

### 11.1 数据中心现在是Token工厂

> "Data centers used to be a place to store files, and they're now a factory to generate tokens. Inference is the workload and tokens are the new commodity."
> 
> "数据中心曾经是存储文件的地方，现在它们是生成token的工厂。推理是工作负载，token是新的商品。"

### 11.2 分层Token市场

Jensen展示了像SaaS一样分层的推理市场：

- 一端是免费层token
- 另一端是每百万150美元的高级研究token

从Blackwell升级到Vera Rubin，将整个投资组合在相同功率预算下上移5-10倍。

### 11.3 Token预算将成为工程师标配

> "Every engineer will carry an annual token budget alongside their salary."
> 
> "每个工程师都会带着年度token预算，就像他们的工资一样。"

---

## 十二、Nemotron联盟

### 12.1 Nemotron 3 Ultra

NVIDIA表示Nemotron 3 Ultra将是世界上最好的基础模型。

### 12.2 Nemotron 4联盟成员

- Black Forest Labs
- Perplexity
- Mistral
- Cursor
- Langchain
- Sarvam

---

## 十三、物理AI：自动驾驶与机器人

### 13.1 RoboTaxi Ready平台

**新合作伙伴**：
- BYD
- Hyundai
- Nissan
- Geely

**现有合作伙伴**：
- Mercedes
- Toyota
- GM

这7家制造商每年生产约1800万辆汽车。

### 13.2 Uber合作

NVIDIA宣布与Uber合作，在多个城市部署这些车辆。

### 13.3 自动驾驶的ChatGPT时刻

> "The ChatGPT moment of self-driving cars has arrived."
> 
> "自动驾驶汽车的ChatGPT时刻已经到来。"

NVIDIA的Alpamayo模型现在让车辆能够：

- 推理
- 用自然语言叙述决策
- 遵循乘客指令

### 13.4 机器人模拟栈

四个开源组件：

1. **Isaac Lab**：训练和评估
2. **Newton**：GPU加速可微物理（与DeepMind和Disney共同开发）
3. **Cosmos World Models**：合成数据的神经模拟
4. **Groot 2**：通用机器人的推理和动作模型

### 13.5 GTC展示110个机器人

演讲以Disney的《冰雪奇缘》角色Olaf走上舞台与黄仁勋对话结束，完全在Omniverse中使用Newton模拟训练。

---

## 十四、NVIDIA DSX：AI工厂平台

### 14.1 数字孪生设计

NVIDIA DSX是基于Omniverse的数字孪生，让数据中心设计师在建设开始前模拟物理、热、电和网络条件。

### 14.2 MaxQ动态优化

DSX MaxQ在数据中心运行后动态优化token吞吐量与可用功率。

黄仁勋认为，通过更好的功率和热管理，现有数据中心内部可获得2倍的有效token输出改进，而无需添加任何芯片。

---

## 十五、OpenAI与AWS合作

### 15.1 OpenAI计算受限

> "As you know, [OpenAI] is completely compute-constrained."
> 
> "如你所知，OpenAI完全受到计算限制。"

黄仁勋宣布OpenAI将在今年登陆AWS，希望能减轻其大规模基础设施需求的负担。

---

## 十六、结构化数据：企业AI的基础

### 16.1 五层蛋糕

黄仁勋用大量时间讲解AI的"五层蛋糕"，结构化数据（SQL、Spark、Pandas和主要云数据仓库）位于基础层。

### 16.2 cuDF和cuVS

**cuDF**：GPU加速数据框
**cuVS**：GPU加速向量存储

### 16.3 实际案例

- **IBM watsonx.data**：Nestlé供应链数据集市刷新速度快5倍，成本降低83%
- **Google BigQuery**：主要客户计算成本降低近80%

---

## 十七、域名特定库

> "We have to have domain-specific libraries that solve problems in every one of these verticals."
> 
> "我们必须有域名特定库来解决每个垂直领域的问题。"

黄仁勋强调AI有很多应用，但不是简单地把GenAI扔到墙上希望它能粘住。

---

## 十八、开源模型发布

### 18.1 六大领域模型

| 领域 | 模型 |
|------|------|
| 语言 | Nemotron 3 |
| 视觉理解 | Nemotron 3 |
| RAG | Nemotron 3 |
| 安全 | Nemotron 3 |
| 语音 | Nemotron 3 |
| 世界模拟 | Cosmos 2 |
| 机器人 | Groot 2 |
| 自动驾驶 | Alpamayo |
| 生物/药物发现 | BioNemo |
| 天气/气候预测 | Earth-2 |

---

## 十九、闭幕：AI生成的乡村歌曲

演讲以一种独特的方式结束：几个机器人（加上黄仁勋）围坐在篝火旁唱着关于主题演讲的乡村歌曲。黄仁勋说这可能是AI生成的。

---

## 二十、对企业数据领导者的意义

### 20.1 结构化数据重回中心

黄仁勋的架构演讲也是一个数据演讲。结构化数据（SQL、Spark、Pandas和主要云数据仓库）位于AI"五层蛋糕"的基础层。

**关键论点**：结构化数据是"业务的基础真值"，生成式AI在可靠之前需要这个基础真值。

### 20.2 代理将访问你的数据

NemoClaw使自主代理能够：

- 访问文件系统
- 执行代码
- 查询数据库
- 跨企业应用通信

### 20.3 数据治理不是可选项

组织需要知道：

- 代理可以读取哪些数据？
- 它遍历哪些数据血缘路径？
- 谁授权它对特定数据集操作？
- 该授权何时最后一次审查？

---

## 附录：关键术语解释

| 术语 | 解释 |
|------|------|
| **Vera Rubin** | NVIDIA下一代AI计算平台，Blackwell的继任者 |
| **Vera CPU** | NVIDIA自主设计的数据中心CPU，88核心 |
| **Rubin GPU** | 与Vera CPU配对的GPU，每片288GB HBM4内存 |
| **Groq 3 LPU** | 语言处理单元，专为推理优化，大量片上SRAM |
| **NVLink 6** | NVIDIA第六代高速互连技术 |
| **DLSS 5** | 深度学习超级采样第5代，AI驱动的图形增强 |
| **OpenClaw** | 开源代理AI框架，被誉为"代理计算机的操作系统" |
| **NemoClaw** | NVIDIA基于OpenClaw的企业级代理参考设计 |
| **Nemotron** | NVIDIA开源大语言模型系列 |
| **Cosmos** | NVIDIA世界模拟模型 |
| **Groot** | NVIDIA通用机器人模型 |
| **Alpamayo** | NVIDIA自动驾驶模型 |
| **DSX** | NVIDIA AI工厂平台，基于Omniverse的数字孪生 |
| **Feynman** | Vera Rubin之后的下一代架构，目标2028年 |

---

## 来源

1. Tom's Hardware Live Blog: https://www.tomshardware.com/news/live/nvidia-gtc-2026-keynote-live-blog-jensen-huang
2. Atlan Analysis: https://atlan.com/know/nvidia-gtc-2026-keynote-recap/
3. NVIDIA GTC 2026 Keynote Video: https://www.youtube.com/watch?v=7O5WW6QhBU8

---

*整理时间：2026-03-18*
*整理人：南乔 @ 九星智囊团*
