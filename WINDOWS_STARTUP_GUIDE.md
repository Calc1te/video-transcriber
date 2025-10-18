# Windows 启动指南

## 快速启动方式

### 方式 1：双击运行 BAT 文件（推荐新手）

1. 打开文件浏览器
2. 找到项目目录：`video_translator`
3. 双击 `run_web.bat` 文件
4. 等待服务器启动
5. 自动打开浏览器或手动访问 `http://127.0.0.1:5000`

### 方式 2：命令行运行

#### 使用 CMD
```cmd
cd C:\Users\YourUsername\path\to\video_translator
python -m video_translator.run_web_server
```

#### 使用 PowerShell
```powershell
cd C:\Users\YourUsername\path\to\video_translator
python -m video_translator.run_web_server
```

### 方式 3：高级选项

```cmd
REM 指定自定义端口
python -m video_translator.run_web_server --port 8080

REM 允许远程访问
python -m video_translator.run_web_server --host 0.0.0.0

REM 启用调试模式
python -m video_translator.run_web_server --debug

REM 查看帮助
python -m video_translator.run_web_server --help
```

## 前置准备

### 1. 检查 Python 安装

打开 CMD 或 PowerShell，输入：
```cmd
python --version
```

应该显示 Python 3.10 或更高版本。

**如果提示找不到 python：**
- 下载 Python: https://www.python.org/downloads/
- 安装时必须勾选 "Add Python to PATH"

### 2. 安装依赖

首次运行时，`run_web.bat` 会自动检查并安装依赖。

或手动安装：
```cmd
pip install -r requirement.txt
```

## 常见问题

### Q: 双击 BAT 文件后窗口立即关闭

**A:** 可能发生了错误。改为在命令行中运行以查看错误信息：
```cmd
cd /d C:\path\to\video_translator
run_web.bat
```

### Q: 提示 "Python 不是内部或外部命令"

**A:** Python 未正确安装或未添加到 PATH。
1. 重新安装 Python
2. 安装时勾选 "Add Python to PATH"
3. 重启电脑

### Q: 提示 "找不到模块"

**A:** 依赖未安装，运行以下命令：
```cmd
pip install -r requirement.txt
```

### Q: 无法访问 http://127.0.0.1:5000

**A:** 检查以下几点：
- 确保服务器还在运行
- 尝试访问 `http://localhost:5000`
- 检查防火墙是否阻止 Python
- 查看命令行中是否有错误信息

### Q: 如何使用其他端口

**A:** 修改启动命令，在命令行中运行：
```cmd
python -m video_translator.run_web_server --port 3000
```

或编辑 `run_web.bat`，将最后一行改为：
```cmd
python -m video_translator.run_web_server --port 3000
```

### Q: 如何停止服务器

**A:** 在命令行中按 `Ctrl+C`

## Windows 版本支持

- ✅ Windows 7 或更高版本
- ✅ Windows 10
- ✅ Windows 11

## 开发者用途

### 创建快捷方式（可选）

1. 右键点击 `run_web.bat`
2. 选择 "发送到" → "桌面（创建快捷方式）"
3. 现在可以从桌面双击启动

### 编辑 BAT 文件

如需自定义启动参数，可用文本编辑器打开 `run_web.bat` 修改最后一行：

```bat
REM 修改这一行
python -m video_translator.run_web_server --port 8080 --host 0.0.0.0
```

## 环境变量（高级）

如需设置环境变量，编辑 `run_web.bat`：

```bat
REM 设置环境变量示例
set FLASK_ENV=production
set FLASK_DEBUG=0
python -m video_translator.run_web_server
```

## 脚本说明

`run_web.bat` 会自动进行以下操作：

1. ✓ 检查 Python 是否已安装
2. ✓ 检查 Flask 依赖
3. ✓ 如果缺少依赖，自动安装
4. ✓ 启动 Flask 服务器
5. ✓ 显示访问地址
6. ✓ 如果出错，显示错误信息并暂停

## 帮助资源

- 快速开始: `QUICK_START_WEB.md`
- 完整指南: `WEB_SERVER_GUIDE.md`
- 功能总结: `WEB_SERVER_SUMMARY.md`
- Python 官网: https://www.python.org/

## 联系支持

如有问题，请查看项目 README 或提交 Issue。

---

**祝你使用愉快！** 🎉
