import json
import os
import tempfile
from typing import Any, List


class JSONHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        #auto create the directory if it doesn't exist
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def read_all(self) -> List[dict]:
        #read all data from the JSON file and return as a list of dictionaries
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def write_all(self, data: List[dict]) -> bool:
        #write the list of dictionaries to the JSON file atomically
        dir_name = os.path.dirname(self.file_path) or "."
        try:
            with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, ensure_ascii=False, indent=2)
                temp_name = tf.name

            os.replace(temp_name, self.file_path)
            return True
        except OSError:
            if "temp_name" in locals() and os.path.exists(temp_name):
                os.remove(temp_name)
            return False