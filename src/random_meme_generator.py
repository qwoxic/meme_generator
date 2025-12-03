import random
from PyQt6.QtGui import QColor
from .constants import RANDOM_TEXTS, AVAILABLE_FONTS

class RandomMemeGenerator:
    @staticmethod
    def generate_meme_data():
        return {
            'text': random.choice(RANDOM_TEXTS),
            'font': random.choice(AVAILABLE_FONTS),
            'size': random.randint(30, 70),
            'color': QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ),
            'has_outline': random.choice([True, False]),
            'has_shadow': random.choice([True, False]),
            'filter': random.choice(['Нет', 'Черно-белый', 'Сепия', 'Размытие'])
        }
    
    @staticmethod
    def split_text(text):
        lines = text.split('\n')
        if len(lines) >= 2:
            return lines[0], '\n'.join(lines[1:])
        else:
            if random.choice([True, False]):
                return lines[0], ""
            else:
                return "", lines[0]
