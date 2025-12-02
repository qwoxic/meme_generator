@echo off
echo Установка Meme Generator...
echo.

echo 1. Проверка Python...
python --version
if errorlevel 1 (
    echo Python не найден! Установите Python 3.8+
    pause
    exit
)

echo 2. Установка зависимостей...
pip install PyQt6 Pillow

echo 3. Создание папки database...
if not exist "database" mkdir database

echo.
echo =================================
echo Установка завершена!
echo =================================
echo.
echo Запуск программы:
echo   python main.py
echo.
echo Создание exe-файла:
echo   build.bat
echo.
pause
