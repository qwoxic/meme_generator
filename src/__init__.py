"""
Генератор мемов - приложение для создания мемов
"""

__version__ = "1.0.0"
__author__ = "Meme Generator Team"

# Экспорт основных классов для удобного импорта
from .main_window import MainWindow
from .image_processor import ImageProcessor
from .text_manager import TextManager, DraggableTextItem
from .meme_renderer import MemeRenderer
from .database import Database
from .export_manager import ExportManager
from .constants import Constants

__all__ = [
    'MainWindow',
    'ImageProcessor',
    'TextManager',
    'DraggableTextItem',
    'MemeRenderer',
    'Database',
    'ExportManager',
    'Constants',
]