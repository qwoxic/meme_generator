import sqlite3
import os
import json
import csv

class Database:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect("data/memes.db")
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS images 
                         (id INTEGER PRIMARY KEY, path TEXT, width INTEGER, height INTEGER, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS memes 
                         (id INTEGER PRIMARY KEY, image_id INTEGER, top_text TEXT, bottom_text TEXT, 
                          font_size INTEGER, text_color TEXT, outline_color TEXT, has_outline BOOLEAN, 
                          has_shadow BOOLEAN, output_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (image_id) REFERENCES images (id))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS meme_versions 
                         (id INTEGER PRIMARY KEY, meme_id INTEGER, version_data TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                          FOREIGN KEY (meme_id) REFERENCES memes (id))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS statistics 
                         (id INTEGER PRIMARY KEY, meme_id INTEGER, views INTEGER DEFAULT 0,
                          downloads INTEGER DEFAULT 0, likes INTEGER DEFAULT 0,
                          last_viewed TIMESTAMP, FOREIGN KEY (meme_id) REFERENCES memes (id))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_settings 
                         (id INTEGER PRIMARY KEY, setting_name TEXT UNIQUE, setting_value TEXT,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        self.conn.commit()
    
    def save_image(self, path, width, height):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO images (path, width, height) VALUES (?, ?, ?)", 
                      (path, width, height))
        self.conn.commit()
        return cursor.lastrowid
    
    def save_meme(self, image_id, top_text, bottom_text, font_size, text_color, 
                  outline_color, has_outline, has_shadow, output_path):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO memes (image_id, top_text, bottom_text, font_size, 
                         text_color, outline_color, has_outline, has_shadow, output_path) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (image_id, top_text, bottom_text, font_size, text_color, 
                       outline_color, has_outline, has_shadow, output_path))
        meme_id = cursor.lastrowid
        
        cursor.execute('''INSERT INTO meme_versions (meme_id, version_data) 
                         VALUES (?, ?)''', 
                      (meme_id, json.dumps({
                          'top_text': top_text, 
                          'bottom_text': bottom_text, 
                          'font_size': font_size, 
                          'text_color': text_color, 
                          'outline_color': outline_color
                      })))
        
        cursor.execute('''INSERT INTO statistics (meme_id, views, downloads, likes) 
                         VALUES (?, 0, 0, 0)''', (meme_id,))
        
        self.conn.commit()
        return meme_id
    
    def get_recent_images(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT path FROM images ORDER BY created_at DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_recent_memes(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT output_path FROM memes ORDER BY created_at DESC LIMIT ?', (limit,))
        return [row[0] for row in cursor.fetchall()]
    
    def increment_views(self, meme_id):
        cursor = self.conn.cursor()
        cursor.execute('''UPDATE statistics SET views = views + 1, 
                         last_viewed = CURRENT_TIMESTAMP WHERE meme_id = ?''', (meme_id,))
        self.conn.commit()
    
    def increment_downloads(self, meme_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE statistics SET downloads = downloads + 1 WHERE meme_id = ?', (meme_id,))
        self.conn.commit()
    
    def get_statistics(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT m.id, m.top_text, m.bottom_text, m.created_at,
                         s.views, s.downloads, s.likes, s.last_viewed
                         FROM memes m
                         LEFT JOIN statistics s ON m.id = s.meme_id
                         ORDER BY m.created_at DESC''')
        return cursor.fetchall()
    
    def save_setting(self, name, value):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO user_settings (setting_name, setting_value) 
                         VALUES (?, ?)''', (name, value))
        self.conn.commit()
    
    def get_setting(self, name, default=None):
        cursor = self.conn.cursor()
        cursor.execute("SELECT setting_value FROM user_settings WHERE setting_name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else default
    
    def close(self):
        self.conn.close()
    
    def export_to_csv(self, filename):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT m.id, m.top_text, m.bottom_text, m.created_at,
                         s.views, s.downloads, s.likes
                         FROM memes m
                         LEFT JOIN statistics s ON m.id = s.meme_id''')
        
        rows = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Верхний текст', 'Нижний текст', 'Дата создания', 
                            'Просмотры', 'Скачивания', 'Лайки'])
            
            for row in rows:
                writer.writerow(row)
