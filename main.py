# main.py
import os
import sys
import logging
from PyQt5.QtWidgets import QApplication

# Añadir el directorio actual al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import PhotoGalleryApp

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("photo_gallery.log")]
)

def main():
    app = QApplication(sys.argv)
    gallery = PhotoGalleryApp()
    gallery.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()