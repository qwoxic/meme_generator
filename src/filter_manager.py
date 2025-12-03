from PyQt6.QtGui import QPixmap, QImage
from PIL import Image, ImageEnhance, ImageFilter

class FilterManager:
    @staticmethod
    def apply_filter(pixmap, filter_name):
        if pixmap.isNull() or filter_name == "Нет":
            return pixmap.copy()
        
        try:
            qimage = pixmap.toImage()
            
            if qimage.format() == QImage.Format.Format_ARGB32:
                format = "RGBA"
            else:
                format = "RGB"
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            
            width = qimage.width()
            height = qimage.height()
            
            ptr = qimage.constBits()
            ptr.setsize(qimage.sizeInBytes())
            img_data = bytes(ptr)
            
            img = Image.frombytes(format, (width, height), img_data)
            
            if filter_name == "Черно-белый":
                if format == "RGBA":
                    rgb = img.convert("RGB")
                    gray = rgb.convert("L")
                    rgba = Image.new("RGBA", img.size)
                    rgba.paste(gray.convert("RGB"), (0, 0))
                    rgba.putalpha(img.split()[3])
                    img = rgba
                else:
                    img = img.convert("L").convert("RGB")
            elif filter_name == "Сепия":
                img = FilterManager._apply_sepia(img)
            elif filter_name == "Размытие":
                img = img.filter(ImageFilter.GaussianBlur(radius=2))
            elif filter_name == "Контраст":
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
            elif filter_name == "Яркость":
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.3)
            
            return FilterManager._pil_to_qimage(img)
        except Exception as e:
            print(f"Filter error: {e}")
            return pixmap.copy()
    
    @staticmethod
    def _apply_sepia(img):
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        width, height = img.size
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                tr = min(255, tr)
                tg = min(255, tg)
                tb = min(255, tb)
                
                pixels[x, y] = (tr, tg, tb)
        
        return img
    
    @staticmethod
    def adjust_brightness(pixmap, factor):
        if pixmap.isNull():
            return pixmap.copy()
        
        try:
            qimage = pixmap.toImage()
            
            if qimage.format() == QImage.Format.Format_ARGB32:
                format = "RGBA"
            else:
                format = "RGB"
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            
            width = qimage.width()
            height = qimage.height()
            
            ptr = qimage.constBits()
            ptr.setsize(qimage.sizeInBytes())
            img_data = bytes(ptr)
            
            img = Image.frombytes(format, (width, height), img_data)
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
            
            return FilterManager._pil_to_qimage(img)
        except Exception as e:
            print(f"Brightness error: {e}")
            return pixmap.copy()
    
    @staticmethod
    def adjust_contrast(pixmap, factor):
        if pixmap.isNull():
            return pixmap.copy()
        
        try:
            qimage = pixmap.toImage()
            
            if qimage.format() == QImage.Format.Format_ARGB32:
                format = "RGBA"
            else:
                format = "RGB"
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            
            width = qimage.width()
            height = qimage.height()
            
            ptr = qimage.constBits()
            ptr.setsize(qimage.sizeInBytes())
            img_data = bytes(ptr)
            
            img = Image.frombytes(format, (width, height), img_data)
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor)
            
            return FilterManager._pil_to_qimage(img)
        except Exception as e:
            print(f"Contrast error: {e}")
            return pixmap.copy()
    
    @staticmethod
    def _pil_to_qimage(pil_img):
        if pil_img.mode == "RGB":
            data = pil_img.tobytes("raw", "RGB")
            qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
        elif pil_img.mode == "RGBA":
            data = pil_img.tobytes("raw", "RGBA")
            qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        elif pil_img.mode == "L":
            pil_img = pil_img.convert("RGB")
            data = pil_img.tobytes("raw", "RGB")
            qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
        else:
            pil_img = pil_img.convert("RGB")
            data = pil_img.tobytes("raw", "RGB")
            qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
        
        return QPixmap.fromImage(qimage)
