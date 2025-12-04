from PyQt6.QtGui import QColor

APP_NAME = "Meme Generator Pro"
APP_VERSION = "2.0"
DEFAULT_TEXT_COLOR = QColor(255, 255, 255)
DEFAULT_OUTLINE_COLOR = QColor(0, 0, 0)
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 150
DEFAULT_FONT_SIZE = 48

RANDOM_TEXTS = [
    "Когда код заработал\nс первого раза",
    "Когда находишь\nбаг в продакшене",
    "Я: Буду рано спать\nТакже я: 3 часа ночи",
    "Ожидание: Красивый UI\nРеальность: Кривые кнопки",
    "Когда deadline был вчера",
    "Работает? Не трогай!",
    "Завтра начну с понедельника",
    "Не баг, а фича",
    "Компьютер: 1% заряда\nЯ: Успею",
    "Смотрю на код который писал неделю назад\nЧей это код?",
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
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: bold;
        margin: 3px;
        min-height: 35px;
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
        font-size: 14px;
        font-weight: bold;
        color: #8A2BE2;
        border: 2px solid #8A2BE2;
        border-radius: 10px;
        margin-top: 10px;
        padding-top: 15px;
        background-color: rgba(22, 33, 62, 0.7);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px 0 10px;
        background-color: #1A1A2E;
    }
"""
