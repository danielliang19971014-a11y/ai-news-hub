#!/usr/bin/env python3
"""
AI 行业每日资讯聚合工具
通过 TLDR 和 The Rundown AI 获取最新资讯，每天定时推送到邮件和微信
"""

import sys
import time
import signal
from src.scheduler import NewsScheduler
from src.logger import logger
from config.settings import settings

def signal_handler(signum, frame):
    """处理中断信号"""
    logger.info("收到中断信号，正在关闭...")
    scheduler.stop()
    sys.exit(0)

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("AI 行业每日资讯聚合工具启动")
    logger.info("=" * 70)
    logger.info(f"邮件配置: {settings.email_sender} → {settings.email_recipient}")
    logger.info(f"每日推送时间: {settings.schedule_time}")
    logger.info(f"微信推送: {'已启用' if settings.serverchan_key else '未启用'}")
    logger.info("=" * 70)
    
    # 验证配置
    if not settings.email_sender or not settings.email_recipient:
        logger.error("❌ 发件人或收件人邮箱未配置，请检查 .env 文件")
        sys.exit(1)
    if not settings.effective_smtp_username or not settings.effective_smtp_password:
        logger.error("❌ SMTP 配置不完整，请检查 SMTP_HOST、SMTP_PORT、SMTP_USERNAME/EMAIL_SENDER 和 SMTP_PASSWORD/EMAIL_PASSWORD")
        sys.exit(1)
    
    try:
        # 创建定时调度器
        scheduler = NewsScheduler()
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 启动定时任务
        scheduler.start()
        
        # 如果需要测试，可以在启动后立即执行一次
        # logger.info("\n📨 执行测试发送...")
        # scheduler.test_send()
        
        logger.info("\n✅ 服务运行中，按 Ctrl+C 停止\n")
        
        # 保持运行
        while True:
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        sys.exit(1)
