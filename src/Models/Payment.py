from dataclasses import dataclass
from .Base import Base
@dataclass
class Payment(Base):
    invoice_id: str = "" # Mã hóa đơn
    booking_id: str = "" # Mã đặt sân
    total_amount: float = 0.0
    payment_time: str = ""