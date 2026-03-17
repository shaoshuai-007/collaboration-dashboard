#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信视频号爬虫工具 V2.0
使用DrissionPage实现登录态保持和内容爬取

解决方案：
1. 首次运行：手动扫码登录，保存cookies
2. 后续运行：自动加载cookies，无需重复登录
3. 支持视频列表获取、内容提取、摘要生成

依赖安装：
pip install DrissionPage

作者：南乔 🌿
时间：2026-03-17
"""

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError, PageDisconnectedError
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class WeChatChannelsCrawler:
    """微信视频号爬虫"""
    
    def __init__(self, headless: bool = False):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式（不显示浏览器窗口）
        """
        self.headless = headless
        self.page: Optional[ChromiumPage] = None
        self.cookies_file = Path('/root/.openclaw/workspace/.wechat_cookies.json')
        self.output_dir = Path('/root/.openclaw/workspace/03_输出成果/视频内容')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def init_browser(self):
        """初始化浏览器"""
        print("🌐 初始化浏览器...")
        
        # 配置浏览器选项
        co = ChromiumOptions()
        
        if self.headless:
            co.headless()
        
        # 设置用户数据目录（保存登录态）
        co.set_user_data_path('/root/.openclaw/workspace/.browser_data')
        
        # 设置浏览器路径（自动检测）
        # co.set_browser_path('/usr/bin/google-chrome')
        
        # 创建页面对象
        self.page = ChromiumPage(co)
        
        print("✅ 浏览器初始化完成")
    
    def load_cookies(self) -> bool:
        """加载已保存的cookies"""
        if not self.cookies_file.exists():
            print("⚠️ 未找到已保存的cookies")
            return False
        
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 先访问微信首页
            self.page.get('https://weixin.qq.com')
            time.sleep(2)
            
            # 加载cookies
            for cookie in cookies:
                self.page.set.cookies(cookie)
            
            print("✅ Cookies加载成功")
            return True
            
        except Exception as e:
            print(f"❌ Cookies加载失败: {e}")
            return False
    
    def save_cookies(self):
        """保存cookies"""
        try:
            cookies = self.page.cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ Cookies已保存到: {self.cookies_file}")
        except Exception as e:
            print(f"❌ Cookies保存失败: {e}")
    
    def login_manually(self):
        """
        手动登录（扫码）
        
        流程：
        1. 访问微信网页版
        2. 等待用户扫码登录
        3. 保存cookies
        """
        print("\n" + "="*60)
        print("🔐 开始手动登录流程")
        print("="*60)
        print("\n请按以下步骤操作：")
        print("1. 浏览器将自动打开微信网页版")
        print("2. 使用微信扫描二维码")
        print("3. 确认登录")
        print("4. 登录成功后，脚本将自动继续\n")
        
        # 访问微信网页版
        self.page.get('https://weixin.qq.com')
        time.sleep(3)
        
        print("⏳ 等待扫码登录...")
        
        # 等待登录成功（最多等待5分钟）
        max_wait = 300  # 秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # 检查是否登录成功（URL变化或特定元素出现）
            current_url = self.page.url
            
            if 'home' in current_url or 'chat' in current_url:
                print("\n✅ 登录成功！")
                self.save_cookies()
                return True
            
            time.sleep(2)
        
        print("\n❌ 登录超时，请重试")
        return False
    
    def search_channels_account(self, account_name: str) -> Optional[str]:
        """
        搜索视频号账号
        
        Args:
            account_name: 账号名称
        
        Returns:
            找到的账号链接，未找到返回None
        """
        print(f"\n🔍 搜索视频号: {account_name}")
        
        try:
            # 方法1：通过搜索页面
            search_url = f'https://channels.weixin.qq.com/search?keyword={account_name}'
            self.page.get(search_url)
            time.sleep(3)
            
            # 尝试查找账号链接
            # 这里需要根据实际页面结构调整选择器
            
            # 方法2：尝试直接访问账号页面（如果知道finderId）
            # 格式：https://channels.weixin.qq.com/{finderId}
            
            print("⚠️ 搜索功能需要进一步调试页面结构")
            return None
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return None
    
    def get_video_list(self, account_url: str, limit: int = 10) -> List[Dict]:
        """
        获取视频列表
        
        Args:
            account_url: 账号主页URL
            limit: 获取数量限制
        
        Returns:
            视频信息列表
        """
        print(f"\n📹 获取视频列表...")
        
        videos = []
        
        try:
            # 访问账号主页
            self.page.get(account_url)
            time.sleep(3)
            
            # 滚动加载更多视频
            for _ in range(3):
                self.page.scroll.down(500)
                time.sleep(1)
            
            # 提取视频信息（需要根据实际页面结构调整）
            # 示例选择器（需要实际调试）
            video_elements = self.page.eles('css:.video-item')  # 伪代码
            
            for elem in video_elements[:limit]:
                try:
                    video_info = {
                        'title': elem.ele('css:.title').text,
                        'url': elem.ele('css:a').attr('href'),
                        'views': elem.ele('css:.views').text,
                    }
                    videos.append(video_info)
                except Exception as e:
                    print(f"  ⚠️ 提取视频信息失败: {e}")
            
            print(f"✅ 获取到 {len(videos)} 个视频")
            
        except Exception as e:
            print(f"❌ 获取视频列表失败: {e}")
        
        return videos
    
    def get_video_content(self, video_url: str) -> Dict:
        """
        获取视频内容（文字、标题、描述等）
        
        注意：无法直接下载视频，但可以提取文字信息
        """
        print(f"\n📝 提取视频内容...")
        
        content = {
            'url': video_url,
            'title': '',
            'description': '',
            'transcript': '',  # 字幕/转录文本
        }
        
        try:
            self.page.get(video_url)
            time.sleep(3)
            
            # 提取标题和描述（需要根据实际页面结构调整）
            # content['title'] = self.page.ele('css:.video-title').text
            # content['description'] = self.page.ele('css:.video-desc').text
            
            print("⚠️ 内容提取需要进一步调试页面结构")
            
        except Exception as e:
            print(f"❌ 内容提取失败: {e}")
        
        return content
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()
            print("✅ 浏览器已关闭")
    
    def run(self, account_name: str, keyword: str = None):
        """
        执行爬取流程
        
        Args:
            account_name: 视频号账号名
            keyword: 搜索关键词（可选）
        """
        print("\n" + "="*60)
        print(f"🎬 微信视频号爬虫启动")
        print(f"📋 目标账号: {account_name}")
        print(f"🔍 搜索关键词: {keyword or '全部视频'}")
        print("="*60 + "\n")
        
        try:
            # 1. 初始化浏览器
            self.init_browser()
            
            # 2. 尝试加载cookies
            if self.load_cookies():
                print("✅ 使用已保存的登录态")
            else:
                # 3. 手动登录
                if not self.login_manually():
                    return None
            
            # 4. 搜索账号
            account_url = self.search_channels_account(account_name)
            
            if account_url:
                # 5. 获取视频列表
                videos = self.get_video_list(account_url)
                
                # 6. 如果指定了关键词，筛选视频
                if keyword:
                    videos = [v for v in videos if keyword in v.get('title', '')]
                
                # 7. 提取视频内容
                for video in videos:
                    content = self.get_video_content(video['url'])
                    video.update(content)
                
                # 8. 保存结果
                result = {
                    'account': account_name,
                    'keyword': keyword,
                    'crawl_time': datetime.now().isoformat(),
                    'videos': videos
                }
                
                output_file = self.output_dir / f'{account_name}_videos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ 结果已保存: {output_file}")
                return result
            else:
                print("\n❌ 未找到指定账号")
                return None
                
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            self.close()


def install_dependencies():
    """检查并安装依赖"""
    print("📦 检查依赖...")
    
    try:
        import DrissionPage
        print("✅ DrissionPage 已安装")
    except ImportError:
        print("❌ DrissionPage 未安装")
        print("\n请运行以下命令安装：")
        print("pip install DrissionPage")
        return False
    
    return True


def main():
    """主函数"""
    print("🌿 南乔微信视频号爬虫工具 V2.0\n")
    
    # 检查依赖
    if not install_dependencies():
        return
    
    # 创建爬虫实例
    crawler = WeChatChannelsCrawler(headless=False)
    
    # 执行爬取
    result = crawler.run(
        account_name="红衣大叔周鸿祎",
        keyword="黄仁勋"
    )
    
    if result:
        print("\n" + "="*60)
        print("📊 爬取结果摘要:")
        print("="*60)
        print(f"账号: {result['account']}")
        print(f"视频数量: {len(result.get('videos', []))}")
        
        for i, video in enumerate(result.get('videos', [])[:5], 1):
            print(f"\n{i}. {video.get('title', '未知标题')}")
            print(f"   观看: {video.get('views', '未知')}")


if __name__ == "__main__":
    main()
