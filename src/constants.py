from PyQt6.QtGui import QColor

APP_NAME = "Meme Generator"
APP_VERSION = "1.0"
DEFAULT_TEXT_COLOR = QColor(255, 255, 255)
DEFAULT_OUTLINE_COLOR = QColor(0, 0, 0)
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 150
DEFAULT_FONT_SIZE = 48

RANDOM_TEXTS = [
    "Когда код заработал с первого раза",
    "Мой код vs Код коллеги",
    "Когда находишь баг в продакшене",
    "План на день vs Реальность",
    "Я: Буду рано спать\nТоже я: 3 часа ночи",
    "Ожидание: Красивый UI\nРеальность: Кривые кнопки",
]

AVAILABLE_FONTS = [
    "Arial", "Times New Roman", "Calibri", "Comic Sans MS", "Impact",
    "Georgia", "Verdana", "Tahoma", "Courier New", "Trebuchet MS",
    "Lucida Sans Unicode", "Palatino Linotype", "Segoe UI", "Roboto",
    "Open Sans", "Montserrat", "Lato", "Helvetica", "Consolas"
]

BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #8A2BE2, stop: 1 #4169E1);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
        min-height: 30px;
    }
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #9B30FF, stop: 1 #4682B4);
    }
    QPushButton:pressed {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #7A1DC2, stop: 1 #1E4B8D);
    }
    QPushButton:disabled {
        background: #555555;
        color: #AAAAAA;
    }
"""

GROUP_BOX_STYLE = """
    QGroupBox {
        font-size: 13px;
        font-weight: bold;
        color: #8A2BE2;
        border: 1px solid #8A2BE2;
        border-radius: 8px;
        margin-top: 8px;
        padding-top: 12px;
        background-color: rgba(255, 255, 255, 0.05);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: #1A1A2E;
    }
"""
