@echo off
echo 正在同步 Link-Text Skill 到 GitHub...
cd /d "%~dp0"

echo 1. 检查 Git 状态
git status

echo.
echo 2. 提交更改（如果有）
if git diff --quiet && git diff --cached --quiet (
    echo 没有需要提交的更改
) else (
    git add .
    git commit -m "自动更新 - $(date +%Y-%m-%d %H:%M)"
    echo 提交完成
)

echo.
echo 3. 推送到 GitHub
git push

echo.
echo 4. 检查最终状态
git status

echo.
echo 同步完成！
pause