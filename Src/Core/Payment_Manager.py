import re
from datetime import datetime
from typing import List, Optional

from Src.Models import Booking, Payment
from Src.Storage.repositories import BookingRepository, PaymentRepository


class PaymentManager:
    def __init__(
        self,
        booking_repo: Optional[BookingRepository] = None,
        payment_repo: Optional[PaymentRepository] = None,
    ) -> None:
        self._booking_repo = booking_repo or BookingRepository()
        self._payment_repo = payment_repo or PaymentRepository()
    #get a set of booking IDs that have already been paid
    def _get_paid_booking_ids(self) -> set[str]:
        return {p.booking_id for p in self._payment_repo.get_all()}

    def _next_invoice_id(self) -> str:
        numbers = []
        for p in self._payment_repo.get_all():
            match = re.fullmatch(r"INV(\d+)", p.invoice_id)
            if match:
                numbers.append(int(match.group(1)))
        return f"INV{max(numbers, default=0) + 1:02d}"

    def find_booking_by_name(self, name: str) -> Optional[Booking]:
        return self._booking_repo.find_by_name(name)

    def get_unpaid_bookings(self) -> List[Booking]:
        paid_ids = self._get_paid_booking_ids()
        all_bookings = self._booking_repo.get_all()
        return [
            b
            for b in all_bookings
            if b.status in ("Chờ thanh toán", "Đã cọc")
            and b.booking_id not in paid_ids
        ]

    def get_all_payments(self) -> List[Payment]:
        return self._payment_repo.get_all()

    @staticmethod
    def calc_hours(start: str, end: str) -> float:
        fmt = "%H:%M"
        delta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
        return round(delta.total_seconds() / 3600, 2)

    def preview(self, booking: Booking, surcharge: float = 0.0) -> dict:
        duration = self.calc_hours(booking.start_time, booking.end_time)
        rental_fee = duration * booking.price_per_hour
        raw_total = rental_fee + surcharge - booking.deposit
        total = max(0.0, raw_total)
        return {
            "duration_hours": duration,
            "price_per_hour": booking.price_per_hour,
            "rental_fee": rental_fee,
            "surcharge": surcharge,
            "deposit_deducted": booking.deposit,
            "total_amount": total,
        }

    def pay(self, booking: Booking, surcharge: float = 0.0) -> Payment:
        paid_ids = self._get_paid_booking_ids()
        if booking.booking_id in paid_ids or booking.status == "Đã thanh toán":
            raise ValueError(f"Đơn {booking.booking_id} đã thanh toán rồi!")

        info = self.preview(booking, surcharge)
        invoice_id = self._next_invoice_id()

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

        if not self._payment_repo.add(payment):
            raise ValueError("Không thể lưu hóa đơn thanh toán.")

        # Cập nhật trạng thái đơn đặt sân thành "Đã thanh toán"
        booking.status = "Đã thanh toán"
        self._booking_repo.update(booking)

        return payment

    @staticmethod
    def format_receipt(p: Payment) -> str:
        return (
            f"       HÓA ĐƠN {p.invoice_id}    \n"
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