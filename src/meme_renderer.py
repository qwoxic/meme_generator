from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import QRectF

class MemeRenderer:
    @staticmethod
    def render_meme(image_pixmap, text_items):
        """
        Рендеринг финального изображения с текстом
        
        Args:
            image_pixmap: Исходное изображение
            text_items: Список текстовых элементов
        
        Returns:
            QPixmap: Готовый мем
        """
        # Создаем новый pixmap с размерами изображения
        result_pixmap = QPixmap(image_pixmap.size())
        result_pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(result_pixmap)
        
        # Рисуем фоновое изображение
        painter.drawPixmap(0, 0, image_pixmap)
        
        # Рисуем все текстовые элементы
        for text_item in text_items:
            if text_item:
                # Сохраняем состояние painter
                painter.save()
                
                # Перемещаем painter к позиции текста
                painter.translate(text_item.pos())
                
                # Рисуем текстовый элемент
                text_item.paint(painter, None, None)
                
                # Восстанавливаем состояние painter
                painter.restore()
        
        painter.end()
        
        return result_pixmap
    
    @staticmethod
    def render_to_image(meme_pixmap, quality=90):
        """
        Конвертация QPixmap в QImage
        
        Args:
            meme_pixmap: QPixmap мема
            quality: Качество изображения (1-100)
        
        Returns:
            QImage: Изображение мема
        """
        image = meme_pixmap.toImage()
        return image