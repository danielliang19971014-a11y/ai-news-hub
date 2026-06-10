import requests
import feedparser
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from src.logger import logger
from config.settings import settings

class NewsFetcher:
    """从各个资讯源获取 AI 新闻"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_tldr(self) -> Optional[List[Dict]]:
        """从 TLDR RSS 获取最新 AI 资讯"""
        try:
            logger.info("开始获取 TLDR 资讯（RSS）...")

            # 1. 先通过 requests 获取 RSS 内容（处理重定向等问题）
            rss_response = self.session.get(settings.tldr_rss_url, timeout=15)
            rss_response.raise_for_status()

            # 2. 用 feedparser 解析 RSS
            feed = feedparser.parse(rss_response.content)

            if not feed.entries:
                logger.warning("TLDR RSS feed 中没有找到任何条目")
                return None

            latest = feed.entries[0]
            digest_url = latest.get('link', '')
            digest_title = latest.get('title', '')

            logger.info(f"最新一期 TLDR: {digest_title}")
            logger.info(f"文章链接: {digest_url}")

            # 3. 抓取文章页面，提取所有新闻摘要
            articles = self._parse_tldr_page(digest_url)

            if not articles:
                logger.warning("未能从 TLDR 页面提取到文章")
                return None

            logger.info(f"成功获取 TLDR 资讯，共 {len(articles)} 条")
            return articles

        except Exception as e:
            logger.error(f"获取 TLDR 资讯失败: {str(e)}")
            return None

    def _parse_tldr_page(self, url: str) -> List[Dict]:
        """解析 TLDR 每日摘要页面，提取所有文章"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            articles = []

            # 查找所有 <article> 标签
            article_elements = soup.find_all('article')

            for article_el in article_elements:
                # 跳过空 article 或太短的
                text = article_el.get_text(strip=True)
                if len(text) < 50:
                    continue

                # 跳过赞助内容
                if '(Sponsor)' in text:
                    continue

                # 尝试提取标题（第一个链接或 <strong> 中的粗体文本）
                title_el = article_el.find(['strong', 'b', 'a'])
                title = title_el.get_text(strip=True) if title_el else ''

                # 如果标题太短或就是正文本身，尝试从文本中提取
                if len(title) < 10:
                    # 取前 100 个字符作为标题
                    title = text[:100]

                # 提取阅读时间（如 "5 minute read"）
                read_time_match = re.search(r'(\d+\s*minute\s*read)', text)
                read_time = read_time_match.group(1) if read_time_match else ''

                # 提取链接
                link_el = article_el.find('a', href=True)
                link = link_el['href'] if link_el else ''

                # 描述 = 去除标题后的文本，截断到合理长度
                description = text
                if title and len(title) > 10:
                    description = text.replace(title, '', 1).strip()
                    # 去除 read time 后面的内容可能是下一篇文章的描述
                    if read_time_match:
                        description = description[:read_time_match.start() + len(read_time)].strip()

                # 如果描述太长，截断到 300 字符
                if len(description) > 500:
                    description = description[:500] + '...'

                articles.append({
                    'source': 'TLDR',
                    'title': title,
                    'description': description,
                    'url': link or url,
                    'read_time': read_time,
                    'category': 'AI / Tech'
                })

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"解析 TLDR 页面失败 ({url}): {str(e)}")
            return []
        except Exception as e:
            logger.error(f"解析 TLDR 页面异常: {str(e)}")
            return []

    def fetch_rundown(self) -> Optional[List[Dict]]:
        """从 The Rundown AI 获取最新 AI 资讯"""
        if not settings.rundown_enabled:
            logger.info("The Rundown 源已禁用（RUNDOWN_ENABLED=False），跳过")
            return []

        # TODO: The Rundown 使用 beehiiv 平台，RSS/API 暂不公开
        # 后续可通过以下方式接入：
        # 1. 邮件订阅 + IMAP 解析
        # 2. 网页抓取 thermodown.ai
        logger.info("The Rundown 源暂未接入，跳过")
        return []

    def fetch_all_news(self) -> List[Dict]:
        """获取所有来源的资讯"""
        all_news = []

        tldr_news = self.fetch_tldr()
        if tldr_news:
            all_news.extend(tldr_news)

        rundown_news = self.fetch_rundown()
        if rundown_news:
            all_news.extend(rundown_news)

        logger.info(f"总共获取 {len(all_news)} 条资讯")
        return all_news
