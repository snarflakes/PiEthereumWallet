import json

class Config:
    def __init__(self, file_path='config.json'):
        try:
            with open(file_path, 'r') as file:
                config_data = json.load(file)
        except FileNotFoundError:
            raise RuntimeError(f"Error: The file {file_path} was not found.")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error: JSON decoding error in file {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")
        
        for key, value in config_data.items():
            if not key.startswith("_comment"):
                if "ABI" in key:
                    parsed_value = self.safe_json_loads(value, key)
                    if parsed_value is None:
                        raise RuntimeError(f"Error: Invalid ABI for key {key}")
                    setattr(self, key, parsed_value)
                else:
                    setattr(self, key, value)

    def safe_json_loads(self, value, key):
        try:
            loaded_value = json.loads(value)
            if not isinstance(loaded_value, list):
                raise ValueError(f"The value for key {key} is not a list")
            return loaded_value
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON for ABI key {key}: {e}")
        except ValueError as e:
            raise RuntimeError(f"Validation error for ABI key {key}: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while parsing JSON for key {key}: {e}")

def load_config(file_path='config.json'):
    return Config(file_path)


