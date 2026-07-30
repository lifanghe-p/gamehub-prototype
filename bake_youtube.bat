@echo off
REM ============================================================
REM  GameHub - Bake real YouTube guides and push to GitHub Pages
REM  Usage (on your own PC, with internet):
REM   1) Copy config.example.json -> config.json
REM   2) Fill in your YouTube Data API v3 key: "youtube_api_key"
REM   3) Double-click this file.
REM  It will: rebuild web/data.json (uses the key) -> commit -> push gh-pages
REM ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] python not found. Install Python 3 and add it to PATH.
  pause
  exit /b 1
)

if not exist "config.json" (
  echo [WARN] config.json not found -> real YouTube videos will NOT be fetched.
  echo         Copy config.example.json to config.json and set youtube_api_key.
  echo         Press any key to continue with current snapshot, or Ctrl+C to cancel.
  pause
)

echo [1/3] Rebuilding web/data.json (reads youtube_api_key from config.json) ...
python build_snapshot.py
if errorlevel 1 (
  echo [ERROR] Bake failed. Check your internet connection and the key in config.json.
  pause
  exit /b 1
)

echo [2/3] Committing web changes ...
git add web
set CHANGED=0
for /f %%i in ('git status --porcelain web') do set CHANGED=1
if "%CHANGED%"=="1" (
  git commit -m "bake real YouTube guides (%date% %time%)"
) else (
  echo        web/ unchanged, skip commit.
)

echo [3/3] Pushing to gh-pages ...
git subtree push --prefix web origin gh-pages
if errorlevel 1 (
  echo [ERROR] Push failed. Check git remote / network / permissions.
  pause
  exit /b 1
)

echo.
echo [OK] Done! Wait 1-2 minutes, then open the live site to see real YouTube guides:
echo      https://lifanghe-p.github.io/gamehub-prototype/
echo      If not updated, go to GitHub repo Settings -> Pages -> Source: gh-pages / (root).
pause
