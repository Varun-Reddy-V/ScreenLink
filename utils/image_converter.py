import cv2
from PyQt6.QtGui import QImage

class ImageConverter:
    @staticmethod
    def bgr_to_qimage(cv_img) -> QImage:
        if cv_img is None:
            return QImage()
        
        height, width, bytes_per_component = cv_img.shape
        bytes_per_line = bytes_per_component * width
        
        # Convert BGR (OpenCV default) to RGB (Qt default)
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Adding .copy() makes a deep copy of the underlying pixel data
        # so Qt owns the memory securely across threads.
        return QImage(
            cv_img_rgb.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        ).copy()