#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄仁勋CES/GTC内容提取器
从多个科技新闻网站提取黄仁勋相关演讲内容
"""

import requests
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

class ContentExtractor:
    """内容提取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.output_dir = Path('/root/.openclaw/workspace/03_输出成果/视频内容')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_article_links(self, html: str, base_url: str) -> list:
        """从HTML中提取文章链接"""
        links = []
        # 匹配文章链接模式
        patterns = [
            r'href="(/article/\d+\.html)"',
            r'href="(/p/\d+\.html)"',
            r'href="(/news/\d+\.html)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches[:5]:  # 限制数量
                full_url = urljoin(base_url, match)
                if full_url not in links:
                    links.append(full_url)
        
        return links
    
    def fetch_article(self, url: str) -> dict:
        """获取文章内容"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                # 提取标题
                title_match = re.search(r'<title>([^<]+)</title>', response.text)
                title = title_match.group(1) if title_match else 'Unknown'
                
                # 提取正文（简单提取）
                # 移除script和style标签
                text = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                
                # 提取关键段落（包含黄仁勋、英伟达等关键词）
                paragraphs = []
                sentences = text.split('。')
                keywords = ['黄仁勋', '英伟达', 'NVIDIA', 'GPU', 'AI', '芯片', 'CES', 'GTC']
                
                for sentence in sentences:
                    if any(kw in sentence for kw in keywords):
                        paragraphs.append(sentence.strip() + '。')
                
                return {
                    'url': url,
                    'title': title,
                    'status': 'success',
                    'key_paragraphs': paragraphs[:20],  # 限制段落数
                    'content_length': len(text)
                }
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
        
        return {'url': url, 'status': 'failed'}
    
    def extract_from_huxiu(self) -> list:
        """从虎嗅提取文章"""
        print("📰 从虎嗅提取文章...")
        
        articles = []
        try:
            # 搜索黄仁勋相关文章
            search_urls = [
                'https://www.huxiu.com/article/4842734.html',  # 之前获取到的英伟达文章
            ]
            
            for url in search_urls:
                result = self.fetch_article(url)
                if result.get('status') == 'success':
                    articles.append(result)
                    print(f"  ✅ {result['title'][:50]}...")
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        return articles
    
    def extract_from_36kr(self) -> list:
        """从36氪提取文章"""
        print("📰 从36氪提取文章...")
        
        articles = []
        try:
            # 访问搜索页面
            response = self.session.get(
                'https://36kr.com/search/articles/黄仁勋CES',
                timeout=15
            )
            
            if response.status_code == 200:
                links = self.extract_article_links(response.text, 'https://36kr.com')
                print(f"  找到 {len(links)} 篇文章")
                
                for url in links[:3]:  # 限制数量
                    result = self.fetch_article(url)
                    if result.get('status') == 'success':
                        articles.append(result)
                        print(f"  ✅ {result['title'][:50]}...")
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        return articles
    
    def generate_summary(self, articles: list) -> dict:
        """生成内容摘要"""
        summary = {
            'title': '黄仁勋演讲内容汇总',
            'extract_time': datetime.now().isoformat(),
            'source_count': len(articles),
            'key_points': [],
            'full_content': []
        }
        
        # 汇总关键点
        all_paragraphs = []
        for article in articles:
            if article.get('key_paragraphs'):
                all_paragraphs.extend(article['key_paragraphs'])
        
        # 去重并提取关键点
        seen = set()
        for p in all_paragraphs:
            if p not in seen and len(p) > 50:
                seen.add(p)
                summary['full_content'].append(p)
                
                # 提取关键信息（短句）
                if len(p) < 200:
                    summary['key_points'].append(p)
        
        return summary
    
    def run(self) -> dict:
        """执行提取"""
        print("\n" + "="*60)
        print("🎬 黄仁勋内容提取器启动")
        print("="*60 + "\n")
        
        all_articles = []
        
        # 从各个网站提取
        all_articles.extend(self.extract_from_huxiu())
        all_articles.extend(self.extract_from_36kr())
        
        # 生成摘要
        summary = self.generate_summary(all_articles)
        
        # 保存结果
        result = {
            'articles': all_articles,
            'summary': summary
        }
        
        # 保存JSON
        json_path = self.output_dir / 'huang_jensun_content.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON已保存: {json_path}")
        
        # 保存Markdown
        md_path = self.output_dir / '黄仁勋演讲内容汇总.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {summary['title']}\n\n")
            f.write(f"提取时间：{summary['extract_time']}\n\n")
            f.write(f"来源文章数：{summary['source_count']}\n\n")
            
            f.write("## 核心要点\n\n")
            for i, point in enumerate(summary['key_points'][:10], 1):
                f.write(f"{i}. {point}\n\n")
            
            f.write("## 详细内容\n\n")
            for article in all_articles:
                if article.get('status') == 'success':
                    f.write(f"### {article['title']}\n\n")
                    f.write(f"来源：{article['url']}\n\n")
                    for p in article.get('key_paragraphs', [])[:5]:
                        f.write(f"{p}\n\n")
                    f.write("---\n\n")
        
        print(f"✅ Markdown已保存: {md_path}")
        
        return result


def main():
    extractor = ContentExtractor()
    result = extractor.run()
    
    print("\n" + "="*60)
    print("📊 提取结果摘要:")
    print("="*60)
    print(f"✅ 成功提取 {len(result['articles'])} 篇文章")
    print(f"✅ 核心要点 {len(result['summary']['key_points'])} 条")
    
    return result


if __name__ == "__main__":
    main()
