import os
import json

class ConfigManager:
    DEFAULT_CONFIG = {
        "clip": {
            "confidence_threshold": 90.0
        },
        "paths": {
            "photos": "",
            "thumbnails": ""
        }
    }
    
    def __init__(self):
        self.config_file = "app_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return self.merge_with_defaults(json.load(f))
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def merge_with_defaults(self, config):
        merged = self.DEFAULT_CONFIG.copy()
        for section, values in config.items():
            if section in merged:
                merged[section].update(values)
        return merged
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception:
            return False
    
    def get_value(self, section, key):
        return self.config.get(section, {}).get(key)
    
    def set_value(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def get_photos_path(self):
        return self.get_value("paths", "photos")
        
    def get_thumbnails_path(self):
        return self.get_value("paths", "thumbnails")
        
    def are_paths_configured(self):
        photos_path = self.get_photos_path()
        thumbnails_path = self.get_thumbnails_path()
        return bool(photos_path and thumbnails_path)        