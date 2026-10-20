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
## Các tệp tham gia

```text
main.py                              Tạo các tab của ứng dụng và gọi giao diện tab 2
src/Component/Tab_booking.py         Hiển thị form, bộ lọc, lịch và nút hủy
src/Core/Booking_Manager.py          Kiểm tra quy tắc đặt sân và xử lý hủy đơn
src/Models/Booking.py                Định nghĩa dữ liệu của một đơn đặt sân
src/Storage/repositories.py          Tìm, thêm và cập nhật đơn trong JSON
src/Storage/json_handler.py          Đọc và ghi tệp JSON
Data/bookings.json                   Danh sách đơn đặt sân
Data/fields.json                     Danh sách sân
```

## Luồng hoạt động

Khi chạy `streamlit run main.py`, hàm `main()` tạo ba tab. Tab **Đặt sân / Hủy sân** gọi `render_tab_dat_san()` trong `Tab_booking.py`. Tab Sân bóng và Thanh toán hiện mới là phần giữ chỗ để ghép module sau.

Trong tab 2, giao diện lấy danh sách sân từ `BookingManager`, rồi cho người dùng lọc theo ngày và sân. Khi chọn sân/ngày, manager yêu cầu `BookingRepository` lấy các đơn còn hiệu lực. Repository chuyển dữ liệu JSON thành các đối tượng `Booking`, và giao diện trình bày chúng thành bảng.

```text
main.py
  └─ render_tab_dat_san()
       └─ BookingManager
            ├─ FieldRepository / BookingRepository
            └─ JSONHandler ── Data/fields.json, Data/bookings.json
```

## Tạo đơn đặt sân

Người dùng nhập tên, số điện thoại, giờ bắt đầu và giờ kết thúc. Ngày và sân được lấy từ bộ lọc phía trên. Khi bấm **Xác nhận đặt sân**, giao diện gọi `BookingManager.create_booking()`.

Manager kiểm tra các điều kiện sau trước khi ghi đơn:

- Tên khách không được để trống.
- Số điện thoại phải có 10 chữ số và bắt đầu bằng `0`.
- Giờ kết thúc phải sau giờ bắt đầu; sân chỉ nhận lịch trong khoảng 05:00–23:00.
- Không nhận đặt sân trong quá khứ.
- Sân phải tồn tại và không ở trạng thái bảo trì.
- Đơn mới không được trùng giờ với một đơn khác trên cùng sân, cùng ngày.

Hai lịch bị trùng nếu:

```text
giờ bắt đầu mới < giờ kết thúc cũ
và
giờ kết thúc mới > giờ bắt đầu cũ
```

Ví dụ: lịch 17:00–18:00 và 18:00–19:00 có thể nối tiếp nhau. Lịch 17:30–18:30 bị trùng với lịch 17:00–18:00.

Nếu dữ liệu hợp lệ, manager tạo mã như `BK04`, tạo đối tượng `Booking` rồi gọi repository để lưu vào `Data/bookings.json`. Ngày được lưu theo dạng `YYYY-MM-DD`, giờ theo dạng `HH:MM`. Tên sân và giá theo giờ cũng được ghi vào đơn để giữ thông tin tại thời điểm đặt.

Nếu kiểm tra thất bại, manager phát sinh `BookingError`; giao diện bắt lỗi đó và hiển thị lý do bằng `st.error()`. Nếu lưu thành công, giao diện lưu thông báo tạm trong `st.session_state` rồi chạy lại trang để bảng hiển thị dữ liệu mới.

## Hủy đơn

Danh sách đơn trong tab chỉ gồm các đơn chưa hủy. Người dùng chọn một đơn rồi bấm **Hủy đơn**. Giao diện gọi `BookingManager.cancel_booking()`; manager tìm đơn theo mã, đổi trạng thái thành `Đã hủy` và gọi `BookingRepository.update()` để ghi lại JSON.

Đơn không bị xóa khỏi tệp. Cách này giữ lịch sử hủy, đồng thời repository loại đơn `Đã hủy` khỏi lịch đang hoạt động. Vì vậy, khung giờ vừa hủy có thể được đặt lại.

## Vai trò của các lớp

### `Booking`

Model trong `src/Models/Booking.py` mô tả các trường của một đơn, gồm mã đơn, mã sân, tên khách, số điện thoại, ngày, giờ bắt đầu/kết thúc, tiền cọc và trạng thái. Model kế thừa `Base`, nên cũng có thời điểm tạo và cập nhật.

### `BookingRepository`

Repository trong `src/Storage/repositories.py` phụ trách truy xuất dữ liệu. `get_by_date_and_field()` lọc theo ngày và mã sân, đồng thời bỏ qua đơn đã hủy. `add()` thêm đơn mới; `update()` ghi thay đổi trạng thái vào JSON.

### `JSONHandler`

`JSONHandler` trong `src/Storage/json_handler.py` đọc và ghi danh sách dictionary trong JSON. Các repository dùng lớp này để không phải tự xử lý thao tác tệp.

## Phạm vi hiện tại

- Tab 2 đã nối với model và dữ liệu JSON của Fields-Manager.
- Tab Sân bóng và Thanh toán trong `main.py` vẫn là nội dung giữ chỗ.
- Form đặt sân hiện chưa có ô nhập tiền cọc. Manager lưu `deposit = 0` nhưng trạng thái đơn mặc định là `Đã cọc`; cần thống nhất hai thông tin này trước khi tích hợp xử lý thanh toán.