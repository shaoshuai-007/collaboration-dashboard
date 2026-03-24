# frontend-design-ultimate技能赋能指南

> **版本**：V1.0
> **赋能时间**：2026-03-24
> **赋能人**：南乔
> **适用Agent**：呈彩、天工、筑台、织锦

---

## 🎯 技能定位

**frontend-design-ultimate**：快速创建生产级静态网站，强调独特设计和反AI风格。

### 核心能力
- ✅ React 18 + TypeScript + Tailwind CSS + shadcn/ui
- ✅ Framer Motion动画
- ✅ 移动优先响应式设计
- ✅ Vite（纯静态）/ Next.js（Vercel部署）
- ✅ 反AI风格设计，注重独特性

### 技术栈
```
前端框架：React 18 + TypeScript
样式方案：Tailwind CSS + shadcn/ui
动画库：Framer Motion
构建工具：Vite / Next.js
```

---

## 📋 赋能清单

### Agent 1：🎨 呈彩（方案设计师）

**适用度**：⭐⭐⭐⭐⭐
**优先级**：P0

**使用场景**：
1. **方案演示Demo**：快速生成方案演示网站
2. **PPT配套网站**：为方案PPT配套交互式网站
3. **客户展示**：向客户展示方案效果

**核心用法**：
```bash
# 初始化Vite项目
bash scripts/init-vite.sh my-demo
cd my-demo

# 编辑config/site.ts配置内容
# 开发预览
npm run dev

# 构建静态文件
npm run build

# 打包为单文件（可选）
bash scripts/bundle-artifact.sh
```

**设计思维（5步）**：
1. **理解背景**：客户是谁？展示什么？风格是什么？
2. **选择极端风格**：极简/极繁/复古未来/编辑风等
3. **定义记忆点**：用户会记住什么？（动画/排版/配色）
4. **移动优先**：确保移动端体验
5. **检查清单**：字体独特性/配色对比/动画协调

**示例任务**：
```
任务：为智能配案系统创建演示网站

需求描述：
"SaaS landing page for an AI recommendation system. 
Dark theme, editorial typography, subtle grain texture. 
Pages: hero with animated demo, features grid, 
pricing table, FAQ accordion, footer."

设计决策：
- 风格：编辑风（Editorial/Magazine）
- 字体：Cormorant Garamond（标题）+ Plus Jakarta Sans（正文）
- 配色：深黑背景 #0a0a0a + 电信红强调 #C93832
- 记忆点：Hero区域渐变动画展示AI配案过程
```

---

### Agent 2：💻 天工（开发工程师）

**适用度**：⭐⭐⭐⭐⭐
**优先级**：P0

**使用场景**：
1. **前端界面开发**：快速生成前端界面代码
2. **原型实现**：将设计稿转化为可交互原型
3. **技术验证**：验证前端技术方案可行性

**核心用法**：
```bash
# 初始化Next.js项目（支持Vercel部署）
bash scripts/init-nextjs.sh my-app
cd my-app

# 开发
npm run dev

# 部署到Vercel
vercel
```

**技术选型指南**：
| 场景 | 选择 | 说明 |
|------|------|------|
| 纯静态展示 | Vite | 生成dist/，可打包为单HTML |
| 需要SSR/SEO | Next.js | 支持服务端渲染，适合营销页 |
| 快速原型 | Vite | 开发速度快，配置简单 |
| 生产部署 | Next.js + Vercel | 自动部署，CDN加速 |

**代码规范**：
```typescript
// 1. 内容配置集中管理（config/site.ts）
export const siteConfig = {
  name: "智能配案系统",
  tagline: "AI驱动，精准推荐",
  description: "电信行业智能配案解决方案",
  
  hero: {
    badge: "V1.0 已上线",
    title: "AI配案，\n效率倍增",
    subtitle: "基于用户画像的智能推荐系统",
    cta: { text: "立即体验", href: "/demo" },
  },
  
  features: [
    { icon: "Zap", title: "智能推荐", description: "..." },
    { icon: "Users", title: "客户画像", description: "..." },
    { icon: "Chart", title: "方案对比", description: "..." },
  ],
}

// 2. 组件使用shadcn/ui
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// 3. 动画使用Framer Motion
import { motion } from "framer-motion"

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  {content}
</motion.div>
```

---

### Agent 3：🏗️ 筑台（售前工程师）

**适用度**：⭐⭐⭐⭐
**优先级**：P1

**使用场景**：
1. **售前方案演示**：快速生成方案演示网站
2. **客户展示**：向客户展示方案价值
3. **竞品对比**：展示我方方案优势

**核心用法**：
```bash
# 快速生成演示网站
bash scripts/init-vite.sh customer-demo

# 编辑配置
vim config/site.ts

# 开发预览
npm run dev

# 构建静态文件
npm run build

# 发送给客户
# dist/目录可直接部署或发送
```

