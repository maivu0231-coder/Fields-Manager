from dataclasses import dataclass
from enum import Enum

from .Base import Base


class FieldStatus(str, Enum):
    AVAILABLE = "Trống"
    IN_USE = "Đang có khách"
    MAINTENANCE = "Bảo trì"


class FieldType(str, Enum):
    FIELD_5 = "Sân 5"
    FIELD_7 = "Sân 7"


@dataclass
class Field(Base):
    field_id: str = ""
    name: str = ""
    field_type: str = FieldType.FIELD_5.value
    price_per_hour: float = 0.0
    status: str = FieldStatus.AVAILABLE.value