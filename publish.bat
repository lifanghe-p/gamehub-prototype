@echo off
cd /d %~dp0
echo ========================================
echo  GameHub 发布到 GitHub Pages (gh-pages)
echo ========================================
echo.
echo [1/3] 准备最新快照（需后端提供实时数据）...
curl -s -o nul -m 2 http://127.0.0.1:8000/api/games >nul 2>&1
if errorlevel 1 (
  echo   backend not running, start server.py ...
  start "GameHubServer" /B python server.py
  timeout /t 6 /nobreak >nul
) else (
  echo   backend already running, skip start.
)
echo   build web/data.json ...
python build_snapshot.py
if errorlevel 1 (
  echo   snapshot failed (ensure server.py running + network). keep existing data.json.
)
taskkill /FI "WINDOWTITLE eq GameHubServer" >nul 2>&1
echo.
echo [2/3] push web/ to gh-pages branch ...
git add web
git commit -m "site update %date% %time%" >nul 2>&1 || echo  (no changes, skip commit)
git subtree push --prefix web origin gh-pages
if errorlevel 1 (
  echo.
  echo  push failed. please confirm:
  echo   1) git remote add origin https://github.com/USER/REPO.git
  echo   2) git push -u origin main
  echo   3) remote repo created
  goto end
)
echo.
echo [3/3] done!
echo   GitHub: Settings - Pages - Source: gh-pages /(root)
echo   wait 1-2 min, then open https://USER.github.io/REPO/
:end
pause
