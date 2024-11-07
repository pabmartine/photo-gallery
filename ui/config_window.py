import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea, 
    QWidget, QGroupBox, QDoubleSpinBox, QPushButton, QMessageBox,
    QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt

class ConfigWindow(QDialog):
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.setFixedSize(600, 400)
        self.config_manager = config_manager
        self.init_ui()
        self.centerWindow()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Grupo de rutas
        paths_group = QGroupBox("Paths")
        paths_layout = QGridLayout()  # Cambiamos a QGridLayout
        
        # Ruta de fotos
        photos_label = QLabel("Photos folder:")
        self.photos_path = QLineEdit()
        self.photos_path.setText(self.config_manager.get_value("paths", "photos"))
        photos_button = QPushButton("Browse...")
        photos_button.clicked.connect(lambda: self.browse_folder(self.photos_path))
        
        # Ruta de miniaturas
        thumbnails_label = QLabel("Thumbnails folder:")
        self.thumbnails_path = QLineEdit()
        self.thumbnails_path.setText(self.config_manager.get_value("paths", "thumbnails"))
        thumbnails_button = QPushButton("Browse...")
        thumbnails_button.clicked.connect(lambda: self.browse_folder(self.thumbnails_path))
        
        # Añadir widgets al grid layout
        paths_layout.addWidget(photos_label, 0, 0)
        paths_layout.addWidget(self.photos_path, 0, 1)
        paths_layout.addWidget(photos_button, 0, 2)
        
        paths_layout.addWidget(thumbnails_label, 1, 0)
        paths_layout.addWidget(self.thumbnails_path, 1, 1)
        paths_layout.addWidget(thumbnails_button, 1, 2)
        
        paths_group.setLayout(paths_layout)
        
        scroll_layout.addWidget(paths_group)
        
        # Grupo CLIP
        clip_group = QGroupBox("CLIP Configuration")
        clip_layout = QVBoxLayout()
        
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Confidence threshold:")
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 100.0)
        self.threshold_spin.setDecimals(1)
        self.threshold_spin.setSingleStep(0.5)
        self.threshold_spin.setValue(
            self.config_manager.get_value("clip", "confidence_threshold")
        )
        self.threshold_spin.setSuffix("%")
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_spin)
        clip_layout.addLayout(threshold_layout)
        
        clip_group.setLayout(clip_layout)
        
        scroll_layout.addWidget(clip_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select folder",
            line_edit.text() or os.path.expanduser("~")
        )
        if folder:
            line_edit.setText(folder)

    def save_config(self):
        
        # Guardar rutas
        self.config_manager.set_value("paths", "photos", self.photos_path.text())
        self.config_manager.set_value("paths", "thumbnails", self.thumbnails_path.text())
        
        # Guardar configuración CLIP
        self.config_manager.set_value(
            "clip", 
            "confidence_threshold", 
            self.threshold_spin.value()
        )
        
        if self.config_manager.save_config():
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Could not save configuration"
            )
    
    def centerWindow(self):
        if self.parent():
            parent_center = self.parent().frameGeometry().center()
            dialog_frame = self.frameGeometry()
            dialog_frame.moveCenter(parent_center)
            self.move(dialog_frame.topLeft())
    
    def showEvent(self, event):
        super().showEvent(event)
        self.centerWindow()