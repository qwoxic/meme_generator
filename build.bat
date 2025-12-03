@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo Создание исполняемого файла...
pyinstaller --onefile --windowed --name "MemeGenerator" ^
--icon=icon.ico ^
--add-data "src;src" ^
--hidden-import PyQt6.QtCore ^
--hidden-import PyQt6.QtGui ^
--hidden-import PyQt6.QtWidgets ^
--hidden-import PIL ^
main.py

echo Готово! Исполняемый файл в папке dist/
pause
