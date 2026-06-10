from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config.settings import settings
from src.logger import logger
from src.news_fetcher import NewsFetcher
from src.notifier import Notifier

class NewsScheduler:
    """定时任务调度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.fetcher = NewsFetcher()
        self.notifier = Notifier()

    def send_daily_news(self):
        """每日发送资讯任务"""
        try:
            logger.info("=" * 50)
            logger.info("开始执行每日资讯推送任务")
            logger.info("=" * 50)

            # 获取新闻
            news_list = self.fetcher.fetch_all_news()

            if not news_list:
                logger.warning("未获取到任何资讯")
                return

            # 准备邮件内容
            subject = f"🤖 AI 行业每日资讯 - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = self.notifier.format_news_html(news_list)
            text_content = self.notifier.format_news_text(news_list)

            # 发送邮件
            self.notifier.send_email(subject, html_content)

            # 发送 macOS 桌面通知
            self.notifier.send_macos_notification(news_list)

            # 发送微信推送
            self.notifier.send_serverchan(subject, text_content)

            logger.info("每日资讯推送任务完成")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"每日资讯推送任务失败: {str(e)}")

    def start(self):
        """启动定时任务"""
        try:
            # 解析调度时间
            hour, minute = map(int, settings.schedule_time.split(':'))

            # 添加定时任务
            self.scheduler.add_job(
                self.send_daily_news,
                'cron',
                hour=hour,
                minute=minute,
                id='daily_news_job',
                name='每日 AI 资讯推送'
            )

            self.scheduler.start()
            logger.info(f"定时任务已启动，每天 {settings.schedule_time} 执行")

        except Exception as e:
            logger.error(f"启动定时任务失败: {str(e)}")
            raise

    def stop(self):
        """停止定时任务"""
        self.scheduler.shutdown()
        logger.info("定时任务已停止")

    def test_send(self):
        """测试发送（立即执行一次）"""
        logger.info("执行测试发送...")
        self.send_daily_news()
