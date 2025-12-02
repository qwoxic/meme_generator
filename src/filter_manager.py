from PyQt6.QtGui import QImage, QColor
from PyQt6.QtCore import QRect
import random

class FilterManager:
    @staticmethod
    def apply_filter(image, filter_name, intensity=1.0):
        """
        Применение фильтра к изображению
        
        Args:
            image: QImage
            filter_name: Название фильтра
            intensity: Интенсивность (0.0 - 1.0)
        
        Returns:
            QImage: Обработанное изображение
        """
        if filter_name == "Нет фильтра":
            return image
        
        result = image.copy()
        
        if filter_name == "Черно-белый":
            return FilterManager._apply_grayscale(result)
        elif filter_name == "Сепия":
            return FilterManager._apply_sepia(result, intensity)
        elif filter_name == "Размытие":
            return FilterManager._apply_blur(result, intensity)
        elif filter_name == "Инверсия":
            return FilterManager._apply_invert(result)
        elif filter_name == "Старое фото":
            return FilterManager._apply_vintage(result, intensity)
        elif filter_name == "Повышенная яркость":
            return FilterManager._apply_brightness(result, intensity)
        elif filter_name == "Повышенный контраст":
            return FilterManager._apply_contrast(result, intensity)
        
        return result
    
    @staticmethod
    def _apply_grayscale(image):
        """Применение черно-белого фильтра"""
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                gray = int(color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114)
                image.setPixelColor(x, y, QColor(gray, gray, gray, color.alpha()))
        return image
    
    @staticmethod
    def _apply_sepia(image, intensity):
        """Применение сепии"""
        depth = int(30 * intensity)
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                r = min(255, color.red() + depth * 2)
                g = min(255, color.green() + depth)
                b = max(0, color.blue() - depth)
                image.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
        return image
    
    @staticmethod
    def _apply_blur(image, intensity):
        """Простое размытие"""
        radius = int(3 * intensity)
        if radius < 1:
            return image
            
        result = image.copy()
        for x in range(radius, image.width() - radius):
            for y in range(radius, image.height() - radius):
                r_sum = g_sum = b_sum = 0
                count = 0
                
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        color = image.pixelColor(x + dx, y + dy)
                        r_sum += color.red()
                        g_sum += color.green()
                        b_sum += color.blue()
                        count += 1
                
                if count > 0:
                    result.setPixelColor(x, y, QColor(
                        r_sum // count,
                        g_sum // count,
                        b_sum // count,
                        image.pixelColor(x, y).alpha()
                    ))
        return result
    
    @staticmethod
    def _apply_invert(image):
        """Инверсия цветов"""
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                image.setPixelColor(x, y, QColor(
                    255 - color.red(),
                    255 - color.green(),
                    255 - color.blue(),
                    color.alpha()
                ))
        return image
    
    @staticmethod
    def _apply_vintage(image, intensity):
        """Эффект старого фото"""
        image = FilterManager._apply_sepia(image, intensity)
        
        # Добавляем шум
        noise = int(10 * intensity)
        for x in range(image.width()):
            for y in range(image.height()):
                if random.random() < 0.02:  # 2% пикселей делаем шумом
                    color = image.pixelColor(x, y)
                    noise_val = random.randint(-noise, noise)
                    r = max(0, min(255, color.red() + noise_val))
                    g = max(0, min(255, color.green() + noise_val))
                    b = max(0, min(255, color.blue() + noise_val))
                    image.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
        return image
    
    @staticmethod
    def _apply_brightness(image, intensity):
        """Увеличение яркости"""
        factor = 1.0 + (intensity * 0.5)  # от 1.0 до 1.5
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                r = min(255, int(color.red() * factor))
                g = min(255, int(color.green() * factor))
                b = min(255, int(color.blue() * factor))
                image.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
        return image
    
    @staticmethod
    def _apply_contrast(image, intensity):
        """Увеличение контрастности"""
        factor = 1.0 + (intensity * 0.5)  # от 1.0 до 1.5
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                r = int((color.red() - 127) * factor + 127)
                g = int((color.green() - 127) * factor + 127)
                b = int((color.blue() - 127) * factor + 127)
                
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                image.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
        return image
