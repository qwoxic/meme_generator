import sys
import os
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow

def main():
    # Создаем директорию для базы данных, если ее нет
    os.makedirs("database", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Meme Generator")
    app.setOrganizationName("MemeCorp")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()