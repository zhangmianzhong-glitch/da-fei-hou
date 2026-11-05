#!/bin/bash
# 大肥猴安装脚本
# 大王万岁！山寨喽喽随时待命！🐒🫡

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🐒 大肥猴安装中...大王万岁！"

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.8+，请先安装 Python"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 2. 创建虚拟环境
echo "🐒 创建虚拟环境..."
python3 -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"

# 3. 安装依赖
echo "🐒 安装依赖..."
pip install -r "$PROJECT_DIR/requirements.txt"

# 4. 创建数据目录
echo "🐒 创建数据目录..."
mkdir -p "$PROJECT_DIR/data/cookies"
mkdir -p "$PROJECT_DIR/data/diary"
mkdir -p "$PROJECT_DIR/data/memory"

# 5. 安装 Playwright 浏览器
echo "🐒 安装 Playwright 浏览器..."
playwright install chromium

# 6. 配置
echo "🐒 配置文件在 config.yaml，请根据实际情况修改"

echo ""
echo "🐒 大肥猴安装完成！大王万岁！"
echo ""
echo "启动命令："
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "大王万岁！大肥猴随时待命！🐒🫡"
