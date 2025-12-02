import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGraphicsView, QGraphicsScene, QFileDialog,
    QMenuBar, QMenu, QStatusBar, QToolBar, QColorDialog, QFontDialog,
    QSpinBox, QComboBox, QMessageBox, QDialog,
    QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QInputDialog
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QPixmap, QColor, QFont, QPainter
)
from PyQt6.QtCore import Qt, QSize
import os

from .image_processor import ImageProcessor
from .text_manager import TextManager
from .meme_renderer import MemeRenderer
from .export_manager import ExportManager
from .database import Database
from .constants import Constants
from .filter_manager import FilterManager
from .random_meme_generator import RandomMemeGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Constants.APP_NAME} v{Constants.APP_VERSION}")
        self.setGeometry(100, 100, Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)
        
        self.database = Database()
        self.image_processor = ImageProcessor()
        self.export_manager = ExportManager(self.database)
        self.filter_manager = FilterManager()
        self.random_generator = RandomMemeGenerator(self.database, self.image_processor)
        
        self.current_filter = "Нет фильтра"
        self.meme_version_id = None
        
        self.init_ui()
        self.init_menus()
        self.init_toolbar()
        self.init_status_bar()
        self.load_saved_settings()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self.text_manager = TextManager(self.scene)
        
        tool_panel = self.create_tool_panel()
        
        main_layout.addWidget(tool_panel)
        main_layout.addWidget(self.graphics_view)
    
    def create_tool_panel(self):
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        self.btn_load_image = QPushButton("📷 Загрузить")
        self.btn_load_image.clicked.connect(self.load_image)
        layout.addWidget(self.btn_load_image)
        
        self.btn_reset_image = QPushButton("🔄 Сбросить")
        self.btn_reset_image.clicked.connect(self.reset_image)
        self.btn_reset_image.setEnabled(False)
        layout.addWidget(self.btn_reset_image)
        
        self.btn_random_meme = QPushButton("🎲 Случайный")
        self.btn_random_meme.clicked.connect(self.generate_random_meme)
        layout.addWidget(self.btn_random_meme)
        
        layout.addStretch()
        
        filter_label = QLabel("Фильтр:")
        layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(Constants.FILTERS)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_combo)
        
        layout.addStretch()
        
        self.btn_add_top_text = QPushButton("⬆ Верх")
        self.btn_add_top_text.clicked.connect(lambda: self.add_text(is_top=True))
        layout.addWidget(self.btn_add_top_text)
        
        self.btn_add_bottom_text = QPushButton("⬇ Низ")
        self.btn_add_bottom_text.clicked.connect(lambda: self.add_text(is_top=False))
        layout.addWidget(self.btn_add_bottom_text)
        
        self.btn_clear_text = QPushButton("❌ Очистить")
        self.btn_clear_text.clicked.connect(self.clear_text)
        layout.addWidget(self.btn_clear_text)
        
        layout.addStretch()
        
        self.btn_save_meme = QPushButton("💾 Сохранить")
        self.btn_save_meme.clicked.connect(self.save_meme)
        self.btn_save_meme.setEnabled(False)
        layout.addWidget(self.btn_save_meme)
        
        return panel
    
    def init_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Файл")
        
        load_action = QAction("Загрузить изображение", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)
        
        save_action = QAction("Сохранить мем", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_meme)
        file_menu.addAction(save_action)
        
        random_meme_action = QAction("Случайный мем", self)
        random_meme_action.setShortcut(QKeySequence("Ctrl+R"))
        random_meme_action.triggered.connect(self.generate_random_meme)
        file_menu.addAction(random_meme_action)
        
        file_menu.addSeparator()
        
        history_menu = file_menu.addMenu("История загрузок")
        self.update_history_menu(history_menu)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        text_menu = menubar.addMenu("Текст")
        
        top_text_action = QAction("Добавить верхний текст", self)
        top_text_action.setShortcut(QKeySequence("Ctrl+T"))
        top_text_action.triggered.connect(lambda: self.add_text(is_top=True))
        text_menu.addAction(top_text_action)
        
        bottom_text_action = QAction("Добавить нижний текст", self)
        bottom_text_action.setShortcut(QKeySequence("Ctrl+B"))
        bottom_text_action.triggered.connect(lambda: self.add_text(is_top=False))
        text_menu.addAction(bottom_text_action)
        
        text_menu.addSeparator()
        
        font_action = QAction("Шрифт...", self)
        font_action.triggered.connect(self.change_font)
        text_menu.addAction(font_action)
        
        color_action = QAction("Цвет текста...", self)
        color_action.triggered.connect(self.change_text_color)
        text_menu.addAction(color_action)
        
        stroke_action = QAction("Обводка текста...", self)
        stroke_action.triggered.connect(self.change_stroke)
        text_menu.addAction(stroke_action)
        
        text_menu.addSeparator()
        
        clear_text_action = QAction("Удалить весь текст", self)
        clear_text_action.triggered.connect(self.clear_text)
        text_menu.addAction(clear_text_action)
        
        reset_pos_action = QAction("Сбросить позиции текста", self)
        reset_pos_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        reset_pos_action.triggered.connect(self.reset_text_positions)
        text_menu.addAction(reset_pos_action)
        
        image_menu = menubar.addMenu("Изображение")
        
        filters_menu = image_menu.addMenu("Фильтры")
        for filter_name in Constants.FILTERS:
            action = QAction(filter_name, self)
            action.triggered.connect(lambda checked, f=filter_name: self.set_filter(f))
            filters_menu.addAction(action)
        
        reset_filter_action = QAction("Сбросить фильтры", self)
        reset_filter_action.triggered.connect(lambda: self.set_filter("Нет фильтра"))
        image_menu.addAction(reset_filter_action)
        
        history_menu = menubar.addMenu("История")
        
        versions_action = QAction("Версии мемов", self)
        versions_action.triggered.connect(self.show_meme_versions)
        history_menu.addAction(versions_action)
        
        random_history_action = QAction("История случайных мемов", self)
        random_history_action.triggered.connect(self.show_random_history)
        history_menu.addAction(random_history_action)
        
        view_menu = menubar.addMenu("Вид")
        
        zoom_in_action = QAction("Увеличить", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Уменьшить", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Сбросить масштаб", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
    
    def update_history_menu(self, history_menu):
        history_menu.clear()
        history = self.database.get_image_history()
        
        if not history:
            no_history_action = QAction("История пуста", self)
            no_history_action.setEnabled(False)
            history_menu.addAction(no_history_action)
        else:
            for image_path in history:
                filename = os.path.basename(image_path)
                action = QAction(filename, self)
                action.triggered.connect(
                    lambda checked, path=image_path: self.load_image_from_path(path)
                )
                history_menu.addAction(action)
    
    def init_toolbar(self):
        toolbar = self.addToolBar("Панель инструментов")
        toolbar.setMovable(False)
        
        toolbar.addAction("📷 Загрузить", self.load_image)
        toolbar.addSeparator()
        toolbar.addAction("🎲 Случайный", self.generate_random_meme)
        toolbar.addSeparator()
        toolbar.addAction("⬆ Верх", lambda: self.add_text(is_top=True))
        toolbar.addAction("⬇ Низ", lambda: self.add_text(is_top=False))
        toolbar.addSeparator()
        toolbar.addAction("💾 Сохранить", self.save_meme)
    
    def init_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def load_image(self):
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Несохраненные изменения",
                "У вас есть несохраненные изменения. Загрузить новое изображение?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            f"Изображения ({Constants.IMAGE_EXTENSIONS})"
        )
        
        if file_path:
            self.load_image_from_path(file_path)
    
    def load_image_from_path(self, file_path):
        pixmap = self.image_processor.load_image(file_path)
        
        if not pixmap.isNull():
            self.scene.clear()
            
            self.current_filter = "Нет фильтра"
            self.filter_combo.setCurrentText(self.current_filter)
            
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            self.database.add_image_to_history(file_path)
            
            file_menu = self.menuBar().findChild(QMenu, "Файл")
            if file_menu:
                for action in file_menu.actions():
                    if action.text() == "История загрузок":
                        history_menu = action.menu()
                        if history_menu:
                            self.update_history_menu(history_menu)
                            break
            
            self.btn_reset_image.setEnabled(True)
            self.btn_save_meme.setEnabled(True)
            self.btn_random_meme.setEnabled(True)
            
            width, height = self.image_processor.get_image_size()
            self.text_manager.update_text_positions(width, height)
            
            self.save_meme_version()
            
            self.status_bar.showMessage(f"Изображение загружено: {file_path}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
    
    def has_unsaved_changes(self):
        if self.text_manager.has_text():
            return True
        if self.current_filter != "Нет фильтра":
            return True
        return False
    
    def reset_image(self):
        self.current_filter = "Нет фильтра"
        self.filter_combo.setCurrentText(self.current_filter)
        
        pixmap = self.image_processor.reset_image()
        if not pixmap.isNull():
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.status_bar.showMessage("Изображение сброшено")
    
    def add_text(self, is_top=True):
        if not self.image_processor.has_image():
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        if is_top:
            if self.text_manager.top_text_item:
                QMessageBox.information(self, "Информация", "Верхний текст уже добавлен")
                return
            text_item = self.text_manager.add_top_text()
            default_text = "Верхний текст"
            settings = self.database.load_text_settings(is_top_text=True)
        else:
            if self.text_manager.bottom_text_item:
                QMessageBox.information(self, "Информация", "Нижний текст уже добавлен")
                return
            text_item = self.text_manager.add_bottom_text()
            default_text = "Нижний текст"
            settings = self.database.load_text_settings(is_top_text=False)
        
        text_item.setPlainText(default_text)
        
        if settings:
            self.text_manager.set_text_settings(settings, is_top)
        else:
            font = QFont("Arial", 36)
            text_item.setFont(font)
            text_item.setDefaultTextColor(QColor("#FFFFFF"))
            text_item.set_stroke("#000000", 2)
        
        self.status_bar.showMessage("Текст добавлен")
        self.save_text_settings(is_top)
    
    def clear_text(self):
        self.text_manager.clear_all_text()
        self.status_bar.showMessage("Текст очищен")
    
    def reset_text_positions(self):
        if self.image_processor.has_image():
            width, height = self.image_processor.get_image_size()
            self.text_manager.update_text_positions(width, height)
            self.status_bar.showMessage("Позиции текста сброшены")
    
    def generate_random_meme(self):
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Несохраненные изменения",
                "У вас есть несохраненные изменения. Создать случайный мем?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        meme_data = self.random_generator.generate_random_meme()
        
        if not meme_data:
            QMessageBox.warning(self, "Ошибка", "Нет изображений в истории для создания случайного мема")
            return
        
        self.load_image_from_path(meme_data['image_path'])
        
        self.current_filter = meme_data['filter_name']
        self.filter_combo.setCurrentText(self.current_filter)
        self.apply_filter(self.current_filter)
        
        self.text_manager.clear_all_text()
        
        self.text_manager.add_top_text(meme_data['top_text'])
        self.text_manager.top_text_item.setFont(QFont(meme_data['font_family'], meme_data['font_size']))
        self.text_manager.top_text_item.setDefaultTextColor(QColor(meme_data['text_color']))
        self.text_manager.top_text_item.set_stroke(meme_data['stroke_color'], meme_data['stroke_width'])
        
        self.text_manager.add_bottom_text(meme_data['bottom_text'])
        self.text_manager.bottom_text_item.setFont(QFont(meme_data['font_family'], meme_data['font_size']))
        self.text_manager.bottom_text_item.setDefaultTextColor(QColor(meme_data['text_color']))
        self.text_manager.bottom_text_item.set_stroke(meme_data['stroke_color'], meme_data['stroke_width'])
        
        self.database.save_random_meme(meme_data)
        self.save_meme_version(meme_data)
        self.save_text_settings(is_top=True)
        self.save_text_settings(is_top=False)
        
        self.status_bar.showMessage(f"Создан случайный мем: {meme_data['top_text']}")
    
    def apply_filter(self, filter_name):
        if not self.image_processor.has_image():
            return
        
        self.current_filter = filter_name
        
        pixmap = self.image_processor.reset_image()
        
        if filter_name != "Нет фильтра":
            image = pixmap.toImage()
            filtered_image = self.filter_manager.apply_filter(image, filter_name)
            pixmap = QPixmap.fromImage(filtered_image)
            self.image_processor.current_pixmap = pixmap
        
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        
        width, height = self.image_processor.get_image_size()
        self.text_manager.update_text_positions(width, height)
        
        if self.text_manager.top_text_item:
            self.scene.addItem(self.text_manager.top_text_item)
        if self.text_manager.bottom_text_item:
            self.scene.addItem(self.text_manager.bottom_text_item)
        
        self.status_bar.showMessage(f"Применен фильтр: {filter_name}")
    
    def set_filter(self, filter_name):
        self.filter_combo.setCurrentText(filter_name)
        self.apply_filter(filter_name)
    
    def save_meme(self):
        if not self.image_processor.has_image():
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        self.save_meme_version()
        
        image_pixmap = self.image_processor.get_current_image()
        
        text_items = [
            self.text_manager.top_text_item,
            self.text_manager.bottom_text_item
        ]
        meme_pixmap = MemeRenderer.render_meme(image_pixmap, text_items)
        
        saved_path = self.export_manager.save_meme(self, meme_pixmap)
        
        if saved_path:
            self.status_bar.showMessage(f"Мем сохранен: {saved_path}")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Успех")
            msg_box.setText(f"Мем успешно сохранен в:\n{saved_path}")
            
            open_button = msg_box.addButton("Открыть папку", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(QMessageBox.StandardButton.Ok)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == open_button:
                import subprocess
                try:
                    if os.name == 'nt':
                        os.startfile(os.path.dirname(saved_path))
                    elif os.name == 'posix':
                        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', 
                                       os.path.dirname(saved_path)])
                except Exception as e:
                    print(f"Не удалось открыть папку: {e}")
        else:
            self.status_bar.showMessage("Сохранение отменено")
    
    def save_meme_version(self, extra_data=None):
        if not self.image_processor.has_image():
            return
        
        meme_data = {
            'image_path': self.image_processor.image_path,
            'filter_name': self.current_filter
        }
        
        top_settings = self.text_manager.get_text_settings(is_top_text=True)
        bottom_settings = self.text_manager.get_text_settings(is_top_text=False)
        
        if top_settings:
            meme_data.update({
                'top_text': top_settings.get('text'),
                'font_family': top_settings.get('font_family'),
                'font_size': top_settings.get('font_size'),
                'text_color': top_settings.get('text_color'),
                'stroke_color': top_settings.get('stroke_color'),
                'stroke_width': top_settings.get('stroke_width')
            })
        
        if bottom_settings:
            meme_data['bottom_text'] = bottom_settings.get('text')
        
        if extra_data:
            meme_data.update(extra_data)
        
        self.meme_version_id = self.database.save_meme_version(
            meme_data, 
            self.meme_version_id
        )
        
        self.database.log_edit_action(
            self.meme_version_id,
            "save_version",
            f"Сохранена версия мема с фильтром: {self.current_filter}"
        )
    
    def save_text_settings(self, is_top_text=True):
        settings = self.text_manager.get_text_settings(is_top_text)
        if settings:
            self.database.save_text_settings(settings, is_top_text)
    
    def change_font(self):
        if self.text_manager.top_text_item and self.text_manager.top_text_item.isSelected():
            is_top = True
            text_item = self.text_manager.top_text_item
        elif self.text_manager.bottom_text_item and self.text_manager.bottom_text_item.isSelected():
            is_top = False
            text_item = self.text_manager.bottom_text_item
        else:
            reply = QMessageBox.question(
                self, "Выбор текста",
                "Какой текст редактировать?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                is_top = True
                text_item = self.text_manager.top_text_item
            elif reply == QMessageBox.StandardButton.No:
                is_top = False
                text_item = self.text_manager.bottom_text_item
            else:
                return
        
        if not text_item:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте текст")
            return
        
        font, ok = QFontDialog.getFont(text_item.font(), self, "Выберите шрифт")
        if ok:
            text_item.setFont(font)
            self.save_text_settings(is_top)
            self.status_bar.showMessage("Шрифт изменен")
    
    def change_text_color(self):
        if self.text_manager.top_text_item and self.text_manager.top_text_item.isSelected():
            is_top = True
            text_item = self.text_manager.top_text_item
        elif self.text_manager.bottom_text_item and self.text_manager.bottom_text_item.isSelected():
            is_top = False
            text_item = self.text_manager.bottom_text_item
        else:
            reply = QMessageBox.question(
                self, "Выбор текста",
                "Какой текст редактировать?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                is_top = True
                text_item = self.text_manager.top_text_item
            elif reply == QMessageBox.StandardButton.No:
                is_top = False
                text_item = self.text_manager.bottom_text_item
            else:
                return
        
        if not text_item:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте текст")
            return
        
        color = QColorDialog.getColor(text_item.defaultTextColor(), self, "Выберите цвет текста")
        if color.isValid():
            text_item.setDefaultTextColor(color)
            self.save_text_settings(is_top)
            self.status_bar.showMessage("Цвет текста изменен")
    
    def change_stroke(self):
        if self.text_manager.top_text_item and self.text_manager.top_text_item.isSelected():
            is_top = True
            text_item = self.text_manager.top_text_item
        elif self.text_manager.bottom_text_item and self.text_manager.bottom_text_item.isSelected():
            is_top = False
            text_item = self.text_manager.bottom_text_item
        else:
            reply = QMessageBox.question(
                self, "Выбор текста",
                "Какой текст редактировать?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                is_top = True
                text_item = self.text_manager.top_text_item
            elif reply == QMessageBox.StandardButton.No:
                is_top = False
                text_item = self.text_manager.bottom_text_item
            else:
                return
        
        if not text_item:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте текст")
            return
        
        color = QColorDialog.getColor(QColor(text_item.stroke_color), self, "Выберите цвет обводки")
        if not color.isValid():
            return
        
        thickness, ok = QInputDialog.getInt(
            self, 
            "Толщина обводки", 
            "Введите толщину обводки (1-10):", 
            text_item.stroke_width, 1, 10
        )
        
        if ok:
            text_item.set_stroke(color.name(), thickness)
            self.save_text_settings(is_top)
            self.status_bar.showMessage("Обводка текста изменена")
    
    def show_meme_versions(self):
        versions = self.database.get_meme_versions(10)
        
        if not versions:
            QMessageBox.information(self, "Версии", "Нет сохраненных версий мемов")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Версии мемов")
        dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        
        for version in versions:
            text_parts = []
            if version['top_text']:
                text_parts.append(f"Верх: {version['top_text'][:20]}...")
            if version['bottom_text']:
                text_parts.append(f"Низ: {version['bottom_text'][:20]}...")
            
            text = f"{version['created_at']}"
            if text_parts:
                text += f" - {' | '.join(text_parts)}"
            if version['filter_name'] and version['filter_name'] != "Нет фильтра":
                text += f" [{version['filter_name']}]"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, version['id'])
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = list_widget.currentItem()
            if selected:
                version_id = selected.data(Qt.ItemDataRole.UserRole)
                QMessageBox.information(self, "Загрузка версии", 
                    f"Загрузка версии ID: {version_id}\n(функция в разработке)")
    
    def show_random_history(self):
        memes = self.database.get_random_memes_history(10)
        
        if not memes:
            QMessageBox.information(self, "История", "Нет истории случайных мемов")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("История случайных мемов")
        dialog.setFixedSize(600, 300)
        
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Дата", "Изображение", "Верхний текст", 
            "Нижний текст", "Фильтр"
        ])
        table.setRowCount(len(memes))
        
        for i, meme in enumerate(memes):
            table.setItem(i, 0, QTableWidgetItem(meme['generated_at']))
            table.setItem(i, 1, QTableWidgetItem(meme['image_path']))
            table.setItem(i, 2, QTableWidgetItem(meme['top_text']))
            table.setItem(i, 3, QTableWidgetItem(meme['bottom_text']))
            table.setItem(i, 4, QTableWidgetItem(meme['filter_name']))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def zoom_in(self):
        self.graphics_view.scale(1.2, 1.2)
    
    def zoom_out(self):
        self.graphics_view.scale(0.8, 0.8)
    
    def reset_zoom(self):
        if self.image_processor.has_image():
            pixmap = self.image_processor.get_current_image()
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def load_saved_settings(self):
        pass
    
    def closeEvent(self, event):
        self.database.close()
        event.accept()
