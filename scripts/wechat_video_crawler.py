#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信视频号爬虫脚本
目标：获取"红衣大叔周鸿祎"的最新视频内容

注意：微信视频号需要登录，此脚本提供多种方法尝试
"""

import requests
import json
import re
import time
from datetime import datetime
from pathlib import Path

class WeChatVideoCrawler:
    """微信视频号爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.output_dir = Path('/root/.openclaw/workspace/03_输出成果/视频内容')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def method1_search_engine(self, keyword: str) -> dict:
        """
        方法1：通过搜索引擎搜索视频信息
        使用公开的搜索引擎API或网页搜索
        """
        print(f"🔍 方法1：搜索引擎搜索 '{keyword}'")
        
        results = {
            'method': 'search_engine',
            'keyword': keyword,
            'videos': [],
            'status': 'pending'
        }
        
        try:
            # 尝试通过Bing搜索
            search_url = f"https://www.bing.com/search?q={keyword}+微信视频号"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                # 提取搜索结果中的链接
                # 这里只是示例，实际需要解析HTML
                results['status'] = 'success'
                results['note'] = '搜索成功，但需要手动解析结果'
            else:
                results['status'] = 'failed'
                results['error'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def method2_bilibili_api(self, uploader: str) -> dict:
        """
        方法2：通过B站API搜索（很多视频号内容会同步到B站）
        """
        print(f"📺 方法2：B站搜索 '{uploader}'")
        
        results = {
            'method': 'bilibili',
            'uploader': uploader,
            'videos': [],
            'status': 'pending'
        }
        
        try:
            # B站搜索API
            search_url = f"https://api.bilibili.com/x/web-interface/search/type"
            params = {
                'keyword': f'{uploader} 黄仁勋',
                'search_type': 'video',
                'page': 1,
                'page_size': 10
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    results['status'] = 'success'
                    results['videos'] = data.get('data', {}).get('result', [])[:5]
                else:
                    results['status'] = 'failed'
                    results['error'] = data.get('message', 'Unknown error')
            else:
                results['status'] = 'failed'
                results['error'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def method3_weibo_api(self, user: str) -> dict:
        """
        方法3：通过微博搜索（周鸿祎有微博账号）
        """
        print(f"📱 方法3：微博搜索 '{user}'")
        
        results = {
            'method': 'weibo',
            'user': user,
            'posts': [],
            'status': 'pending'
        }
        
        try:
            # 微博搜索页面
            search_url = f"https://s.weibo.com/weibo/{user}%20黄仁勋"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                results['status'] = 'success'
                results['note'] = '搜索成功，但需要登录才能获取完整内容'
            else:
                results['status'] = 'failed'
                results['error'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def method4_tech_news_sites(self, topic: str) -> dict:
        """
        方法4：从科技新闻网站获取相关内容
        """
        print(f"📰 方法4：科技新闻网站搜索 '{topic}'")
        
        results = {
            'method': 'tech_news',
            'topic': topic,
            'articles': [],
            'status': 'pending'
        }
        
        sites = [
            {'name': '虎嗅', 'url': f'https://www.huxiu.com/search?s={topic}'},
            {'name': '36氪', 'url': f'https://36kr.com/search/articles/{topic}'},
            {'name': '钛媒体', 'url': f'https://www.tmtpost.com/search?q={topic}'},
        ]
        
        for site in sites:
            try:
                response = self.session.get(site['url'], timeout=10)
                if response.status_code == 200:
                    results['articles'].append({
                        'site': site['name'],
                        'url': site['url'],
                        'status': 'success',
                        'content_length': len(response.text)
                    })
            except Exception as e:
                results['articles'].append({
                    'site': site['name'],
                    'url': site['url'],
                    'status': 'error',
                    'error': str(e)
                })
        
        results['status'] = 'success' if results['articles'] else 'failed'
        return results
    
    def method5_selenium_browser(self, url: str) -> dict:
        """
        方法5：使用Selenium模拟浏览器（需要安装Chrome/Firefox）
        """
        print(f"🌐 方法5：Selenium浏览器模拟")
        
        results = {
            'method': 'selenium',
            'url': url,
            'status': 'pending',
            'note': '需要安装selenium和浏览器驱动'
        }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # 创建浏览器实例
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 获取页面内容
            page_content = driver.page_source
            driver.quit()
            
            results['status'] = 'success'
            results['content_length'] = len(page_content)
            
        except ImportError:
            results['status'] = 'error'
            results['error'] = '未安装selenium，请运行: pip install selenium'
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def crawl_wechat_video(self, account_name: str, keyword: str) -> dict:
        """
        主爬取方法：尝试多种方法获取视频内容
        
        Args:
            account_name: 视频号账号名（如"红衣大叔周鸿祎"）
            keyword: 搜索关键词（如"黄仁勋CES预言"）
        
        Returns:
            包含所有方法结果的字典
        """
        print(f"\n{'='*60}")
        print(f"🎬 开始爬取微信视频号: {account_name}")
        print(f"🔍 搜索关键词: {keyword}")
        print(f"{'='*60}\n")
        
        all_results = {
            'account': account_name,
            'keyword': keyword,
            'crawl_time': datetime.now().isoformat(),
            'methods': {}
        }
        
        # 方法1：搜索引擎
        all_results['methods']['search_engine'] = self.method1_search_engine(
            f"{account_name} {keyword}"
        )
        
        # 方法2：B站API
        all_results['methods']['bilibili'] = self.method2_bilibili_api(account_name)
        
        # 方法3：微博
        all_results['methods']['weibo'] = self.method3_weibo_api(account_name)
        
        # 方法4：科技新闻网站
        all_results['methods']['tech_news'] = self.method4_tech_news_sites(keyword)
        
        # 方法5：Selenium（可选）
        # all_results['methods']['selenium'] = self.method5_selenium_browser(
        #     'https://weixin.qq.com'
        # )
        
        return all_results
    
    def save_results(self, results: dict, filename: str = None) -> str:
        """保存结果到文件"""
        if filename is None:
            filename = f"crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结果已保存到: {filepath}")
        return str(filepath)


def main():
    """主函数"""
    print("🌿 南乔微信视频号爬虫启动！")
    print("目标：红衣大叔周鸿祎 - 黄仁勋CES预言\n")
    
    # 创建爬虫实例
    crawler = WeChatVideoCrawler()
    
    # 执行爬取
    results = crawler.crawl_wechat_video(
        account_name="红衣大叔周鸿祎",
        keyword="黄仁勋CES预言"
    )
    
    # 保存结果
    filepath = crawler.save_results(results)
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 爬取结果摘要:")
    print("="*60)
    
    for method, result in results['methods'].items():
        status_emoji = "✅" if result.get('status') == 'success' else "❌"
        print(f"{status_emoji} {method}: {result.get('status', 'unknown')}")
        if 'error' in result:
            print(f"   错误: {result['error']}")
        if 'note' in result:
            print(f"   备注: {result['note']}")
    
    print(f"\n详细结果请查看: {filepath}")
    
    return results


if __name__ == "__main__":
    main()
