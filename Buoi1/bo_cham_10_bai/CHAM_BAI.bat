@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ================================================
echo BO CHAM 10 BAI A-J - BUOI 14 PYTHON
echo ================================================
echo Vi du bai: A, B, ..., J hoac 1, 2, ..., 10
set /p BAI=Nhap bai can cham: 
set /p FILE=Nhap duong dan file .py (bo trong de dung ten mac dinh): 
if "%FILE%"=="" (
    python cham.py %BAI%
) else (
    python cham.py %BAI% "%FILE%"
)
echo.
pause
