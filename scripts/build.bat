@echo off
echo =========================================
echo  Сборка Meme Generator в exe-файл
echo =========================================

rem Проверяем установлен ли Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен или не добавлен в PATH
    echo Скачайте Python с python.org
    pause
    exit /b 1
)

rem Проверяем установлен ли PyInstaller
echo Проверка зависимостей...
pip list | findstr "pyinstaller" >nul
if errorlevel 1 (
    echo Установка PyInstaller...
    pip install pyinstaller
)

echo Установка зависимостей...
pip install -r requirements.txt

echo =========================================
echo  Начинаем сборку...
echo =========================================

rem Создаем временную папку для сборки
if not exist "build" mkdir build
if not exist "dist" mkdir dist

rem Вариант 1: Обычный exe (с консолью)
echo Вариант 1: Сборка с консолью...
pyinstaller --onefile --name="MemeGenerator" --icon=icon.ico main.py

rem Вариант 2: Без консоли (только окно) - раскомментировать если нужно
rem echo Вариант 2: Сборка без консоли...
rem pyinstaller --onefile --windowed --name="MemeGenerator" --icon=icon.ico main.py

echo =========================================
echo  Сборка завершена!
echo =========================================

if exist "dist\MemeGenerator.exe" (
    echo Файл создан: dist\MemeGenerator.exe
    echo Размер: 
    for %%F in ("dist\MemeGenerator.exe") do echo   %%~zF байт
    
    echo.
    echo Что дальше:
    echo 1. dist\MemeGenerator.exe - запустить программу
    echo 2. Можно скопировать exe-файл в любое место
    echo 3. Для удаления: удалите папки build и dist
) else (
    echo ОШИБКА: Файл не создан
)

echo.
echo Папки созданные при сборке:
echo   build\ - временные файлы (можно удалить)
echo   dist\  - готовый exe-файл
echo   MemeGenerator.spec - конфиг сборки

echo.
pause
