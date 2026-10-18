import re
from datetime import date,datetime,time
from typing import List

from Src.Models import Booking, Field
from Src.Storage.repositories import BookingRepository, FieldRepository
STATUS_CANCELLED="Đã hủy"
STATUS_BOOKED="Đã cọc"
STATUS_PENDING_PAYMENT = "Chờ thanh toán"
OPENING_TIME = time(6, 0)
CLOSING_TIME = time(22, 0)
class BookingError(Exception):
    pass# a booking manager class to handle booking operations
class BookingManager:
    def __init__(
        self,
        booking_repository: BookingRepository | None = None,
                field_repository: FieldRepository | None = None,
            ) -> None:
        self.booking_repository = booking_repository or BookingRepository()
        self.field_repository = field_repository or FieldRepository()
    #return all fileds
    def list_fields(self) -> List[Field]:
        return self.field_repository.get_all()
    #return all bookings for a given date and field
    def list_bookings(self, booking_date: date, field_id: str) -> List[Booking]:
        return self.booking_repository.get_by_date_and_field(
            booking_date.isoformat(), field_id
        )
    @staticmethod#allow call a function without creating an instance of the class
    #parse a time string in ISO format to a time object
    def _parse_time(value: str)->time:
        try:
            return time.fromisoformat(value)
        except (TypeError, ValueError) as error:
            raise BookingError(f"Giờ trong dữ liệu không hợp lệ: {value!r}.") from error
    #create a function to generate the next booking ID based on existing bookings
    def _next_booking_id(self) -> str:
        numbers = []
        for booking in self.booking_repository.get_all():
            match = re.fullmatch(r"BK(\d+)", booking.booking_id)
            if match:
                numbers.append(int(match.group(1)))
        return f"BK{max(numbers, default=0) + 1:02d}"
    #create a new booking
    def create_booking(
        self,
        field_id: str,
        booking_date: date,
        customer_name: str,
        phone: str,
        start_time: time,
        end_time: time,
        deposit: float = 0.0,
    ) -> Booking:
        customer_name = " ".join(customer_name.strip().split())
        phone = phone.strip()

        if not customer_name:
            raise BookingError("Vui lòng nhập tên khách.")
        if not re.fullmatch(r"0\d{9}", phone):
            raise BookingError("Số điện thoại cần có 10 chữ số và bắt đầu bằng 0.")
        if start_time >= end_time:
            raise BookingError("Giờ kết thúc phải lớn hơn giờ bắt đầu.")
        if start_time < OPENING_TIME or end_time > CLOSING_TIME:
            raise BookingError("Sân chỉ hoạt động từ 05:00 đến 23:00.")
        if datetime.combine(booking_date, start_time) < datetime.now():
            raise BookingError("Không thể đặt sân trong quá khứ.")
        if deposit < 0:
            raise BookingError("Tiền cọc không được là số âm.")

        field = self.field_repository.get_by_id(field_id)
        if field is None:
            raise BookingError("Không tìm thấy sân đã chọn.")
        if field.status.strip().casefold() == "bảo trì":
            raise BookingError("Sân đang bảo trì, không thể nhận đặt sân.")

        duration_hours = (
            datetime.combine(booking_date, end_time)
            - datetime.combine(booking_date, start_time)
        ).total_seconds() / 3600.0
        estimated_fee = duration_hours * field.price_per_hour
        if deposit > estimated_fee:
            raise BookingError(
                f"Tiền cọc ({deposit:,.0f} đ) không được vượt quá tiền thuê sân dự kiến ({estimated_fee:,.0f} đ)."
            )

        for existing in self.list_bookings(booking_date, field_id):
            existing_start = self._parse_time(existing.start_time)
            existing_end = self._parse_time(existing.end_time)
            if start_time < existing_end and end_time > existing_start:
                raise BookingError(
                    f"Trùng lịch với đơn {existing.booking_id} "
                    f"({existing_start:%H:%M} - {existing_end:%H:%M})."
                )

        status = STATUS_BOOKED if deposit > 0 else STATUS_PENDING_PAYMENT

        booking = Booking(
            booking_id=self._next_booking_id(),
            field_id=field.field_id,
            customer_name=customer_name,
            phone=phone,
            booking_date=booking_date.isoformat(),
            start_time=start_time.strftime("%H:%M"),
            end_time=end_time.strftime("%H:%M"),
            deposit=float(deposit),
            status=status,
            field_name=field.name,
            price_per_hour=field.price_per_hour,
        )
        if not self.booking_repository.add(booking):
            raise BookingError("Không thể lưu đơn đặt sân. Vui lòng thử lại.")
        return booking
    #cancel an existing booking
    def cancel_booking(self, booking_id: str) -> Booking:
        booking = self.booking_repository.get_by_id(booking_id)
        if booking is None:
            raise BookingError("Không tìm thấy đơn đặt sân.")
        if booking.status == STATUS_CANCELLED:
            raise BookingError(f"Đơn {booking_id} đã được hủy trước đó.")

        booking.status = STATUS_CANCELLED
        if not self.booking_repository.update(booking):
            raise BookingError("Không thể cập nhật trạng thái hủy đơn.")
        return booking