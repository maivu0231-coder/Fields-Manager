from dataclasses import dataclass, field
from datetime import datetime
from .Base import Base

@dataclass
class Payment(Base):
    invoice_id: str = ""         # Mã hóa đơn (VD: "INV01")
    booking_id: str = ""         # Mã đơn đặt sân (VD: "BK01")
    customer_name: str = ""      # Tên khách hàng
    field_name: str = ""         # Tên sân
    duration_hours: float = 0.0  # Số giờ đá thực tế (end_time - start_time)
    price_per_hour: float = 0.0  # Đơn giá sân
    rental_fee: float = 0.0      # Tiền thuê sân = duration_hours * price_per_hour
    surcharge: float = 0.0       # Phụ phí (nước uống, bóng, đèn,...)
    deposit_deducted: float = 0.0# Tiền cọc được trừ ra
    total_amount: float = 0.0    # Tiền phải trả = rental_fee + surcharge - deposit_deducted
    payment_time: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    