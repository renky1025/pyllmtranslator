@echo off
chcp 65001 >nul
echo LLM翻译工具 - 打包脚本
echo ========================

echo 正在激活虚拟环境...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo 虚拟环境已激活
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

echo.
echo 开始打包...
python build_exe.py

echo.
echo 按任意键退出...
pause >nul