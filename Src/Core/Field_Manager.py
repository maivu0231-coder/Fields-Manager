import re
import unicodedata
from datetime import datetime
from typing import List, Optional, Tuple

import streamlit as st

from Src.Models.Fields import Field, FieldStatus, FieldType
from Src.Storage.repositories import BookingRepository, FieldRepository


def remove_accents(input_str: str) -> str:
    if not input_str:
        return ""
    text = input_str.replace("đ", "d").replace("Đ", "D")
    nfkd_form = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()


class FieldService:

    SESSION_KEY = "fields_data_cache"

    def __init__(
        self,
        repository: Optional[FieldRepository] = None,
        booking_repository: Optional[BookingRepository] = None,
    ) -> None:
        self.repository = repository or FieldRepository()
        self.booking_repository = booking_repository or BookingRepository()
        self._ensure_storage_and_cache()

    def _get_default_seed_data(self) -> List[Field]:
        return [
            Field(
                field_id="S01",
                name="Sân 5A",
                field_type=FieldType.FIELD_5.value,
                price_per_hour=200000.0,
                status=FieldStatus.AVAILABLE.value,
            ),
            Field(
                field_id="S02",
                name="Sân 5B",
                field_type=FieldType.FIELD_5.value,
                price_per_hour=200000.0,
                status=FieldStatus.IN_USE.value,
            ),
            Field(
                field_id="S03",
                name="Sân 7A",
                field_type=FieldType.FIELD_7.value,
                price_per_hour=350000.0,
                status=FieldStatus.AVAILABLE.value,
            ),
            Field(
                field_id="S04",
                name="Sân 7B",
                field_type=FieldType.FIELD_7.value,
                price_per_hour=350000.0,
                status=FieldStatus.MAINTENANCE.value,
            ),
        ]
    #save the list of Field objects to the file and update the session state cache
    def _save_to_file(self, fields: List[Field]) -> bool:
        ok = self.repository.handler.write_all([field.to_dict() for field in fields])
        if ok:
            st.session_state[self.SESSION_KEY] = fields
        return ok
    #ensure that the storage file exists and load the data into the session state cache
    def _ensure_storage_and_cache(self) -> None:
        fields = self.repository.get_all()
        if not fields:
            fields = self._get_default_seed_data()
            self._save_to_file(fields)
        else:
            st.session_state[self.SESSION_KEY] = fields

    def get_all(self) -> List[Field]:
        fields = self.repository.get_all()
        st.session_state[self.SESSION_KEY] = fields
        return fields

    def filter(
        self,
        status: str = "Tất cả",
        field_type: str = "Tất cả",
        search_term: str = "",
    ) -> List[Field]:#filter the list of Field objects based on status, field_type, and search_term
        records = self.get_all()

        if status != "Tất cả":
            records = [f for f in records if f.status == status]

        if field_type != "Tất cả":
            records = [f for f in records if f.field_type == field_type]

        clean_kw = " ".join(search_term.strip().split())
        if clean_kw:
            raw_kw = clean_kw.lower()
            no_accent_kw = remove_accents(clean_kw)

            result = []
            for f in records:
                name_raw = f.name.lower()
                code_raw = f.field_id.lower()
                name_no_accent = remove_accents(f.name)
                code_no_accent = remove_accents(f.field_id)

                if (
                    raw_kw in name_raw
                    or raw_kw in code_raw
                    or no_accent_kw in name_no_accent
                    or no_accent_kw in code_no_accent
                ):
                    result.append(f)
            return result

        return records

    def add(
        self, code: str, name: str, field_type: str, price: float, status: str
    ) -> Tuple[bool, str]:
        clean_code = re.sub(r"\s+", " ", code.strip().upper())
        clean_name = re.sub(r"\s+", " ", name.strip())

        if not clean_code or not clean_name:
            return (
                False,
                "❌ Mã sân và Tên sân không được để trống hoặc chỉ chứa khoảng trắng!",
            )

        if len(clean_code) > 20:
            return False, "❌ Mã sân không được vượt quá 20 ký tự!"

        if len(clean_name) > 100:
            return False, "❌ Tên sân không được vượt quá 100 ký tự!"

        if price <= 0:
            return False, "❌ Giá thuê mỗi giờ phải lớn hơn 0!"

        if price > 50000000:
            return False, "❌ Giá thuê vượt quá mức hợp lý (tối đa 50,000,000 VNĐ)!"

        current_fields = self.get_all()
        if any(f.field_id == clean_code for f in current_fields):
            return False, f"❌ Mã sân '{clean_code}' đã tồn tại trên hệ thống!"

        new_field = Field(
            field_id=clean_code,
            name=clean_name,
            field_type=field_type,
            price_per_hour=float(price),
            status=status,
        )
        updated = [*current_fields, new_field]
        if not self._save_to_file(updated):
            return False, "❌ Không thể lưu sân mới vào file dữ liệu."
        return True, f"✅ Thêm thành công sân '{clean_code}' và tự động lưu vào file!"

    def update(
        self, code: str, name: str, field_type: str, price: float, status: str
    ) -> Tuple[bool, str]:
        clean_name = re.sub(r"\s+", " ", name.strip())
        if not clean_name:
            return False, "❌ Tên sân bóng không được để trống!"

        if len(clean_name) > 100:
            return False, "❌ Tên sân không được vượt quá 100 ký tự!"

        if price <= 0:
            return False, "❌ Giá thuê phải lớn hơn 0!"

        if price > 50000000:
            return False, "❌ Giá thuê vượt quá mức hợp lý (tối đa 50,000,000 VNĐ)!"

        current_fields = self.get_all()
        for field in current_fields:
            if field.field_id == code:
                updated_field = Field(
                    field_id=field.field_id,
                    name=clean_name,
                    field_type=field_type,
                    price_per_hour=float(price),
                    status=status,
                    created_at=field.created_at,
                    updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                updated = [
                    updated_field if item.field_id == code else item
                    for item in current_fields
                ]
                if not self._save_to_file(updated):
                    return False, "❌ Không thể lưu thay đổi vào file dữ liệu."

                if field.name != clean_name:
                    all_bookings = self.booking_repository.get_all()
                    changed = False
                    for b in all_bookings:
                        if b.field_id == code and b.status != "Đã hủy":
                            b.field_name = clean_name
                            changed = True
                    if changed:
                        self.booking_repository.handler.write_all(
                            [b.to_dict() for b in all_bookings]
                        )

                return True, f"✅ Cập nhật sân '{code}' thành công và đã ghi file!"
        return False, f"❌ Không tìm thấy sân mã '{code}'."

    def delete(self, code: str) -> Tuple[bool, str]:
        records = self.get_all()
        target = next((f for f in records if f.field_id == code), None)

        if not target:
            return False, f"❌ Không tìm thấy sân mã '{code}'."

        if target.status == FieldStatus.IN_USE.value:
            return (
                False,
                f"⚠️ Cảnh báo: Sân '{code}' đang ở trạng thái 'Đang có khách'. Không thể xóa!",
            )

        active_bookings = [
            b
            for b in self.booking_repository.get_all()
            if b.field_id == code and b.status != "Đã hủy"
        ]
        if active_bookings:
            return (
                False,
                f"⚠️ Cảnh báo: Sân '{code}' đang có {len(active_bookings)} đơn đặt sân chưa hủy. Không thể xóa!",
            )

        updated = [f for f in records if f.field_id != code]
        if not self._save_to_file(updated):
            return False, "❌ Không thể cập nhật file dữ liệu sau khi xóa sân."
        return True, f"✅ Đã xóa sân '{code}' và cập nhật file lưu trữ!"

    def reset_to_default(self) -> Tuple[bool, str]:
        default_data = self._get_default_seed_data()
        if not self._save_to_file(default_data):
            return False, "❌ Không thể ghi dữ liệu mặc định vào file."
        return True, "✅ Đã khôi phục dữ liệu mặc định thành công!"