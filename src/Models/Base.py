from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from typing import Any, Dict
@dataclass
class Base:
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self) -> Dict[str, Any]:
        #convert dataclass object to dictionary
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        #inilize dataclass object from dictionary
        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)