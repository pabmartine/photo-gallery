import os
import json
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from collections import defaultdict
import imagehash

class DuplicateDetector:
    def __init__(self):
        self.duplicates_file = "duplicates.json"
        self.hash_threshold = 5
        self.similarity_threshold = 0.85
        self.batch_size = 50

    def get_exif_data(self, image_path):
        try:
            with Image.open(image_path) as img:
                if not hasattr(img, "_getexif") or not callable(img._getexif):
                    return {}
                    
                exif = img._getexif()
                if not exif:
                    return {}

                relevant_tags = {
                    "DateTime", "DateTimeOriginal", "CreateDate",
                    "Make", "Model", "Orientation",
                }

                exif_data = {}
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in relevant_tags:
                        if "DateTime" in tag and isinstance(value, str):
                            try:
                                dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                exif_data[tag] = dt.isoformat()
                            except ValueError:
                                exif_data[tag] = value
                        else:
                            exif_data[tag] = str(value) if not isinstance(value, (str, int, float)) else value
                return exif_data
        except Exception:
            return {}

    def compute_image_hash(self, image_path):
        try:
            with Image.open(image_path) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                return str(imagehash.average_hash(img))
        except Exception:
            return None

    def _process_hash_comparison(self, img_hash, img_path, hash_dict, duplicates):
        for existing_hash, existing_path in hash_dict.items():
            if img_path != existing_path["path"]:
                try:
                    hash_diff = abs(int(img_hash, 16) - int(existing_hash, 16))
                    if hash_diff <= self.hash_threshold:
                        duplicates["hash"].append({
                            "original": existing_path["path"],
                            "duplicate": img_path,
                            "similarity": 1 - (hash_diff / 64.0),
                            "method": "hash"
                        })
                except ValueError:
                    continue
        hash_dict[img_hash] = {"path": img_path}

    def _process_exif_comparison(self, img_path, duplicates):
        exif_data = self.get_exif_data(img_path)
        if not exif_data:
            return

        if not hasattr(self, "_exif_data"):
            self._exif_data = {}

        for prev_path, prev_exif in self._exif_data.items():
            if img_path == prev_path:
                continue
                
            for tag in ["DateTime", "DateTimeOriginal", "CreateDate"]:
                if tag in exif_data and tag in prev_exif and exif_data[tag] == prev_exif[tag]:
                    duplicates["exif"].append({
                        "original": prev_path,
                        "duplicate": img_path,
                        "similarity": 1.0,
                        "method": "exif"
                    })
                    break

        self._exif_data[img_path] = exif_data

    def find_duplicates(self, images_data, progress_callback=None):
        total_images = len(images_data)
        duplicates = defaultdict(list)
        processed = set()
        hash_dict = {}

        for start_idx in range(0, total_images, self.batch_size):
            if progress_callback:
                progress_callback(start_idx, total_images)

            end_idx = min(start_idx + self.batch_size, total_images)
            batch = images_data[start_idx:end_idx]

            for img_data in batch:
                img_path = img_data["original"]
                if img_path in processed:
                    continue

                img_hash = self.compute_image_hash(img_path)
                if img_hash:
                    self._process_hash_comparison(img_hash, img_path, hash_dict, duplicates)

                self._process_exif_comparison(img_path, duplicates)
                processed.add(img_path)

        try:
            with open(self.duplicates_file, "w") as f:
                json.dump(dict(duplicates), f, indent=4)
        except Exception:
            pass

        return duplicates