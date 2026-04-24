@echo off
title Qualitaets-Framework
cd /d "%~dp0"
:: Cache loeschen (verhindert veraltete .pyc Probleme)
if exist "nicegui_app\__pycache__" rd /s /q "nicegui_app\__pycache__" >nul 2>&1
echo Starte Qualitaets-Framework...
echo.
".venv\Scripts\python.exe" -B nicegui_app\main.py
pause
