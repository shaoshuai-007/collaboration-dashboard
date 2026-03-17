#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新版千帆API - qianfan-code-latest
"""

import requests
import json

API_KEY = "bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19"
URL = "https://qianfan.baidubce.com/v2/coding/chat/completions"

def test_api():
    print("=== 测试 qianfan-code-latest 模型 ===\n")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qianfan-code-latest",
        "messages": [{"role": "user", "content": "你好，请回复OK"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if 'choices' in result:
            print(f"\n✅ 成功！回复: {result['choices'][0]['message']['content']}")
        else:
            print(f"\n❌ 响应格式异常")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_api()
