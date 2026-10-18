from dataclasses import dataclass, field
from datetime import datetime
from .Base import Base


@dataclass
class Payment(Base):
    invoice_id: str = ""
    booking_id: str = ""
    customer_name: str = ""
    field_name: str = ""
    duration_hours: float = 0.0
    price_per_hour: float = 0.0
    rental_fee: float = 0.0
    surcharge: float = 0.0
    deposit_deducted: float = 0.0
    total_amount: float = 0.0
    payment_time: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )