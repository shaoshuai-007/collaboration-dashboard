"""
语音交互模块 - Voice Interaction Module
功能：语音识别（STT）+ 语音合成（TTS）
支持：中文识别、音频文件输入、实时语音对话
"""

import os
import json
import base64
import tempfile
import asyncio
from typing import Optional, Union
import speech_recognition as sr
from datetime import datetime

# TTS后备方案
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# 百度ASR
try:
    from aip import AipSpeech
    BAIDU_AIP_AVAILABLE = True
except ImportError:
    BAIDU_AIP_AVAILABLE = False

# AssemblyAI
try:
    import requests
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False


class VoiceInteraction:
    """语音交互核心类"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.mkdtemp()
        
    def recognize_from_file(self, audio_file: str, language: str = "zh-CN") -> dict:
        """
        从音频文件识别语音
        
        Args:
            audio_file: 音频文件路径（支持wav, mp3, flac, ogg）
            language: 语言代码，默认中文(zh-CN)
            
        Returns:
            dict: {"success": bool, "text": str, "error": str}
        """
        try:
            # 尝试加载音频文件
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                
            # 使用Google Speech Recognition识别
            text = self.recognizer.recognize_google(audio_data, language=language)
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "file": audio_file
            }
            
        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": "无法识别音频内容"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "text": "",
                "error": f"语音识别服务错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"识别失败: {str(e)}"
            }
    
    def recognize_from_microphone(self, duration: int = 5, language: str = "zh-CN") -> dict:
        """
        从麦克风实时识别语音（需要物理设备）
        
        Args:
            duration: 录音时长（秒）
            language: 语言代码
            
        Returns:
            dict: {"success": bool, "text": str, "error": str}
        """
        try:
            with sr.Microphone() as source:
                print("🎤 正在聆听...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=duration)
                
            text = self.recognizer.recognize_google(audio, language=language)
            
            return {
                "success": True,
                "text": text,
                "language": language
            }
            
        except sr.WaitTimeoutError:
            return {
                "success": False,
                "text": "",
                "error": "录音超时，未检测到声音"
            }
        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": "未能识别语音内容"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"录音失败: {str(e)}"
            }
    
    def recognize_from_base64(self, base64_audio: str, language: str = "zh-CN") -> dict:
        """
        从Base64编码的音频数据识别语音
        
        Args:
            base64_audio: Base64编码的音频数据
            language: 语言代码
            
        Returns:
            dict: {"success": bool, "text": str, "error": str}
        """
        try:
            # 解码Base64
            audio_bytes = base64.b64decode(base64_audio)
            
            # 保存为临时文件
            temp_file = os.path.join(self.temp_dir, f"audio_{datetime.now().timestamp()}.wav")
            with open(temp_file, "wb") as f:
                f.write(audio_bytes)
            
            # 识别
            result = self.recognize_from_file(temp_file, language)
            
            # 清理临时文件
            try:
                os.remove(temp_file)
            except:
                pass
                
            return result
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Base64音频识别失败: {str(e)}"
            }
    
    def get_available_microphones(self) -> list:
        """获取可用的麦克风列表"""
        try:
            mics = sr.Microphone.list_microphone_names()
            return [{"index": i, "name": name} for i, name in enumerate(mics)]
        except Exception as e:
            return [{"error": str(e)}]


# 全局实例
_voice_instance = None

def get_voice_instance():
    """获取语音交互实例"""
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = VoiceInteraction()
    return _voice_instance


def speech_to_text(audio_file: str = None, base64_audio: str = None, 
                  use_microphone: bool = False, duration: int = 5,
                  language: str = "zh-CN") -> dict:
    """
    语音识别主函数
    
    Args:
        audio_file: 音频文件路径
        base64_audio: Base64编码的音频
        use_microphone: 是否使用麦克风
        duration: 麦克风录音时长
        language: 语言代码
        
    Returns:
        dict: 识别结果
    """
    voice = get_voice_instance()
    
    if audio_file:
        return voice.recognize_from_file(audio_file, language)
    elif base64_audio:
        return voice.recognize_from_base64(base64_audio, language)
    elif use_microphone:
        return voice.recognize_from_microphone(duration, language)
    else:
        return {
            "success": False,
            "text": "",
            "error": "请提供音频文件、Base64音频或启用麦克风"
        }


def list_microphones() -> list:
    """列出可用麦克风"""
    voice = get_voice_instance()
    return voice.get_available_microphones()


# ========== 百度语音识别 ==========

class BaiduASR:
    """百度语音识别"""
    
    def __init__(self, app_id: str, api_key: str, secret_key: str):
        self.client = AipSpeech(app_id, api_key, secret_key)
    
    def recognize_file(self, audio_file: str) -> dict:
        """从音频文件识别"""
        try:
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # 百度ASR识别（16k采样率）
            result = self.client.asr(audio_data, 'wav', 16000, {
                'dev_pid': 1537,  # 中文普通话
            })
            
            if 'result' in result:
                return {
                    "success": True,
                    "text": result['result'][0],
                    "confidence": result.get('confidence', 0)
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "error": result.get('err_msg', '识别失败')
                }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }


# 百度ASR全局实例
_baidu_asr = None

def init_baidu_asr(app_id: str, api_key: str, secret_key: str):
    """初始化百度ASR"""
    global _baidu_asr
    if BAIDU_AIP_AVAILABLE:
        _baidu_asr = BaiduASR(app_id, api_key, secret_key)
        return True
    return False


def baidu_speech_to_text(audio_file: str) -> dict:
    """使用百度ASR识别语音"""
    if _baidu_asr is None:
        return {
            "success": False,
            "text": "",
            "error": "请先调用init_baidu_asr()初始化API密钥"
        }
    return _baidu_asr.recognize_file(audio_file)


# ========== AssemblyAI 语音识别 ==========

class AssemblyAI:
    """AssemblyAI 语音识别 - 每月30分钟免费"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com/v2"
    
    def upload_audio(self, audio_file: str) -> str:
        """上传音频文件"""
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{self.base_url}/upload",
                headers={"authorization": self.api_key},
                data=f
            )
        return response.json()["upload_url"]
    
    def transcribe(self, audio_url: str, language_code: str = "zh") -> dict:
        """开始转写"""
        response = requests.post(
            f"{self.base_url}/transcript",
            headers={"authorization": self.api_key},
            json={
                "audio_url": audio_url,
                "language_code": language_code
            }
        )
        return response.json()
    
    def get_result(self, transcript_id: str) -> dict:
        """获取转写结果"""
        response = requests.get(
            f"{self.base_url}/transcript/{transcript_id}",
            headers={"authorization": self.api_key}
        )
        return response.json()
    
    def recognize_file(self, audio_file: str, language_code: str = "zh") -> dict:
        """从文件识别（完整流程）"""
        try:
            # 1. 上传音频
            audio_url = self.upload_audio(audio_file)
            
            # 2. 开始转写
            result = self.transcribe(audio_url, language_code)
            transcript_id = result["id"]
            
            # 3. 等待结果
            import time
            max_wait = 60  # 最多等60秒
            while max_wait > 0:
                status = self.get_result(transcript_id)
                if status["status"] == "completed":
                    return {
                        "success": True,
                        "text": status["text"],
                        "confidence": status.get("confidence", 0)
                    }
                elif status["status"] == "error":
                    return {
                        "success": False,
                        "text": "",
                        "error": status.get("error", "转写失败")
                    }
                time.sleep(1)
                max_wait -= 1
            
            return {
                "success": False,
                "text": "",
                "error": "转写超时"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }


