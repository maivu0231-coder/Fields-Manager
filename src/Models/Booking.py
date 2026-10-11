from dataclasses import dataclass
from.Base import Base

@dataclass
class Booking(Base):
    booking_id: str = ""
    field_id: str = ""
    customer_name: str = ""
    phone: str = ""
    booking_date: str = ""
    start_time: str = ""
    end_time: str = ""
    deposit: float = 0.0
    status: str = "Đã cọc"
    field_name: str = ""
    price_per_hour: float = 0.0
