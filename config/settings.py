import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    # Email 配置
    email_sender: str = os.getenv("EMAIL_SENDER", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    email_recipient: str = os.getenv("EMAIL_RECIPIENT", "")

    # SMTP 配置（支持任意 SMTP 服务）
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.qq.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "False").lower() in ("1", "true", "yes")
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "True").lower() in ("1", "true", "yes")

    # Server 酱配置
    serverchan_key: str = os.getenv("SERVERCHAN_KEY", "")

    # TLDR RSS 配置
    tldr_rss_url: str = os.getenv("TLDR_RSS_URL", "https://tldr.tech/api/rss/tech")

    # The Rundown 配置（RSS/API 暂不可用，默认关闭）
    rundown_enabled: bool = os.getenv("RUNDOWN_ENABLED", "False").lower() in ("1", "true", "yes")

    # macOS 桌面通知
    macos_notification_enabled: bool = os.getenv("MACOS_NOTIFICATION_ENABLED", "True").lower() in ("1", "true", "yes")

    # 定时配置
    schedule_time: str = os.getenv("SCHEDULE_TIME", "08:00")

    # 明确使用北京时间，并拒绝严重延迟的云端补发
    schedule_timezone: str = os.getenv("SCHEDULE_TIMEZONE", "Asia/Shanghai")
    send_window_minutes: int = int(os.getenv("SEND_WINDOW_MINUTES", "60"))
    local_email_enabled: bool = os.getenv("LOCAL_EMAIL_ENABLED", "False").lower() in ("1", "true", "yes")

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = "logs/ai-news-hub.log"

    @property
    def effective_smtp_username(self) -> str:
        return self.smtp_username or self.email_sender

    @property
    def effective_smtp_password(self) -> str:
        return self.smtp_password or self.email_password

settings = Settings()
