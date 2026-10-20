import os
from datetime import datetime
from typing import Any, List, Optional

from Src.Models import Booking, Field, Payment
from Src.Storage.HashTable import CustomHashTable
from Src.Storage.json_handler import JSONHandler

DEFAULT_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Data")
)


class BaseRepository:
  
    def __init__(self, file_name: str, id_field_name: str, model_cls):
        file_path = os.path.join(DEFAULT_DATA_DIR, file_name)
        self.handler = JSONHandler(file_path)
        self.id_field_name = id_field_name
        self.model_cls = model_cls
        self.hash_table = CustomHashTable()
        self._load_into_hash_table()

    def _load_into_hash_table(self) -> None:

        self.hash_table = CustomHashTable()
        raw_items = self.handler.read_all()
        for item in raw_items:
            entity = self.model_cls.from_dict(item)
            entity_id = str(getattr(entity, self.id_field_name))
            self.hash_table.put(entity_id, entity)
    #a function to sync the hash table to the file
    def _sync_to_file(self) -> bool:
        all_dicts = [entity.to_dict() for entity in self.hash_table.values()]
        return self.handler.write_all(all_dicts)

    def get_all(self) -> List[Any]:
        self._load_into_hash_table()
        return self.hash_table.values()

    def get_by_id(self, item_id: str) -> Optional[Any]:
        self._load_into_hash_table()
        return self.hash_table.get(str(item_id))

    def add(self, entity: Any) -> bool:
        self._load_into_hash_table()
        entity_id = str(getattr(entity, self.id_field_name))
        self.hash_table.put(entity_id, entity)
        return self._sync_to_file()
    #a function to update an existing entity
    def update(self, entity: Any) -> bool:
        self._load_into_hash_table()
        target_id = str(getattr(entity, self.id_field_name))

        if not self.hash_table.contains(target_id):
            return False

        entity.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hash_table.put(target_id, entity)
        return self._sync_to_file()
    #a function to delete an existing entity
    def delete(self, item_id: str) -> bool:
        self._load_into_hash_table()
        if self.hash_table.remove(str(item_id)):
            return self._sync_to_file()
        return False


class FieldRepository(BaseRepository):
    def __init__(self):
        super().__init__("fields.json", "field_id", Field)


class BookingRepository(BaseRepository):
    def __init__(self):
        super().__init__("bookings.json", "booking_id", Booking)

    def get_by_date_and_field(self, booking_date: str, field_id: str) -> List[Booking]:
        all_bookings = self.get_all()
        filtered = [
            b
            for b in all_bookings
            if b.booking_date == booking_date
            and b.field_id == field_id
            and b.status != "Đã hủy"
        ]
        return sorted(filtered, key=lambda b: b.start_time)

    def get_pending_payments(self) -> List[Booking]:
        all_bookings = self.get_all()
        return [
            b
            for b in all_bookings
            if b.status in ("Chờ thanh toán", "Đã cọc")
        ]

    def find_by_name(self, name: str) -> Optional[Booking]:
        clean_kw = name.strip().lower()
        if not clean_kw:
            return None
        for b in self.get_all():
            if clean_kw in b.customer_name.lower() and b.status != "Đã hủy":
                return b
        return None


class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__("payments.json", "invoice_id", Payment)