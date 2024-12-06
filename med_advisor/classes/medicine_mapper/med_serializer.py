import os
import json

PATH="./medicine_mapper/json-outputs/scraped_data.json"
DIR_PATH="./medicine_mapper/json-outputs/"

class JsonFileHandler:
    def __init__(self, file_path=PATH):
        self.file_path = file_path
        #self.lock = threading.Lock()

    def deserialize(self):
        """Deserializes data from the JSON file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def serialize(self, data):
        if not os.path.exists(DIR_PATH):
                os.makedirs(DIR_PATH)
        """Serializes data to the JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)