import json
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

class ImageClassifierThread(QThread):
    progress = pyqtSignal(str, str, float)
    finished = pyqtSignal()

    def __init__(self, model, processor, images_data, config_manager=None):
        super().__init__()
        self.model = model
        self.processor = processor
        self.images_data = images_data
        self.confidence_threshold = config_manager.get_value("clip", "confidence_threshold") if config_manager else 90.0

        self.labels = [
            "a real photograph taken with a camera, showing natural lighting and perspective, with no digital elements or text overlays",
            "a digital screenshot that must show computer interface elements like windows, menus, toolbars, or mobile UI elements with perfect pixel edges",
            "a scanned paper document that must show scanner artifacts, paper texture, and printed text or forms with typical scanning imperfections",
            "an internet meme that must have text overlaid at top or bottom using meme fonts, edited for humor with added digital text",
        ]

        self.label_mapping = {
            self.labels[0]: "photo",
            self.labels[1]: "screenshot",
            self.labels[2]: "document",
            self.labels[3]: "meme",
        }

    def classify_image(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(
                text=self.labels, images=image, return_tensors="pt", padding=True
            )
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            best_idx = probs.argmax()
            confidence = probs[0][best_idx].item() * 100

            full_label = self.labels[best_idx]
            simple_label = self.label_mapping[full_label]

            if simple_label != "photo" and confidence < self.confidence_threshold:
                return "photo", confidence

            return simple_label, confidence

        except Exception:
            return "error", 0.0

    def run(self):
        classification_results = {}
        for image_data in self.images_data:
            label, confidence = self.classify_image(image_data["original"])
            classification_results[image_data["thumbnail"]] = {
                "label": label,
                "confidence": confidence,
            }
            self.progress.emit(image_data["thumbnail"], label, confidence)

        with open("classification_results.json", "w") as f:
            json.dump(classification_results, f, indent=4)

        self.finished.emit()