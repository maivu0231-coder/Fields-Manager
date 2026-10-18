# Cách khởi tạo môi trường ảo
python -m venv venv
# chạy môi trường ảo
.venv\Scripts\Activate.ps1
# cách chạy chương trình
-cả chương trình: Python -m streamlit run Fields-Manager
# Thiết kế các class trong module models
-Base:Quản lý thời gian tạo (created_at), thời gian cập nhật (updated_at) và cung cấp cơ chế chuyển đổi dữ liệu chung (to_dict, from_dict).
-FieldStatus:Định nghĩa tập trạng thái sân hợp lệ: AVAILABLE ("Trống"), IN_USE ("Đang có khách"), MAINTENANCE ("Bảo trì").
-FieldType:Định nghĩa phân loại sân chuẩn: FIELD_5 ("Sân 5"), FIELD_7 ("Sân 7").
-Booking:Biểu diễn thực thể Đơn đặt sân: booking_id (khóa chính), field_id (khóa ngoại), field_name, customer_name, phone, booking_date, start_time, end_time, price_per_hour, deposit, status.
-Payment:Biểu diễn thực thể Hóa đơn thanh toán: invoice_id (khóa chính), booking_id (khóa ngoại), customer_name, field_name, duration_hours, price_per_hour, rental_fee, surcharge, deposit_deducted, total_amount, payment_time
# thiết kế module quản lí dữ liệu và truy xuất dữ liệu
-xây dựng lớp quản lí tệp tin JsonHandler.Chịu trách nhiệm giao tiếp trực tiếp với hệ thống tệp tin (File System) cho các file fields.json, bookings.json, payments.json:
+Tự động khởi tạo (_ensure_file_exists): Kiểm tra và tự động tạo thư mục Data/ cũng như khởi tạo file JSON rỗng [] (chuẩn mã hóa utf-8) nếu file chưa tồn tại.
+Đọc dữ liệu an toàn (read_all): Bắt ngoại lệ json.JSONDecodeError và OSError. Nếu file trống hoặc bị hỏng định dạng, hàm trả về danh sách rỗng [] thay vì làm dừng chương trình.
+Ghi dữ liệu nguyên tử — Atomic Write (write_all): Thay vì ghi đè trực tiếp vào file gốc (dễ gây mất hoặc hỏng dữ liệu nếu mất điện/lỗi giữa chừng), hàm ghi toàn bộ dữ liệu ra một tệp tạm (tempfile.NamedTemporaryFile) trong cùng thư mục, sau đó dùng lệnh nguyên tử os.replace(temp_name, self.file_path) để tráo file.
# Xây dựng cấu trúc dữ liệu bảng băm 
# Xây dựng các Repository
-Lớp cơ sở BaseRepository:
   Liên kết JSONHandler, lớp Model tương ứng và CustomHashTable.
   Cung cấp bộ thao tác CRUD chuẩn hóa với độ phức tạp $O(1)$ trên bảng băm và tự động đồng bộ xuống file JSON: get_all(), get_by_id(item_id), add(entity), update(entity) (tự động cập nhật mốc thời gian updated_at), và delete(item_id).
-Các lớp kế thừa chuyên biệt:
+FieldRepository: Quản lý fields.json với khóa chính field_id và mô hình Field.  
+BookingRepository: Quản lý bookings.json với khóa chính booking_id và mô hình Booking. Mở rộng thêm các phương thức truy vấn nghiệp vụ: get_by_date_and_field() (lọc đơn theo ngày, sân, loại bỏ đơn "Đã hủy" và sắp xếp tăng dần theo start_time), get_pending_payments(), và find_by_name().   
+PaymentRepository: Quản lý payments.json với khóa chính invoice_id và mô hình Payment.