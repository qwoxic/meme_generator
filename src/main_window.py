import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGraphicsView, QGraphicsScene, QFileDialog,
    QMenuBar, QMenu, QStatusBar, QToolBar, QColorDialog, QFontDialog,
    QSpinBox, QComboBox, QMessageBox, QSplitter, QDockWidget
)
from PyQt6.QtGui import QAction, QKeySequence, QPixmap, QColor, QFont
from PyQt6.QtCore import Qt, QSize
from .image_processor import ImageProcessor
from .text_manager import TextManager
from .meme_renderer import MemeRenderer
from .export_manager import ExportManager
from .database import Database
from .constants import Constants

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Constants.APP_NAME} v{Constants.APP_VERSION}")
        self.setGeometry(100, 100, Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)
        
        # Инициализация компонентов
        self.database = Database()
        self.image_processor = ImageProcessor()
        self.export_manager = ExportManager(self.database)
        
        # Инициализация UI
        self.init_ui()
        self.init_menus()
        self.init_toolbar()
        self.init_status_bar()
        
        # Загрузка сохраненных настроек
        self.load_saved_settings()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Создание графической сцены
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Инициализация менеджера текста
        self.text_manager = TextManager(self.scene)
        
        # Панель инструментов
        tool_panel = self.create_tool_panel()
        
        # Добавление виджетов в основной layout
        main_layout.addWidget(tool_panel)
        main_layout.addWidget(self.graphics_view)
    
    def create_tool_panel(self):
        """Создание панели инструментов"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Кнопки для работы с изображениями
        self.btn_load_image = QPushButton("Загрузить изображение")
        self.btn_load_image.clicked.connect(self.load_image)
        layout.addWidget(self.btn_load_image)
        
        self.btn_reset_image = QPushButton("Сбросить")
        self.btn_reset_image.clicked.connect(self.reset_image)
        self.btn_reset_image.setEnabled(False)
        layout.addWidget(self.btn_reset_image)
        
        layout.addStretch()
        
        # Кнопки для работы с текстом
        self.btn_add_top_text = QPushButton("Верхний текст")
        self.btn_add_top_text.clicked.connect(lambda: self.add_text(is_top=True))
        layout.addWidget(self.btn_add_top_text)
        
        self.btn_add_bottom_text = QPushButton("Нижний текст")
        self.btn_add_bottom_text.clicked.connect(lambda: self.add_text(is_top=False))
        layout.addWidget(self.btn_add_bottom_text)
        
        self.btn_clear_text = QPushButton("Очистить текст")
        self.btn_clear_text.clicked.connect(self.clear_text)
        layout.addWidget(self.btn_clear_text)
        
        layout.addStretch()
        
        # Кнопка сохранения
        self.btn_save_meme = QPushButton("Сохранить мем")
        self.btn_save_meme.clicked.connect(self.save_meme)
        self.btn_save_meme.setEnabled(False)
        layout.addWidget(self.btn_save_meme)
        
        return panel
    
    def init_menus(self):
        """Инициализация меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        load_action = QAction("Загрузить изображение", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)
        
        save_action = QAction("Сохранить мем", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_meme)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        history_menu = file_menu.addMenu("История загрузок")
        self.update_history_menu(history_menu)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Текст"
        text_menu = menubar.addMenu("Текст")
        
        top_text_action = QAction("Добавить верхний текст", self)
        top_text_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        top_text_action.triggered.connect(lambda: self.add_text(is_top=True))
        text_menu.addAction(top_text_action)
        
        bottom_text_action = QAction("Добавить нижний текст", self)
        bottom_text_action.triggered.connect(lambda: self.add_text(is_top=False))
        text_menu.addAction(bottom_text_action)
        
        text_menu.addSeparator()
        
        clear_text_action = QAction("Удалить весь текст", self)
        clear_text_action.triggered.connect(self.clear_text)
        text_menu.addAction(clear_text_action)
        
        reset_pos_action = QAction("Сбросить позиции текста", self)
        reset_pos_action.setShortcut(QKeySequence("Ctrl+R"))
        reset_pos_action.triggered.connect(self.reset_text_positions)
        text_menu.addAction(reset_pos_action)
        
        # Меню "Настройки"
        settings_menu = menubar.addMenu("Настройки")
        
        font_action = QAction("Шрифт...", self)
        font_action.triggered.connect(self.change_font)
        settings_menu.addAction(font_action)
        
        color_action = QAction("Цвет текста...", self)
        color_action.triggered.connect(self.change_text_color)
        settings_menu.addAction(color_action)
        
        stroke_action = QAction("Обводка текста...", self)
        stroke_action.triggered.connect(self.change_stroke)
        settings_menu.addAction(stroke_action)
        
        # Меню "Вид"
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
        """Обновление меню истории"""
        history_menu.clear()
        history = self.database.get_image_history()
        
        if not history:
            no_history_action = QAction("История пуста", self)
            no_history_action.setEnabled(False)
            history_menu.addAction(no_history_action)
        else:
            for image_path in history:
                action = QAction(image_path, self)
                action.triggered.connect(
                    lambda checked, path=image_path: self.load_image_from_path(path)
                )
                history_menu.addAction(action)
    
    def init_toolbar(self):
        """Инициализация панели инструментов"""
        toolbar = self.addToolBar("Панель инструментов")
        toolbar.setMovable(False)
        
        toolbar.addAction("Загрузить", self.load_image)
        toolbar.addSeparator()
        toolbar.addAction("Верхний текст", lambda: self.add_text(is_top=True))
        toolbar.addAction("Нижний текст", lambda: self.add_text(is_top=False))
        toolbar.addSeparator()
        toolbar.addAction("Сохранить", self.save_meme)
    
    def init_status_bar(self):
        """Инициализация строки состояния"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def load_image(self):
        """Загрузка изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            f"Изображения ({Constants.IMAGE_EXTENSIONS})"
        )
        
        if file_path:
            self.load_image_from_path(file_path)
    
    def load_image_from_path(self, file_path):
        """Загрузка изображения по пути"""
        pixmap = self.image_processor.load_image(file_path)
        
        if not pixmap.isNull():
            # Очищаем сцену
            self.scene.clear()
            
            # Добавляем изображение на сцену
            self.scene.addPixmap(pixmap)
            
            # Устанавливаем размер сцены
            self.scene.setSceneRect(pixmap.rect())
            
            # Масштабируем view под изображение
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            # Добавляем изображение в историю
            self.database.add_image_to_history(file_path)
            
            # Обновляем меню истории
            self.update_history_menu(self.menuBar().findChild(QMenu, "История загрузок"))
            
            # Активируем кнопки
            self.btn_reset_image.setEnabled(True)
            self.btn_save_meme.setEnabled(True)
            
            # Обновляем позиции текста
            self.text_manager.update_text_positions(
                pixmap.width(),
                pixmap.height()
            )
            
            self.status_bar.showMessage(f"Изображение загружено: {file_path}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
    
    def reset_image(self):
        """Сброс изображения"""
        pixmap = self.image_processor.reset_image()
        if not pixmap.isNull():
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.status_bar.showMessage("Изображение сброшено")
    
    def add_text(self, is_top=True):
        """Добавление текста"""
        if not self.image_processor.has_image():
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        if is_top:
            text_item = self.text_manager.add_top_text()
            settings = self.database.load_text_settings(is_top_text=True)
        else:
            text_item = self.text_manager.add_bottom_text()
            settings = self.database.load_text_settings(is_top_text=False)
        
        if settings:
            self.text_manager.set_text_settings(settings, is_top)
        
        self.status_bar.showMessage("Текст добавлен")
    
    def clear_text(self):
        """Очистка текста"""
        self.text_manager.clear_all_text()
        self.status_bar.showMessage("Текст очищен")
    
    def reset_text_positions(self):
        """Сброс позиций текста"""
        if self.image_processor.has_image():
            width, height = self.image_processor.get_image_size()
            self.text_manager.update_text_positions(width, height)
            self.status_bar.showMessage("Позиции текста сброшены")
    
    def save_meme(self):
        """Сохранение мема"""
        if not self.image_processor.has_image():
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return
        
        # Получаем текущее изображение
        image_pixmap = self.image_processor.get_current_image()
        
        # Рендерим мем с текстом
        text_items = [
            self.text_manager.top_text_item,
            self.text_manager.bottom_text_item
        ]
        meme_pixmap = MemeRenderer.render_meme(image_pixmap, text_items)
        
        # Сохраняем мем
        saved_path = self.export_manager.save_meme(self, meme_pixmap)
        
        if saved_path:
            self.status_bar.showMessage(f"Мем сохранен: {saved_path}")
            QMessageBox.information(self, "Успех", f"Мем успешно сохранен в:\n{saved_path}")
        else:
            self.status_bar.showMessage("Сохранение отменено")
    
    def change_font(self):
        """Изменение шрифта"""
        font, ok = QFontDialog.getFont()
        if ok:
            # Здесь нужно определить, какой текст редактируется
            # Для простоты применяем ко всем текстовым элементам
            if self.text_manager.top_text_item:
                self.text_manager.top_text_item.setFont(font)
                # Сохраняем настройки
                settings = self.text_manager.get_text_settings(is_top_text=True)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=True)
            
            if self.text_manager.bottom_text_item:
                self.text_manager.bottom_text_item.setFont(font)
                # Сохраняем настройки
                settings = self.text_manager.get_text_settings(is_top_text=False)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=False)
    
    def change_text_color(self):
        """Изменение цвета текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Применяем ко всем текстовым элементам
            if self.text_manager.top_text_item:
                self.text_manager.top_text_item.setDefaultTextColor(color)
                settings = self.text_manager.get_text_settings(is_top_text=True)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=True)
            
            if self.text_manager.bottom_text_item:
                self.text_manager.bottom_text_item.setDefaultTextColor(color)
                settings = self.text_manager.get_text_settings(is_top_text=False)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=False)
    
    def change_stroke(self):
        """Изменение обводки текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Здесь нужно добавить диалог для выбора толщины
            # Для простоты используем фиксированное значение
            stroke_width = 2
            
            if self.text_manager.top_text_item:
                self.text_manager.top_text_item.set_stroke(color.name(), stroke_width)
                settings = self.text_manager.get_text_settings(is_top_text=True)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=True)
            
            if self.text_manager.bottom_text_item:
                self.text_manager.bottom_text_item.set_stroke(color.name(), stroke_width)
                settings = self.text_manager.get_text_settings(is_top_text=False)
                if settings:
                    self.database.save_text_settings(settings, is_top_text=False)
    
    def zoom_in(self):
        """Увеличение масштаба"""
        self.graphics_view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Уменьшение масштаба"""
        self.graphics_view.scale(0.8, 0.8)
    
    def reset_zoom(self):
        """Сброс масштаба"""
        if self.image_processor.has_image():
            pixmap = self.image_processor.get_current_image()
            self.graphics_view.fitInView(pixmap.rect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def load_saved_settings(self):
        """Загрузка сохраненных настроек"""
        # Этот метод можно расширить для загрузки других настроек
        pass
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.database.close()
        event.accept()