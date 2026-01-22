@echo off
setlocal enableextensions
set ROOT=%~dp0
set PYEXE=C:\Users\sarah\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYEXE%" set PYEXE=py
if "%1"=="" (
  "%PYEXE%" "%ROOT%tools\backup_all_py.py"
) else (
  "%PYEXE%" "%ROOT%tools\backup_all_py.py" "%~1"
)
endlocal
