import os
from typing import List, Optional
from datetime import datetime
from Models import Field, Booking, Payment
from .json_handler import JSONHandler
from Core.algorithms import binary_search, merge_sort
#default data directory relative to the project root
DEFAULT_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)


class BaseRepository:
    #base repository class for CRUD operations on JSON files
    def __init__(self, file_name: str, id_field_name: str, model_cls):
        file_path = os.path.join(DEFAULT_DATA_DIR, file_name)
        self.handler = JSONHandler(file_path)
        self.id_field_name = id_field_name
        self.model_cls = model_cls
        self._sorted_cache = None
        self._sorted_keys = None

    def get_all(self) -> List[any]:
        raw_items = self.handler.read_all()
        return [self.model_cls.from_dict(item) for item in raw_items]

    def get_by_id(self, item_id: str) -> Optional[any]:
        raw_items = self.handler.read_all()
        for item in raw_items:
            if str(item.get(self.id_field_name)) == str(item_id):
                return self.model_cls.from_dict(item)
        return None

    def add(self, entity) -> bool:
        raw_items = self.handler.read_all()
        raw_items.append(entity.to_dict())
        return self.handler.write_all(raw_items)

    def update(self, entity) -> bool:
        raw_items = self.handler.read_all()
        target_id = getattr(entity, self.id_field_name)
        updated = False

        entity.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for idx, item in enumerate(raw_items):
            if str(item.get(self.id_field_name)) == str(target_id):
                raw_items[idx] = entity.to_dict()
                updated = True
                break

        if updated:
            return self.handler.write_all(raw_items)
        return False

    def delete(self, item_id: str) -> bool:
        raw_items = self.handler.read_all()
        filtered = [
            item for item in raw_items 
            if str(item.get(self.id_field_name)) != str(item_id)
        ]
        if len(filtered) != len(raw_items):
            return self.handler.write_all(filtered)
        return False


class FieldRepository(BaseRepository):
    def __init__(self):
        super().__init__("fields.json", "field_id", Field)


class BookingRepository(BaseRepository):
    def __init__(self):
        super().__init__("bookings.json", "booking_id", Booking)

    def get_by_date_and_field(self, booking_date: str, field_id: str) -> List[Booking]:
       #get all bookings for a specific date and field, excluding canceled bookings
        all_bookings = self.get_all()
        return [
            b for b in all_bookings 
            if b.booking_date == booking_date and b.field_id == field_id and b.status != "Đã hủy"
        ]

    def get_pending_payments(self) -> List[Booking]:
        #get all bookings that are pending payment
        all_bookings = self.get_all()
        return [b for b in all_bookings if b.status == "Chờ thanh toán"]
    
    def find_by_name(self, name: str):
        if not name:
            return None
        if self._sorted_cache is None:
            all_bookings = self.get_all()
            self._sorted_cache = merge_sort(
                all_bookings,
                key=lambda b: b.customer_name.lower()
            )
            self._sorted_keys = [
                b.customer_name.lower() for b in self._sorted_cache
            ]
        target = name.strip().lower()
        idx = binary_search(self._sorted_keys, target)
        if idx != -1:
            return self._sorted_cache[idx]
        return None

class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__("payments.json", "invoice_id", Payment)