@echo off
REM Dominion Flow Plugin - Windows Hook Launcher
REM Calls Git Bash to run session-start.sh with proper path handling

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "HOOK_DIR=%~dp0"
REM Remove trailing backslash
set "HOOK_DIR=%HOOK_DIR:~0,-1%"

REM Convert Windows path to Unix-style for Git Bash
set "UNIX_HOOK_DIR=%HOOK_DIR:\=/%"
set "UNIX_HOOK_DIR=%UNIX_HOOK_DIR:C:=/c%"

REM Define the script to run
set "SCRIPT_PATH=%UNIX_HOOK_DIR%/session-start.sh"

REM Try common Git Bash locations
set "GIT_BASH="

REM Check Program Files
if exist "C:\Program Files\Git\bin\bash.exe" (
    set "GIT_BASH=C:\Program Files\Git\bin\bash.exe"
    goto :found_bash
)

REM Check Program Files (x86)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    set "GIT_BASH=C:\Program Files (x86)\Git\bin\bash.exe"
    goto :found_bash
)

REM Check user's AppData
if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "GIT_BASH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
    goto :found_bash
)

REM Check if bash is in PATH
where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "GIT_BASH=bash"
    goto :found_bash
)

REM Fallback: No Git Bash found
echo [Dominion Flow Hook] Warning: Git Bash not found
echo.
echo ============================================
echo   DOMINION FLOW - Session Context (Fallback)
echo ============================================
echo.
echo [INFO] Git Bash is required for full context injection.
echo [INFO] Install Git for Windows: https://git-scm.com/download/win
echo.
echo Quick Actions:
echo   - Check .planning/CONSCIENCE.md for project state
echo   - Check ~/.claude/warrior-handoffs/ for latest handoff
echo   - Use /fire-dashboard for project status
echo.
goto :end

:found_bash
REM Run the bash script
"%GIT_BASH%" "%SCRIPT_PATH%"

:end
endlocal
