import json

class Config:
    def __init__(self, file_path='config.json'):
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        for key, value in config_data.items():
            if not key.startswith("_comment"):
                if "ABI" in key:
                    setattr(self, key, json.loads(value))
                else:
                    setattr(self, key, value)

def load_config(file_path='config.json'):
    return Config(file_path)

