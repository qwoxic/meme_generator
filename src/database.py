import sqlite3
import json
from datetime import datetime
from .constants import Constants

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(Constants.DATABASE_PATH)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Создание таблиц базы данных"""
        # Таблица истории изображений
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица сохраненных мемов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_path TEXT NOT NULL,
                save_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица настроек текста
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                font_family TEXT,
                font_size INTEGER,
                text_color TEXT,
                stroke_color TEXT,
                stroke_width INTEGER,
                is_top_text INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def add_image_to_history(self, image_path):
        """Добавление изображения в историю"""
        # Удаляем старые записи, если превышен лимит
        self.cursor.execute('SELECT COUNT(*) FROM image_history')
        count = self.cursor.fetchone()[0]
        
        if count >= Constants.MAX_HISTORY_ITEMS:
            self.cursor.execute('''
                DELETE FROM image_history 
                WHERE id = (SELECT MIN(id) FROM image_history)
            ''')
        
        # Добавляем новое изображение
        self.cursor.execute(
            'INSERT INTO image_history (image_path) VALUES (?)',
            (image_path,)
        )
        self.conn.commit()
    
    def get_image_history(self):
        """Получение истории изображений"""
        self.cursor.execute(
            'SELECT image_path FROM image_history ORDER BY timestamp DESC'
        )
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_saved_meme(self, meme_path):
        """Добавление пути сохраненного мема"""
        self.cursor.execute(
            'INSERT INTO saved_memes (meme_path) VALUES (?)',
            (meme_path,)
        )
        self.conn.commit()
    
    def save_text_settings(self, settings, is_top_text=True):
        """Сохранение настроек текста"""
        # Удаляем старые настройки для этого типа текста
        self.cursor.execute(
            'DELETE FROM text_settings WHERE is_top_text = ?',
            (1 if is_top_text else 0,)
        )
        
        # Сохраняем новые настройки
        self.cursor.execute('''
            INSERT INTO text_settings 
            (font_family, font_size, text_color, stroke_color, stroke_width, is_top_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            settings.get('font_family'),
            settings.get('font_size'),
            settings.get('text_color'),
            settings.get('stroke_color'),
            settings.get('stroke_width'),
            1 if is_top_text else 0
        ))
        self.conn.commit()
    
    def load_text_settings(self, is_top_text=True):
        """Загрузка настроек текста"""
        self.cursor.execute(
            'SELECT font_family, font_size, text_color, stroke_color, stroke_width '
            'FROM text_settings WHERE is_top_text = ?',
            (1 if is_top_text else 0,)
        )
        row = self.cursor.fetchone()
        
        if row:
            return {
                'font_family': row[0],
                'font_size': row[1],
                'text_color': row[2],
                'stroke_color': row[3],
                'stroke_width': row[4]
            }
        return None
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()