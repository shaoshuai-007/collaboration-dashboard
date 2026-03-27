# 🎤 语音交互技能 - Voice Interaction Skill

**技能名称**: voice-interaction  
**功能**: 语音识别（STT）+ 语音合成（TTS）  
**状态**: 🟢 可用  
**作者**: 南乔  
**创建时间**: 2026-03-27

---

## 📋 功能概述

| 功能 | 说明 | 状态 |
|------|------|:----:|
| 语音识别（STT） | 将语音转为文字 | 🟢 可用（需API密钥） |
| 语音合成（TTS） | 将文字转为语音 | 🟢 可用（已有tts工具） |
| 音频文件识别 | 支持wav/mp3/flac/ogg | 🟢 可用 |

---

## 🗣️ 语音识别方案对比

| 方案 | 免费额度 | 需密钥 | 优点 |
|------|:--------:|:------:|------|
| **AssemblyAI** ⭐ | 30分钟/月 | ✅ | 只需邮箱注册，无需信用卡 |
| **百度ASR** | 60分钟/月 | ✅ | 额度大，需实名认证 |
| **讯飞ASR** | 60分钟/月 | ✅ | 额度大，需实名认证 |
| Google Speech | 无限 | ❌ | 国内被墙 |

**推荐**：AssemblyAI（注册最简单）

---

## 🎯 触发场景

- 用户说"识别语音"、"语音转文字"
- 用户提供音频文件要求转文字
- 用户要求与AI语音对话

---

## 📦 核心模块

### 1. 语音识别（STT）

```python
from skills.voice_interaction.voice_interaction import speech_to_text, list_microphones

# 方式1：从音频文件识别
result = speech_to_text(audio_file="/path/to/audio.wav")

# 方式2：从Base64音频识别
result = speech_to_text(base64_audio="SUQzBAAAAAA...")

# 方式3：从麦克风实时识别（需要物理设备）
result = speech_to_text(use_microphone=True, duration=5)

# 列出可用麦克风
mics = list_microphones()
```

### 2. 语音合成（TTS）

使用已集成的tts工具：

```python
# 使用tts工具（已有）
tts(text="你好，我是南乔")
# 输出: MEDIA:/tmp/tts-xxx/voice-xxx.mp3
```

### 3. 完整对话流程

```python
def voice_conversation(audio_input):
    """语音对话流程"""
    
    # Step 1: 语音识别
    stt_result = speech_to_text(audio_file=audio_input)
    if not stt_result["success"]:
        return {"error": stt_result["error"]}
    
    user_text = stt_result["text"]
    
    # Step 2: AI处理（调用千帆模型）
    ai_response = call_qianfan_api(user_text)
    
    # Step 3: 语音合成
    tts_audio = tts(text=ai_response)
    
    return {
        "user_text": user_text,
        "ai_response": ai_response,
        "tts_audio": tts_audio
    }
```

---

## 🔧 依赖安装

```bash
# 系统依赖
apt-get install portaudio19-dev python3-pyaudio

# Python依赖
pip install SpeechRecognition pyaudio --break-system-packages
```

---

## 📊 支持的音频格式

| 格式 | 扩展名 | 支持情况 |
|------|--------|:--------:|
| WAV | .wav | ✅ 完全支持 |
| MP3 | .mp3 | ✅ |
| FLAC | .flac | ✅ |
| OGG | .ogg | ✅ |

---

## 🌐 支持的语言

| 语言 | 代码 | 支持情况 |
|------|------|:--------:|
| 中文 | zh-CN | ✅ 完全支持 |
| 英语 | en-US | ✅ |
| 其他 | - | ✅ Google API支持 |

---

## 📝 使用示例

### 示例1：识别音频文件

```bash
# 命令行使用
python voice_interaction.py file /root/audio recording.wav
```

**返回**:
```json
{
  "success": true,
  "text": "你好，我想了解一下电信套餐",
  "language": "zh-CN",
  "file": "/root/audio recording.wav"
}
```

### 示例2：语音对话

```python
# 用户发送语音消息 → 识别为文字 → AI处理 → 合成语音回复
```

---

## 🔄 集成到OpenClaw

### 步骤1：注册技能

在OpenClaw中注册voice-interaction技能：

```json
{
  "skill": "voice-interaction",
  "triggers": ["语音", "说话", "识别", "语音识别", "语音转文字"],
  "handler": "skills.voice_interaction.handler"
}
```

### 步骤2：创建处理函数

```python
# skills/voice_interaction/handler.py
from .voice_interaction import speech_to_text

def handle_voice_message(message, context):
    """处理语音消息"""
    
    # 获取语音文件
    voice_file = message.get_voice()
    
    # 识别语音
    result = speech_to_text(audio_file=voice_file)
    
    if result["success"]:
        text = result["text"]
        # 进一步处理...
        return {"status": "ok", "text": text}
    else:
        return {"status": "error", "error": result["error"]}
```

---

## 🚀 进阶功能

### 1. 噪声过滤

```python
# 调整噪声阈值
recognizer.energy_threshold = 300  # 默认300
```

### 2. 多语言识别

```python
# 英文
result = speech_to_text(audio_file="english.wav", language="en-US")

# 中文
result = speech_to_text(audio_file="chinese.wav", language="zh-CN")
```

### 3. 置信度获取

```python
# 获取识别置信度
text = recognizer.recognize_google(audio, language="zh-CN", show_all=True)
# 返回包含confidence的完整结果
```

---

## ⚠️ 注意事项

1. **麦克风需要物理设备** - 服务器环境无法使用
2. **网络要求** - Google Speech Recognition需要联网
3. **音频质量** - 清晰的音频能提高识别准确率
4. **免费配额** - Google API有免费配额限制

---

## ⚠️ 严格输出规则（必须遵守）

**所有音频播放内容，统一使用以下格式：**

```
/play 音频链接
```

### 规则详情

| 规则 | 说明 |
|------|------|
| 格式 | 必须使用 `/play 音频链接` 格式 |
| 独占一行 | 单独一行展示，不与其他内容混排 |
| 不暴露链接 | 不显示任何URL、链接、网址、原始地址 |
| 文字简洁 | 如需文字说明，简洁明了 |

### ❌ 禁止的输出格式

```
MEDIA:xxx.mp3              # 禁止
http://xxx.mp3             # 禁止
<audio src="xxx">          # 禁止
[[audio_as_voice]]         # 禁止
点击播放：xxx.mp3          # 禁止
```

### ✅ 正确的输出格式

```
/play http://120.48.169.242/nanqiao_voice.mp3
```

---

## 📦 文件结构

```
skills/voice-interaction/
├── SKILL.md                    # 本文件
├── voice_interaction.py        # 核心模块
└── handler.py                 # OpenClaw集成处理函数
```

---

## 🔗 相关技能

- **tts** - 语音合成（已有）
- **qqbot-media** - QQ消息处理

---

*南有乔木，不可休思*
*语音交互，让沟通更自然*
