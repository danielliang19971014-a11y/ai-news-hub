#!/usr/bin/env python3
"""
AI 行业每日资讯聚合工具
通过 TLDR 获取最新 AI 资讯，每天定时推送到邮件和桌面

运行模式：
  python3 main.py             本地常驻模式（launchd 保活，桌面通知）
  python3 main.py --once      CI 一次性模式（GitHub Actions 云端触发，仅邮件）
  python3 main.py --test      立即执行一次测试发送（调试用）
"""

import sys
import time
import argparse
import signal
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo
from src.scheduler import NewsScheduler
from src.logger import logger
from config.settings import settings


def is_scheduled_send_allowed(now: Optional[datetime] = None) -> bool:
    """只允许严重延迟的云端定时任务在北京时间发送窗口内发邮件。"""
    timezone = ZoneInfo(settings.schedule_timezone)
    current = now.astimezone(timezone) if now else datetime.now(timezone)
    hour, minute = map(int, settings.schedule_time.split(':'))
    window_minutes = max(1, settings.send_window_minutes)

    window_start = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if current < window_start:
        window_start -= timedelta(days=1)
    window_end = window_start + timedelta(minutes=window_minutes)
    allowed = window_start <= current < window_end

    if not allowed:
        logger.warning(
            "跳过延迟定时任务：当前北京时间为 %s，允许发送窗口为 %s 起 %s 分钟",
            current.strftime("%Y-%m-%d %H:%M:%S %Z"),
            settings.schedule_time,
            window_minutes,
        )

    return allowed


def run_once(allow_retry: bool = True) -> bool:
    """
    一次性执行资讯推送，完成后退出。
    供 GitHub Actions 等 CI 环境调用。
    如果当天 TLDR 资讯尚未发布，等待重试。
    """
    from src.news_fetcher import NewsFetcher
    from src.notifier import Notifier

    fetcher = NewsFetcher()
    notifier = Notifier()

    max_attempts = 3 if allow_retry else 1
    retry_delay = 120  # 秒

    for attempt in range(1, max_attempts + 1):
        logger.info("=" * 50)
        logger.info(f"执行每日资讯推送 (CI 模式, 第 {attempt}/{max_attempts} 次)")
        logger.info("=" * 50)

        news_list = fetcher.fetch_all_news()

        if news_list:
            today = datetime.now(ZoneInfo(settings.schedule_timezone)).strftime('%Y-%m-%d')
            subject = f"🤖 AI 行业每日资讯 - {today}"
            html_content = notifier.format_news_html(news_list)

            # CI 环境只发邮件，不做桌面通知
            success = notifier.send_email(subject, html_content)
            if success:
                logger.info("✅ 邮件推送成功（GitHub Actions）")
                logger.info("=" * 50)
                return True

            logger.error("邮件发送失败")
            if attempt < max_attempts:
                logger.info(f"等待 {retry_delay}s 后重试...")
                time.sleep(retry_delay)
            continue

        # 没有获取到资讯
        if attempt < max_attempts:
            logger.warning(
                f"未获取到资讯（可能当日内容尚未发布），"
                f"等待 {retry_delay}s 后重试..."
            )
            time.sleep(retry_delay)
        else:
            logger.warning("多次重试后仍未获取到资讯，交由下一个候选定时任务重试")
            return False

    logger.info("CI 推送任务结束")
    return False


def signal_handler(signum, frame):
    """处理中断信号"""
    logger.info("收到中断信号，正在关闭...")
    scheduler.stop()
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI 行业每日资讯聚合工具')
    parser.add_argument(
        '--once', action='store_true',
        help='一次性执行推送后退出（用于 GitHub Actions / cron）'
    )
    parser.add_argument(
        '--scheduled', action='store_true',
        help='仅在配置的北京时间发送窗口内执行（用于云端定时任务）'
    )
    parser.add_argument(
        '--test', action='store_true',
        help='立即执行一次测试发送（调试用）'
    )
    args = parser.parse_args()

    # --- CI 一次性模式 ---
    if args.once and args.scheduled and not is_scheduled_send_allowed():
        sys.exit(0)

    if args.once:
        if not settings.email_sender or not settings.email_recipient:
            logger.error("❌ 邮件配置不完整，请设置环境变量 EMAIL_SENDER 和 EMAIL_RECIPIENT")
            sys.exit(1)
        if not settings.effective_smtp_username or not settings.effective_smtp_password:
            logger.error("❌ SMTP 凭据不完整，请设置环境变量")
            sys.exit(1)

        sys.exit(0 if run_once() else 1)

    # --- 测试模式 ---
    if args.test:
        logger.info("📨 执行测试发送...")
        scheduler = NewsScheduler()
        scheduler.test_send()
        sys.exit(0)

    # --- 本地常驻模式（launchd 保活）---
    logger.info("=" * 70)
    logger.info("AI 行业每日资讯聚合工具启动（本地常驻模式）")
    logger.info("=" * 70)
    logger.info(f"邮件配置: {settings.email_sender} → {settings.email_recipient}")
    logger.info(f"每日推送时间: {settings.schedule_time}")
    logger.info("桌面通知: 已启用 (macOS)")
    logger.info("=" * 70)

    if not settings.email_sender or not settings.email_recipient:
        logger.error("❌ 发件人或收件人邮箱未配置，请检查 .env 文件")
        sys.exit(1)
    if not settings.effective_smtp_username or not settings.effective_smtp_password:
        logger.error("❌ SMTP 配置不完整")
        sys.exit(1)

    try:
        scheduler = NewsScheduler()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        scheduler.start()
        logger.info("\n✅ 服务运行中，按 Ctrl+C 停止\n")

        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        sys.exit(1)
