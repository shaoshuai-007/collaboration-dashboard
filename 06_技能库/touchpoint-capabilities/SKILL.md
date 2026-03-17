---
name: touchpoint-capabilities
description: 触点能力技能。支持QQ消息推送、邮箱发送、文件传输等触点能力。
metadata: {"clawdbot":{"emoji":"📡"}}
triggers:
  - 发送邮件
  - 发送文件
  - QQ推送
  - 触点能力
priority: 90
---

# 触点能力技能

## 📱 QQ Bot 消息推送

### 发送消息到QQ
使用 `sessions_send` 工具：

```
sessions_send(
  sessionKey="agent:main:qqbot:dm:8236c3da8cf6f5df6fee66d42adaae97",
  message="消息内容"
)
```

### 发送图片到QQ
使用 `<qqimg>` 标签：

```
<qqimg>/path/to/image.jpg</qqimg>
```

### QQ发送文件方案
**限制**：QQ Bot API不支持直接发送文件

**解决方案**：
1. 将Markdown文件转成PDF
2. 将PDF转成长图
3. 使用 `<qqimg>` 发送图片

```bash
# Markdown转PDF
pandoc input.md -o output.pdf

# PDF转图片
pdftoppm output.pdf output -png
```

---

## 📧 邮箱能力

### QQ邮箱SMTP发送 ✅ 已配置
**技能**：`send-email` (wangyendt/wayne-skills)
**配置**：
- SMTP服务器：smtp.qq.com
- 端口：587
- 发件人：417895006@qq.com
- 授权码：已存储在MEMORY.md

**发送命令**：
```bash
python3 /root/.agents/skills/send-email/scripts/send_email.py \
  --to "收件人@domain.com" \
  --from-addr "417895006@qq.com" \
  --subject "主题" \
  --content "内容" \
  --smtp-server smtp.qq.com \
  --smtp-port 587 \
  --username "417895006@qq.com" \
  --password "授权码"
```

### 临时邮箱 (agent-email)
已安装：`@zaddy6/agentemail`

```bash
# 创建临时邮箱
agent-email create

# 读取邮件
agent-email read default

# 查看邮件详情
agent-email show default <messageId>
```

### 发送邮件 (需要SMTP配置)
**方案一**：配置系统邮件服务
```bash
# 安装msmtp
apt install msmtp

# 配置 ~/.msmtprc
account default
host smtp.example.com
port 587
from user@example.com
auth on
user user@example.com
password your_password
tls on
```

**方案二**：使用curl调用邮件API
```bash
# 使用Resend API
curl -X POST 'https://api.resend.com/emails' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "onboarding@resend.dev",
    "to": "sunzheng@tydic.com",
    "subject": "报告",
    "html": "<p>内容</p>"
  }'
```

---

## 📎 文件发送能力

### Telegram发送文件 (send-file技能)
```bash
alma send file /path/to/document.pdf "说明文字"
```

### 飞书发送文件
使用飞书技能：`feishu-doc`

---

## 📋 触点能力清单

| 触点 | 能力 | 状态 |
|------|------|:----:|
| QQ消息 | sessions_send | ✅ |
| QQ图片 | qqimg标签 | ✅ |
| QQ文件 | 转图片发送 | ✅ |
| 邮件接收 | agent-email | ✅ |
| 邮件发送 | QQ邮箱SMTP | ✅ |
| Telegram | alma send | ⏳ |
| 飞书 | feishu技能 | ✅ |

---

## 🔧 配置建议

1. **QQ文件发送**：安装 `pandoc` + `pdftoppm` 实现文件转图片
2. **邮件发送**：申请Resend API密钥或配置SMTP
3. **Telegram**：配置ALMA_CHAT_ID环境变量

## 📝 用户偏好

- 用户：少帅
- QQ：417895006
- QQ openid：`8236C3DA8CF6F5DF6FEE66D42ADAAE97`
- 邮箱：sunzheng@tydic.com
- 推送偏好：重要报告/提醒优先发送至QQ
