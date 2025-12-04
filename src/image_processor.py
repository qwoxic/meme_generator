from PyQt6.QtGui import QPixmap

class ImageProcessor:
    @staticmethod
    def load_image(path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return QPixmap()
        return pixmap
