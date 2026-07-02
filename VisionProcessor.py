import cv2
import numpy as np


class VisionProcessor:
    def __init__(self):
        self._raw_image = None
        self.gray_image = None
        self.current_processed_rgb = None

    def load_image(self, file_path):
        """Загрузка изображения с диска"""
        if not file_path or not isinstance(file_path, str):
            return False

        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if image is None:
            return False

        self._raw_image = image
        self.gray_image = cv2.cvtColor(self._raw_image, cv2.COLOR_BGR2GRAY)
        self.current_processed_rgb = None
        return True

    def apply_thermal_filter(self, style_name):
        """Наложение псевдоцвета (эффект тепловизора)"""
        if self.gray_image is None:
            return None

        if style_name == "Сине-красный (Jet)":
            colormap_code = cv2.COLORMAP_JET
        else:
            colormap_code = cv2.COLORMAP_HOT

        thermal_img = cv2.applyColorMap(self.gray_image, colormap_code)
        self.current_processed_rgb = cv2.cvtColor(thermal_img, cv2.COLOR_BGR2RGB)
        return self.current_processed_rgb

    def save_image(self, save_path):
        """Сохранение обработанного изображения на диск"""
        if self.current_processed_rgb is None:
            return False

        if not save_path or not isinstance(save_path, str):
            return False

        bgr_to_save = cv2.cvtColor(self.current_processed_rgb, cv2.COLOR_RGB2BGR)
        return cv2.imwrite(save_path, bgr_to_save)
