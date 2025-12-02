class Database:
    # ... существующий код ...
    
    def create_tables(self):
        """Создание таблиц базы данных"""
        # Существующие таблицы...
        
        # Новая таблица: версии мемов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meme_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                image_path TEXT NOT NULL,
                top_text TEXT,
                bottom_text TEXT,
                font_family TEXT,
                font_size INTEGER,
                text_color TEXT,
                stroke_color TEXT,
                stroke_width INTEGER,
                filter_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES meme_versions (id)
            )
        ''')
        
        # Новая таблица: история редактирования
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meme_edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id INTEGER,
                action_type TEXT NOT NULL,
                action_details TEXT,
                edited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meme_id) REFERENCES meme_versions (id)
            )
        ''')
        
        # Новая таблица: случайные мемы
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS random_memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                top_text TEXT,
                bottom_text TEXT,
                filter_name TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_meme_version(self, meme_data, parent_id=None):
        """
        Сохранение версии мема
        
        Args:
            meme_data: Словарь с данными мема
            parent_id: ID родительской версии
        """
        self.cursor.execute('''
            INSERT INTO meme_versions 
            (parent_id, image_path, top_text, bottom_text, 
             font_family, font_size, text_color, stroke_color, 
             stroke_width, filter_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            parent_id,
            meme_data.get('image_path'),
            meme_data.get('top_text'),
            meme_data.get('bottom_text'),
            meme_data.get('font_family'),
            meme_data.get('font_size'),
            meme_data.get('text_color'),
            meme_data.get('stroke_color'),
            meme_data.get('stroke_width'),
            meme_data.get('filter_name')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def log_edit_action(self, meme_id, action_type, details=None):
        """
        Логирование действия редактирования
        
        Args:
            meme_id: ID мема
            action_type: Тип действия
            details: Детали действия
        """
        self.cursor.execute('''
            INSERT INTO meme_edits (meme_id, action_type, action_details)
            VALUES (?, ?, ?)
        ''', (meme_id, action_type, details))
        self.conn.commit()
    
    def get_meme_versions(self, limit=10):
        """
        Получение последних версий мемов
        
        Args:
            limit: Количество версий
        
        Returns:
            list: Список версий
        """
        self.cursor.execute('''
            SELECT * FROM meme_versions 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [column[0] for column in self.cursor.description]
        versions = []
        
        for row in self.cursor.fetchall():
            versions.append(dict(zip(columns, row)))
        
        return versions
    
    def save_random_meme(self, meme_data):
        """
        Сохранение случайного мема
        
        Args:
            meme_data: Данные случайного мема
        """
        self.cursor.execute('''
            INSERT INTO random_memes 
            (image_path, top_text, bottom_text, filter_name)
            VALUES (?, ?, ?, ?)
        ''', (
            meme_data.get('image_path'),
            meme_data.get('top_text'),
            meme_data.get('bottom_text'),
            meme_data.get('filter_name')
        ))
        self.conn.commit()
    
    def get_random_memes_history(self, limit=5):
        """
        Получение истории случайных мемов
        
        Args:
            limit: Количество записей
        
        Returns:
            list: История случайных мемов
        """
        self.cursor.execute('''
            SELECT * FROM random_memes 
            ORDER BY generated_at DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [column[0] for column in self.cursor.description]
        memes = []
        
        for row in self.cursor.fetchall():
            memes.append(dict(zip(columns, row)))
        
        return memes