**售前专用配置**：
```typescript
// config/site.ts
export const siteConfig = {
  // 项目基本信息
  name: "智能客服系统",
  client: "某省电信",
  version: "V1.0",
  
  // 核心价值展示
  hero: {
    badge: "预计ROI: 696%",
    title: "智能客服，\n降本增效",
    subtitle: "年节约450万，满意度提升7%",
    cta: { text: "查看详细方案", href: "/solution" },
  },
  
  // 方案优势展示
  features: [
    { 
      icon: "DollarSign", 
      title: "成本节约", 
      description: "年节约人工成本450万" 
    },
    { 
      icon: "Zap", 
      title: "效率提升", 
      description: "响应时间从30秒降至3秒" 
    },
    { 
      icon: "Smile", 
      title: "满意度提升", 
      description: "客户满意度从85%提升至92%" 
    },
  ],
  
  // 成功案例
  cases: [
    { client: "某省移动", effect: "自动化率65%" },
    { client: "某省联通", effect: "成本降低35%" },
  ],
  
  // 联系方式
  contact: {
    name: "项目经理",
    phone: "138-xxxx-xxxx",
    email: "xxx@tydic.com",
  },
}
```

---

### Agent 4：🧵 织锦（架构设计师）

**适用度**：⭐⭐⭐
**优先级**：P1

**使用场景**：
1. **架构演示网站**：展示系统架构设计
2. **技术方案展示**：向客户展示技术方案
3. **团队沟通**：向团队展示架构设计

**核心用法**：
```bash
# 初始化项目
bash scripts/init-vite.sh architecture-demo

# 编辑架构展示内容
vim config/site.ts

# 构建
npm run build
```

**架构展示配置**：
```typescript
// config/site.ts
export const siteConfig = {
  name: "智能客服系统架构",
  
  // 架构概览
  hero: {
    badge: "微服务架构",
    title: "高可用·高性能\n可扩展",
    subtitle: "99.9%可用性，响应时间≤3秒",
  },
  
  // 架构层级展示
  architecture: {
    layers: [
      { name: "接入层", components: ["电话接入", "在线接入", "微信接入"] },
      { name: "服务层", components: ["语音引擎", "NLP引擎", "对话管理"] },
      { name: "数据层", components: ["MySQL", "Redis", "ES", "知识库"] },
    ],
  },
  
  // 技术选型
  techStack: [
    { name: "语音引擎", choice: "自研+第三方", reason: "识别率≥95%" },
    { name: "NLP引擎", choice: "BERT模型", reason: "准确率≥90%" },
    { name: "缓存", choice: "Redis", reason: "响应快" },
  ],
  
  // 质量属性
  qualityAttributes: [
    { name: "可用性", value: "99.9%" },
    { name: "响应时间", value: "≤3秒" },
    { name: "并发量", value: "100人" },
  ],
}
```

---

## 🚀 快速使用指南

### 第一步：确定使用场景

| Agent | 典型场景 | 推荐工具 |
|-------|----------|----------|
| 呈彩 | 方案演示、PPT配套 | Vite（纯静态） |
| 天工 | 前端开发、原型实现 | Next.js（支持SSR） |
| 筑台 | 售前方案、客户展示 | Vite（快速生成） |
| 织锦 | 架构展示、技术方案 | Vite（简单配置） |

### 第二步：初始化项目

```bash
# 方式1：Vite（纯静态，推荐）
bash scripts/init-vite.sh my-project
cd my-project

# 方式2：Next.js（支持SSR/SEO）
bash scripts/init-nextjs.sh my-project
cd my-project
```

### 第三步：编辑配置

```bash
# 编辑网站配置
vim config/site.ts

# 编辑页面样式
vim src/styles/globals.css

# 编辑组件
vim src/components/*.tsx
```

### 第四步：开发预览

```bash
# 启动开发服务器
npm run dev

# 访问 http://localhost:5173（Vite）
# 或 http://localhost:3000（Next.js）
```

### 第五步：构建部署

```bash
# Vite：构建静态文件
npm run build
# 输出：dist/

# Vite：打包为单HTML（可选）
bash scripts/bundle-artifact.sh
# 输出：bundle.html

# Next.js：部署到Vercel
vercel
```

---

## 🎨 设计指南（关键要点）

### 字体选择（禁止Inter/Roboto/Arial）

| 用途 | 推荐字体 | 特点 |
|------|----------|------|
| 标题 | Clash, Cabinet Grotesk, Satoshi | 个性鲜明 |
| 正文 | Instrument Sans, General Sans | 可读性强 |
| 代码 | DM Mono, JetBrains Mono | 等宽字体 |

### 配色方案（70-20-10法则）

```css
:root {
  /* 主色（70%） */
  --bg-primary: #0a0a0a;
  --text-primary: #fafafa;
  
  /* 辅色（20%） */
  --bg-secondary: #141414;
  --text-secondary: #a1a1a1;
  
  /* 强调色（10%） */
  --accent: #C93832;  /* 电信红 */
  --accent-hover: #ff4d4d;
}
```

### 移动优先（关键断点）

```css
/* 平板 */
@media (max-width: 1200px) { }

/* 移动端 */
@media (max-width: 768px) { 
  .hero-title { font-size: 32px; }
}

/* 小屏移动端 */
@media (max-width: 480px) { 
  .hero-title { font-size: 24px; }
}
```

