import os
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QClipboard

class ExportManager:
    @staticmethod
    def save_meme(pixmap, parent=None):
        if pixmap.isNull():
            return None
        
        file_path, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить мем",
            f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )
        
        if file_path:
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                quality = 90
            else:
                quality = -1
            
            if pixmap.save(file_path, quality=quality):
                return file_path
        
        return None
    
    @staticmethod
    def copy_to_clipboard(pixmap, parent=None):
        if not pixmap.isNull():
            clipboard = parent.clipboard()
            clipboard.setPixmap(pixmap)
            return True
        return False
