import random
from datetime import datetime
from .constants import Constants
from .filter_manager import FilterManager

class RandomMemeGenerator:
    def __init__(self, database, image_processor):
        self.database = database
        self.image_processor = image_processor
        self.current_image_path = None
    
    def generate_random_meme(self):
        """
        Генерация случайного мема
        
        Returns:
            dict: Данные для создания мема
        """
        # 1. Случайное изображение из истории
        image_path = self._get_random_image()
        if not image_path:
            return None
        
        # 2. Случайный фильтр
        filter_name = random.choice(Constants.FILTERS)
        
        # 3. Случайные фразы
        phrases = random.sample(Constants.MEME_PHRASES, 2)
        top_text = phrases[0]
        bottom_text = phrases[1]
        
        # 4. Случайный шрифт
        font = random.choice(Constants.AVAILABLE_FONTS)
        
        # 5. Случайные цвета
        text_color = self._random_color()
        stroke_color = self._random_dark_color()
        
        return {
            'image_path': image_path,
            'filter_name': filter_name,
            'top_text': top_text,
            'bottom_text': bottom_text,
            'font_family': font,
            'font_size': random.randint(30, 50),
            'text_color': text_color,
            'stroke_color': stroke_color,
            'stroke_width': random.randint(1, 3)
        }
    
    def _get_random_image(self):
        """Получение случайного изображения из истории"""
        history = self.database.get_image_history()
        if history:
            return random.choice(history)
        
        # Если истории нет, можно использовать стандартные изображения
        # или вернуть None
        return None
    
    def _random_color(self):
        """Генерация случайного цвета"""
        colors = [
            "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", 
            "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500",
            "#800080", "#008000", "#800000", "#000080"
        ]
        return random.choice(colors)
    
    def _random_dark_color(self):
        """Генерация случайного темного цвета"""
        colors = [
            "#000000", "#333333", "#660000", "#003300",
            "#000066", "#330033", "#003333", "#333300"
        ]
        return random.choice(colors)
    
    def save_generated_meme(self, meme_data):
        """
        Сохранение сгенерированного мема в базу данных
        
        Args:
            meme_data: Данные мема
        """
        if not meme_data:
            return
        
        # Сохраняем как новую версию
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Здесь можно добавить сохранение в таблицу случайных мемов
        print(f"Сохранен случайный мем: {meme_data['top_text']} - {meme_data['bottom_text']}")
