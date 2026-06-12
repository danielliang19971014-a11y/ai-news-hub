# 🤖 AI 行业每日资讯聚合工具

自动从 **TLDR** 获取最新 AI/科技资讯，**标题自动翻译为中文**，每天定时推送到你的邮箱和桌面。

## ✨ 功能特性

- 🔄 自动从 TLDR RSS 获取每日 AI 资讯（10+ 条/天）
- 🌐 **标题自动翻译为中文**，快速浏览，感兴趣再点原文
- 📧 每日邮件推送（双语标题 + 原文链接）
- 💻 **macOS 原生桌面通知**
- 💬 微信推送通知（Server 酱，可选）
- ⏰ 可配置的推送时间
- 📝 详细的日志记录
- 🚀 一键安装，开箱即用

## 📋 项目结构

```
ai-news-hub/
├── main.py                 # 主程序入口
├── install.sh              # 一键安装脚本
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── config/
│   ├── __init__.py
│   └── settings.py         # 配置管理
├── src/
│   ├── __init__.py
│   ├── logger.py           # 日志模块
│   ├── news_fetcher.py     # 资讯获取（RSS + 网页解析）
│   ├── notifier.py         # 通知模块（邮件 + 桌面 + 微信）
│   └── scheduler.py        # 定时调度模块
└── logs/                   # 日志目录（自动创建）
```

## 🚀 快速开始

### 系统要求

- Python 3.9+
- macOS / Linux / Windows

### 1. 克隆并安装

```bash
git clone <your-repo-url> ai-news-hub
cd ai-news-hub
bash install.sh
```

### 2. 配置邮箱

编辑 `.env` 文件：

```env
# 必填：QQ 邮箱配置
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_qq_smtp_auth_code
EMAIL_RECIPIENT=your_email@qq.com
```

> **QQ 邮箱 SMTP 授权码获取：**
> 登录 QQ 邮箱 → 设置 → 账户 → POP3/IMAP/SMTP 服务 → 开启 SMTP → 生成授权码
>
> ⚠️ 使用的是**授权码**，不是 QQ 登录密码。

如果你使用其他邮箱（Gmail、163 等），修改 SMTP 配置：

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=False
SMTP_USE_SSL=True
```

### 3. 运行

```bash
# 测试运行（立即推送一次）
python3 main.py
```

### 4. 后台持续运行（可选）

#### macOS（launchd）

创建 `~/Library/LaunchAgents/com.ai-news-hub.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-news-hub</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/ai-news-hub/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/ai-news-hub/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/ai-news-hub/logs/stderr.log</string>
</dict>
</plist>
```

```bash
# 加载服务
launchctl load ~/Library/LaunchAgents/com.ai-news-hub.plist

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.ai-news-hub.plist
```

#### Linux（systemd）

创建 `~/.config/systemd/user/ai-news-hub.service`：

```ini
[Unit]
Description=AI News Hub
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/ai-news-hub/main.py
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
```

```bash
systemctl --user start ai-news-hub
systemctl --user enable ai-news-hub
```

## 📖 推送渠道

| 渠道 | 说明 | 配置 |
|------|------|------|
| 📧 邮件 | 精美的 HTML 邮件，中文标题 + 英文原标题 | 必配 `EMAIL_*` |
| 💻 桌面通知 | macOS Notification Center 弹窗 | 默认开启 |
| 💬 微信 | 通过 Server 酱推送到微信 | 可选 `SERVERCHAN_KEY` |

### 微信推送（可选）

1. 访问 [Server 酱](https://sct.ftqq.com/) 用 GitHub 登录
2. 获取 SCKEY
3. 在 `.env` 中填写 `SERVERCHAN_KEY=你的SCKEY`
4. 关注 Server 酱公众号完成绑定

## 🔧 配置参考

### 完整 `.env` 示例

```env
# 邮箱配置（必填）
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_qq_smtp_auth_code
EMAIL_RECIPIENT=your_email@qq.com

# SMTP 配置（可选，默认 QQ 邮箱）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=your_email@qq.com
SMTP_PASSWORD=your_qq_smtp_auth_code
SMTP_USE_TLS=False
SMTP_USE_SSL=True

# TLDR RSS 源
TLDR_RSS_URL=https://tldr.tech/api/rss/tech

# The Rundown（暂不可用）
RUNDOWN_ENABLED=False

# macOS 桌面通知
MACOS_NOTIFICATION_ENABLED=True

# 微信推送（可选）
SERVERCHAN_KEY=

# 推送时间（24小时制）
SCHEDULE_TIME=08:00

# 调度时区与发送窗口
SCHEDULE_TIMEZONE=Asia/Shanghai
SEND_WINDOW_MINUTES=60

# 本机常驻任务是否同时发邮件（建议关闭，避免和 GitHub Actions 重复）
LOCAL_EMAIL_ENABLED=False

# 日志级别
LOG_LEVEL=INFO
```

### 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `EMAIL_SENDER` | 发件人邮箱 | - |
| `EMAIL_PASSWORD` | 邮箱密码/授权码 | - |
| `EMAIL_RECIPIENT` | 收件人邮箱 | - |
| `SMTP_HOST` | SMTP 服务器 | `smtp.qq.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SCHEDULE_TIME` | 每日推送时间 | `08:00` |
| `SCHEDULE_TIMEZONE` | 调度时区 | `Asia/Shanghai` |
| `SEND_WINDOW_MINUTES` | 云端延迟任务允许发送的分钟数 | `60` |
| `LOCAL_EMAIL_ENABLED` | 本机定时任务是否发邮件 | `False` |
| `SERVERCHAN_KEY` | Server 酱密钥 | - |
| `MACOS_NOTIFICATION_ENABLED` | 桌面通知开关 | `True` |
| `RUNDOWN_ENABLED` | The Rundown 源 | `False` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 📊 资讯来源

### TLDR
- 网站：[tldr.tech](https://tldr.tech/)
- 全球最大的科技简报之一，日订阅量 120 万+
- 每天精选 10+ 条 AI/科技/创业资讯，每条附有深度摘要
- 本项目通过 RSS + 网页解析获取完整内容

### The Rundown AI（暂不可用）
- 网站：[therundown.ai](https://www.therundown.ai/)
- 基于 beehiiv 平台，RSS/API 暂不公开
- 设 `RUNDOWN_ENABLED=True` 可启用（后续接入）

## 🐛 故障排查

**问题 1：邮件发送失败**
- 确认使用 SMTP **授权码**而非登录密码
- QQ 邮箱：检查是否开启了 SMTP 服务
- Gmail：需开启两步验证后生成应用专用密码
- 查看日志：`tail -f logs/ai-news-hub.log`

**问题 2：获取资讯失败**
- 检查网络连接
- 确认 `tldr.tech` 是否可访问
- 查看详细错误日志

**问题 3：标题没有翻译**
- 检查网络是否能访问 Google Translate
- 翻译失败会自动降级为英文原标题，不影响推送

**问题 4：桌面通知不显示**
- 仅支持 macOS
- 检查系统偏好设置 → 通知 → 允许终端/脚本通知
- 设置 `MACOS_NOTIFICATION_ENABLED=False` 可关闭

## 📦 依赖包

| 包名 | 用途 |
|------|------|
| `requests` | HTTP 请求 |
| `APScheduler` | 定时任务 |
| `feedparser` | RSS 解析 |
| `beautifulsoup4` + `lxml` | HTML 解析 |
| `deep-translator` | 标题中英翻译 |
| `python-dotenv` | 环境变量 |

## 📄 许可

MIT License

---

**每天 5 分钟，AI 资讯尽在掌握 📬**