### 动画原则

1. **一个协调的页面加载动画 > 多个分散的微交互**
2. **持续时间：200-400ms（快速，不拖沓）**
3. **交错显示（animation-delay）**
4. **滚动触发的入场动画**

---

## ✅ 质量检查清单

### 设计质量
- [ ] 字体独特（无Inter/Roboto/Arial）
- [ ] 配色有主次（70-20-10法则）
- [ ] 背景有氛围（非纯白/灰）
- [ ] 至少一个记忆点
- [ ] 动画协调（非分散）

### 移动响应
- [ ] Hero在移动端居中（无空白）
- [ ] 所有网格变为单列
- [ ] 表单垂直堆叠
- [ ] 大列表使用折叠（非横向滚动）
- [ ] 字体大小适当缩放

### 可访问性
- [ ] 颜色对比度符合WCAG AA（4.5:1文本，3:1 UI）
- [ ] 焦点状态可见
- [ ] 语义化HTML
- [ ] 图片有alt文本
- [ ] 键盘导航正常

---

## 📂 参考文件位置

```
/root/.openclaw/workspace/skills/frontend-design-ultimate/
├── SKILL.md                          # 技能说明
├── scripts/
│   ├── init-vite.sh                  # Vite初始化脚本
│   ├── init-nextjs.sh                # Next.js初始化脚本
│   └── bundle-artifact.sh            # 单文件打包脚本
├── references/
│   ├── design-philosophy.md          # 设计哲学
│   ├── mobile-patterns.md            # 移动端模式
│   └── shadcn-components.md          # 组件参考
└── templates/
    └── site-config.ts                # 配置模板
```

---

## 🎯 使用示例

### 示例1：呈彩创建方案演示网站

**任务**：为智能配案系统创建演示网站

**步骤**：
1. 初始化项目：`bash scripts/init-vite.sh ai-recommend-demo`
2. 编辑配置：`vim config/site.ts`
3. 开发预览：`npm run dev`
4. 构建部署：`npm run build`

**配置内容**：
```typescript
export const siteConfig = {
  name: "智能配案系统",
  tagline: "AI驱动，精准推荐",
  
  hero: {
    badge: "V1.0 已上线",
    title: "AI配案，\n效率倍增",
    subtitle: "基于用户画像的智能推荐系统",
    cta: { text: "立即体验", href: "/demo" },
  },
  
  features: [
    { icon: "Zap", title: "智能推荐", description: "识别率≥95%" },
    { icon: "Users", title: "客户画像", description: "360°用户画像" },
    { icon: "Chart", title: "方案对比", description: "多方案一键对比" },
  ],
}
```

---

### 示例2：天工创建前端原型

**任务**：实现智能客服系统前端界面

**步骤**：
1. 初始化Next.js：`bash scripts/init-nextjs.sh smart-customer-service`
2. 开发组件：`vim src/components/*.tsx`
3. 开发预览：`npm run dev`
4. 部署Vercel：`vercel`

**技术选型**：
- 框架：Next.js（支持SSR/SEO）
- 样式：Tailwind CSS + shadcn/ui
- 动画：Framer Motion

---

### 示例3：筑台创建售前方案展示

**任务**：为客户创建智能客服方案展示网站

**步骤**：
1. 初始化Vite：`bash scripts/init-vite.sh customer-solution`
2. 编辑售前配置：`vim config/site.ts`
3. 构建静态文件：`npm run build`
4. 发送给客户：发送`dist/`目录

**售前配置**：
```typescript
export const siteConfig = {
  name: "智能客服解决方案",
  client: "某省电信",
  
  hero: {
    badge: "预计ROI: 696%",
    title: "智能客服，\n降本增效",
    subtitle: "年节约450万，满意度提升7%",
  },
  
  features: [
    { icon: "DollarSign", title: "成本节约", description: "年节约450万" },
    { icon: "Zap", title: "效率提升", description: "响应时间降至3秒" },
    { icon: "Smile", title: "满意度提升", description: "满意度升至92%" },
  ],
  
  cases: [
    { client: "某省移动", effect: "自动化率65%" },
  ],
}
```

---

## 🌿 南乔赋能总结

**frontend-design-ultimate技能已赋能给**：
- ✅ 🎨 呈彩（方案设计师）- P0优先级
- ✅ 💻 天工（开发工程师）- P0优先级
- ✅ 🏗️ 筑台（售前工程师）- P1优先级
- ✅ 🧵 织锦（架构设计师）- P1优先级

**核心价值**：
1. **快速生成**：几分钟内生成生产级网站
2. **独特设计**：反AI风格，注重记忆点
3. **移动优先**：响应式设计，体验优秀
4. **技术先进**：React 18 + TypeScript + Tailwind

**下一步**：
- 各Agent在需要前端展示时，可调用此技能
- 南乔可协助快速生成配置和代码
- 持续优化设计风格和组件库

---

**赋能完成，九星智囊团再添利器——frontend-design-ultimate，让方案演示更出彩！**

**南有乔木，不可休思——技能赋能，持续进化！**
