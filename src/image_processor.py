from PyQt6.QtGui import QPixmap

class ImageProcessor:
    @staticmethod
    def load_image(path):
        return QPixmap(path)
