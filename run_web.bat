@echo off
REM 视频翻译 Web 服务器启动脚本 (Windows)
REM Video Translator Web Server Launcher (Windows)

chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════╗
echo ║   视频翻译 Web 服务器启动脚本            ║
echo ║   Video Translator Web Server        ║
echo ╚══════════════════════════════════════╝
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 找不到 Python
    echo 请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 检查依赖
echo 正在检查依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask 未安装，正在安装...
    echo.
    pip install -r requirement.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

echo ✓ 依赖检查完成
echo.

REM 启动服务器
echo 🚀 启动服务器...
echo.
echo 访问地址: http://127.0.0.1:5000
echo 按 Ctrl+C 停止服务器
echo.

python -m video_translator.run_web_server

REM 如果执行失败，显示错误
if errorlevel 1 (
    echo.
    echo ❌ 启动失败
    pause
    exit /b 1
)
