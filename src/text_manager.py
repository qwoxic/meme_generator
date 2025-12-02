from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem

class DraggableTextItem(QGraphicsTextItem):
    """Перетаскиваемый текстовый элемент"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setDefaultTextColor(QColor("#FFFFFF"))
        self.setFont(QFont("Arial", 36))
        
        self.stroke_color = QColor("#000000")
        self.stroke_width = 2
        
        self.setAcceptHoverEvents(True)
    
    def paint(self, painter, option, widget=None):
        """Отрисовка текста с обводкой"""
        # Рисуем обводку
        if self.stroke_width > 0:
            painter.setPen(QPen(
                self.stroke_color,
                self.stroke_width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            ))
            
            path = QPainterPath()
            path.addText(0, 0, self.font(), self.toPlainText())
            painter.drawPath(path)
        
        # Рисуем основной текст
        painter.setPen(QPen(self.defaultTextColor()))
        super().paint(painter, option, widget)
    
    def set_stroke(self, color, width):
        """Установка параметров обводки"""
        self.stroke_color = QColor(color)
        self.stroke_width = width
        self.update()

class TextManager:
    def __init__(self, scene):
        self.scene = scene
        self.top_text_item = None
        self.bottom_text_item = None
        
    def add_top_text(self, text="Верхний текст"):
        """Добавление верхнего текста"""
        if self.top_text_item:
            self.scene.removeItem(self.top_text_item)
        
        self.top_text_item = DraggableTextItem(text)
        self.scene.addItem(self.top_text_item)
        self.update_text_positions()
        return self.top_text_item
    
    def add_bottom_text(self, text="Нижний текст"):
        """Добавление нижнего текста"""
        if self.bottom_text_item:
            self.scene.removeItem(self.bottom_text_item)
        
        self.bottom_text_item = DraggableTextItem(text)
        self.scene.addItem(self.bottom_text_item)
        self.update_text_positions()
        return self.bottom_text_item
    
    def update_text_positions(self, image_width=0, image_height=0):
        """Обновление позиций текста"""
        if self.top_text_item:
            text_rect = self.top_text_item.boundingRect()
            x = (image_width - text_rect.width()) / 2 if image_width > 0 else 10
            self.top_text_item.setPos(x, 10)
        
        if self.bottom_text_item and image_height > 0:
            text_rect = self.bottom_text_item.boundingRect()
            x = (image_width - text_rect.width()) / 2 if image_width > 0 else 10
            y = image_height - text_rect.height() - 10
            self.bottom_text_item.setPos(x, y)
    
    def clear_all_text(self):
        """Удаление всего текста"""
        if self.top_text_item:
            self.scene.removeItem(self.top_text_item)
            self.top_text_item = None
        
        if self.bottom_text_item:
            self.scene.removeItem(self.bottom_text_item)
            self.bottom_text_item = None
    
    def get_text_settings(self, is_top_text=True):
        """Получение настроек текста"""
        text_item = self.top_text_item if is_top_text else self.bottom_text_item
        if text_item:
            return {
                'text': text_item.toPlainText(),
                'font_family': text_item.font().family(),
                'font_size': text_item.font().pointSize(),
                'text_color': text_item.defaultTextColor().name(),
                'stroke_color': text_item.stroke_color.name(),
                'stroke_width': text_item.stroke_width
            }
        return None
    
    def set_text_settings(self, settings, is_top_text=True):
        """Установка настроек текста"""
        text_item = self.top_text_item if is_top_text else self.bottom_text_item
        if text_item and settings:
            font = QFont(
                settings.get('font_family', 'Arial'),
                settings.get('font_size', 36)
            )
            text_item.setFont(font)
            text_item.setDefaultTextColor(QColor(settings.get('text_color', '#FFFFFF')))
            text_item.set_stroke(
                settings.get('stroke_color', '#000000'),
                settings.get('stroke_width', 2)
            )
            text_item.update()
    
    def has_text(self):
        """Проверка наличия текста"""
        return self.top_text_item is not None or self.bottom_text_item is not None