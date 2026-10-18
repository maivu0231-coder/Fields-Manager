from dataclasses import dataclass,asdict,field,fields
from datetime import datetime
from typing import Any, Dict
@dataclass
class Base:
    created_at: datetime = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: datetime = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #a function to convert the dataclass to a dictionary, including nested dataclasses
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    @classmethod
    #a function to create an instance of the dataclass from a dictionary, including nested dataclasses
    def from_dict(cls,data:Dict[str,Any])->'Base':
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k:v for k,v in data.items() if k in field_names}
        return cls(**filtered_data)

