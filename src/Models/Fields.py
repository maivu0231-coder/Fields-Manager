from dataclasses import dataclass
from .Base import Base
@dataclass
class Field(Base):
    field_id: str = ""
    name: str = ""
    field_type: str = ""
    price_per_hour: float = 0.0
    status: str = "Trống"
