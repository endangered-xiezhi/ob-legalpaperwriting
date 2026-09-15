#!/bin/bash
set -e

# ==============================================================================
# 法脉 LexTrace —— 依赖全自动安装脚本 (Cross-Platform / Linux / macOS)
# ==============================================================================

echo "========================================================"
echo "  ⚖️  法脉 LexTrace: 自动依赖配置程序"
echo "========================================================"

# 1. 检查 Python
if command -v python3 >/dev/null 2>&1; then
    echo "✓ 检测到 Python: $(python3 --version)"
    echo "正在安装 Python 依赖 (requirements.txt)..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple || pip3 install -r requirements.txt
else
    echo "❌ 未检测到 Python 3，请先安装 Python 3.10+ 后重试。"
    exit 1
fi

# 2. 检查 Node.js / npm
if command -v npm >/dev/null 2>&1; then
    echo "✓ 检测到 Node: $(node -v) / npm: $(npm -v)"
    echo "正在安装 Web 界面依赖 (node_modules)..."
    npm install --registry=https://registry.npmmirror.com || npm install
else
    echo "⚠️  未检测到 Node.js / npm。"
    echo "请访问 https://nodejs.org/ 下载并安装 LTS 长期稳定版。"
    exit 1
fi

echo "========================================================"
echo "🎉 所有环境依赖已安装完毕！"
echo "您可以通过运行 ./启动LexTrace.command 或 npm run dev 启动服务。"
echo "========================================================"
