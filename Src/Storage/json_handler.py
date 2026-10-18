import json
import os
import tempfile
from typing import List
class JSONHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()
    #create a function to check if the file exists, if not create it with an empty list
    def _ensure_file_exists(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    #create a function to read all data from the file and return it as a list of dictionaries
    def read_all(self)->List[dict]:
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data=json.loads(content)
                return data if isinstance(data,list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    #write a function to write a list of dict to the file 
    def write_all(self,data:List[dict])->bool:
        dir_name = os.path.dirname(self.file_path)
        try:
            with tempfile.NamedTemporaryFile("w",delete=False,dir=dir_name,encoding="utf-8") as tf:
                json.dump(data,tf,ensure_ascii=False,indent=4)
                temp_name=tf.name
            os.replace(temp_name,self.file_path)
            return True
        except OSError:
            if "temp_name" in locals() and os.path.exists(temp_name):
                os.remove(temp_name)
            return False