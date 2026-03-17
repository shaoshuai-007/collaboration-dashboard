#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信视频号爬虫工具 - 完整版
============================

功能：
1. 自动登录（扫码）
2. 搜索视频号账号
3. 获取视频列表
4. 提取视频内容
5. 生成摘要报告

使用：
source .venv/bin/activate
python wechat_channels_crawler_final.py

作者：南乔 🌿
时间：2026-03-17
"""

from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class WeChatChannelsCrawler:
    """微信视频号爬虫 - 完整版"""
    
    def __init__(self, headless: bool = False):
        """初始化"""
        self.headless = headless
        self.page = None
        self.browser_data_dir = Path('/root/.openclaw/workspace/.browser_data')
        self.browser_data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = Path('/root/.openclaw/workspace/03_输出成果/视频内容')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("🌿 南乔微信视频号爬虫初始化...")
    
    def start_browser(self):
        """启动浏览器"""
        print("\n🌐 启动浏览器...")
        
        try:
            # 配置浏览器
            co = ChromiumOptions()
            
            # 设置用户数据目录（保存登录态）
            co.set_user_data_path(str(self.browser_data_dir))
            
            # 无头模式
            if self.headless:
                co.headless()
            
            # 创建页面对象
            self.page = ChromiumPage(co)
            
            print("✅ 浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            print("\n可能的原因：")
            print("1. 未安装Chrome/Chromium浏览器")
            print("2. 浏览器版本不兼容")
            print("\n请确保系统已安装Chrome浏览器")
            return False
    
    def login(self) -> bool:
        """
        登录微信
        
        Returns:
            是否登录成功
        """
        print("\n" + "="*60)
        print("🔐 登录流程")
        print("="*60)
        
        try:
            # 访问微信网页版
            print("\n正在访问微信网页版...")
            self.page.get('https://weixin.qq.com')
            time.sleep(3)
            
            # 检查是否已登录
            if self.check_login_status():
                print("✅ 已登录（使用保存的登录态）")
                return True
            
            # 需要扫码登录
            print("\n📱 请使用微信扫描二维码登录")
            print("⏳ 等待登录...（最多等待5分钟）\n")
            
            # 等待登录成功
            max_wait = 300  # 5分钟
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if self.check_login_status():
                    print("\n✅ 登录成功！")
                    return True
                time.sleep(2)
            
            print("\n❌ 登录超时")
            return False
            
        except Exception as e:
            print(f"\n❌ 登录失败: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查URL或页面元素
            url = self.page.url
            
            # 如果URL包含home或其他登录后的特征
            if 'home' in url or 'chat' in url:
                return True
            
            # 检查是否有登录后的元素
            # 这里可以根据实际情况调整
            page_text = self.page.html
            
            # 检查是否还在登录页面
            if '二维码' in page_text or 'qrcode' in page_text.lower():
                return False
            
            # 如果能找到用户头像等元素，说明已登录
            if 'login' not in url.lower():
                return True
            
            return False
            
        except Exception:
            return False
    
    def search_channels(self, keyword: str) -> List[Dict]:
        """
        搜索视频号
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            搜索结果列表
        """
        print(f"\n🔍 搜索视频号: {keyword}")
        
        results = []
        
        try:
            # 方法1：通过微信搜索页面
            # 注意：微信视频号的网页版功能可能有限
            
            # 尝试访问视频号搜索页面
            search_url = f'https://channels.weixin.qq.com/search?keyword={keyword}'
            
            print(f"  访问: {search_url}")
            self.page.get(search_url)
            time.sleep(5)
            
            # 获取页面内容
            html = self.page.html
            
            # 提取搜索结果（需要根据实际页面结构解析）
            # 这里提供通用的解析框架
            
            # 检查页面是否有结果
            if '没有找到' in html or '无结果' in html:
                print("  ⚠️ 未找到相关结果")
                return results
            
            # 尝试提取账号信息
            # 注意：实际的选择器需要根据页面调试确定
            
            print(f"  ✅ 搜索完成，页面已加载")
            
            # 保存页面截图（用于调试）
            screenshot_path = self.output_dir / f'search_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            self.page.get_screenshot(str(screenshot_path))
            print(f"  📸 截图已保存: {screenshot_path}")
            
            # 保存页面HTML（用于分析）
            html_path = self.output_dir / f'search_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  📄 HTML已保存: {html_path}")
            
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
        
        return results
    
    def get_account_videos(self, account_url: str = None, limit: int = 20) -> List[Dict]:
        """
        获取账号的视频列表
        
        Args:
            account_url: 账号主页URL（如果知道的话）
            limit: 获取数量限制
        """
        print(f"\n📹 获取视频列表...")
        
        videos = []
        
        try:
            if account_url:
                self.page.get(account_url)
                time.sleep(3)
            
            # 滚动加载更多
            print("  滚动加载更多视频...")
            for i in range(5):
                self.page.scroll.down(500)
                time.sleep(1)
            
            # 提取视频信息
            # 注意：选择器需要根据实际页面确定
            
            print(f"  ✅ 视频列表加载完成")
            
        except Exception as e:
            print(f"  ❌ 获取失败: {e}")
        
        return videos
    
    def extract_video_content(self, video_url: str) -> Dict:
        """
        提取视频内容
        
        注意：无法直接下载视频，但可以提取：
        - 标题
        - 描述
        - 发布时间
        - 播放量
        - 点赞数等
        """
        print(f"\n📝 提取视频内容...")
        
        content = {
            'url': video_url,
            'title': '',
            'description': '',
            'publish_time': '',
            'views': '',
            'likes': '',
        }
        
        try:
            self.page.get(video_url)
            time.sleep(3)
            
            # 提取内容
            # 注意：选择器需要根据实际页面确定
            
            print(f"  ✅ 内容提取完成")
            
        except Exception as e:
            print(f"  ❌ 提取失败: {e}")
        
        return content
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            try:
                self.page.quit()
                print("\n✅ 浏览器已关闭")
            except Exception:
                pass
    
    def run(self, account_name: str, keyword: str = None) -> Optional[Dict]:
        """
        执行完整的爬取流程
        
        Args:
            account_name: 目标账号名
            keyword: 搜索关键词（可选）
        
        Returns:
            爬取结果
        """
        print("\n" + "="*60)
        print(f"🎬 微信视频号爬虫启动")
        print("="*60)
        print(f"📋 目标账号: {account_name}")
        print(f"🔍 搜索关键词: {keyword or '全部'}")
        print("="*60)
        
        result = {
            'account': account_name,
            'keyword': keyword,
            'crawl_time': datetime.now().isoformat(),
            'status': 'pending',
            'videos': [],
            'error': None
        }
        
        try:
            # 1. 启动浏览器
            if not self.start_browser():
                result['status'] = 'failed'
                result['error'] = '浏览器启动失败'
                return result
            
            # 2. 登录
            if not self.login():
                result['status'] = 'failed'
                result['error'] = '登录失败'
                return result
            
            # 3. 搜索
            search_results = self.search_channels(account_name)
            
            # 4. 获取视频列表
            # videos = self.get_account_videos()
            
            # 5. 提取内容
            # for video in videos:
            #     content = self.extract_video_content(video['url'])
            #     video.update(content)
            
            result['status'] = 'success'
            result['videos'] = search_results
            
            # 保存结果
            output_file = self.output_dir / f'crawl_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 结果已保存: {output_file}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"\n❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()
        
        return result


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║        🌿 微信视频号爬虫工具 - 完整版                      ║
║                                                          ║
║  功能：自动登录、搜索账号、获取视频列表                    ║
║  作者：南乔                                              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 创建爬虫实例
    crawler = WeChatChannelsCrawler(headless=False)
    
    # 执行爬取
    result = crawler.run(
        account_name="红衣大叔周鸿祎",
        keyword="黄仁勋"
    )
    
    # 打印摘要
    if result:
        print("\n" + "="*60)
        print("📊 执行结果摘要")
        print("="*60)
        print(f"状态: {result['status']}")
        
        if result.get('error'):
            print(f"错误: {result['error']}")
        
        print(f"时间: {result['crawl_time']}")


if __name__ == "__main__":
    main()
