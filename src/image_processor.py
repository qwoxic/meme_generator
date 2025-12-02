from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class ImageProcessor:
    def __init__(self):
        self.original_pixmap = None
        self.current_pixmap = None
        self.image_path = None
    
    def load_image(self, image_path):
        """Загрузка изображения"""
        self.image_path = image_path
        self.original_pixmap = QPixmap(image_path)
        self.current_pixmap = self.original_pixmap.copy()
        return self.current_pixmap
    
    def reset_image(self):
        """Сброс изображения к исходному состоянию"""
        if self.original_pixmap:
            self.current_pixmap = self.original_pixmap.copy()
        return self.current_pixmap
    
    def scale_image(self, width, height):
        """Масштабирование изображения"""
        if self.current_pixmap:
            self.current_pixmap = self.original_pixmap.scaled(
                width, height, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        return self.current_pixmap
    
    def get_image_size(self):
        """Получение размеров изображения"""
        if self.current_pixmap:
            return self.current_pixmap.width(), self.current_pixmap.height()
        return 0, 0
    
    def get_original_image(self):
        """Получение оригинального изображения"""
        return self.original_pixmap
    
    def get_current_image(self):
        """Получение текущего изображения"""
        return self.current_pixmap
    
    def has_image(self):
        """Проверка наличия изображения"""
        return self.current_pixmap is not None and not self.current_pixmap.isNull()