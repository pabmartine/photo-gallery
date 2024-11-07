# Photo Gallery Manager

## Description
Photo Gallery Manager is a desktop application developed in Python that efficiently manages and organizes photo collections. The application offers advanced features such as automatic image classification using CLIP technology, duplicate detection, and an intuitive graphical interface for photo navigation and management.

## Key Features
- 📁 Automatic photo organization in directory structure
- 🖼️ Automatic thumbnail generation
- 🤖 Automatic image classification using CLIP (distinguishes between photos, screenshots, documents, and memes)
- 🔍 Duplicate detection using image hashing and EXIF metadata
- 🗂️ Filter by year, month, and image type
- 🔄 Ascending/descending date sorting
- ✨ Intuitive graphical interface with pagination system
- ✅ Multiple selection mode for batch operations

## System Requirements
- Python 3.8 or higher
- Linux environment (tested on Ubuntu)
- At least 2GB of available RAM (4GB recommended)
- Disk space for storing images and thumbnails

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/photo-gallery.git
cd photo-gallery
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv py-images-env
source py-images-env/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install PyQt5 Pillow torch transformers imagehash
```

Alternatively, you can install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Configuration
1. Run the application for the first time:
```bash
python main.py
```

2. Go to "Options" in the top menu
3. Configure:
   - Photos folder: directory where original photos are located
   - Thumbnails folder: directory where thumbnails will be saved
   - CLIP confidence threshold: adjust automatic classification sensitivity

## Usage

### Initial Generation
1. Once paths are configured, go to "Tools > Generation"
2. Execute in order:
   - "Generate Thumbnails"
   - "Generate Index"
   - "Generate Labels"
   - Or use "Update All" to execute the entire process

### Navigation
- Use filters in the "Filter" menu to organize by year, month, or image type
- The "Sort" menu allows switching between ascending and descending order
- Pagination at the bottom allows navigation between image groups

### Selection and Deletion
1. Go to "Tools > Selection"
2. Activate selection mode
3. Select images individually or use "Select All"
4. Use the "Delete" option to remove selected images

## File Structure
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

## Generated Files
The application generates several JSON files to maintain state:
- `index.json`: Index of all images and their metadata
- `classification_results.json`: CLIP classification results
- `duplicates.json`: Record of duplicate images
- `app_config.json`: Application configuration

## Development Notes
- Interface built with PyQt5
- Image classification using OpenAI's CLIP model
- Duplicate detection based on perceptual hashing and EXIF metadata
- Modular structure to facilitate future extensions

## Known Limitations
- Initial image classification can be slow depending on collection size
- Currently only supports JPG, JPEG, and PNG image formats
- Thumbnail generation and classification processes consume significant resources

## License
This project is licensed under the terms of the MIT license.