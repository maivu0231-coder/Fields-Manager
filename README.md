# ⚽ HỆ THỐNG QUẢN LÝ SÂN BÓNG ĐÁ (FILE-BASED PERSISTENCE)

Dự án **Quản Lý Sân Bóng Đá** được xây dựng theo phong cách lập trình (vibe) sạch sẽ từ repository **`maivu0231-coder/Fields-Manager`**.

---

## CẤU TRÚC THƯ MỤC

```text
QuanLySanBong/
├── Data/
│   └── fields_data.json      # File tự động lưu trữ dữ liệu bền vững (JSON Format)
├── Src/
│   ├── Models/
│   │   ├── Base.py           # Dataclass cơ sở chứa id, created_at, updated_at
│   │   └── Fields.py         # Dataclass Field quản lý thuộc tính sân bóng
│   ├── Core/
│   │   └── Field_Manager.py  # Tầng xử lý File I/O + Edge Cases + In-Memory Cache
│   └── Component/
│       └── Tab_Field.py      # Giao diện Streamlit ListView & Form Gộp Thêm/Xóa
├── Main.py                   # File chạy chính của ứng dụng
└── README.md                 # Tài liệu hướng dẫn sử dụng dự án
```

---

## ĐẶC ĐIỂM THIẾT KẾ & VIBE LẬP TRÌNH

1. **Pathlib An Toàn**: Sử dụng `Path(__file__).resolve()` định vị file tuyệt đối, tránh lỗi `FileNotFoundError`.
2. **Lưu File Bền Vững (JSON Persistence)**: Mọi thao tác *Thêm, Sửa, Xóa* tự động đọc/ghi ngay lập tức vào file `Data/fields_data.json` chuẩn UTF-8.
3. **Quản Lý Edge Cases**:
   - **Tìm kiếm tiếng Việt thông minh**: Hỗ trợ tìm kiếm có dấu hoặc không dấu (`san 5` -> `Sân 5A`).
   - **Làm sạch dữ liệu**: Tự động loại bỏ khoảng trắng thừa, viết hoa mã sân (`s01` -> `S01`).
   - **Ràng buộc dữ liệu**: Kiểm tra rỗng, trùng mã sân, giá âm hoặc giá vượt mức hợp lý.
   - **Chặn xóa an toàn**: Cảnh báo và không cho phép xóa sân đang ở trạng thái `Đang có khách`.
4. **Giao Diện Gộp**: Gộp chung form **Thêm** và **Xóa** sân bóng trên cùng một màn hình giúp tối ưu thao tác.

---

## HƯỚNG DẪN KHỞI CHẠY

1. **Cài đặt môi trường**:
   ```bash
   pip install streamlit pandas
   ```

2. **Khởi chạy ứng dụng**:
   ```bash
   python -m streamlit run Main.py
   ```
