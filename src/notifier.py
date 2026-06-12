import smtplib
import subprocess
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
from deep_translator import GoogleTranslator
from config.settings import settings
from src.logger import logger

class Notifier:
    """发送邮件和微信推送通知"""

    # 翻译缓存，避免重复翻译相同标题
    _translation_cache = {}

    @staticmethod
    def translate_titles(news_list: List[Dict]) -> Dict[str, str]:
        """批量翻译标题为中文，带缓存"""
        titles_to_translate = []
        for item in news_list:
            title = item.get('title', '')
            if title and title not in Notifier._translation_cache:
                titles_to_translate.append(title)

        if titles_to_translate:
            try:
                logger.info(f"正在翻译 {len(titles_to_translate)} 条标题...")
                translator = GoogleTranslator(source='en', target='zh-CN')
                translated = translator.translate_batch(titles_to_translate)

                for en, zh in zip(titles_to_translate, translated):
                    Notifier._translation_cache[en] = zh

                logger.info("标题翻译完成")
            except Exception as e:
                logger.warning(f"标题翻译失败，将使用英文原标题: {str(e)}")
                # 失败时把英文标题作为"翻译"填充
                for title in titles_to_translate:
                    Notifier._translation_cache[title] = title

        return Notifier._translation_cache

    @staticmethod
    def send_email(subject: str, html_content: str) -> bool:
        """发送邮件"""
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.email_sender
            msg['To'] = settings.email_recipient

            # 添加 HTML 内容
            part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part)

            smtp_username = settings.effective_smtp_username
            smtp_password = settings.effective_smtp_password
            if not smtp_username or not smtp_password:
                logger.error("未配置 SMTP 用户名或密码，邮件无法发送")
                return False

            if settings.smtp_use_ssl:
                server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)

            with server:
                if settings.smtp_use_tls and not settings.smtp_use_ssl:
                    server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(
                    settings.email_sender,
                    settings.email_recipient,
                    msg.as_string()
                )

            logger.info(f"邮件发送成功：{subject}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

    @staticmethod
    def send_serverchan(title: str, desp: str) -> bool:
        """发送 Server 酱（微信）推送"""
        try:
            if not settings.serverchan_key:
                logger.warning("未配置 Server 酱密钥，跳过微信推送")
                return False

            url = f"https://sctapi.ftqq.com/{settings.serverchan_key}.send"
            data = {
                'title': title,
                'desp': desp
            }

            response = requests.post(url, data=data, timeout=10)
            result = response.json()

            if result.get('code') == 0:
                logger.info(f"Server 酱推送成功：{title}")
                return True
            else:
                logger.error(f"Server 酱推送失败: {result.get('message')}")
                return False

        except Exception as e:
            logger.error(f"Server 酱推送异常: {str(e)}")
            return False

    @staticmethod
    def send_macos_notification(news_list: List[Dict]) -> bool:
        """发送 macOS 原生桌面通知"""
        if not settings.macos_notification_enabled:
            return False

        try:
            if not news_list:
                return False

            # 统计来源
            sources = set(item.get('source', '') for item in news_list)
            source_str = ' + '.join(sorted(sources))

            # 副标题：来源 + 文章数
            subtitle = f"{source_str} · {len(news_list)} 篇文章"

            # 正文：前 5 条标题（中文翻译优先）
            Notifier.translate_titles(news_list)
            body_lines = []
            for item in news_list[:5]:
                en_title = item.get('title', '')
                zh_title = Notifier._translation_cache.get(en_title, en_title)
                # 用中文标题，截断长标题
                if len(zh_title) > 60:
                    zh_title = zh_title[:57] + '...'
                body_lines.append(f"• {zh_title}")

            body = '\n'.join(body_lines)

            # 转义 AppleScript 特殊字符
            body_safe = body.replace('\\', '\\\\').replace('"', '\\"')
            subtitle_safe = subtitle.replace('\\', '\\\\').replace('"', '\\"')

            # 用 osascript 调用原生通知
            script = f'display notification "{body_safe}" with title "🤖 AI 行业每日资讯" subtitle "{subtitle_safe}" sound name "Glass"'

            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                timeout=5
            )

            logger.info("macOS 桌面通知发送成功")
            return True

        except Exception as e:
            logger.warning(f"macOS 桌面通知发送失败（不影响其他推送）: {str(e)}")
            return False

    @staticmethod
    def format_news_html(news_list: List[Dict]) -> str:
        """格式化新闻为 HTML（中文标题 + 英文原标题）"""
        # 先批量翻译
        Notifier.translate_titles(news_list)

        today = datetime.now().strftime("%Y-%m-%d")
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 650px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0 0 6px 0; font-size: 22px; }}
                .header p {{ margin: 0; opacity: 0.85; font-size: 14px; }}
                .news-item {{ border-left: 4px solid #667eea; padding: 16px 18px; margin-bottom: 18px; background: #f9f9fb; border-radius: 4px; }}
                .source-tag {{ color: #667eea; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }}
                .title-zh {{ font-size: 16px; font-weight: bold; color: #222; margin: 8px 0 4px 0; line-height: 1.5; }}
                .title-en {{ font-size: 12px; color: #999; font-style: italic; margin: 0 0 8px 0; }}
                .description {{ color: #555; font-size: 14px; margin: 8px 0; line-height: 1.6; }}
                .link {{ display: inline-block; margin-top: 8px; }}
                .link a {{ color: #667eea; text-decoration: none; font-weight: bold; font-size: 13px; }}
                .link a:hover {{ text-decoration: underline; }}
                .footer {{ text-align: center; color: #aaa; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI 行业每日资讯</h1>
                    <p>{today}</p>
                </div>
        """

        # 按来源分组
        sources = {}
        for news in news_list:
            source = news.get('source', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(news)

        # 添加新闻
        for source, items in sources.items():
            html += f"<h2>📰 {source}</h2>"
            for item in items:
                en_title = item.get('title', '')
                zh_title = Notifier._translation_cache.get(en_title, en_title)
                description = item.get('description', '')
                url = item.get('url', '#')
                category = item.get('category', 'AI')

                html += f"""
                <div class="news-item">
                    <div class="source-tag">{category}</div>
                    <div class="title-zh">{zh_title}</div>
                    <div class="title-en">{en_title}</div>
                    <div class="description">{description}</div>
                    <div class="link"><a href="{url}">阅读原文 →</a></div>
                </div>
                """

        html += """
                <div class="footer">
                    <p>AI 行业资讯聚合工具 | 每天推送 · 中文标题辅助快速浏览</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    @staticmethod
    def format_news_text(news_list: List[Dict]) -> str:
        """格式化新闻为纯文本（中文标题 + 英文原标题）"""
        # 先批量翻译
        Notifier.translate_titles(news_list)

        text = f"🤖 AI 行业每日资讯 - {datetime.now().strftime('%Y-%m-%d')}\n\n"

        # 按来源分组
        sources = {}
        for news in news_list:
            source = news.get('source', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(news)

        for source, items in sources.items():
            text += f"\n📰 {source}\n"
            text += "-" * 50 + "\n"
            for i, item in enumerate(items, 1):
                en_title = item.get('title', '')
                zh_title = Notifier._translation_cache.get(en_title, en_title)
                text += f"\n{i}. {zh_title}\n"
                text += f"   ({en_title})\n"
                text += f"   {item.get('description', '')}\n"
                text += f"   {item.get('url', '')}\n"

        text += f"\n\n---\nAI 行业资讯聚合工具 | 每天北京时间 08:00 时段推送"
        return text
