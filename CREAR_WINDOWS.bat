@echo off
title Crear Descargador de Videos para Windows
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_windows.ps1"
echo.
pause
