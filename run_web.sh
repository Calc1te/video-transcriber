#!/bin/bash
# 快速启动脚本

echo "╔══════════════════════════════════════╗"
echo "║   视频翻译 Web 服务器启动脚本        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 找不到 Python"
    echo "请先安装 Python 3.10 或更高版本"
    exit 1
fi

echo "✓ Python 已安装"

# 检查依赖
echo "正在检查依赖..."
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask 未安装，正在安装..."
    pip install -r requirement.txt
fi

echo "✓ 依赖检查完成"
echo ""

# 启动服务器
echo "🚀 启动服务器..."
echo ""
echo "访问地址: http://127.0.0.1:5000"
echo "按 Ctrl+C 停止服务器"
echo ""

python -m video_translator.run_web_server
