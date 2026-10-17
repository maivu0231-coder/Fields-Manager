from datetime import datetime
from typing import List, Optional

from Models import Booking, Payment
from Storage.repositories import BookingRepository, PaymentRepository

class PaymentManager:
    
    def __init__(self):
        self._booking_repo = BookingRepository()
        self._payment_repo = PaymentRepository()
        self._booking_by_id = {
            b.booking_id: b for b in self._booking_repo.get_all()
        }
        self._paid_ids = {
            p.booking_id for p in self._payment_repo.get_all()
        }
        
    def find_booking_by_name(self, name: str) -> Optional[Booking]:
        return self._booking_repo.find_by_name(name)
    
    def get_unpaid_bookings(self) -> List[Booking]:
        all_bookings = self._booking_repo.get_all()
        return [
            b for b in all_bookings
            if b.status == "Chờ thanh toán"
            and b.booking_id not in self._paid_ids
        ]
    
    @staticmethod
    def calc_hours(start: str, end: str) -> float:
        fmt = "%H:%M"
        delta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
        return round(delta.total_seconds() / 3600, 2)
    
    def preview(self, booking: Booking, surcharge: float = 0.0) -> dict:
        duration = self.calc_hours(booking.start_time, booking.end_time)
        rental_fee = duration * booking.price_per_hour
        raw_total = rental_fee + surcharge - booking.deposit
        if raw_total < 0:
            total = 0.0
        else:
            total = raw_total
        return {
            "duration_hours": duration,
            "price_per_hour": booking.price_per_hour,
            "rental_fee": rental_fee,
            "surcharge": surcharge,
            "deposit_deducted": booking.deposit,
            "total_amount": total,
        }
        
    def pay(self, booking: Booking, surcharge: float = 0.0) -> Payment:
        if booking.booking_id in self._paid_ids:
            raise ValueError(f"Đơn {booking.booking_id} đã thanh toán rồi!")
        info = self.preview(booking, surcharge)
        invoice_id = f"INV{len(self._payment_repo.get_all()) + 1:02d}"
        
        payment = Payment(
            invoice_id=invoice_id,
            booking_id=booking.booking_id,
            customer_name=booking.customer_name,
            field_name=booking.field_name,
            duration_hours=info["duration_hours"],
            price_per_hour=info["price_per_hour"],
            rental_fee=info["rental_fee"],
            surcharge=info["surcharge"],
            deposit_deducted=info["deposit_deducted"],
            total_amount=info["total_amount"],
        )
        self._payment_repo.add(payment)
        self._paid_ids.add(booking.booking_id)
        return
    
    @staticmethod
    def format_receipt(p: Payment) -> str:
        return (
            f"===== HÓA ĐƠN {p.invoice_id} =====\n"
            f"Mã đơn    : {p.booking_id}\n"
            f"Khách     : {p.customer_name}\n"
            f"Sân       : {p.field_name}\n"
            f"Thời lượng: {p.duration_hours} h\n"
            f"Đơn giá   : {p.price_per_hour:,.0f} đ/h\n"
            f"Tiền thuê : {p.rental_fee:,.0f} đ\n"
            f"Phụ phí   : {p.surcharge:,.0f} đ\n"
            f"Tiền cọc  : -{p.deposit_deducted:,.0f} đ\n"
            f"------------------------------\n"
            f"TỔNG TIỀN : {p.total_amount:,.0f} đ\n"
            f"Thời điểm : {p.payment_time}\n"
        )