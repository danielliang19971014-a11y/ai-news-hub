#!/bin/bash
# AI News Hub - 快速安装脚本
# 克隆后运行此脚本即可完成安装

set -e

echo "================================================"
echo "  🤖 AI 行业每日资讯聚合工具 - 快速安装"
echo "================================================"

# 检查 Python 版本
echo ""
echo "🔍 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.8 或更高版本"
    echo "   macOS: brew install python3"
    echo "   或访问: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION"

# 安装依赖
echo ""
echo "📦 安装依赖包..."
python3 -m pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 创建 .env 文件
echo ""
echo "⚙️  配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  请编辑 .env 文件，填写以下必填项："
    echo ""
    echo "  1. EMAIL_SENDER      - 发件邮箱地址（如 QQ 邮箱）"
    echo "  2. EMAIL_PASSWORD    - 邮箱 SMTP 授权码（非登录密码）"
    echo "  3. EMAIL_RECIPIENT   - 接收资讯的邮箱地址"
    echo ""
    echo "  可选配置："
    echo "  4. SERVERCHAN_KEY    - Server 酱密钥（微信推送）"
    echo "  5. SCHEDULE_TIME     - 每日推送时间（默认 08:00）"
    echo ""
    echo "  QQ 邮箱 SMTP 开启方式："
    echo "  登录 QQ 邮箱 → 设置 → 账户 → POP3/SMTP 服务 → 开启并获取授权码"
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "================================================"
echo "  ✅ 安装完成！"
echo "================================================"
echo ""
echo "🎯 快速开始："
echo ""
echo "  # 1. 编辑 .env 填写你的邮箱配置"
echo "  nano .env"
echo ""
echo "  # 2. 测试运行（立即推送一次）"
echo "  python3 main.py"
echo ""
echo "  # 3. 后台持续运行（macOS）- 可选"
echo "  # 参考 README.md 中的 launchd 配置"
echo ""
echo "📖 详细文档: README.md"
