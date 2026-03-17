#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试百度千帆 Coding Plan - 标准API endpoint
"""

import requests
import json

API_KEY = "bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19"

# 不同的endpoint
ENDPOINTS = [
    # OpenAI兼容 - v2
    ("https://qianfan.baidubce.com/v2/chat/completions", "qwen-plus"),
    # 标准千帆API
    ("https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro", None),
    ("https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k", None),
    # Coding Plan专用
    ("https://qianfan.baidubce.com/v2/chat/completions", "deepseek-v3"),
]

def test_endpoints():
    print("=== 测试不同API endpoint ===\n")
    
    for url, model in ENDPOINTS:
        print(f"测试: {url}")
        if model:
            print(f"  模型: {model}")
        
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            if model:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "回复OK"}],
                    "max_tokens": 10
                }
            else:
                # 标准千帆格式
                payload = {
                    "messages": [{"role": "user", "content": "回复OK"}]
                }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            result = response.json()
            
            if 'choices' in result:
                print(f"  ✅ 成功！回复: {result['choices'][0]['message']['content'][:50]}")
            elif 'result' in result:
                print(f"  ✅ 成功！回复: {result['result'][:50]}")
            else:
                print(f"  ❌ 响应: {json.dumps(result, ensure_ascii=False)[:150]}")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:100]}")
        print()

if __name__ == "__main__":
    test_endpoints()
