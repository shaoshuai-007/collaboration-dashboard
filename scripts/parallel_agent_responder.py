#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行Agent响应器
- 多Agent并行调用API
- 流式输出支持
- 结果缓存

Author: 九星智囊团
Date: 2026-03-17
"""

import os
import json
import time
import hashlib
import requests
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# 配置
QIANFAN_API_KEY = os.environ.get("QIANFAN_API_KEY", "")
API_URL = "https://qianfan.baidubce.com/v2/coding/chat/completions"
CACHE_DIR = "/root/.openclaw/workspace/03_输出成果/agent_cache"
MAX_WORKERS = 5  # 最大并行数

# 创建缓存目录
os.makedirs(CACHE_DIR, exist_ok=True)

# Token统计
token_lock = Lock()
total_tokens_used = 0


def get_cache_key(system_prompt: str, user_message: str) -> str:
    """生成缓存键"""
    content = f"{system_prompt}|{user_message}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_response(cache_key: str) -> Optional[str]:
    """获取缓存响应"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 缓存有效期24小时
                if time.time() - data.get("timestamp", 0) < 86400:
                    return data.get("response")
        except:
            pass
    return None


def save_cached_response(cache_key: str, response: str):
    """保存缓存响应"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "response": response,
                "timestamp": time.time()
            }, f, ensure_ascii=False)
    except:
        pass


def call_qianfan_single(system_prompt: str, user_message: str, 
                        agent_id: str = "", temperature: float = 0.7) -> Tuple[str, str]:
    """单个Agent调用API（带缓存）"""
    global total_tokens_used
    
    # 检查缓存
    cache_key = get_cache_key(system_prompt, user_message)
    cached = get_cached_response(cache_key)
    if cached:
        print(f"[{agent_id}] 命中缓存", flush=True)
        return cached, agent_id
    
    if not QIANFAN_API_KEY:
        return None, agent_id
    
    try:
        headers = {
            "Authorization": f"Bearer {QIANFAN_API_KEY}",
            "Content-Type": "application/json"
        }
        combined_message = f"{system_prompt}\n\n---\n\n{user_message}"
        payload = {
            "model": "qianfan-code-latest",
            "messages": [{"role": "user", "content": combined_message}],
            "temperature": temperature,
            "top_p": 0.9
        }
        
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        print(f"[{agent_id}] API耗时: {elapsed:.1f}秒", flush=True)
        
        result = response.json()
        
        # 统计token
        if 'usage' in result:
            with token_lock:
                total_tokens_used += result['usage'].get('total_tokens', 0)
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            # 保存缓存
            save_cached_response(cache_key, content)
            return content, agent_id
            
        return None, agent_id
        
    except Exception as e:
        print(f"[{agent_id}] API调用失败: {e}", flush=True)
        return None, agent_id


def call_agents_parallel(agents: List[Dict], task: str, memory_context: str = "") -> Dict[str, str]:
    """
    并行调用多个Agent
    
    Args:
        agents: Agent列表 [{"id": "caiwei", "system_prompt": "...", "role": "需求分析专家"}, ...]
        task: 任务描述
        memory_context: 对话上下文
    
    Returns:
        Dict[agent_id, response]
    """
    results = {}
    
    # 构建并行任务
    tasks = []
    for agent in agents:
        discussion_prompts = {
            '需求分析专家': '请从需求拆解、用户故事、验收标准角度分析',
            '项目经理': '请从进度计划、风险管控、里程碑角度分析',
            '架构设计师': '请从技术选型、架构方案、扩展性角度分析',
            '售前工程师': '请从成本估算、资源需求角度分析',
            '详细设计师': '请从接口设计、模块划分角度分析',
            '方案设计师': '请从UI设计、用户体验角度分析',
            '资源管家': '请从人员配置、技术资源角度分析',
            '总指挥': '请从整体平衡、决策建议角度分析'
        }
        
        role_prompt = discussion_prompts.get(agent.get('role', ''), '请发表专业意见')
        
        user_message = f"""当前任务：{task}

已有讨论：
{memory_context}

{role_prompt}。如果有不同意见请明确提出质疑。"""
        
        tasks.append({
            "agent_id": agent['id'],
            "system_prompt": agent.get('system_prompt', ''),
            "user_message": user_message
        })
    
    # 并行执行
    start_time = time.time()
    print(f"[并行调度] 启动 {len(tasks)} 个Agent并行响应...", flush=True)
    
    with ThreadPoolExecutor(max_workers=min(len(tasks), MAX_WORKERS)) as executor:
        futures = {
            executor.submit(
                call_qianfan_single, 
                t['system_prompt'], 
                t['user_message'],
                t['agent_id']
            ): t['agent_id'] 
            for t in tasks
        }
        
        for future in as_completed(futures):
            try:
                response, agent_id = future.result()
                if response:
                    results[agent_id] = response
            except Exception as e:
                print(f"[并行调度] 任务异常: {e}", flush=True)
    
    elapsed = time.time() - start_time
    print(f"[并行调度] 完成，总耗时: {elapsed:.1f}秒（串行约需{len(tasks)*20}秒）", flush=True)
    
    return results


def call_qianfan_stream(system_prompt: str, user_message: str, 
                        callback=None, agent_id: str = ""):
    """
    流式调用千帆API
    
    Args:
        system_prompt: 系统提示
        user_message: 用户消息
        callback: 每收到一段内容就调用的回调函数 callback(agent_id, chunk)
        agent_id: Agent标识
    """
    if not QIANFAN_API_KEY:
        if callback:
            callback(agent_id, "error: API Key未配置")
        return

    try:
        headers = {
            "Authorization": f"Bearer {QIANFAN_API_KEY}",
            "Content-Type": "application/json"
        }
        combined_message = f"{system_prompt}\n\n---\n\n{user_message}"
        payload = {
            "model": "qianfan-code-latest",
            "messages": [{"role": "user", "content": combined_message}],
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": True
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=60, stream=True)
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_str = line_text[6:]
                    if data_str.strip() and data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunk = delta['content']
                                    full_content += chunk
                                    if callback:
                                        callback(agent_id, chunk)
                        except json.JSONDecodeError:
                            continue
        
        return full_content

    except Exception as e:
        print(f"[{agent_id}] 流式调用失败: {e}")
        if callback:
            callback(agent_id, f"error: {e}")


# 测试
if __name__ == "__main__":
    test_agents = [
        {
            "id": "caiwei",
            "role": "需求分析专家",
            "system_prompt": "你是需求分析专家采薇，专注需求分析。"
        },
        {
            "id": "zhijin",
            "role": "架构设计师",
            "system_prompt": "你是架构设计师织锦，专注技术架构。"
        },
        {
            "id": "yuheng",
            "role": "项目经理",
            "system_prompt": "你是项目经理玉衡，专注项目管理。"
        }
    ]
    
    task = "设计一个用户登录系统"
    
    results = call_agents_parallel(test_agents, task)
    
    print("\n" + "="*50)
    print("并行调用结果：")
    for agent_id, response in results.items():
        print(f"\n[{agent_id}]: {response[:100]}...")
