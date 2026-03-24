# frontend-design-ultimate技能赋能记录

> **赋能时间**：2026-03-24 12:10
> **赋能人**：南乔
> **技能来源**：少帅安装

---

## 🎯 技能定位

**frontend-design-ultimate**：几分钟内生成生产级静态网站

**技术栈**：
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Framer Motion（动画）
- Vite（纯静态）/ Next.js（Vercel部署）

---

## 👥 赋能对象

| Agent | 适用度 | 优先级 | 状态 |
|:-----:|:------:|:------:|:----:|
| 🎨 呈彩 | ⭐⭐⭐⭐⭐ | P0 | ✅ 已赋能 |
| 💻 天工 | ⭐⭐⭐⭐⭐ | P0 | ✅ 已赋能 |
| 🏗️ 筑台 | ⭐⭐⭐⭐ | P1 | ✅ 已赋能 |
| 🧵 织锦 | ⭐⭐⭐ | P1 | ✅ 已赋能 |

---

## 🚀 核心价值

1. **快速生成**：几分钟内生成生产级网站
2. **独特设计**：反AI风格，注重记忆点
3. **移动优先**：响应式设计，体验优秀
4. **技术先进**：React 18 + TypeScript + Tailwind

---

## 📋 使用场景

| Agent | 典型场景 | 配置重点 |
|:-----:|----------|----------|
| 🎨 呈彩 | 方案演示网站 | 突出方案价值、记忆点设计 |
| 💻 天工 | 前端界面开发 | 技术选型、代码规范、组件复用 |
| 🏗️ 筑台 | 售前方案展示 | ROI展示、成功案例、联系方式 |
| 🧵 织锦 | 架构演示网站 | 分层展示、技术选型、质量属性 |

---

## 🔧 快速使用

### 初始化项目
```bash
# Vite（纯静态，推荐）
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh my-site

# Next.js（支持SSR/SEO）
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-nextjs.sh my-site
```

### 编辑配置
```bash
cd my-site
vim config/site.ts  # 编辑网站内容
```

### 开发和构建
```bash
npm run dev      # 开发预览
npm run build    # 构建静态文件
```

---

## 📂 文件位置

```
/root/.openclaw/workspace/skills/frontend-design-ultimate/
├── SKILL.md                  # 技能说明
├── scripts/                  # 初始化脚本
│   ├── init-vite.sh
│   └── init-nextjs.sh
└── references/               # 参考文档

/root/.openclaw/workspace/知识库/方法论/
├── frontend-design-ultimate赋能指南.md    # 完整指南（9KB）
└── frontend-design-ultimate快速参考.md    # 快速参考（3KB）
```

---

## ✅ 设计要点

1. **❌ 禁止字体**：Inter、Roboto、Arial、Open Sans
2. **✅ 推荐字体**：Clash、Satoshi、Plus Jakarta Sans
3. **✅ 配色法则**：70%主色 + 20%辅色 + 10%强调色
4. **✅ 移动优先**：确保移动端体验
5. **✅ 一个记忆点**：动画/排版/配色至少有一个让人记住

---

## 📝 配置模板

```typescript
// config/site.ts
export const siteConfig = {
  name: "项目名称",
  tagline: "一句话描述",
  
  hero: {
    badge: "标签",
    title: "主标题",
    subtitle: "副标题",
    cta: { text: "按钮文字", href: "/link" },
  },
  
  features: [
    { icon: "Zap", title: "特性1", description: "描述1" },
    { icon: "Users", title: "特性2", description: "描述2" },
  ],
}
```

---

## 🎯 使用示例

### 示例1：呈彩创建方案演示网站
```bash
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh ai-recommend-demo
cd ai-recommend-demo
vim config/site.ts  # 配置智能配案系统内容
npm run dev
```

### 示例2：天工创建前端原型
```bash
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-nextjs.sh smart-service
cd smart-service
vim src/components/*.tsx  # 开发组件
npm run dev
vercel  # 部署到Vercel
```

### 示例3：筑台创建售前方案展示
```bash
bash /root/.openclaw/workspace/skills/frontend-design-ultimate/scripts/init-vite.sh customer-solution
cd customer-solution
vim config/site.ts  # 配置售前方案内容
npm run build
# 发送dist/目录给客户
```

---

## 📊 质量检查清单

**设计质量**：
- [ ] 字体独特（无Inter/Roboto）
- [ ] 配色有主次
- [ ] 背景有氛围
- [ ] 有记忆点

**移动响应**：
- [ ] 移动端居中
- [ ] 网格变单列
- [ ] 字体适当缩放

**可访问性**：
- [ ] 颜色对比度符合WCAG AA
- [ ] 焦点状态可见
- [ ] 语义化HTML

---

**赋能完成，九星智囊团再添利器——frontend-design-ultimate，让方案演示更出彩！**

**南有乔木，不可休思——技能赋能，持续进化！**
