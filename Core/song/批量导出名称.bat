@echo off
setlocal enabledelayedexpansion

:: 设置编码为UTF-8
chcp 65001 >nul

:: 检查name_list.txt是否存在，不存在则创建
if not exist "name_list.txt" (
    echo Creating name_list.txt...
    type nul > name_list.txt
)

:: 清空name_list.txt内容
echo Clearing name_list.txt...
>name_list.txt (
    for %%f in (*.wav) do (
        echo %%~nf
    )
)

echo WAV file names have been added to name_list.txt.
