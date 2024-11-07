# ui/widgets/thumbnail_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image, ImageOps

class ThumbnailWidget(QWidget):
    def __init__(self, thumbnail_path, original_path, parent=None):
        super().__init__(parent)
        self.thumbnail_path = thumbnail_path
        self.original_path = original_path
        self.is_selected = False
        self.selection_mode = False
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Container para el checkbox y la imagen
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(14, 14)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border: 1px solid gray;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QCheckBox::indicator:checked {
                background-color: #0078d7;
                border: 1px solid #0078d7;
            }
        """)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        self.checkbox.hide()
        
        # Label para la imagen
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Cargar la imagen
        try:
            with Image.open(thumbnail_path) as img:
                img = img.convert('RGB')
                img = ImageOps.exif_transpose(img)
                img.thumbnail((150, 150))
                
                pixmap = QPixmap(thumbnail_path)
                scaled_pixmap = pixmap.scaled(
                    150, 150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error cargando thumbnail {thumbnail_path}: {e}")
        
        # Añadir widgets al layout
        self.content_layout.addWidget(self.image_label)
        self.layout.addWidget(self.content_widget)
        
        # Colocar el checkbox en la esquina superior derecha
        self.checkbox.setParent(self)
        self.checkbox.move(self.width() - 18, 4)
        
        # Establecer tamaño fijo del widget
        self.setFixedSize(150, 150)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Mantener el checkbox en la esquina superior derecha
        self.checkbox.move(self.width() - 18, 4)
    
    def mousePressEvent(self, event):
        if self.selection_mode:
            self.checkbox.setChecked(not self.checkbox.isChecked())
        else:
            # Buscar el widget padre que tenga el método open_full_image
            parent = self.parent()
            while parent:
                if hasattr(parent, 'open_full_image'):
                    parent.open_full_image(self.original_path)
                    break
                parent = parent.parent()
    
    def set_selection_mode(self, enabled):
        self.selection_mode = enabled
        self.checkbox.setVisible(enabled)
        if not enabled:
            self.checkbox.setChecked(False)
    
    def on_checkbox_changed(self, state):
        self.is_selected = state == Qt.Checked
        # Notificar al padre
        parent = self.parent()
        while parent:
            if hasattr(parent, 'update_delete_action'):
                parent.update_delete_action()
                break
            parent = parent.parent()