import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MemeGeneratorPro

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MemeGeneratorPro()
    window.show()
    sys.exit(app.exec())
