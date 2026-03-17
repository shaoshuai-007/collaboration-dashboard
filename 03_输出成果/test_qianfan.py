#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试百度千帆 Coding Plan 套餐连通性
"""

from openai import OpenAI
import traceback

# 用户提供的API Key
API_KEY = "bce-v3/ALTAKSP-14YyizFlbkiA0cKHpR4ya/b2b8db94725048693a15c4479c980c848a6a4c19"
BASE_URL = "https://qianfan.baidubce.com/v2"
TEST_MODEL = "qwen-plus"

def test_connection():
    """测试连通性"""
    print("=== 开始验证 Coding Plan 套餐连通性 ===")
    
    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        print("✅ 客户端初始化成功")
        
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[
                {"role": "system", "content": "你是产品经理，立场是成本优先"},
                {"role": "user", "content": "开发一个用户数据管理系统，建议采用微服务架构，成本20万"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        print("✅ LLM调用成功！")
        print("📝 测试回复：")
        print(response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ 调用失败：{str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    print("\n" + "🎉 验证通过！" if success else "❌ 验证失败")
