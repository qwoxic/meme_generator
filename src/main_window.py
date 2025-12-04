import sys
import os
import random
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from .constants import *
from .database import Database
from .image_processor import ImageProcessor
from .text_manager import TextManager
from .meme_renderer import MemeRenderer
from .export_manager import ExportManager
from .filter_manager import FilterManager
from .random_meme_generator import RandomMemeGenerator
from .statistics_dialog import StatisticsDialog
from .text_style_dialog import TextStyleDialog

class MemeGeneratorPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.export_manager = ExportManager()
        self.current_image_id = None
        self.current_meme_id = None
        self.original_pixmap = None
        self.current_pixmap = None
        self.text_edit_visible = None
        self.displayed_pixmap = None
        
        self.top_text_style = {
            'font': 'Impact',
            'size': 48,
            'color': QColor(255, 255, 255),
            'outline_color': QColor(0, 0, 0),
            'has_outline': True,
            'has_shadow': False,
            'has_gradient': False,
            'gradient_type': 'Линейный'
        }
        
        self.bottom_text_style = {
            'font': 'Impact',
            'size': 48,
            'color': QColor(255, 255, 255),
            'outline_color': QColor(0, 0, 0),
            'has_outline': True,
            'has_shadow': False,
            'has_gradient': False,
            'gradient_type': 'Линейный'
        }
        
        self.init_ui()
        self.showMaximized()
        self.load_settings()
    
    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A2E;
                color: white;
                font-family: Arial;
            }
            QTextEdit {
                background-color: rgba(22, 33, 62, 0.9);
                color: white;
                border: 2px solid #8A2BE2;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                selection-background-color: #8A2BE2;
            }
            QLabel {
                color: #E6E6FA;
                font-size: 12px;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #8A2BE2;
                height: 8px;
                background: #16213E;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8A2BE2, stop:1 #4169E1);
                border: 2px solid #9370DB;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QComboBox {
                background-color: #16213E;
                color: white;
                border: 2px solid #8A2BE2;
                border-radius: 5px;
                padding: 6px;
                font-size: 12px;
                selection-background-color: #8A2BE2;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                border-left: 3px solid white;
                border-bottom: 3px solid white;
                margin-right: 10px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)
        
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)
        
        file_group = QGroupBox("📁 Файл")
        file_group.setStyleSheet(GROUP_BOX_STYLE)
        file_layout = QVBoxLayout()
        file_layout.setSpacing(5)
        
        self.load_btn = QPushButton("📂 Загрузить изображение (Ctrl+O)")
        self.load_btn.setStyleSheet(BUTTON_STYLE)
        self.load_btn.clicked.connect(self.load_image)
        self.load_btn.setShortcut("Ctrl+O")
        file_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Сохранить мем (Ctrl+S)")
        self.save_btn.setStyleSheet(BUTTON_STYLE)
        self.save_btn.clicked.connect(self.save_meme)
        self.save_btn.setShortcut("Ctrl+S")
        self.save_btn.setEnabled(False)
        file_layout.addWidget(self.save_btn)
        
        self.copy_btn = QPushButton("📋 Копировать в буфер (Ctrl+C)")
        self.copy_btn.setStyleSheet(BUTTON_STYLE)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setShortcut("Ctrl+C")
        file_layout.addWidget(self.copy_btn)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        text_group = QGroupBox("📝 Текст")
        text_group.setStyleSheet(GROUP_BOX_STYLE)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        text_buttons_layout = QHBoxLayout()
        
        self.top_text_btn = QPushButton("⬆️ Верх")
        self.top_text_btn.setStyleSheet(BUTTON_STYLE)
        self.top_text_btn.clicked.connect(lambda: self.show_text_input('top'))
        
        self.bottom_text_btn = QPushButton("⬇️ Низ")
        self.bottom_text_btn.setStyleSheet(BUTTON_STYLE)
        self.bottom_text_btn.clicked.connect(lambda: self.show_text_input('bottom'))
        
        text_buttons_layout.addWidget(self.top_text_btn)
        text_buttons_layout.addWidget(self.bottom_text_btn)
        
        text_layout.addLayout(text_buttons_layout)
        
        self.style_btn = QPushButton("🎨 Стиль текста...")
        self.style_btn.setStyleSheet(BUTTON_STYLE)
        self.style_btn.clicked.connect(self.open_text_style_dialog)
        text_layout.addWidget(self.style_btn)
        
        self.clear_text_btn = QPushButton("🗑️ Очистить текст")
        self.clear_text_btn.setStyleSheet(BUTTON_STYLE)
        self.clear_text_btn.clicked.connect(self.clear_all_text)
        text_layout.addWidget(self.clear_text_btn)
        
        text_group.setLayout(text_layout)
        left_layout.addWidget(text_group)
        
        effects_group = QGroupBox("🎭 Эффекты")
        effects_group.setStyleSheet(GROUP_BOX_STYLE)
        effects_layout = QVBoxLayout()
        effects_layout.setSpacing(8)
        
        effects_layout.addWidget(QLabel("Фильтр:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Нет", "Черно-белый", "Сепия", "Размытие", "Контраст", "Яркость"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        effects_layout.addWidget(self.filter_combo)
        
        effects_layout.addWidget(QLabel("Яркость:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        effects_layout.addWidget(self.brightness_slider)
        
        effects_layout.addWidget(QLabel("Контраст:"))
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)
        effects_layout.addWidget(self.contrast_slider)
        
        self.reset_filters_btn = QPushButton("🔄 Сбросить фильтры")
        self.reset_filters_btn.setStyleSheet(BUTTON_STYLE)
        self.reset_filters_btn.clicked.connect(self.reset_filters)
        effects_layout.addWidget(self.reset_filters_btn)
        
        effects_group.setLayout(effects_layout)
        left_layout.addWidget(effects_group)
        
        tools_group = QGroupBox("🛠️ Инструменты")
        tools_group.setStyleSheet(GROUP_BOX_STYLE)
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(5)
        
        self.random_btn = QPushButton("🎲 Случайный мем (Ctrl+R)")
        self.random_btn.setStyleSheet(BUTTON_STYLE)
        self.random_btn.clicked.connect(self.generate_random_meme)
        self.random_btn.setShortcut("Ctrl+R")
        tools_layout.addWidget(self.random_btn)
        
        self.stats_btn = QPushButton("📊 Статистика (F2)")
        self.stats_btn.setStyleSheet(BUTTON_STYLE)
        self.stats_btn.clicked.connect(self.show_statistics)
        self.stats_btn.setShortcut("F2")
        tools_layout.addWidget(self.stats_btn)
        
        self.history_btn = QPushButton("📜 История (F3)")
        self.history_btn.setStyleSheet(BUTTON_STYLE)
        self.history_btn.clicked.connect(self.show_history)
        self.history_btn.setShortcut("F3")
        tools_layout.addWidget(self.history_btn)
        
        tools_group.setLayout(tools_layout)
        left_layout.addWidget(tools_group)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_panel.setLayout(right_layout)
        
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.image_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0A0A1A;
            }
            QScrollBar:vertical {
                border: none;
                background: #16213E;
                width: 14px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #8A2BE2;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #16213E;
                height: 14px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #8A2BE2;
                border-radius: 7px;
                min-width: 30px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        self.image_container = QWidget()
        self.image_container.setStyleSheet("background-color: #0A0A1A;")
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setContentsMargins(20, 20, 20, 20)
        self.image_layout.setSpacing(0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0A0A1A;
            }
        """)
        self.image_label.setText("")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.image_layout.addWidget(self.image_label)
        self.image_scroll.setWidget(self.image_container)
        
        right_layout.addWidget(self.image_scroll, stretch=1)
        
        self.text_input_panel = QWidget()
        self.text_input_panel.setFixedHeight(120)
        self.text_input_panel.setStyleSheet("""
            background-color: rgba(22, 33, 62, 0.95); 
            padding: 10px;
            border-top: 2px solid #8A2BE2;
        """)
        text_input_layout = QVBoxLayout(self.text_input_panel)
        
        self.text_input_label = QLabel("Редактирование текста:")
        self.text_input_label.setStyleSheet("color: #E6E6FA; font-weight: bold; font-size: 14px;")
        text_input_layout.addWidget(self.text_input_label)
        
        text_edits_layout = QHBoxLayout()
        
        self.top_text_edit = QTextEdit()
        self.top_text_edit.setMaximumHeight(50)
        self.top_text_edit.setPlaceholderText("Введите верхний текст...")
        self.top_text_edit.textChanged.connect(self.update_preview)
        self.top_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(10, 10, 26, 0.9);
                color: white;
                border: 2px solid #8A2BE2;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.bottom_text_edit = QTextEdit()
        self.bottom_text_edit.setMaximumHeight(50)
        self.bottom_text_edit.setPlaceholderText("Введите нижний текст...")
        self.bottom_text_edit.textChanged.connect(self.update_preview)
        self.bottom_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(10, 10, 26, 0.9);
                color: white;
                border: 2px solid #8A2BE2;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        text_edits_layout.addWidget(self.top_text_edit)
        text_edits_layout.addWidget(self.bottom_text_edit)
        
        text_input_layout.addLayout(text_edits_layout)
        self.text_input_panel.hide()
        
        right_layout.addWidget(self.text_input_panel)
        
        main_layout.addWidget(right_panel, stretch=1)
        
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        self.load_recent_images()
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Все файлы (*)"
        )
        if file_path:
            self.original_pixmap = ImageProcessor.load_image(file_path)
            if not self.original_pixmap.isNull():
                self.current_pixmap = self.original_pixmap.copy()
                self.displayed_pixmap = None
                self.update_preview()
                self.save_btn.setEnabled(True)
                self.current_image_id = self.db.save_image(
                    file_path, 
                    self.original_pixmap.width(),
                    self.original_pixmap.height()
                )
                self.db.save_setting('last_image_path', file_path)
                self.filter_combo.setCurrentIndex(0)
                self.brightness_slider.setValue(100)
                self.contrast_slider.setValue(100)
                self.text_input_panel.hide()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
    
    def show_text_input(self, position):
        self.text_input_panel.show()
        self.text_input_panel.raise_()
        
        if position == 'top':
            self.top_text_edit.show()
            self.bottom_text_edit.hide()
            self.top_text_edit.setFocus()
            self.text_input_label.setText("Редактирование ВЕРХНЕГО текста:")
        else:
            self.top_text_edit.hide()
            self.bottom_text_edit.show()
            self.bottom_text_edit.setFocus()
            self.text_input_label.setText("Редактирование НИЖНЕГО текста:")
    
    def open_text_style_dialog(self):
        dialog = TextStyleDialog(self)
        dialog.font_combo.setCurrentFont(QFont(self.top_text_style['font']))
        dialog.size_spin.setValue(self.top_text_style['size'])
        dialog.text_color = self.top_text_style['color']
        dialog.outline_color = self.top_text_style['outline_color']
        dialog.outline_cb.setChecked(self.top_text_style['has_outline'])
        dialog.shadow_cb.setChecked(self.top_text_style['has_shadow'])
        dialog.gradient_cb.setChecked(self.top_text_style['has_gradient'])
        
        if self.top_text_style['gradient_type'] == "Линейный":
            dialog.gradient_combo.setCurrentIndex(0)
        elif self.top_text_style['gradient_type'] == "Радиальный":
            dialog.gradient_combo.setCurrentIndex(1)
        else:
            dialog.gradient_combo.setCurrentIndex(2)
        
        if dialog.exec():
            self.top_text_style['font'] = dialog.font_combo.currentFont().family()
            self.top_text_style['size'] = dialog.size_spin.value()
            self.top_text_style['color'] = dialog.text_color
            self.top_text_style['outline_color'] = dialog.outline_color
            self.top_text_style['has_outline'] = dialog.outline_cb.isChecked()
            self.top_text_style['has_shadow'] = dialog.shadow_cb.isChecked()
            self.top_text_style['has_gradient'] = dialog.gradient_cb.isChecked()
            
            gradient_text = dialog.gradient_combo.currentText()
            if gradient_text == "Линейный":
                self.top_text_style['gradient_type'] = "Линейный"
            elif gradient_text == "Радиальный":
                self.top_text_style['gradient_type'] = "Радиальный"
            else:
                self.top_text_style['gradient_type'] = "Конический"
            
            self.bottom_text_style.update(self.top_text_style)
            self.update_preview()
    
    def update_preview(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            pixmap = self.current_pixmap.copy()
            
            top_text = self.top_text_edit.toPlainText().strip()
            bottom_text = self.bottom_text_edit.toPlainText().strip()
            
            if top_text or bottom_text:
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                if top_text:
                    base_size = self.top_text_style['size']
                    scaled_size = int(base_size * (min(pixmap.width(), pixmap.height()) / 800))
                    scaled_size = max(20, min(scaled_size, 100))
                    
                    rect = QRect(20, 20, pixmap.width() - 40, pixmap.height() // 3)
                    TextManager.draw_text(
                        painter, rect, top_text,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                        self.top_text_style['font'],
                        scaled_size,
                        self.top_text_style['color'],
                        self.top_text_style['outline_color'],
                        self.top_text_style['has_outline'],
                        self.top_text_style['has_shadow'],
                        self.top_text_style['gradient_type'] if self.top_text_style['has_gradient'] else None
                    )
                
                if bottom_text:
                    base_size = self.bottom_text_style['size']
                    scaled_size = int(base_size * (min(pixmap.width(), pixmap.height()) / 800))
                    scaled_size = max(20, min(scaled_size, 100))
                    
                    rect = QRect(20, pixmap.height() * 2 // 3, 
                               pixmap.width() - 40, pixmap.height() // 3 - 20)
                    TextManager.draw_text(
                        painter, rect, bottom_text,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                        self.bottom_text_style['font'],
                        scaled_size,
                        self.bottom_text_style['color'],
                        self.bottom_text_style['outline_color'],
                        self.bottom_text_style['has_outline'],
                        self.bottom_text_style['has_shadow'],
                        self.bottom_text_style['gradient_type'] if self.bottom_text_style['has_gradient'] else None
                    )
                
                painter.end()
            
            self.displayed_pixmap = pixmap
            self.show_pixmap(pixmap)
        elif self.original_pixmap:
            self.show_pixmap(self.original_pixmap)
        else:
            self.image_label.setText("Загрузите изображение\n(Поддерживаются форматы: PNG, JPG, JPEG, BMP, GIF, WEBP)")
            self.image_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #0A0A1A;
                    color: #8A2BE2;
                    font-weight: bold;
                    padding: 50px;
                }
            """)
    
    def show_pixmap(self, pixmap):
        if pixmap.isNull():
            return

        scroll_viewport = self.image_scroll.viewport()
        available_size = scroll_viewport.size()

        pixmap_size = pixmap.size()

        scaled = pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)
        self.image_label.setText("")

        if scaled.width() < available_size.width() and scaled.height() < available_size.height():
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_label.setMinimumSize(scaled.size())
        else:
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            self.image_label.setMinimumSize(QSize(0, 0))
        
        self.image_label.update()
    
    def apply_filter(self, filter_name):
        if self.original_pixmap:
            filtered = FilterManager.apply_filter(self.original_pixmap, filter_name)
            
            brightness_factor = self.brightness_slider.value() / 100.0
            if brightness_factor != 1.0:
                filtered = FilterManager.adjust_brightness(filtered, brightness_factor)
            
            contrast_factor = self.contrast_slider.value() / 100.0
            if contrast_factor != 1.0:
                filtered = FilterManager.adjust_contrast(filtered, contrast_factor)
            
            self.current_pixmap = filtered
            self.update_preview()
    
    def adjust_brightness(self, value):
        if self.original_pixmap:
            self.apply_filter(self.filter_combo.currentText())
    
    def adjust_contrast(self, value):
        if self.original_pixmap:
            self.apply_filter(self.filter_combo.currentText())
    
    def reset_filters(self):
        self.filter_combo.setCurrentIndex(0)
        self.brightness_slider.setValue(100)
        self.contrast_slider.setValue(100)
        if self.original_pixmap:
            self.current_pixmap = self.original_pixmap.copy()
            self.update_preview()
    
    def save_meme(self):
        if not self.current_pixmap or self.current_pixmap.isNull():
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить мем", "my_meme.png",
            "PNG Изображения (*.png);;JPEG Изображения (*.jpg *.jpeg);;Все файлы (*)"
        )
        
        if file_path:
            pixmap = self.current_pixmap.copy()
            
            top_text = self.top_text_edit.toPlainText().strip()
            bottom_text = self.bottom_text_edit.toPlainText().strip()
            
            if top_text or bottom_text:
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                
                if top_text:
                    rect = QRect(20, 20, pixmap.width() - 40, pixmap.height() // 3)
                    TextManager.draw_text(
                        painter, rect, top_text,
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                        self.top_text_style['font'],
                        self.top_text_style['size'],
                        self.top_text_style['color'],
                        self.top_text_style['outline_color'],
                        self.top_text_style['has_outline'],
                        self.top_text_style['has_shadow'],
                        self.top_text_style['gradient_type'] if self.top_text_style['has_gradient'] else None
                    )
                
                if bottom_text:
                    rect = QRect(20, pixmap.height() * 2 // 3, 
                               pixmap.width() - 40, pixmap.height() // 3 - 20)
                    TextManager.draw_text(
                        painter, rect, bottom_text,
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                        self.bottom_text_style['font'],
                        self.bottom_text_style['size'],
                        self.bottom_text_style['color'],
                        self.bottom_text_style['outline_color'],
                        self.bottom_text_style['has_outline'],
                        self.bottom_text_style['has_shadow'],
                        self.bottom_text_style['gradient_type'] if self.bottom_text_style['has_gradient'] else None
                    )
                
                painter.end()
            
            if pixmap.save(file_path):
                self.current_meme_id = self.db.save_meme(
                    self.current_image_id,
                    self.top_text_edit.toPlainText(),
                    self.bottom_text_edit.toPlainText(),
                    self.top_text_style['size'],
                    self.top_text_style['color'].name(),
                    self.top_text_style['outline_color'].name(),
                    self.top_text_style['has_outline'],
                    self.top_text_style['has_shadow'],
                    file_path
                )
                
                self.db.increment_downloads(self.current_meme_id)
                QMessageBox.information(self, "Успех", "Мем успешно сохранен!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")
    
    def copy_to_clipboard(self):
        if self.displayed_pixmap and not self.displayed_pixmap.isNull():
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(self.displayed_pixmap)
    
    def export_statistics(self):
        dialog = StatisticsDialog(self.db, self)
        dialog.exec()
    
    def show_statistics(self):
        dialog = StatisticsDialog(self.db, self)
        dialog.exec()
    
    def show_history(self):
        recent = self.db.get_recent_memes()
        if recent:
            dialog = QDialog(self)
            dialog.setWindowTitle("История мемов")
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1A1A2E;
                    color: white;
                }
                QListWidget {
                    background-color: #16213E;
                    color: white;
                    border: 1px solid #8A2BE2;
                    border-radius: 5px;
                    font-size: 12px;
                }
            """)
            
            screen = QApplication.primaryScreen().geometry()
            dialog.setGeometry(
                screen.width() // 2 - 250,
                screen.height() // 2 - 150,
                500, 300
            )
            
            layout = QVBoxLayout()
            list_widget = QListWidget()
            
            for path in recent:
                if os.path.exists(path):
                    item = QListWidgetItem(os.path.basename(path))
                    item.file_path = path
                    list_widget.addItem(item)
            
            layout.addWidget(list_widget)
            
            button_layout = QHBoxLayout()
            open_btn = QPushButton("Открыть")
            open_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn = QPushButton("Удалить")
            delete_btn.setStyleSheet(BUTTON_STYLE)
            close_btn = QPushButton("Закрыть")
            close_btn.setStyleSheet(BUTTON_STYLE)
            
            open_btn.clicked.connect(lambda: self.open_meme_from_list(list_widget))
            delete_btn.clicked.connect(lambda: self.delete_meme_from_list(list_widget))
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(open_btn)
            button_layout.addWidget(delete_btn)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.exec()
        else:
            QMessageBox.information(self, "История", "Нет сохраненных мемов")
    
    def open_meme_from_list(self, list_widget):
        item = list_widget.currentItem()
        if item and hasattr(item, 'file_path'):
            if os.name == 'nt':
                os.startfile(item.file_path)
            else:
                os.system(f'xdg-open "{item.file_path}"')
    
    def delete_meme_from_list(self, list_widget):
        item = list_widget.currentItem()
        if item and hasattr(item, 'file_path'):
            reply = QMessageBox.question(
                self, "Удаление",
                f"Удалить '{os.path.basename(item.file_path)}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(item.file_path)
                    list_widget.takeItem(list_widget.row(item))
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось удалить: {str(e)}")
    
    def generate_random_meme(self):
        if not self.original_pixmap:
            recent = self.db.get_recent_images()
            if recent:
                self.original_pixmap = ImageProcessor.load_image(recent[0])
                self.current_pixmap = self.original_pixmap.copy()
            else:
                QMessageBox.warning(self, "Ошибка", "Нет доступных изображений")
                return
        
        random_text = random.choice(RANDOM_TEXTS)
        lines = random_text.split('\n')
        
        if len(lines) >= 2:
            self.top_text_edit.setText(lines[0])
            self.bottom_text_edit.setText('\n'.join(lines[1:]))
        else:
            if random.choice([True, False]):
                self.top_text_edit.setText(random_text)
                self.bottom_text_edit.clear()
            else:
                self.top_text_edit.clear()
                self.bottom_text_edit.setText(random_text)
        
        self.top_text_style['font'] = random.choice(AVAILABLE_FONTS)
        self.top_text_style['size'] = random.randint(30, 70)
        self.top_text_style['color'] = QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        self.top_text_style['has_outline'] = random.choice([True, False])
        self.top_text_style['has_shadow'] = random.choice([True, False])
        
        filter_choice = random.choice(['Нет', 'Черно-белый', 'Сепия', 'Размытие'])
        self.filter_combo.setCurrentText(filter_choice)
        self.apply_filter(filter_choice)
        
        self.update_preview()
        self.text_input_panel.show()
    
    def clear_all_text(self):
        self.top_text_edit.clear()
        self.bottom_text_edit.clear()
        self.update_preview()
    
    def load_settings(self):
        last_image = self.db.get_setting('last_image_path')
        if last_image and os.path.exists(last_image):
            self.original_pixmap = ImageProcessor.load_image(last_image)
            self.current_pixmap = self.original_pixmap.copy()
            self.update_preview()
            self.save_btn.setEnabled(True)
    
    def load_recent_images(self):
        pass
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'current_pixmap') and self.current_pixmap and not self.current_pixmap.isNull():
            self.show_pixmap(self.current_pixmap)
