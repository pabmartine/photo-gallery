# Photo Gallery Manager

## Descripción
Photo Gallery Manager es una aplicación de escritorio desarrollada en Python que permite gestionar y organizar colecciones de fotografías de manera eficiente. La aplicación ofrece funcionalidades avanzadas como clasificación automática de imágenes usando tecnología CLIP, detección de duplicados y una interfaz gráfica intuitiva para la navegación y gestión de fotos.

## Características Principales
- 📁 Organización automática de fotos en estructura de directorios
- 🖼️ Generación automática de miniaturas
- 🤖 Clasificación automática de imágenes usando CLIP (distingue entre fotos, capturas de pantalla, documentos y memes)
- 🔍 Detección de duplicados mediante hash de imagen y metadatos EXIF
- 🗂️ Filtrado por año, mes y tipo de imagen
- 🔄 Ordenación ascendente/descendente por fecha
- ✨ Interfaz gráfica intuitiva con sistema de paginación
- ✅ Modo de selección múltiple para operaciones por lotes

## Requisitos del Sistema
- Python 3.8 o superior
- Entorno Linux (probado en Ubuntu)
- Al menos 2GB de RAM disponible (recomendado 4GB)
- Espacio en disco para almacenar las imágenes y miniaturas

## Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/photo-gallery.git
cd photo-gallery
```

### 2. Crear y Activar el Entorno Virtual
```bash
python -m venv py-images-env
source py-images-env/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install PyQt5 Pillow torch transformers imagehash
```

Alternativamente, puedes instalar desde requirements.txt:
```bash
pip install -r requirements.txt
```

## Configuración
1. Ejecuta la aplicación por primera vez:
```bash
python main.py
```

2. Ve a "Opciones" en el menú superior
3. Configura:
   - Carpeta de fotos: directorio donde se encuentran las fotos originales
   - Carpeta de miniaturas: directorio donde se guardarán las miniaturas
   - Umbral de confianza CLIP: ajusta la sensibilidad de la clasificación automática

## Uso

### Generación Inicial
1. Una vez configuradas las rutas, ve al menú "Herramientas > Generación"
2. Ejecuta en orden:
   - "Generar Miniaturas"
   - "Generar Índice"
   - "Generar Etiquetas"
   - O usa "Actualizar Todo" para ejecutar todo el proceso

### Navegación
- Usa los filtros en el menú "Filtrar" para organizar por año, mes o tipo de imagen
- El menú "Ordenar" permite cambiar entre orden ascendente y descendente
- La paginación en la parte inferior permite navegar entre grupos de imágenes

### Selección y Eliminación
1. Ve a "Herramientas > Selección"
2. Activa el modo selección
3. Selecciona imágenes individualmente o usa "Seleccionar Todo"
4. Usa la opción "Eliminar" para borrar las imágenes seleccionadas

## Estructura de Archivos
```
photo-gallery/
├── main.py
├── config/
│   ├── __init__.py
│   └── config_manager.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── config_window.py
│   ├── image_window.py
│   └── widgets/
│       ├── __init__.py
│       ├── flow_layout.py
│       └── thumbnail_widget.py
├── utils/
│   ├── __init__.py
│   ├── duplicate_detector.py
│   └── image_classifier.py
└── constants/
    ├── __init__.py
    └── app_constants.py
```

## Archivos Generados
La aplicación genera varios archivos JSON para mantener el estado:
- `index.json`: Índice de todas las imágenes y sus metadatos
- `classification_results.json`: Resultados de la clasificación CLIP
- `duplicates.json`: Registro de imágenes duplicadas
- `app_config.json`: Configuración de la aplicación

## Notas de Desarrollo
- Interfaz construida con PyQt5
- Clasificación de imágenes mediante modelo CLIP de OpenAI
- Detección de duplicados basada en perceptual hashing y metadatos EXIF
- Estructura modular para facilitar extensiones futuras

## Limitaciones Conocidas
- La clasificación inicial de imágenes puede ser lenta dependiendo del tamaño de la colección
- Actualmente solo soporta formatos de imagen JPG, JPEG y PNG
- Los procesos de generación de miniaturas y clasificación consumen recursos significativos

## Licencia
Este proyecto está licenciado bajo los términos de la licencia MIT. del proyecto: https://github.com/tu-usuario/photo-gallery