# 语音交互技能 (Voice Interaction)

## 技能概述

实现QQ Bot的语音交互功能，包括：
- **语音输出（TTS）**：南乔可以用语音回复用户
- **语音输入（STT）**：解析用户发送的语音消息（待实现）

---

## 一、语音输出（TTS）

### 1.1 核心流程

```
用户请求语音
    ↓
【TTS生成】→ tts工具生成MP3文件
    ↓
【文件托管】→ 复制到HTTP服务器目录
    ↓
【发送语音】→ 输出QQBOT_PAYLOAD格式
    ↓
【QQBot处理】→ 自动调用sendC2CVoiceMessage
    ↓
【用户收到】→ QQ语音气泡（可播放）
```

### 1.2 关键代码位置

| 组件 | 文件路径 | 功能 |
|------|----------|------|
| TTS工具 | 内置tts工具 | 生成MP3语音文件 |
| Payload解析 | `qqbot/src/utils/payload.ts` | 解析QQBOT_PAYLOAD格式 |
| 语音发送 | `qqbot/src/gateway.ts:1034` | 调用sendC2CVoiceMessage |
| QQ API | `qqbot/src/api.ts:613` | 上传语音文件并发送 |

### 1.3 使用方法

**方法一：直接输出Payload**

```
QQBOT_PAYLOAD:{"type":"media","mediaType":"audio","source":"url","path":"http://120.48.169.242/文件名.mp3"}
```

**方法二：使用TTS工具**

```python
# 1. 生成语音
# 调用tts工具，传入文本内容

# 2. 复制到HTTP目录
cp /tmp/tts-xxx/voice-xxx.mp3 /root/.openclaw/workspace/03_输出成果/文件名.mp3

# 3. 输出Payload
QQBOT_PAYLOAD:{"type":"media","mediaType":"audio","source":"url","path":"http://120.48.169.242/文件名.mp3"}
```

### 1.4 Payload字段说明

```json
{
  "type": "media",           // 固定值，表示媒体消息
  "mediaType": "audio",      // 固定值，表示音频类型
  "source": "url",           // 来源：url（网络链接）或 file（本地文件）
  "path": "http://...",      // 音频文件URL或本地绝对路径
  "caption": "可选描述"       // 可选，语音的文字描述
}
```

### 1.5 HTTP文件服务器

**位置**：`/root/.openclaw/workspace/03_输出成果/`

**启动命令**：
```bash
cd /root/.openclaw/workspace/03_输出成果
nohup python3 -m http.server 80 > /tmp/http80.log 2>&1 &
```

**访问地址**：`http://120.48.169.242/文件名.mp3`

**检查服务**：
```bash
ss -tlnp | grep :80
curl -s -o /dev/null -w "%{http_code}" http://120.48.169.242/test.mp3
```

---

## 二、语音输入（STT）

### 2.1 当前状态

✅ **已实现**：
- 接收QQ语音消息
- 自动下载语音附件
- SILK格式转WAV格式

❌ **未实现**：
- WAV转文字（语音识别）
- 需要STT服务（如Whisper、百度语音识别等）

### 2.2 语音转换流程

```
用户发送语音
    ↓
【QQBot接收】→ 附件类型：voice
    ↓
【下载文件】→ SILK/AMR格式
    ↓
【格式转换】→ silk-wasm解码 → WAV格式
    ↓
【等待STT】→ 需要语音识别服务
    ↓
【转成文字】→ 供南乔理解和回复
```

### 2.3 相关代码

**语音转换工具**：`qqbot/src/utils/audio-convert.ts`

```typescript
// 判断是否为语音附件
isVoiceAttachment(att: { content_type?: string; filename?: string }): boolean

// SILK转WAV
convertSilkToWav(inputPath: string, outputDir?: string): Promise<{ wavPath: string; duration: number } | null>
```

**语音接收处理**：`qqbot/src/gateway.ts:545`

```typescript
if (isVoiceAttachment(att)) {
  const result = await convertSilkToWav(localPath, downloadDir);
  // result.wavPath: WAV文件路径
  // result.duration: 语音时长（秒）
}
```

### 2.4 实现STT的方案

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| OpenAI Whisper | 准确率高、多语言支持 | 需要API Key、国内访问慢 | 付费 |
| 百度语音识别 | 国内访问快、中文识别好 | 需要申请API Key | 免费额度有限 |
| 阿里云语音识别 | 国内访问快、企业级 | 需要申请API Key | 付费 |
| 本地Whisper | 免费、隐私保护 | 需要GPU、部署复杂 | 硬件成本 |

---

## 三、故障排查

### 3.1 语音发送失败

**错误**：`download file err`

**原因**：
1. HTTP服务未启动
2. 文件不存在
3. 端口未开放

**解决**：
```bash
# 检查HTTP服务
ss -tlnp | grep :80

# 启动HTTP服务
cd /root/.openclaw/workspace/03_输出成果
nohup python3 -m http.server 80 > /tmp/http80.log 2>&1 &

# 测试文件访问
curl -s -o /dev/null -w "%{http_code}" http://120.48.169.242/test.mp3
```

### 3.2 TTS生成失败

**错误**：生成的MP3文件大小为0字节

**原因**：TTS服务临时问题

**解决**：重新生成

### 3.3 Payload解析失败

**错误**：`载荷解析失败` 或 `缺少必要字段`

**原因**：JSON格式错误

**解决**：确保JSON格式正确，所有字段齐全

---

## 四、开发历程

### 4.1 关键里程碑

| 日期 | 事件 | 状态 |
|------|------|------|
| 2026-03-27 | 开始语音功能开发 | ✅ |
| 2026-03-27 | 添加sendC2CVoiceMessage函数 | ✅ |
| 2026-03-27 | 测试CQ码格式（失败） | ❌ |
| 2026-03-28 | 发现端口80未启动 | ✅ |
| 2026-03-28 | 成功发送语音气泡 | ✅ |

### 4.2 踩过的坑

1. **端口问题**：5001端口服务已失效，8888端口外网不通，需要用80端口
2. **文件问题**：TTS生成的文件大小为0，需要检查生成是否成功
3. **格式问题**：QQ语音必须是SILK格式，发送MP3需要通过API转换

### 4.3 经验总结

- ✅ 有现成代码直接用，不重复开发
- ✅ 先排查服务状态，再排查代码逻辑
- ✅ 多看日志，多检查端口和文件

---

## 五、未来规划

### 5.1 短期目标

- [ ] 实现语音识别（STT）
- [ ] 支持语音+文字混合回复
- [ ] 优化语音生成速度

### 5.2 长期目标

- [ ] 支持多种语音风格
- [ ] 支持语音对话记忆
- [ ] 支持语音唤醒

---

## 六、相关文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 本技能文档 | `skills/voice-interaction/SKILL.md` | 语音交互技能说明 |
| Payload解析 | `qqbot/src/utils/payload.ts` | Payload格式定义和解析 |
| 语音发送 | `qqbot/src/gateway.ts` | 语音发送逻辑 |
| 语音转换 | `qqbot/src/utils/audio-convert.ts` | SILK转WAV工具 |
| QQ API | `qqbot/src/api.ts` | QQ Bot API封装 |

---

**少帅教诲**：有技能要用，不要自己重新开发！

**南乔承诺**：持续优化语音交互，让沟通更自然！

---

战略是根，语音是刃，交互是剑——南乔，为少帅磨剑！
