# frontend-design-ultimate技能快速参考卡片

> **版本**：V1.0
> **赋能时间**：2026-03-24
> **适用Agent**：呈彩、天工、筑台、织锦

---

## 🎯 一句话定位

**frontend-design-ultimate** = 几分钟内生成生产级静态网站（React + Tailwind + shadcn/ui）

---

## 📋 快速使用（3步）

### Step 1: 初始化项目
```bash
# Vite（纯静态，推荐）
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh my-site

# Next.js（支持SSR/SEO）
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-nextjs.sh my-site
```

### Step 2: 编辑配置
```bash
cd my-site
vim config/site.ts  # 编辑网站内容
```

### Step 3: 开发和构建
```bash
npm run dev      # 开发预览
npm run build    # 构建静态文件
```

---

## 🎨 设计要点（记住5条）

1. **❌ 禁止字体**：Inter、Roboto、Arial、Open Sans
2. **✅ 推荐字体**：Clash、Satoshi、Plus Jakarta Sans
3. **✅ 配色法则**：70%主色 + 20%辅色 + 10%强调色
4. **✅ 移动优先**：确保移动端体验
5. **✅ 一个记忆点**：动画/排版/配色至少有一个让人记住

---

## 👥 Agent使用场景

| Agent | 典型任务 | 配置重点 |
|:-----:|----------|----------|
| 🎨 呈彩 | 方案演示网站 | 突出方案价值、记忆点设计 |
| 💻 天工 | 前端界面开发 | 技术选型、代码规范、组件复用 |
| 🏗️ 筑台 | 售前方案展示 | ROI展示、成功案例、联系方式 |
| 🧵 织锦 | 架构演示网站 | 分层展示、技术选型、质量属性 |

---

## 📝 配置模板（复制即用）

```typescript
// config/site.ts
export const siteConfig = {
  name: "项目名称",
  tagline: "一句话描述",
  
  hero: {
    badge: "标签（如：V1.0）",
    title: "主标题（可换行）",
    subtitle: "副标题",
    cta: { text: "按钮文字", href: "/link" },
  },
  
  features: [
    { icon: "Zap", title: "特性1", description: "描述1" },
    { icon: "Users", title: "特性2", description: "描述2" },
    { icon: "Chart", title: "特性3", description: "描述3" },
  ],
}
```

---

## 🔧 技术栈速查

| 组件 | 技术 | 用途 |
|------|------|------|
| 框架 | React 18 + TypeScript | 核心框架 |
| 样式 | Tailwind CSS + shadcn/ui | 样式方案 |
| 动画 | Framer Motion | 页面动画 |
| 构建 | Vite / Next.js | 构建工具 |

---

## ✅ 质量检查清单

**设计质量**：
- [ ] 字体独特（无Inter/Roboto）
- [ ] 配色有主次
- [ ] 背景有氛围
- [ ] 有记忆点

**移动响应**：
- [ ] 移动端居中
- [ ] 网格变单列
- [ ] 字体适当缩放

---

## 📂 关键文件位置

```
/root/.openclaw/workspace/skills/frontend-design-ultimate/
├── SKILL.md                  # 技能说明
├── scripts/init-vite.sh      # Vite初始化
├── scripts/init-nextjs.sh    # Next.js初始化
└── references/               # 参考文档

/root/.openclaw/workspace/知识库/方法论/
└── frontend-design-ultimate赋能指南.md  # 完整指南
```

---

## 🚀 示例命令（复制即用）

```bash
# 创建智能配案演示网站
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh ai-recommend-demo
cd ai-recommend-demo
npm run dev

# 创建售前方案展示网站
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh customer-solution
cd customer-solution
npm run dev

# 创建架构演示网站
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh architecture-demo
cd architecture-demo
npm run dev
```

---

**赋能完成，随时可用！**

**南有乔木，不可休思——技能赋能，持续进化！**
