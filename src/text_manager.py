from PyQt6.QtGui import QPainter, QPen, QFont, QColor, QBrush, QLinearGradient, QRadialGradient, QConicalGradient
from PyQt6.QtCore import Qt, QPointF

class TextManager:
    @staticmethod
    def draw_text(painter, rect, text, alignment, font_family, font_size, 
                  text_color, outline_color, has_outline, has_shadow, gradient_type=None):
        if not text.strip():
            return
        
        font = QFont(font_family, font_size)
        font.setBold(True)
        painter.setFont(font)
        
        if gradient_type:
            gradient = TextManager._create_gradient(rect, gradient_type)
            painter.setPen(QPen(QBrush(gradient), 2))
        else:
            painter.setPen(QPen(text_color, 2))
        
        if has_outline:
            TextManager._draw_outline(painter, rect, text, alignment, outline_color)
        
        if has_shadow:
            TextManager._draw_shadow(painter, rect, text, alignment)
        
        painter.drawText(rect, alignment, text)
    
    @staticmethod
    def _draw_outline(painter, rect, text, alignment, outline_color):
        painter.save()
        outline_pen = QPen(outline_color)
        outline_pen.setWidth(6)
        painter.setPen(outline_pen)
        
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in offsets:
            outline_rect = rect.translated(dx, dy)
            painter.drawText(outline_rect, alignment, text)
        
        painter.restore()
    
    @staticmethod
    def _draw_shadow(painter, rect, text, alignment):
        painter.save()
        shadow_color = QColor(0, 0, 0, 150)
        shadow_pen = QPen(shadow_color)
        shadow_pen.setWidth(3)
        painter.setPen(shadow_pen)
        
        shadow_rect = rect.translated(2, 2)
        painter.drawText(shadow_rect, alignment, text)
        
        painter.restore()
    
    @staticmethod
    def _create_gradient(rect, gradient_type):
        if gradient_type == "Линейный":
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        elif gradient_type == "Радиальный":
            center = QPointF(rect.center())
            gradient = QRadialGradient(center, min(rect.width(), rect.height()) / 2)
        else:
            center = QPointF(rect.center())
            gradient = QConicalGradient(center, 45)
        
        gradient.setColorAt(0, QColor(255, 0, 0))
        gradient.setColorAt(0.5, QColor(0, 255, 0))
        gradient.setColorAt(1, QColor(0, 0, 255))
        
        return gradient
