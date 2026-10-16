# Cách khởi tạo môi trường ảo trên terminal
python -m venv venv
# Cách kích hoạt môi trường ảo 
.venv\Scripts\Activate.ps1
# Xây dựng logic nghiệp vụ ta viết vào folder core 
# xây dựng giao diện ta viết vào folder components
# dùng trực tiếp các class trong models


## 💰 Tab 3: Thanh toán & Xuất hóa đơn

### Người phụ trách
- [Tên bạn]

### Chức năng
- Danh sách booking có status "Chờ thanh toán" và chưa có trong payments.json.
- Tính tiền: rental_fee + surcharge - deposit.
- Thanh toán → ghi payments.json → in hóa đơn.
- Tìm kiếm theo tên khách — O(log n).

### Cấu trúc dữ liệu
| Cấu trúc | Vị trí | Độ phức tạp |
|---|---|---|
| Hash Map | PaymentManager._booking_by_id | O(1) |
| Set | PaymentManager._paid_ids | O(1) |

### Thuật toán tự cài đặt (không dùng hàm có sẵn)
| Thuật toán | File | Vị trí |
|---|---|---|
| Binary Search | Core/algorithms.py | BookingRepository.find_by_name() |
| Merge Sort | Core/algorithms.py | BookingRepository._load_sorted_cache() |

### Logic tính tiền
