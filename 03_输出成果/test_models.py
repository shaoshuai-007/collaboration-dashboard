#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试百度千帆 Coding Plan 套餐 - 不同模型
"""

from openai import OpenAI
import traceback

API_KEY = "bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19"
BASE_URL = "https://qianfan.baidubce.com/v2"

# 尝试不同的模型名称
MODELS_TO_TRY = [
    "qwen-plus",
    "qwen-turbo", 
    "deepseek-v3",
    "deepseek-r1",
    "ernie-4.0-8k",
    "ernie-3.5-8k",
]

def test_models():
    print("=== 测试 Coding Plan 套餐可用模型 ===\n")
    
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    for model in MODELS_TO_TRY:
        print(f"测试模型: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "回复OK"}],
                max_tokens=10
            )
            print(f"  ✅ 成功！回复: {response.choices[0].message.content[:50]}")
            print()
        except Exception as e:
            error_msg = str(e)
            if "model_not_found" in error_msg or "does not exist" in error_msg:
                print(f"  ❌ 模型不存在")
            elif "not_allowed" in error_msg:
                print(f"  ❌ 不允许访问")
            else:
                print(f"  ❌ 错误: {error_msg[:100]}")
            print()

if __name__ == "__main__":
    test_models()
