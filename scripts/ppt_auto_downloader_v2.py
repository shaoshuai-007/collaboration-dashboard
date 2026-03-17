#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT模板自动下载器 V2
支持从多个平台自动下载PPT模板

Author: 南乔
Date: 2026-03-17
"""

import requests
import os
import time
import re
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

class PPTAutoDownloaderV2:
    """PPT模板自动下载器 V2"""
    
    def __init__(self, download_dir=None):
        self.download_dir = download_dir or "/root/.openclaw/workspace/02_工作台/PPT模板库/已下载"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 确保下载目录存在
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建分类目录
        categories = ['科技风', '商务风', '创意风', '数据风', '简约风', '学术风']
        for cat in categories:
            Path(os.path.join(self.download_dir, cat)).mkdir(exist_ok=True)
    
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"❌ 获取页面失败: {e}")
            return None
    
    def extract_download_link(self, html, base_url):
        """从HTML中提取下载链接"""
        download_links = []
        
        # 常见的下载链接模式
        patterns = [
            r'href="([^"]*\.pptx[^"]*)"',
            r'href="([^"]*download[^"]*\.pptx[^"]*)"',
            r'"downloadUrl"\s*:\s*"([^"]*)"',
            r'"file_url"\s*:\s*"([^"]*)"',
            r'data-url="([^"]*\.pptx[^"]*)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                # 转换为完整URL
                if not match.startswith('http'):
                    match = urljoin(base_url, match)
                download_links.append(match)
        
        # 去重
        download_links = list(set(download_links))
        
        return download_links
    
    def download_file(self, url, filepath):
        """下载文件"""
        try:
            print(f"  📥 下载中...")
            
            resp = self.session.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            
            # 获取文件大小
            total_size = int(resp.headers.get('content-length', 0))
            
            # 保存文件
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  📥 下载进度: {progress:.1f}%", end='')
            
            print(f"\n  ✅ 下载完成: {filepath}")
            print(f"  📦 大小: {downloaded / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"\n  ❌ 下载失败: {e}")
            return False
    
    def download_from_slidesgo(self, template_url, name, category="简约风"):
        """从Slidesgo下载模板（需要登录或Premium）"""
        print(f"\n{'='*60}")
        print(f"📋 模板: {name}")
        print(f"🏷️  分类: {category}")
        print(f"🔗 URL: {template_url}")
        print(f"{'='*60}")
        
        # Slidesgo通常需要注册或付费
        # 这里我们记录信息，实际下载可能需要手动
        
        print("  ⚠️  Slidesgo模板通常需要注册账户")
        print("  📝 建议手动下载或使用Premium账户")
        
        # 获取页面内容
        html = self.fetch_page(template_url)
        if html:
            # 提取下载链接（如果有）
            links = self.extract_download_link(html, template_url)
            if links:
                print(f"  ✅ 找到 {len(links)} 个下载链接")
                for link in links[:3]:
                    print(f"     - {link}")
            else:
                print("  ℹ️  未找到直接下载链接")
        
        return {
            'name': name,
            'url': template_url,
            'category': category,
            'status': 'manual_required',
            'message': '需要手动下载或注册账户'
        }
    
    def download_from_slidescarnival(self, template_url, name, category="简约风"):
        """从SlidesCarnival下载模板"""
        print(f"\n{'='*60}")
        print(f"📋 模板: {name}")
        print(f"🏷️  分类: {category}")
        print(f"🔗 URL: {template_url}")
        print(f"{'='*60}")
        
        # 获取页面内容
        html = self.fetch_page(template_url)
        if not html:
            return None
        
        # 查找PowerPoint下载链接
        # SlidesCarnival通常提供Google Slides和PowerPoint两种格式
        
        # 查找PowerPoint链接
        ppt_patterns = [
            r'href="([^"]*powerpoint[^"]*)"',
            r'href="([^"]*\.pptx[^"]*)"',
        ]
        
        for pattern in ppt_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                # 找到链接
                for match in matches:
                    if not match.startswith('http'):
                        match = urljoin(template_url, match)
                    
                    print(f"  ✅ 找到PowerPoint链接: {match}")
                    
                    # 尝试下载
                    filename = f"{category}_{name.replace(' ', '_')}.pptx"
                    filepath = os.path.join(self.download_dir, category, filename)
                    
                    if self.download_file(match, filepath):
                        return {
                            'name': name,
                            'url': template_url,
                            'category': category,
                            'status': 'success',
                            'filepath': filepath
                        }
        
        print("  ℹ️  SlidesCarnival需要通过Google Slides复制后导出")
        return {
            'name': name,
            'url': template_url,
            'category': category,
            'status': 'manual_required',
            'message': '需要通过Google Slides复制后导出'
        }
    
    def download_from_freepik(self, template_url, name, category="创意风"):
        """从Freepik下载模板"""
        print(f"\n{'='*60}")
        print(f"📋 模板: {name}")
        print(f"🏷️  分类: {category}")
        print(f"🔗 URL: {template_url}")
        print(f"{'='*60}")
        
        # Freepik需要注册
        print("  ⚠️  Freepik需要注册账户才能下载")
        
        return {
            'name': name,
            'url': template_url,
            'category': category,
            'status': 'manual_required',
            'message': '需要注册Freepik账户'
        }
    
    def batch_download(self, template_list):
        """批量下载模板"""
        results = []
        
        print(f"\n🚀 开始批量下载")
        print(f"📋 模板数量: {len(template_list)}")
        
        for i, template in enumerate(template_list, 1):
            print(f"\n[{i}/{len(template_list)}]")
            
            platform = template.get('platform', 'slidesgo')
            name = template.get('name', 'Unknown')
            url = template.get('url', '')
            category = template.get('category', '简约风')
            
            if platform == 'slidesgo':
                result = self.download_from_slidesgo(url, name, category)
            elif platform == 'slidescarnival':
                result = self.download_from_slidescarnival(url, name, category)
            elif platform == 'freepik':
                result = self.download_from_freepik(url, name, category)
            else:
                result = {
                    'name': name,
                    'url': url,
                    'status': 'unknown_platform'
                }
            
            results.append(result)
            
            # 避免请求过快
            time.sleep(2)
        
        # 统计结果
        success_count = sum(1 for r in results if r and r.get('status') == 'success')
        manual_count = sum(1 for r in results if r and r.get('status') == 'manual_required')
        
        print(f"\n{'='*60}")
        print(f"📊 下载统计")
        print(f"{'='*60}")
        print(f"✅ 自动下载成功: {success_count}")
        print(f"📝 需要手动下载: {manual_count}")
        print(f"❌ 下载失败: {len(results) - success_count - manual_count}")
        
        return results
    
    def generate_download_report(self, results):
        """生成下载报告"""
        report_path = os.path.join(self.download_dir, "下载报告.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# PPT模板下载报告\n\n")
            f.write(f"下载时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"总计: {len(results)} 份模板\n\n")
            
            # 按状态分类
            success = [r for r in results if r and r.get('status') == 'success']
            manual = [r for r in results if r and r.get('status') == 'manual_required']
            
            f.write("## ✅ 自动下载成功\n\n")
            for r in success:
                f.write(f"- [{r['name']}]({r['url']}) - {r['category']}\n")
            
            f.write("\n## 📝 需要手动下载\n\n")
            for r in manual:
                f.write(f"- [{r['name']}]({r['url']}) - {r['category']}\n")
                if r.get('message'):
                    f.write(f"  - {r['message']}\n")
        
        print(f"\n📄 下载报告已保存: {report_path}")
        return report_path


def main():
    """主函数"""
    print("🧭 PPT模板自动下载器 V2")
    print("=" * 60)
    
    # 创建下载器
    downloader = PPTAutoDownloaderV2()
    
    # 测试模板列表
    templates = [
        {
            'name': 'Minimalist Business Slides',
            'url': 'https://slidesgo.com/theme/minimalist-business-slides',
            'category': '简约风',
            'platform': 'slidesgo'
        },
        {
            'name': 'Tech Startup',
            'url': 'https://slidesgo.com/theme/tech-startup',
            'category': '科技风',
            'platform': 'slidesgo'
        },
        {
            'name': 'Data Charts',
            'url': 'https://slidesgo.com/theme/data-charts',
            'category': '数据风',
            'platform': 'slidesgo'
        }
    ]
    
    # 批量下载
    results = downloader.batch_download(templates)
    
    # 生成报告
    downloader.generate_download_report(results)
    
    print("\n✅ 下载流程完成！")


if __name__ == "__main__":
    main()
