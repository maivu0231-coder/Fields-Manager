import json
import re
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import streamlit as st
from Src.Models.Fields import Field, FieldStatus, FieldType

# Vibe maivu0231-coder: Đường dẫn tuyệt đối chuẩn xác qua Pathlib
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "Data"
JSON_FILE = DATA_DIR / "fields_data.json"

def remove_accents(input_str: str) -> str:
    """Bỏ dấu tiếng Việt để phục vụ tìm kiếm thông minh (Edge Case)"""
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

class FieldService:
    """Tầng nghiệp vụ quản lý File I/O + In-Memory Cache + Edge Cases"""

    SESSION_KEY = "fields_data_cache"

    def __init__(self) -> None:
        self._ensure_storage_and_cache()

    def _get_default_seed_data(self) -> List[Field]:
        return [
            Field(id=1, field_code="S01", field_name="Sân 5A (Cỏ nhân tạo)", field_type=FieldType.FIELD_5.value, price_per_hour=200000, status=FieldStatus.AVAILABLE.value),
            Field(id=2, field_code="S02", field_name="Sân 5B (Cỏ nhân tạo)", field_type=FieldType.FIELD_5.value, price_per_hour=200000, status=FieldStatus.IN_USE.value),
            Field(id=3, field_code="S03", field_name="Sân 7A (Sân VIP Đèn Led)", field_type=FieldType.FIELD_7.value, price_per_hour=350000, status=FieldStatus.AVAILABLE.value),
            Field(id=4, field_code="S04", field_name="Sân 7B (Cỏ tự nhiên)", field_type=FieldType.FIELD_7.value, price_per_hour=350000, status=FieldStatus.MAINTENANCE.value),
        ]

    def _save_to_file(self, fields: List[Field]) -> None:
        """Ghi dữ liệu bền vững ra file JSON (Chuẩn UTF-8, định dạng maivu0231)"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            dict_data = [f.to_dict() for f in fields]
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(dict_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            st.error(f"Lỗi ghi file dữ liệu: {e}")

    def _load_from_file(self) -> List[Field]:
        """Đọc dữ liệu từ file JSON vào bộ nhớ"""
        if not JSON_FILE.exists():
            default_data = self._get_default_seed_data()
            self._save_to_file(default_data)
            return default_data
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Field.from_dict(item) for item in data]
        except Exception:
            default_data = self._get_default_seed_data()
            self._save_to_file(default_data)
            return default_data

    def _ensure_storage_and_cache(self) -> None:
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = self._load_from_file()

    def get_all(self) -> List[Field]:
        return st.session_state.get(self.SESSION_KEY, [])

    def filter(self, status: str = "Tất cả", field_type: str = "Tất cả", search_term: str = "") -> List[Field]:
        """Tìm kiếm thông tinh lọc Edge Cases (không dấu, khoảng trắng thừa)"""
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
                name_raw = f.field_name.lower()
                code_raw = f.field_code.lower()
                name_no_accent = remove_accents(f.field_name)
                code_no_accent = remove_accents(f.field_code)

                if (raw_kw in name_raw or raw_kw in code_raw or 
                    no_accent_kw in name_no_accent or no_accent_kw in code_no_accent):
                    result.append(f)
            return result
            
        return records

    def add(self, code: str, name: str, field_type: str, price: float, status: str) -> Tuple[bool, str]:
        """Thêm sân mới + Xử lý Edge Cases nhập liệu"""
        clean_code = re.sub(r'\s+', ' ', code.strip().upper())
        clean_name = re.sub(r'\s+', ' ', name.strip())

        if not clean_code or not clean_name:
            return False, "❌ Mã sân và Tên sân không được để trống hoặc chỉ chứa khoảng trắng!"

        if len(clean_code) > 20:
            return False, "❌ Mã sân không được vượt quá 20 ký tự!"

        if len(clean_name) > 100:
            return False, "❌ Tên sân không được vượt quá 100 ký tự!"

        if price < 0:
            return False, "❌ Giá thuê mỗi giờ không được là số âm!"

        if price > 50000000:
            return False, "❌ Giá thuê vượt quá mức hợp lý (tối đa 50,000,000 VNĐ)!"

        if any(f.field_code == clean_code for f in self.get_all()):
            return False, f"❌ Mã sân '{clean_code}' đã tồn tại trên hệ thống!"

        new_id = max([f.id for f in self.get_all() if f.id], default=0) + 1
        new_field = Field(
            id=new_id,
            field_code=clean_code,
            field_name=clean_name,
            field_type=field_type,
            price_per_hour=price,
            status=status
        )
        st.session_state[self.SESSION_KEY].append(new_field)
        self._save_to_file(st.session_state[self.SESSION_KEY])
        return True, f"✅ Thêm thành công sân '{clean_code}' và tự động lưu vào file!"

    def update(self, code: str, name: str, field_type: str, price: float, status: str) -> Tuple[bool, str]:
        """Cập nhật sân + Xử lý Edge Cases"""
        clean_name = re.sub(r'\s+', ' ', name.strip())
        if not clean_name:
            return False, "❌ Tên sân bóng không được để trống!"

        if price < 0:
            return False, "❌ Giá thuê không được nhỏ hơn 0!"

        for field in self.get_all():
            if field.field_code == code:
                field.field_name = clean_name
                field.field_type = field_type
                field.price_per_hour = float(price)
                field.status = status
                field.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_to_file(self.get_all())
                return True, f"✅ Cập nhật sân '{code}' thành công và đã ghi file!"
        return False, f"❌ Không tìm thấy sân mã '{code}'."

    def delete(self, code: str) -> Tuple[bool, str]:
        """Xóa sân + Edge Case: Chặn xóa khi sân đang có khách"""
        records = self.get_all()
        target = next((f for f in records if f.field_code == code), None)

        if not target:
            return False, f"❌ Không tìm thấy sân mã '{code}'."

        if target.status == FieldStatus.IN_USE.value:
            return False, f"⚠️ Cảnh báo: Sân '{code}' đang ở trạng thái 'Đang có khách'. Không thể xóa!"

        updated = [f for f in records if f.field_code != code]
        st.session_state[self.SESSION_KEY] = updated
        self._save_to_file(updated)
        return True, f"✅ Đã xóa sân '{code}' và cập nhật file lưu trữ!"

    def reset_to_default(self) -> Tuple[bool, str]:
        """Khôi phục dữ liệu gốc"""
        default_data = self._get_default_seed_data()
        st.session_state[self.SESSION_KEY] = default_data
        self._save_to_file(default_data)
        return True, "✅ Đã khôi phục dữ liệu mặc định thành công!"
