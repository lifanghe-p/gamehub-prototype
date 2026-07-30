@echo off
chcp 65001 >nul
REM ============================================================
REM  把整个项目推到 GitHub 的 main 分支（代码备份）
REM  用法：把下面的 REPO_URL 改成你的仓库地址，双击运行
REM ============================================================
set "REPO_URL=https://github.com/lifanghe-p/gamehub-prototype.git"
REM 示例（二选一）：
REM set "REPO_URL=https://github.com/alice/gamehub.git"
REM set "REPO_URL=git@github.com:alice/gamehub.git"

cd /d "%~dp0"

echo [1/3] 设置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git remote -v

echo [2/3] 推送 main 分支...
git push -u origin main
if errorlevel 1 (
  echo.
  echo 推送失败：通常会要求登录。
  echo  - 如果用 HTTPS：用户名填 GitHub 账号，密码处粘贴 Personal Access Token（不是账号密码）。
  echo  - 如果用 SSH：确认本机已配置 GitHub SSH key。
  pause
  exit /b 1
)

echo [3/3] main 推送完成！
echo 接着发布网站：再双击 publish.bat（推 gh-pages 分支）。
echo 然后在 GitHub 仓库 Settings - Pages 选择 gh-pages 分支 / (root)。
pause
