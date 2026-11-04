@echo off
setlocal
set "project_dir=%~dp0"
if not defined SIMUO_PYTHON set "SIMUO_PYTHON=%project_dir%.venv\Scripts\python.exe"
if not exist "%SIMUO_PYTHON%" (
    echo SimuO's Python environment was not found: "%SIMUO_PYTHON%" 1>&2
    echo Follow the Windows setup in README.md or set SIMUO_PYTHON to a Python executable. 1>&2
    exit /b 1
)
"%SIMUO_PYTHON%" "%project_dir%src\main.py" %*
exit /b %errorlevel%
