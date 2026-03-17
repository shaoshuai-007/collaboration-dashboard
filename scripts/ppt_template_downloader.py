#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT模板自动下载器
使用Chromium headless + CDP协议自动下载PPT模板

Author: 南乔
Date: 2026-03-17
"""

import requests
import json
import time
import os
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

class PPTTemplateDownloader:
    """PPT模板自动下载器"""
    
    def __init__(self, cdp_port=9222, download_dir=None):
        self.cdp_url = f"http://localhost:{cdp_port}"
        self.download_dir = download_dir or "/root/.openclaw/workspace/02_工作台/PPT模板库/已下载"
        self.session = requests.Session()
        
        # 确保下载目录存在
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        
    def check_browser(self):
        """检查浏览器是否运行"""
        try:
            resp = self.session.get(f"{self.cdp_url}/json/version", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def create_page(self, url):
        """创建新页面"""
        try:
            resp = self.session.put(f"{self.cdp_url}/json/new?{url}", timeout=10)
            return resp.json()
        except Exception as e:
            print(f"❌ 创建页面失败: {e}")
            return None
    
    def get_pages(self):
        """获取所有页面"""
        try:
            resp = self.session.get(f"{self.cdp_url}/json/list", timeout=5)
            return resp.json()
        except:
            return []
    
    def close_page(self, page_id):
        """关闭页面"""
        try:
            self.session.get(f"{self.cdp_url}/json/close/{page_id}", timeout=5)
        except:
            pass
    
    def get_page_content(self, ws_url):
        """获取页面内容（通过WebSocket）"""
        # 这里简化处理，实际需要WebSocket连接
        # 暂时使用web_fetch方式
        pass
    
    def download_from_slidesgo(self, template_url, category="未分类"):
        """从Slidesgo下载模板"""
        print(f"\n🌐 访问: {template_url}")
        
        # 1. 创建页面
        page = self.create_page(template_url)
        if not page:
            return None
        
        page_id = page.get('id')
        
        # 2. 等待页面加载
        time.sleep(3)
        
        # 3. 获取页面信息
        try:
            # 使用web_fetch获取页面内容
            from web_fetch import fetch_page
            
            # 4. 尝试直接下载
            # Slidesgo的下载链接通常在页面上
            # 这里需要解析页面找到下载链接
            
            print(f"✅ 页面已加载")
            print(f"   标题: {page.get('title', 'N/A')}")
            
            # 5. 关闭页面
            if page_id:
                self.close_page(page_id)
            
            return {
                'status': 'loaded',
                'url': template_url,
                'title': page.get('title', 'Unknown')
            }
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            if page_id:
                self.close_page(page_id)
            return None
    
    def batch_download(self, urls, category="未分类"):
        """批量下载"""
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(urls)}] 处理: {url}")
            print(f"{'='*60}")
            
            result = self.download_from_slidesgo(url, category)
            results.append(result)
            
            # 避免请求过快
            time.sleep(2)
        
        return results
    
    def get_download_info(self, template_url):
        """获取模板下载信息（通过web_fetch）"""
        try:
            # 使用web_fetch工具
            import subprocess
            result = subprocess.run(
                ['curl', '-s', template_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            html = result.stdout
            
            # 解析下载链接
            # Slidesgo的下载按钮通常有特定的class或data属性
            
            # 查找下载链接
            download_patterns = [
                r'href="([^"]*download[^"]*)"',
                r'data-download="([^"]*)"',
                r'"downloadUrl":"([^"]*)"',
            ]
            
            for pattern in download_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    return matches[0] if matches else None
            
            return None
            
        except Exception as e:
            print(f"❌ 获取下载信息失败: {e}")
            return None


class SimplePPTDownloader:
    """简化版PPT下载器（使用web_fetch）"""
    
    def __init__(self, download_dir=None):
        self.download_dir = download_dir or "/root/.openclaw/workspace/02_工作台/PPT模板库/已下载"
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
    
    def download_template(self, url, filename=None):
        """下载模板文件"""
        try:
            print(f"📥 下载: {url}")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 从URL提取文件名
            if not filename:
                filename = url.split('/')[-1]
                if not filename.endswith('.pptx'):
                    filename += '.pptx'
            
            filepath = os.path.join(self.download_dir, filename)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ 保存成功: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return None
    
    def download_from_direct_link(self, url, filename=None):
        """从直接链接下载"""
        return self.download_template(url, filename)


def test_browser_connection():
    """测试浏览器连接"""
    print("=" * 60)
    print("测试浏览器连接")
    print("=" * 60)
    
    downloader = PPTTemplateDownloader()
    
    if downloader.check_browser():
        print("✅ 浏览器运行正常")
        
        # 获取版本信息
        resp = requests.get(f"{downloader.cdp_url}/json/version")
        version = resp.json()
        print(f"   浏览器: {version.get('Browser', 'Unknown')}")
        print(f"   协议版本: {version.get('Protocol-Version', 'Unknown')}")
        
        return True
    else:
        print("❌ 浏览器未运行")
        print("   请先启动: chromium --headless --remote-debugging-port=9222")
        return False


def test_page_creation():
    """测试页面创建"""
    print("\n" + "=" * 60)
    print("测试页面创建")
    print("=" * 60)
    
    downloader = PPTTemplateDownloader()
    
    test_url = "https://slidesgo.com/theme/minimalist-business-slides"
    page = downloader.create_page(test_url)
    
    if page:
        print(f"✅ 页面创建成功")
        print(f"   ID: {page.get('id', 'N/A')}")
        print(f"   URL: {page.get('url', 'N/A')}")
        print(f"   标题: {page.get('title', 'N/A')}")
        return True
    else:
        print("❌ 页面创建失败")
        return False


def demo_download_workflow():
    """演示下载流程"""
    print("\n" + "=" * 60)
    print("PPT模板自动下载演示")
    print("=" * 60)
    
    # 测试模板列表
    templates = [
        {
            'name': 'Minimalist Business Slides',
            'url': 'https://slidesgo.com/theme/minimalist-business-slides',
            'category': '简约风'
        },
        {
            'name': 'Tech Startup',
            'url': 'https://slidesgo.com/theme/tech-startup',
            'category': '科技风'
        },
        {
            'name': 'Data Charts',
            'url': 'https://slidesgo.com/theme/data-charts',
            'category': '数据风'
        }
    ]
    
    downloader = PPTTemplateDownloader()
    
    print(f"\n📋 待下载模板: {len(templates)} 份")
    
    for i, template in enumerate(templates, 1):
        print(f"\n[{i}/{len(templates)}] {template['name']}")
        result = downloader.download_from_slidesgo(
            template['url'], 
            template['category']
        )
        
        if result:
            print(f"   ✅ 处理成功")
        else:
            print(f"   ❌ 处理失败")


if __name__ == "__main__":
    print("🧭 PPT模板自动下载器")
    print("=" * 60)
    
    # 测试浏览器连接
    if test_browser_connection():
        # 测试页面创建
        test_page_creation()
        
        # 演示下载流程
        demo_download_workflow()
    else:
        print("\n❌ 请先启动浏览器:")
        print("   chromium --headless --no-sandbox --remote-debugging-port=9222")