# AssemblyAI 全局实例
_assemblyai = None

def init_assemblyai(api_key: str):
    """初始化AssemblyAI"""
    global _assemblyai
    if ASSEMBLYAI_AVAILABLE:
        _assemblyai = AssemblyAI(api_key)
        return True
    return False


def assemblyai_speech_to_text(audio_file: str, language_code: str = "zh") -> dict:
    """使用AssemblyAI识别语音"""
    if _assemblyai is None:
        return {
            "success": False,
            "text": "",
            "error": "请先调用init_assemblyai(api_key)初始化API密钥"
        }
    return _assemblyai.recognize_file(audio_file, language_code)


# ========== TTS 语音合成 ==========

async def _edge_tts_async(text: str, voice: str = "zh-CN-XiaoxiaoNeural", output_file: str = None) -> str:
    """
    Edge-TTS 异步合成
    
    Args:
        text: 要合成的文本
        voice: 语音角色（如 zh-CN-XiaoxiaoNeural）
        output_file: 输出文件路径
        
    Returns:
        str: 生成的音频文件路径
    """
    if not output_file:
        output_file = f"/tmp/edge_tts_{datetime.now().timestamp()}.mp3"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file


def edge_speak(text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> dict:
    """
    使用Edge-TTS合成语音
    
    Args:
        text: 要合成的文本
        voice: 语音角色
        
    Returns:
        dict: {"success": bool, "audio_file": str, "error": str}
    """
    if not EDGE_TTS_AVAILABLE:
        return {
            "success": False,
            "audio_file": "",
            "error": "edge-tts未安装，请运行: pip install edge-tts"
        }
    
    try:
        output_file = asyncio.run(_edge_tts_async(text, voice))
        return {
            "success": True,
            "audio_file": output_file,
            "voice": voice
        }
    except Exception as e:
        return {
            "success": False,
            "audio_file": "",
            "error": str(e)
        }


# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
🎤 语音识别工具

用法:
    python voice_interaction.py file <音频文件>     - 从文件识别
    python voice_interaction.py mic [时长]         - 从麦克风识别
    python voice_interaction.py list                - 列出可用麦克风
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "file":
        if len(sys.argv) < 3:
            print("请提供音频文件路径")
            sys.exit(1)
        result = speech_to_text(audio_file=sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif cmd == "mic":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        result = speech_to_text(use_microphone=True, duration=duration)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif cmd == "list":
        mics = list_microphones()
        print(json.dumps(mics, ensure_ascii=False, indent=2))
        
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
