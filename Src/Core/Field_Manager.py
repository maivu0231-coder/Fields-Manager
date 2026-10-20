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
    """
    Tầng nghiệp vụ quản lý sân bóng.
    Mọi thao tác truy xuất theo mã sân (get_by_id, add, update, delete)
    đều thông qua CustomHashTable của FieldRepository với độ phức tạp O(1).
    """

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

    def _refresh_cache(self) -> List[Field]:
        """Đồng bộ lại st.session_state từ CustomHashTable trong Repository."""
        fields = self.repository.get_all()
        st.session_state[self.SESSION_KEY] = fields
        return fields

    def _ensure_storage_and_cache(self) -> None:
        fields = self.repository.get_all()
        if not fields:
            default_fields = self._get_default_seed_data()
            for item in default_fields:
                self.repository.add(item)
            fields = self._refresh_cache()
        else:
            st.session_state[self.SESSION_KEY] = fields

    def get_all(self) -> List[Field]:
        return self._refresh_cache()

    def get_by_id(self, code: str) -> Optional[Field]:
        """Tra cứu sân theo mã bằng CustomHashTable O(1)."""
        clean_code = code.strip().upper()
        return self.repository.get_by_id(clean_code)

    def filter(
        self,
        status: str = "Tất cả",
        field_type: str = "Tất cả",
        search_term: str = "",
    ) -> List[Field]:
        records = self.get_all()

        if status != "Tất cả":
            records = [f for f in records if f.status == status]

        if field_type != "Tất cả":
            records = [f for f in records if f.field_type == field_type]

        clean_kw = " ".join(search_term.strip().split())
        if clean_kw:
            # Nếu người dùng nhập đúng mã sân trong bảng băm thì ưu tiên khớp nhanh
            exact_match = self.repository.get_by_id(clean_kw.upper())
            if exact_match and exact_match in records and len(clean_kw) <= 5:
                # Vẫn lấy thêm các kết quả khớp chuỗi con nếu có
                pass

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

        # Kiểm tra trùng mã sân bằng CustomHashTable O(1) thay vì duyệt list O(n)
        if self.repository.get_by_id(clean_code) is not None:
            return False, f"❌ Mã sân '{clean_code}' đã tồn tại trên hệ thống!"

        new_field = Field(
            field_id=clean_code,
            name=clean_name,
            field_type=field_type,
            price_per_hour=float(price),
            status=status,
        )

        # Thêm trực tiếp vào CustomHashTable O(1) và đồng bộ xuống file
        if not self.repository.add(new_field):
            return False, "❌ Không thể lưu sân mới vào file dữ liệu."

        self._refresh_cache()
        return True, f"✅ Thêm thành công sân '{clean_code}' vào Bảng băm & File JSON!"

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

        # Tìm sân trong CustomHashTable O(1) thay vì dùng vòng lặp for O(n)
        existing_field = self.repository.get_by_id(code)
        if existing_field is None:
            return False, f"❌ Không tìm thấy sân mã '{code}'."

        old_name = existing_field.name
        updated_field = Field(
            field_id=existing_field.field_id,
            name=clean_name,
            field_type=field_type,
            price_per_hour=float(price),
            status=status,
            created_at=existing_field.created_at,
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Cập nhật trên CustomHashTable O(1)
        if not self.repository.update(updated_field):
            return False, "❌ Không thể lưu thay đổi vào file dữ liệu."

        # Nếu đổi tên sân, cập nhật lại tên sân trong các đơn đặt chưa hủy qua BookingRepository
        if old_name != clean_name:
            for b in self.booking_repository.get_all():
                if b.field_id == code and b.status != "Đã hủy":
                    b.field_name = clean_name
                    self.booking_repository.update(b)

        self._refresh_cache()
        return True, f"✅ Cập nhật sân '{code}' thành công và đã ghi file!"

    def delete(self, code: str) -> Tuple[bool, str]:
        # Tra cứu sân cần xóa bằng CustomHashTable O(1) thay vì next(...) O(n)
        target = self.repository.get_by_id(code)
        if target is None:
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

        # Xóa khỏi CustomHashTable O(1)
        if not self.repository.delete(code):
            return False, "❌ Không thể cập nhật file dữ liệu sau khi xóa sân."

        self._refresh_cache()
        return True, f"✅ Đã xóa sân '{code}' khỏi Bảng băm và cập nhật file lưu trữ!"

    def reset_to_default(self) -> Tuple[bool, str]:
        default_data = self._get_default_seed_data()
        if not self.repository.handler.write_all([f.to_dict() for f in default_data]):
            return False, "❌ Không thể ghi dữ liệu mặc định vào file."
        self._refresh_cache()
        return True, "✅ Đã khôi phục dữ liệu mặc định thành công!"