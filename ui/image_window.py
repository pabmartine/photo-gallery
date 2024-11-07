from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PIL import Image, ImageOps

class ImageWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Imagen Completa")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        label = QLabel()
        
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.width() - 20,
                self.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)
            label.setFixedSize(scaled_pixmap.size())
            self.setFixedSize(scaled_pixmap.size() + QSize(20, 20))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        label = self.findChild(QLabel)
        if label and label.pixmap():
            original_pixmap = label.pixmap()
            scaled_pixmap = original_pixmap.scaled(
                self.width() - 20,
                self.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            label.setPixmap(scaled_pixmap)