@echo off
setlocal
rem Locate the repository two levels above Testing\Tools.
for %%I in ("%~dp0..\..") do set "project_dir=%%~fI"
if not defined SIMUO_PYTHON set "SIMUO_PYTHON=%project_dir%\.venv\Scripts\python.exe"
if not exist "%SIMUO_PYTHON%" (
    echo SimuO's Python environment was not found: "%SIMUO_PYTHON%" 1>&2
    echo Follow the setup in "%project_dir%\README.md" or set SIMUO_PYTHON to a Python executable. 1>&2
    exit /b 1
)
"%SIMUO_PYTHON%" "%project_dir%\src\main.py" %*
exit /b %errorlevel%
