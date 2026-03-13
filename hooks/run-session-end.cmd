@echo off
REM Dominion Flow Plugin - Windows Session End Hook Launcher
REM Calls Git Bash to run session-end.sh

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "HOOK_DIR=%~dp0"
set "HOOK_DIR=%HOOK_DIR:~0,-1%"

REM Convert Windows path to Unix-style for Git Bash
set "UNIX_HOOK_DIR=%HOOK_DIR:\=/%"
set "UNIX_HOOK_DIR=%UNIX_HOOK_DIR:C:=/c%"

REM Define the script to run
set "SCRIPT_PATH=%UNIX_HOOK_DIR%/session-end.sh"

REM Try common Git Bash locations
set "GIT_BASH="

if exist "C:\Program Files\Git\bin\bash.exe" (
    set "GIT_BASH=C:\Program Files\Git\bin\bash.exe"
    goto :found_bash
)

if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    set "GIT_BASH=C:\Program Files (x86)\Git\bin\bash.exe"
    goto :found_bash
)

if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "GIT_BASH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
    goto :found_bash
)

where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "GIT_BASH=bash"
    goto :found_bash
)

REM Fallback: No Git Bash found — skip silently
goto :end

:found_bash
"%GIT_BASH%" "%SCRIPT_PATH%"

:end
endlocal
