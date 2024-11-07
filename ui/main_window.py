# ui/main_window.py
import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
    QFrame, QPushButton, QLabel, QMenu, QAction, QActionGroup,
    QProgressDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from transformers import CLIPProcessor, CLIPModel

from config.config_manager import ConfigManager
from constants.app_constants import MONTHS
from utils.duplicate_detector import DuplicateDetector
from utils.image_classifier import ImageClassifierThread
from ui.widgets.flow_layout import FlowLayout
from ui.widgets.thumbnail_widget import ThumbnailWidget
from ui.config_window import ConfigWindow
from ui.image_window import ImageWindow

class PhotoGalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galería de Fotos")
        self.setGeometry(100, 100, 924, 800)
        self.setMinimumSize(400, 300)

        self.setup_variables()
        self.setup_ui()
        self.load_initial_data()

    def setup_variables(self):
        self.config_manager = ConfigManager()
        self.image_windows = []
        self.model = None
        self.processor = None
        
        # Filtros y ordenación
        self.filter_year = None
        self.filter_month = None
        self.filter_label = None
        self.sort_order = "ascendente"
        self.show_duplicates = False
        
        # Paginación
        self.items_per_page = 100
        self.current_page = 0
        self.total_pages = 0
        self.filtered_images = []
        self.loaded_thumbnails = set()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Área de scroll
        self.setup_scroll_area()
        main_layout.addWidget(self.scroll_area)

        # Paginación
        self.setup_pagination_frame()
        main_layout.addWidget(self.pagination_frame)
        self.pagination_frame.hide()

        # Menús
        self.setup_menu()

    def load_filter_options(self):
        """Carga las opciones de filtrado desde los archivos de datos"""
        if not os.path.exists("index.json"):
            return

        # Limpiar menús existentes
        self.year_menu.clear()
        self.month_menu.clear()
        self.label_menu.clear()

        # Cargar datos del índice
        with open("index.json", "r") as f:
            images = json.load(f)

        # Obtener años y meses únicos
        years = sorted(set(image["year"] for image in images))
        months = sorted(set(image["month"] for image in images))

        # Obtener etiquetas si existen
        labels = set()
        if os.path.exists("classification_results.json"):
            try:
                with open("classification_results.json", "r") as f:
                    classification_data = json.load(f)
                    labels = set(item["label"] for item in classification_data.values())
            except Exception as e:
                print(f"Error cargando etiquetas: {e}")

        # Crear los grupos de acciones
        self.year_action_group = QActionGroup(self)
        self.month_action_group = QActionGroup(self)
        self.label_action_group = QActionGroup(self)

        # Configurar las acciones
        self.setup_filter_actions("Todos", years, months, labels)
     
    def load_initial_data(self):
        if os.path.exists("index.json"):
            self.load_filter_options()
            self.load_gallery()

    def setup_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.flow_layout = FlowLayout(self.content_widget, margin=1, spacing=1)
        self.content_widget.setLayout(self.flow_layout)
        self.scroll_area.setWidget(self.content_widget)

    def setup_pagination_frame(self):
        self.pagination_frame = QFrame()
        self.pagination_frame.setFrameStyle(QFrame.StyledPanel)
        self.pagination_frame.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border-top: 1px solid #ccc; }"
        )
        
        layout = QHBoxLayout(self.pagination_frame)
        layout.setContentsMargins(10, 5, 10, 5)

        self.prev_button = QPushButton("« Anterior")
        self.page_label = QLabel()
        self.next_button = QPushButton("Siguiente »")

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        layout.addStretch()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)
        layout.addStretch()

        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

    def setup_menu(self):
        menubar = self.menuBar()
        self.setup_filter_menu(menubar)
        self.setup_sort_menu(menubar)
        self.setup_tools_menu(menubar)
        
        config_action = QAction("Opciones", self)
        config_action.triggered.connect(self.open_config_window)
        menubar.addAction(config_action)

    def setup_filter_menu(self, menubar):
        self.filter_menu = menubar.addMenu("Filtrar")
        self.year_menu = QMenu("Año", self)
        self.month_menu = QMenu("Mes", self)
        self.label_menu = QMenu("Etiquetas", self)
        self.filter_menu.addMenu(self.year_menu)
        self.filter_menu.addMenu(self.month_menu)
        self.filter_menu.addMenu(self.label_menu)

        show_duplicates_action = QAction("Mostrar Duplicados", self, checkable=True)
        show_duplicates_action.triggered.connect(
            lambda checked: self.set_filter(show_duplicates=checked)
        )
        self.filter_menu.addAction(show_duplicates_action)

    def setup_sort_menu(self, menubar):
        sort_menu = menubar.addMenu("Ordenar")
        sort_asc_action = QAction("Ascendente", self, checkable=True)
        sort_desc_action = QAction("Descendente", self, checkable=True)
        
        sort_asc_action.triggered.connect(
            lambda: self.set_sort_order("ascendente", sort_asc_action, sort_desc_action)
        )
        sort_desc_action.triggered.connect(
            lambda: self.set_sort_order("descendente", sort_asc_action, sort_desc_action)
        )
        
        sort_menu.addAction(sort_asc_action)
        sort_menu.addAction(sort_desc_action)
        sort_asc_action.setChecked(True)

    def setup_tools_menu(self, menubar):
        tools_menu = menubar.addMenu("Herramientas")
        
        # Submenú Generación
        generation_menu = QMenu("Generación", self)
        tools_menu.addMenu(generation_menu)
        
        # Crear todas las acciones primero
        self.update_all_action = QAction("Actualizar Todo", self)
        self.generate_thumbnails_action = QAction("Generar Miniaturas", self)
        self.generate_index_action = QAction("Generar Índice", self)
        self.generate_labels_action = QAction("Generar Etiquetas", self)
        self.generate_duplicates_action = QAction("Generar Duplicados", self)
        
        # Conectar las señales
        self.update_all_action.triggered.connect(self.update_all)
        self.generate_thumbnails_action.triggered.connect(self.generate_thumbnails)
        self.generate_index_action.triggered.connect(self.generate_index)
        self.generate_labels_action.triggered.connect(self.start_classification)
        self.generate_duplicates_action.triggered.connect(self.start_duplicate_detection)
        
        # Agregar las acciones al menú
        generation_menu.addAction(self.update_all_action)
        generation_menu.addSeparator()
        generation_menu.addAction(self.generate_thumbnails_action)
        generation_menu.addAction(self.generate_index_action)
        generation_menu.addAction(self.generate_labels_action)
        generation_menu.addAction(self.generate_duplicates_action)

        # Submenú Selección
        selection_menu = QMenu("Selección", self)
        tools_menu.addMenu(selection_menu)
        
        self.activate_selection_action = QAction("Activar", self, checkable=True)
        self.select_all_action = QAction("Seleccionar Todo", self, checkable=True)
        self.delete_action = QAction("Eliminar", self)
        
        selection_menu.addAction(self.activate_selection_action)
        selection_menu.addAction(self.select_all_action)
        selection_menu.addSeparator()
        selection_menu.addAction(self.delete_action)
        
        self.activate_selection_action.triggered.connect(self.toggle_selection_mode)
        self.select_all_action.triggered.connect(self.select_all)
        self.delete_action.triggered.connect(self.delete_selected)
        
        self.select_all_action.setEnabled(False)
        self.delete_action.setEnabled(False)
        
        self.activate_selection_action.triggered.connect(
            lambda checked: self.select_all_action.setEnabled(checked)
        )

        # Guardar referencia a las acciones de generación después de crearlas
        self.generation_actions = [
            self.update_all_action,
            self.generate_thumbnails_action,
            self.generate_index_action,
            self.generate_labels_action,
            self.generate_duplicates_action
        ]
        
        # Deshabilitar inicialmente todas las acciones
        self.update_tools_menu_state()

    def update_tools_menu_state(self):
        """Actualiza el estado de las opciones del menú herramientas"""
        enabled = self.config_manager.are_paths_configured()
        for action in self.generation_actions:
            action.setEnabled(enabled)

    def check_paths(self):
        """Verifica que existan las rutas necesarias y las crea si es necesario"""
        photos_path = self.config_manager.get_photos_path()
        thumbnails_path = self.config_manager.get_thumbnails_path()
        
        if not photos_path or not thumbnails_path:
            QMessageBox.critical(
                self,
                "Error",
                "Las rutas de fotos y miniaturas deben estar configuradas."
            )
            return False

        try:
            if not os.path.exists(photos_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    "La carpeta de fotos no existe. Por favor, verifique la configuración."
                )
                return False
                
            if not os.path.exists(thumbnails_path):
                os.makedirs(thumbnails_path)
                
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al acceder a las rutas: {str(e)}"
            )
            return False
        

    def update_config(self):
        if hasattr(self, 'classifier_thread'):
            self.classifier_thread.confidence_threshold = self.config_manager.get_value(
                "clip", "confidence_threshold"
            )

    def toggle_selection_mode(self, checked):
        self.selection_mode = checked
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and item.widget():
                thumbnail = item.widget()
                if isinstance(thumbnail, ThumbnailWidget):
                    thumbnail.set_selection_mode(checked)
        
        if not checked:
            self.delete_action.setEnabled(False)
            self.select_all_action.setChecked(False)

    def select_all(self):
        if not self.activate_selection_action.isChecked():
            return
        
        should_select = self.select_all_action.isChecked()
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and item.widget():
                thumbnail = item.widget()
                if isinstance(thumbnail, ThumbnailWidget):
                    thumbnail.checkbox.setChecked(should_select)

        self.update_delete_action()

    def update_delete_action(self):
        has_selections = any(
            item.widget().is_selected
            for i in range(self.flow_layout.count())
            if (item := self.flow_layout.itemAt(i)) and isinstance(item.widget(), ThumbnailWidget)
        )
        self.delete_action.setEnabled(has_selections)

    def open_full_image(self, image_path):
        image_window = ImageWindow(image_path)
        image_window.setAttribute(Qt.WA_DeleteOnClose)
        image_window.destroyed.connect(lambda: self.image_windows.remove(image_window))
        self.image_windows.append(image_window)
        image_window.show()

    def open_config_window(self):
        config_window = ConfigWindow(self, self.config_manager)
        if config_window.exec_() == QDialog.Accepted:
            self.update_config()
            self.update_tools_menu_state()

    def update_pagination_controls(self):
        total_images = len(self.filtered_images)
        self.total_pages = (total_images - 1) // self.items_per_page + 1
        
        if total_images > self.items_per_page:
            self.pagination_frame.show()
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)
            self.page_label.setText(
                f"Página {self.current_page + 1} de {self.total_pages} "
                f"(Total: {total_images} imágenes)"
            )
        else:
            self.pagination_frame.hide()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_current_page()
            self.scroll_area.verticalScrollBar().setValue(0)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_current_page()
            self.scroll_area.verticalScrollBar().setValue(0)

    def get_selected_images(self):
        selected = []
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and isinstance(item.widget(), ThumbnailWidget):
                thumbnail = item.widget()
                if thumbnail.is_selected:
                    selected.append({
                        'thumbnail': thumbnail.thumbnail_path,
                        'original': thumbnail.original_path
                    })
        return selected

    def delete_selected(self):
        selected = self.get_selected_images()
        if not selected:
            return
        
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            f'Está a punto de eliminar {len(selected)} imágenes. ¿Desea continuar?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.perform_deletion(selected)

    def perform_deletion(self, selected_images):
        try:
            # Eliminar archivos físicos
            for image in selected_images:
                if os.path.exists(image['original']):
                    os.remove(image['original'])
                if os.path.exists(image['thumbnail']):
                    os.remove(image['thumbnail'])

            # Actualizar archivos JSON
            self.update_json_after_deletion(selected_images)
            self.load_gallery()
            
            QMessageBox.information(
                self,
                "Eliminación completada",
                f"Se han eliminado {len(selected_images)} imágenes correctamente."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Ha ocurrido un error durante la eliminación: {str(e)}"
            )

    def update_json_after_deletion(self, selected_images):
        deleted_originals = {img['original'] for img in selected_images}
        deleted_thumbnails = {img['thumbnail'] for img in selected_images}

        # Actualizar index.json
        if os.path.exists("index.json"):
            with open("index.json", 'r') as f:
                index_data = json.load(f)
            index_data = [img for img in index_data if img['original'] not in deleted_originals]
            with open("index.json", 'w') as f:
                json.dump(index_data, f, indent=4)

        # Actualizar classification_results.json
        if os.path.exists("classification_results.json"):
            with open("classification_results.json", 'r') as f:
                class_data = json.load(f)
            class_data = {k: v for k, v in class_data.items() if k not in deleted_thumbnails}
            with open("classification_results.json", 'w') as f:
                json.dump(class_data, f, indent=4)

        # Actualizar duplicates.json
        if os.path.exists("duplicates.json"):
            with open("duplicates.json", 'r') as f:
                dup_data = json.load(f)
            for method in dup_data:
                dup_data[method] = [
                    dup for dup in dup_data[method]
                    if dup['original'] not in deleted_originals
                    and dup['duplicate'] not in deleted_originals
                ]
            with open("duplicates.json", 'w') as f:
                json.dump(dup_data, f, indent=4)

    def generate_thumbnails(self):
        if not self.check_paths():
            return

        photos_path = self.config_manager.get_photos_path()
        thumbnails_path = self.config_manager.get_thumbnails_path()

        total_images = sum(1 for _, _, files in os.walk(photos_path)
                         for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png')))

        progress_dialog = QProgressDialog(
            "Generando miniaturas...", "Cancelar", 0, total_images, self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        current_progress = 0

        for root, _, files in os.walk(photos_path):
            if progress_dialog.wasCanceled():
                break

            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(root, photos_path)
                    thumb_dir = os.path.join(thumbnails_path, relative_path)
                    os.makedirs(thumb_dir, exist_ok=True)

                    if self.generate_thumbnail(file_path, thumb_dir):
                        current_progress += 1
                        progress_dialog.setValue(current_progress)

        progress_dialog.close()

    def generate_thumbnail(self, file_path, thumb_dir):
        try:
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                min_dimension = min(img.size)
                crop_box = (
                    (img.width - min_dimension) // 2,
                    (img.height - min_dimension) // 2,
                    (img.width + min_dimension) // 2,
                    (img.height + min_dimension) // 2,
                )
                img = img.crop(crop_box)
                img.thumbnail((300, 300))
                img = ImageOps.exif_transpose(img)
                img.save(
                    os.path.join(thumb_dir, os.path.basename(file_path)),
                    "JPEG",
                    quality=85,
                )
                return True
        except Exception:
            return False

    def generate_index(self):
        if not self.check_paths():
            return

        photos_path = self.config_manager.get_photos_path()
        thumbnails_path = self.config_manager.get_thumbnails_path()

        index = []
        total_images = sum(1 for _, _, files in os.walk(photos_path)
                         for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png')))

        progress_dialog = QProgressDialog(
            "Generando índice...", "Cancelar", 0, total_images, self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        current_progress = 0

        for root, _, files in os.walk(photos_path):
            if progress_dialog.wasCanceled():
                break

            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    relative_path = os.path.relpath(root, photos_path)
                    thumbnail_file = os.path.join(thumbnails_path, relative_path, file)
                    original_file = os.path.join(root, file)

                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) >= 2:
                        year, month = path_parts[:2]
                        filename_base = os.path.splitext(file)[0]
                        filename_parts = filename_base.split("_")
                        
                        if len(filename_parts) >= 6:
                            day = filename_parts[2]
                            timestamp = "_".join(filename_parts[:6])
                        else:
                            day = "01"
                            timestamp = f"{year}_{month}_{day}_00_00_00"

                        index.append({
                            "thumbnail": thumbnail_file,
                            "original": original_file,
                            "year": year,
                            "month": month,
                            "day": day,
                            "timestamp": timestamp
                        })

                    current_progress += 1
                    progress_dialog.setValue(current_progress)

        index.sort(key=lambda x: x["timestamp"])
        with open("index.json", "w") as f:
            json.dump(index, f, indent=4)

        progress_dialog.close()

    def start_classification(self):
        if not self.check_paths():
            return

        if not os.path.exists("index.json"):
            return

        if self.model is None:
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        with open("index.json", "r") as f:
            images_data = json.load(f)

        self.classifier_thread = ImageClassifierThread(
            self.model, 
            self.processor, 
            images_data,
            self.config_manager
        )
        self.classifier_thread.progress.connect(self.update_classification_progress)
        self.classifier_thread.finished.connect(self.classification_finished)

        self.progress_dialog = QProgressDialog(
            "Clasificando imágenes...", "Cancelar", 0, len(images_data), self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        self.classifier_thread.start()

    def update_classification_progress(self, thumbnail_path, label, confidence):
        self.progress_dialog.setValue(self.progress_dialog.value() + 1)

    def classification_finished(self):
        self.progress_dialog.close()
        self.load_filter_options()
        self.load_gallery()

    def start_duplicate_detection(self):

        if not self.check_paths():
            return
            
        if not os.path.exists("index.json"):
            return

        with open("index.json", "r") as f:
            images_data = json.load(f)

        progress_dialog = QProgressDialog(
            "Buscando duplicados...", "Cancelar", 0, len(images_data), self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        detector = DuplicateDetector()
        duplicates = detector.find_duplicates(
            images_data, 
            lambda current, total: progress_dialog.setValue(current)
        )

        progress_dialog.close()

        total_duplicates = sum(len(group) for group in duplicates.values())
        QMessageBox.information(
            self,
            "Detección Completada",
            f"Se encontraron {total_duplicates} duplicados:\n"
            f"- Por hash: {len(duplicates.get('hash', []))}\n"
            f"- Por metadatos EXIF: {len(duplicates.get('exif', []))}"
        )

    def update_all(self):
        self.generate_thumbnails()
        self.generate_index()
        self.load_filter_options()
        self.start_classification()

    def set_sort_order(self, order, asc_action, desc_action):
        self.sort_order = order
        asc_action.setChecked(order == "ascendente")
        desc_action.setChecked(order == "descendente")
        self.loaded_thumbnails.clear()
        self.load_gallery()

    def create_thumbnail(self, thumbnail_path, original_path):
        thumbnail = ThumbnailWidget(thumbnail_path, original_path, self.content_widget)
        if hasattr(self, 'selection_mode') and self.selection_mode:
            thumbnail.set_selection_mode(True)
        return thumbnail

    def setup_filter_actions(self, all_text, years, months, labels):
        # Configuración del grupo de años
        all_years_action = QAction(all_text, self, checkable=True)
        all_years_action.triggered.connect(lambda: self.set_filter(year=all_text))
        self.year_menu.addAction(all_years_action)
        self.year_action_group.addAction(all_years_action)
        all_years_action.setChecked(True)

        for year in years:
            action = QAction(year, self, checkable=True)
            action.triggered.connect(lambda checked, y=year: self.set_filter(year=y))
            self.year_menu.addAction(action)
            self.year_action_group.addAction(action)

        # Configuración del grupo de meses
        all_months_action = QAction(all_text, self, checkable=True)
        all_months_action.triggered.connect(lambda: self.set_filter(month=all_text))
        self.month_menu.addAction(all_months_action)
        self.month_action_group.addAction(all_months_action)
        all_months_action.setChecked(True)

        for month in months:
            month_name = MONTHS.get(month, month)
            action = QAction(month_name, self, checkable=True)
            action.triggered.connect(lambda checked, m=month: self.set_filter(month=m))
            self.month_menu.addAction(action)
            self.month_action_group.addAction(action)

        # Configuración del grupo de etiquetas
        all_labels_action = QAction(all_text, self, checkable=True)
        all_labels_action.triggered.connect(lambda: self.set_filter(label=all_text))
        self.label_menu.addAction(all_labels_action)
        self.label_action_group.addAction(all_labels_action)
        all_labels_action.setChecked(True)

        for label in sorted(labels):
            action = QAction(label, self, checkable=True)
            action.triggered.connect(lambda checked, l=label: self.set_filter(label=l))
            self.label_menu.addAction(action)
            self.label_action_group.addAction(action)

    def load_gallery(self):
        if not os.path.exists("index.json"):
            return

        with open("index.json", "r") as f:
            images = json.load(f)
        
        classifications = {}
        if os.path.exists("classification_results.json"):
            with open("classification_results.json", "r") as f:
                classifications = json.load(f)

        self.filtered_images = self.filter_images(images, classifications)
        self.filtered_images.sort(
            key=lambda x: x["timestamp"],
            reverse=self.sort_order == "descendente"
        )
        
        self.current_page = 0
        self.load_current_page()

    def filter_images(self, images, classifications):
        filtered = images.copy()

        if self.filter_year:
            filtered = [img for img in filtered if img["year"] == self.filter_year]
        if self.filter_month:
            filtered = [img for img in filtered if img["month"] == self.filter_month]
        if self.filter_label and classifications:
            filtered = [
                img for img in filtered
                if img["thumbnail"] in classifications
                and classifications[img["thumbnail"]]["label"] == self.filter_label
            ]

        if self.show_duplicates and os.path.exists("duplicates.json"):
            with open("duplicates.json", "r") as f:
                duplicates = json.load(f)

            duplicate_paths = {
                path
                for method_duplicates in duplicates.values()
                for dup in method_duplicates
                for path in (dup["original"], dup["duplicate"])
            }

            filtered = [img for img in filtered if img["original"] in duplicate_paths]

        return filtered

    def set_filter(self, year=None, month=None, label=None, show_duplicates=None):
        if year is not None:
            self.filter_year = year if year != "Todos" else None
        if month is not None:
            self.filter_month = month if month != "Todos" else None
        if label is not None:
            self.filter_label = label if label != "Todos" else None
        if show_duplicates is not None:
            self.show_duplicates = show_duplicates

        self.loaded_thumbnails.clear()
        self.load_gallery()

    def load_current_page(self):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_images))
        
        for image in self.filtered_images[start_idx:end_idx]:
            thumbnail = self.create_thumbnail(image["thumbnail"], image["original"])
            if thumbnail:
                self.flow_layout.addWidget(thumbnail)

        self.update_pagination_controls()
        
        size = self.flow_layout.minimumSize()
        self.content_widget.setMinimumSize(size)
        self.content_widget.updateGeometry()