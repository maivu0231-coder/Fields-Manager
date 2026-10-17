from enum import Enum
from dataclasses import dataclass
from Src.Models.Base import Base

class FieldStatus(str, Enum):
    AVAILABLE = "Còn trống"
    IN_USE = "Đang có khách"
    MAINTENANCE = "Bảo trì"

class FieldType(str, Enum):
    FIELD_5 = "Sân 5"
    FIELD_7 = "Sân 7"
    FIELD_11 = "Sân 11"

@dataclass
class Field(Base):
    """Dataclass quản lý thông tin sân bóng theo phong cách maivu0231-coder"""
    field_code: str = ""
    field_name: str = ""
    field_type: str = FieldType.FIELD_5.value
    price_per_hour: float = 0.0
    status: str = FieldStatus.AVAILABLE.value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "field_code": self.field_code,
            "field_name": self.field_name,
            "field_type": self.field_type if isinstance(self.field_type, str) else self.field_type.value,
            "price_per_hour": self.price_per_hour,
            "status": self.status if isinstance(self.status, str) else self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            field_code=data.get("field_code", ""),
            field_name=data.get("field_name", ""),
            field_type=data.get("field_type", FieldType.FIELD_5.value),
            price_per_hour=float(data.get("price_per_hour", 0.0)),
            status=data.get("status", FieldStatus.AVAILABLE.value),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
