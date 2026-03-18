#!/usr/bin/env python3
"""HTML转PNG截图工具"""
import subprocess
import os
import sys

html_path = sys.argv[1] if len(sys.argv) > 1 else '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.html'
output_path = sys.argv[2] if len(sys.argv) > 2 else '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.png'

# 使用headless chrome截图
chrome_paths = [
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
]

chrome = None
for path in chrome_paths:
    if os.path.exists(path):
        chrome = path
        break

if not chrome:
    print("未找到Chrome浏览器")
    sys.exit(1)

# 转换为file:// URL
if not html_path.startswith('file://'):
    html_url = f'file://{html_path}'
else:
    html_url = html_path

cmd = [
    chrome,
    '--headless',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--window-size=1600,1200',
    '--screenshot=' + output_path,
    html_url
]

print(f"正在截图: {html_url}")
result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(output_path):
    print(f"截图成功: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path)} bytes")
else:
    print(f"截图失败: {result.stderr}")
    sys.exit(1)
