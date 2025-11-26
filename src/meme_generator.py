import sys
import os
import random
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QMessageBox, QGraphicsView, 
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem,
                             QInputDialog, QStatusBar, QMenuBar, QMenu,
                             QComboBox, QSlider, QLabel, QColorDialog, QDialog,
                             QDialogButtonBox, QFormLayout)
from PyQt6.QtGui import (QPixmap, QFont, QColor, QImage, QPainter, QAction, QKeySequence,
                        QClipboard)
from PyQt6.QtCore import Qt

class Database:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect('memes.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meme_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memes_created INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_image_to_history(self, path):
        conn = sqlite3.connect('memes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM image_history')
        count = cursor.fetchone()[0]
        if count >= 10:
            cursor.execute('DELETE FROM image_history WHERE id IN (SELECT id FROM image_history ORDER BY timestamp ASC LIMIT 1)')
        cursor.execute('INSERT INTO image_history (path) VALUES (?)', (path,))
        conn.commit()
        conn.close()
    
    def get_image_history(self):
        conn = sqlite3.connect('memes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM image_history ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()
        return [result[0] for result in results]
    
    def increment_meme_count(self):
        conn = sqlite3.connect('memes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM meme_stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO meme_stats (memes_created) VALUES (1)')
        else:
            cursor.execute('UPDATE meme_stats SET memes_created = memes_created + 1')
        conn.commit()
        conn.close()
    
    def get_meme_stats(self):
        conn = sqlite3.connect('memes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT memes_created FROM meme_stats')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

class TextSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки текста")
        self.setModal(True)
        self.setFixedSize(350, 300)
        self.current_color = QColor('white')
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Impact", "Comic Sans MS", 
                                 "Verdana", "Courier New", "Georgia", "Trebuchet MS"])
        layout.addRow("Шрифт:", self.font_combo)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(20)
        self.size_slider.setMaximum(60)
        self.size_slider.setValue(30)
        self.size_label = QLabel("30")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_label)
        layout.addRow("Размер:", size_layout)
        
        self.color_btn = QPushButton("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addRow("Цвет:", self.color_btn)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color

class MemeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Генератор Мемов')
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_image_path = None
        self.top_text_item = None
        self.bottom_text_item = None
        self.is_modified = False
        self.db = Database()
        self.meme_count = self.db.get_meme_stats()
        
        # База данных популярных мем-фраз
        self.meme_phrases = [
            "КОГДА ДЕДЛАЙН\nЧЕРЕЗ 5 МИНУТ",
            "ОЖИДАНИЕ\nРЕАЛЬНОСТЬ", 
            "МОЙ КОД\nПРОШЕЛ ТЕСТЫ",
            "УЧИТЕЛЬ: НЕТ ДЗ\nЯ: ОТЛИЧНО",
            "СОН\nПРОСЫПАНИЕ",
            "ПЛАН НА ДЕНЬ\nРЕАЛЬНОСТЬ",
            "КОГДА ВИДИШЬ\nСВОЙ БАГ\nВ ПРОДАКШЕНЕ"
        ]
        
        self.quick_templates = [
            "ОЖИДАНИЕ vs РЕАЛЬНОСТЬ",
            "КОГДА ТЫ ПОНИМАЕШЬ...",
            "МОЙ КОД РАБОТАЕТ!",
            "ПОНЕСЛАСЬ...",
            "У МЕНЯ ВСЁ ПОЛУЧИТСЯ"
        ]
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        buttons = [
            ('📁 Загрузить изображение', 'Ctrl+O', self.load_image),
            ('🔝 Верхний текст', 'Ctrl+T', lambda: self.add_text('top')),
            ('🔽 Нижний текст', 'Ctrl+B', lambda: self.add_text('bottom')),
            ('🎨 Настройки текста', '', self.show_text_settings),
            ('🎭 Быстрые шаблоны', '', self.show_templates),
            ('🎲 Случайный мем', 'Ctrl+R', self.generate_random_meme),
            ('📋 Копировать мем', 'Ctrl+C', self.copy_to_clipboard),
            ('💾 Сохранить мем', 'Ctrl+S', self.save_meme),
            ('📊 Статистика', '', self.show_stats),
            ('🗑️ Очистить текст', 'Del', self.clear_all_text),
            ('🔄 Новый проект', '', self.reset_all)
        ]
        
        for text, shortcut, callback in buttons:
            btn = QPushButton(text)
            if shortcut:
                btn.setToolTip(f"Горячая клавиша: {shortcut}")
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton { 
                    padding: 12px; 
                    font-size: 14px; 
                    text-align: left;
                    background: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: #34495e;
                }
                QPushButton:pressed {
                    background: #1abc9c;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        stats_label = QLabel(f"📊 Создано мемов: {self.meme_count}")
        stats_label.setStyleSheet("padding: 10px; font-size: 12px; color: #7f8c8d; background: #ecf0f1; border-radius: 5px;")
        left_layout.addWidget(stats_label)
        
        main_layout.addWidget(left_panel)
        
        # Основная рабочая область
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("QGraphicsView { border: 2px solid #bdc3c7; background: #ecf0f1; border-radius: 8px; }")
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        main_layout.addWidget(self.view)
        
        self.create_menus()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f'✅ Готов к созданию мемов | 📊 Всего создано: {self.meme_count}')
        
    def resizeEvent(self, event):
        # Автоматическое масштабирование при изменении размера окна
        if hasattr(self, 'image_item'):
            self.fit_image_to_view()
        super().resizeEvent(event)
        
    def fit_image_to_view(self):
        if hasattr(self, 'image_item'):
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { background: #2c3e50; color: white; } QMenuBar::item:selected { background: #1abc9c; }")
        
        file_menu = menubar.addMenu('📁 Файл')
        
        load_action = QAction('🔄 Загрузить изображение', self)
        load_action.setShortcut(QKeySequence('Ctrl+O'))
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)
        
        random_action = QAction('🎲 Случайный мем', self)
        random_action.setShortcut(QKeySequence('Ctrl+R'))
        random_action.triggered.connect(self.generate_random_meme)
        file_menu.addAction(random_action)
        
        copy_action = QAction('📋 Копировать мем', self)
        copy_action.setShortcut(QKeySequence('Ctrl+C'))
        copy_action.triggered.connect(self.copy_to_clipboard)
        file_menu.addAction(copy_action)
        
        save_action = QAction('💾 Сохранить мем', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.save_meme)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        exit_action = QAction('🚪 Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu('✏️ Редактирование')
        
        top_text_action = QAction('🔝 Верхний текст', self)
        top_text_action.setShortcut(QKeySequence('Ctrl+T'))
        top_text_action.triggered.connect(lambda: self.add_text('top'))
        edit_menu.addAction(top_text_action)
        
        bottom_text_action = QAction('🔽 Нижний текст', self)
        bottom_text_action.setShortcut(QKeySequence('Ctrl+B'))
        bottom_text_action.triggered.connect(lambda: self.add_text('bottom'))
        edit_menu.addAction(bottom_text_action)
        
        templates_action = QAction('🎭 Быстрые шаблоны', self)
        templates_action.triggered.connect(self.show_templates)
        edit_menu.addAction(templates_action)
        
        text_settings_action = QAction('🎨 Настройки текста', self)
        text_settings_action.triggered.connect(self.show_text_settings)
        edit_menu.addAction(text_settings_action)
    
    def load_image(self):
        # Проверка несохраненных изменений
        if self.is_modified:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('⚠️ Внимание')
            msg_box.setText('Есть несохраненные изменения. Продолжить?')
            msg_box.setIcon(QMessageBox.Icon.Question)
            yes_btn = msg_box.addButton('✅ Да', QMessageBox.ButtonRole.YesRole)
            no_btn = msg_box.addButton('❌ Нет', QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(no_btn)
            msg_box.exec()
            if msg_box.clickedButton() == no_btn:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите изображение', '', 
            'Images (*.png *.jpg *.jpeg *.bmp)')
        
        if file_path:
            self.current_image_path = file_path
            self.scene.clear()
            self.top_text_item = None
            self.bottom_text_item = None
            self.is_modified = False
            
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.image_item = QGraphicsPixmapItem(pixmap)
                self.scene.addItem(self.image_item)
                self.fit_image_to_view()
                self.status_bar.showMessage(f'✅ Загружено: {os.path.basename(file_path)} | 📊 Всего создано: {self.meme_count}')
                self.update_title()
                self.db.add_image_to_history(file_path)
            else:
                QMessageBox.warning(self, '❌ Ошибка', 'Не удалось загрузить изображение')
    
    def add_text(self, position, text=None):
        if not hasattr(self, 'image_item'):
            QMessageBox.warning(self, '⚠️ Внимание', 'Сначала загрузите изображение!')
            return
            
        # Проверка на дублирование текстовых блоков
        if position == 'top' and self.top_text_item is not None:
            QMessageBox.information(self, 'ℹ️ Информация', 'Верхний текст уже добавлен!')
            return
        elif position == 'bottom' and self.bottom_text_item is not None:
            QMessageBox.information(self, 'ℹ️ Информация', 'Нижний текст уже добавлен!')
            return
        
        if text is None:
            default_text = "ВЕРХНИЙ ТЕКСТ" if position == 'top' else "НИЖНИЙ ТЕКСТ"
            text, ok = QInputDialog.getText(self, 'Введите текст', 'Текст мема:', text=default_text)
            if not ok or not text:
                return
        
        text_item = QGraphicsTextItem(text)
        text_item.setDefaultTextColor(QColor('white'))
        text_item.setFont(QFont('Impact', 42, QFont.Weight.Bold))
        
        # Включение перемещения и выделения текста
        text_item.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable
        )
        
        # Точное позиционирование по центру
        image_rect = self.image_item.boundingRect()
        text_rect = text_item.boundingRect()
        
        if position == 'top':
            x = (image_rect.width() - text_rect.width()) / 2
            text_item.setPos(x, 30)
            self.top_text_item = text_item
        else:
            x = (image_rect.width() - text_rect.width()) / 2
            y = image_rect.height() - text_rect.height() - 30
            text_item.setPos(x, y)
            self.bottom_text_item = text_item
        
        self.scene.addItem(text_item)
        self.set_modified(True)
    
    def show_text_settings(self):
        dialog = TextSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            font = dialog.font_combo.currentText()
            size = dialog.size_slider.value()
            color = dialog.current_color
            
            # Применение настроек к выделенному тексту
            for item in self.scene.selectedItems():
                if isinstance(item, QGraphicsTextItem):
                    item.setFont(QFont(font, size, QFont.Weight.Bold))
                    item.setDefaultTextColor(color)
    
    def show_templates(self):
        if not hasattr(self, 'image_item'):
            QMessageBox.warning(self, '⚠️ Внимание', 'Сначала загрузите изображение!')
            return
            
        template, ok = QInputDialog.getItem(self, 'Быстрые шаблоны', 
                                           'Выберите шаблон:', self.quick_templates, 0, False)
        if ok and template:
            if self.top_text_item is None:
                self.add_text('top', template)
            elif self.bottom_text_item is None:
                self.add_text('bottom', template)
            else:
                QMessageBox.information(self, 'ℹ️ Информация', 'Оба текстовых блока уже заняты!')
    
    def copy_to_clipboard(self):
        if not hasattr(self, 'image_item'):
            QMessageBox.warning(self, '⚠️ Внимание', 'Нет изображения для копирования!')
            return
            
        # Создание изображения мема для буфера обмена
        rect = self.scene.sceneRect()
        image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        
        clipboard = QApplication.clipboard()
        clipboard.setImage(image)
        
        self.status_bar.showMessage(f'✅ Мем скопирован в буфер обмена | 📊 Всего создано: {self.meme_count}')
        QMessageBox.information(self, '✅ Успех', 'Мем скопирован в буфер обмена!')
    
    def generate_random_meme(self):
        history = self.db.get_image_history()
        if not history:
            QMessageBox.warning(self, '⚠️ Внимание', 'Сначала загрузите несколько изображений!')
            return
        
        random_image = random.choice(history)
        random_phrase = random.choice(self.meme_phrases)
        
        self.current_image_path = random_image
        self.scene.clear()
        self.top_text_item = None
        self.bottom_text_item = None
        self.is_modified = False
        
        pixmap = QPixmap(random_image)
        if not pixmap.isNull():
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.image_item)
            self.fit_image_to_view()
            
            # Разделение фразы на верхнюю и нижнюю части
            lines = random_phrase.split('\n')
            if len(lines) >= 1:
                self.add_text('top', lines[0])
            if len(lines) >= 2:
                self.add_text('bottom', lines[1])
            
            self.status_bar.showMessage(f'🎲 Создан случайный мем | 📊 Всего создано: {self.meme_count}')
            self.update_title()
        else:
            QMessageBox.warning(self, '❌ Ошибка', 'Не удалось загрузить случайное изображение')
    
    def show_stats(self):
        stats_text = f"""
📊 СТАТИСТИКА ГЕНЕРАТОРА МЕМОВ:

🖼️ Создано мемов: {self.meme_count}
🎲 Фраз в базе: {len(self.meme_phrases)}
🎭 Шаблонов: {len(self.quick_templates)}
📝 Текущий проект: {os.path.basename(self.current_image_path) if self.current_image_path else 'Не загружен'}

✨ Продолжаем творить!
        """
        QMessageBox.information(self, "📊 Статистика", stats_text.strip())
        
    def set_modified(self, modified):
        self.is_modified = modified
        self.update_title()
        
    def update_title(self):
        title = '🎨 Генератор Мемов'
        if self.is_modified:
            title += ' ✏️'
        if self.current_image_path:
            title += f' - {os.path.basename(self.current_image_path)}'
        self.setWindowTitle(title)
        
    def clear_all_text(self):
        if self.top_text_item or self.bottom_text_item:
            self.scene.clear()
            if hasattr(self, 'image_item'):
                self.scene.addItem(self.image_item)
            self.top_text_item = None
            self.bottom_text_item = None
            self.set_modified(True)
            self.status_bar.showMessage(f'✅ Текст очищен | 📊 Всего создано: {self.meme_count}')
        
    def reset_all(self):
        if self.is_modified:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('🔄 Новый проект')
            msg_box.setText('Начать новый проект? Несохраненные изменения будут потеряны.')
            msg_box.setIcon(QMessageBox.Icon.Question)
            yes_btn = msg_box.addButton('✅ Да', QMessageBox.ButtonRole.YesRole)
            no_btn = msg_box.addButton('❌ Нет', QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(no_btn)
            msg_box.exec()
            if msg_box.clickedButton() == no_btn:
                return
                
        self.scene.clear()
        self.top_text_item = None
        self.bottom_text_item = None
        self.current_image_path = None
        self.is_modified = False
        self.update_title()
        self.status_bar.showMessage(f'✅ Готов к созданию мемов | 📊 Всего создано: {self.meme_count}')
        
    def save_meme(self):
        if not hasattr(self, 'image_item'):
            QMessageBox.warning(self, '⚠️ Внимание', 'Нет изображения для сохранения!')
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить мем', f'meme_{random.randint(1000,9999)}.png', 
            'PNG (*.png);;JPEG (*.jpg *.jpeg)')
            
        if file_path:
            # Рендеринг сцены в изображение
            rect = self.scene.sceneRect()
            image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            
            image.save(file_path)
            self.set_modified(False)
            
            # Обновление статистики
            self.meme_count += 1
            self.db.increment_meme_count()
            
            self.status_bar.showMessage(f'💾 Сохранено: {os.path.basename(file_path)} | 📊 Всего создано: {self.meme_count}')
            QMessageBox.information(self, '✅ Успех', f'Мем сохранен!\n\n📍 {file_path}')
    
    def keyPressEvent(self, event):
        # Обработка горячих клавиш
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_text()
        elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.copy_to_clipboard()
        else:
            super().keyPressEvent(event)
            
    def delete_selected_text(self):
        # Удаление выделенного текста
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsTextItem):
                if item == self.top_text_item:
                    self.top_text_item = None
                elif item == self.bottom_text_item:
                    self.bottom_text_item = None
                self.scene.removeItem(item)
                self.set_modified(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Стилизация приложения
    app.setStyleSheet("""
        QMainWindow {
            background: #34495e;
        }
        QMessageBox {
            background: #ecf0f1;
            font-size: 14px;
        }
    """)
    
    generator = MemeGenerator()
    generator.show()
    sys.exit(app.exec())
