import os
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QImage
from .constants import Constants

class ExportManager:
    def __init__(self, database):
        self.database = database
    
    def save_meme(self, parent_window, meme_pixmap):
        """
        Сохранение мема в файл
        
        Args:
            parent_window: Родительское окно для диалога
            meme_pixmap: QPixmap мема для сохранения
        
        Returns:
            str: Путь к сохраненному файлу или None
        """
        if meme_pixmap.isNull():
            return None
        
        # Открываем диалог сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            parent_window,
            "Сохранить мем",
            f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            Constants.EXPORT_EXTENSIONS
        )
        
        if not file_path:
            return None
        
        # Определяем формат по расширению
        if file_path.lower().endswith(('.jpg', '.jpeg')):
            format = "JPEG"
            quality = 90
        else:
            format = "PNG"
            quality = -1  # Максимальное качество для PNG
        
        # Сохраняем изображение
        if meme_pixmap.save(file_path, format, quality):
            # Добавляем в базу данных
            self.database.add_saved_meme(file_path)
            return file_path
        
        return None
    
    def copy_to_clipboard(self, parent_window, meme_pixmap):
        """
        Копирование мема в буфер обмена
        
        Args:
            parent_window: Родительское окно
            meme_pixmap: QPixmap мема
        """
        if not meme_pixmap.isNull():
            clipboard = parent_window.clipboard()
            clipboard.setPixmap(meme_pixmap)
    
    def get_export_formats(self):
        """
        Получение списка поддерживаемых форматов экспорта
        
        Returns:
            list: Список форматов
        """
        return ["PNG", "JPEG"]
    
    def get_default_save_path(self):
        """
        Получение пути для сохранения по умолчанию
        
        Returns:
            str: Путь для сохранения
        """
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        return os.path.join(desktop_path, filename)