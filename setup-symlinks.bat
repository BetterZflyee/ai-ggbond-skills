@echo off
chcp 65001 >nul
echo ==========================================
echo 创建 Skills 软链接到 .trae/skills/
echo ==========================================
echo.

REM 获取当前目录
set "SOURCE_DIR=%~dp0skills"
set "TARGET_DIR=%~dp0..\.trae\skills"

echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

REM 创建软链接
echo 正在创建软链接...

mklink /D "%TARGET_DIR%\ai-super-individual-wechat-writer" "%SOURCE_DIR%\ai-super-individual-wechat-writer"
mklink /D "%TARGET_DIR%\wechat-sticker-creator" "%SOURCE_DIR%\wechat-sticker-creator"
mklink /D "%TARGET_DIR%\marketing-image-generator" "%SOURCE_DIR%\marketing-image-generator"
mklink /D "%TARGET_DIR%\baoyu-cover-image" "%SOURCE_DIR%\baoyu-cover-image"
mklink /D "%TARGET_DIR%\baoyu-post-to-wechat" "%SOURCE_DIR%\baoyu-post-to-wechat"

echo.
echo ==========================================
echo 软链接创建完成！
echo ==========================================
echo.
pause
