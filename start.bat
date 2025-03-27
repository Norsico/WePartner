@echo off
chcp 65001 > nul
echo 正在启动 wxChatBot...
echo.

:: 激活虚拟环境并运行程序
call .venv\Scripts\activate.bat
python main.py

:: 如果程序异常退出，暂停显示错误信息
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 程序异常退出，错误代码：%ERRORLEVEL%
    pause
) 