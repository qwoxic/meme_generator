from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from .constants import BUTTON_STYLE

class TextStyleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Стиль текста")
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A2E;
                color: white;
                font-family: Arial;
            }
            QLabel {
                color: #E6E6FA;
                font-size: 12px;
                padding: 3px;
            }
            QFontComboBox, QSpinBox, QComboBox {
                background-color: #16213E;
                color: white;
                border: 1px solid #8A2BE2;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                selection-background-color: #8A2BE2;
            }
            QCheckBox {
                color: #E6E6FA;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #8A2BE2;
                border-radius: 3px;
                background-color: #16213E;
            }
            QCheckBox::indicator:checked {
                background-color: #8A2BE2;
            }
        """)
        self.text_color = QColor(255, 255, 255)
        self.outline_color = QColor(0, 0, 0)
        self.init_ui()
        self.center_window()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Шрифт:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Impact"))
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Размер:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 150)
        self.size_spin.setValue(48)
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)
        
        colors_layout = QGridLayout()
        
        self.color_btn = QPushButton("Цвет текста")
        self.color_btn.setStyleSheet(BUTTON_STYLE)
        self.color_btn.clicked.connect(self.choose_color)
        
        self.outline_btn = QPushButton("Цвет обводки")
        self.outline_btn.setStyleSheet(BUTTON_STYLE)
        self.outline_btn.clicked.connect(self.choose_outline_color)
        
        colors_layout.addWidget(self.color_btn, 0, 0)
        colors_layout.addWidget(self.outline_btn, 0, 1)
        
        layout.addLayout(colors_layout)
        
        self.outline_cb = QCheckBox("Обводка")
        self.shadow_cb = QCheckBox("Тень")
        self.gradient_cb = QCheckBox("Градиент")
        
        layout.addWidget(self.outline_cb)
        layout.addWidget(self.shadow_cb)
        layout.addWidget(self.gradient_cb)
        
        gradient_layout = QHBoxLayout()
        gradient_layout.addWidget(QLabel("Тип градиента:"))
        self.gradient_combo = QComboBox()
        self.gradient_combo.addItems(["Линейный", "Радиальный", "Конический"])
        gradient_layout.addWidget(self.gradient_combo)
        layout.addLayout(gradient_layout)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Применить")
        ok_btn.setStyleSheet(BUTTON_STYLE)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(BUTTON_STYLE)
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def choose_color(self):
        color = QColorDialog.getColor(self.text_color, self, "Выберите цвет текста")
        if color.isValid():
            self.text_color = color
    
    def choose_outline_color(self):
        color = QColorDialog.getColor(self.outline_color, self, "Выберите цвет обводки")
        if color.isValid():
            self.outline_color = color
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 2 - 200,
            screen.height() // 2 - 200,
            400, 400
        )
