from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import QRectF

class MemeRenderer:
    @staticmethod
    def render_meme(image_pixmap, text_items):
        result_pixmap = QPixmap(image_pixmap.size())
        result_pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(result_pixmap)
        painter.drawPixmap(0, 0, image_pixmap)
        
        for item in text_items:
            if item['text'].strip():
                MemeRenderer._draw_text_item(painter, result_pixmap.rect(), item)
        
        painter.end()
        return result_pixmap
    
    @staticmethod
    def _draw_text_item(painter, rect, item):
        from .text_manager import TextManager
        
        rectf = QRectF(rect)
        
        if item['position'] == 'top':
            text_rect = QRectF(0, 10, rectf.width(), rectf.height() // 2 - 10)
            alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        else:
            text_rect = QRectF(0, rectf.height() // 2, rectf.width(), rectf.height() // 2 - 10)
            alignment = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        
        TextManager.draw_text(
            painter, text_rect, item['text'], alignment,
            item['style']['font'], item['style']['size'],
            item['style']['color'], item['style']['outline_color'],
            item['style']['has_outline'], item['style']['has_shadow'],
            item['style']['gradient_type'] if item['style']['has_gradient'] else None
        )
