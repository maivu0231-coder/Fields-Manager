# Cách khởi tạo môi trường ảo trên terminal
python -m venv venv
# Cách kích hoạt môi trường ảo 
.venv\Scripts\Activate.ps1
# Xây dựng logic nghiệp vụ ta viết vào folder core 
# xây dựng giao diện ta viết vào folder components
# dùng trực tiếp các class trong models


# 💰 Tab 3 — Thanh toán & Xuất hóa đơn

> **Module:** Thanh toán sân bóng
> **Người phụ trách:** [Tên bạn] — MSSV: [MSSV]
> **Nhánh Git:** `feat/payment`
> **Ngày hoàn thành:** 16/10/2026

---

## 📖 Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc module](#2-kiến-trúc-module)
3. [Luồng hoạt động](#3-luồng-hoạt-động)
4. [Cấu trúc dữ liệu](#4-cấu-trúc-dữ-liệu)
5. [Thuật toán tự cài đặt](#5-thuật-toán-tự-cài-đặt)
6. [Logic nghiệp vụ](#6-logic-nghiệp-vụ)
7. [Lưu trữ dữ liệu](#7-lưu-trữ-dữ-liệu)
8. [Giao diện Streamlit](#8-giao-diện-streamlit)
9. [API tích hợp](#9-api-tích-hợp)
10. [Kịch bản test](#10-kịch-bản-test)
11. [Xử lý lỗi](#11-xử-lý-lỗi)
12. [Câu hỏi bảo vệ](#12-câu-hỏi-bảo-vệ)

---

# 💰 Tab 3 — Thanh toán & Xuất hóa đơn

## Chức năng

Module Tab 3 cho phép nhân viên quầy thu ngân xem danh sách các đơn đặt sân **chờ thanh toán**, xem chi tiết hóa đơn (thời gian đá, đơn giá, tiền thuê, tiền cọc), nhập thêm phụ phí phát sinh (nước uống, bóng, đèn), xác nhận thanh toán để sinh hóa đơn và lưu lịch sử, tra cứu nhanh đơn theo tên khách hàng với độ phức tạp O(log n). Module còn chống thanh toán trùng đơn bằng Set `_paid_ids`, đảm bảo mỗi booking chỉ được thanh toán một lần.

## Kiến trúc

Module gồm 3 file chính, tách biệt theo tầng:

- `Core/algorithms.py` — chứa thuật toán tự cài đặt: `binary_search` (O(log n)) và `merge_sort` (O(n log n)). Không dùng `bisect`, `sorted` hay `max` của Python.
- `Core/Payment_Manager.py` — class `PaymentManager` xử lý toàn bộ logic nghiệp vụ thanh toán. **Không import streamlit** để đảm bảo tách biệt logic khỏi UI.
- `Component/Tab_Payment.py` — hàm `render_tab_payment(pm)` chỉ render giao diện Streamlit, mọi thao tác xử lý đều gọi qua `PaymentManager`.

Ngoài ra module tận dụng các file có sẵn của nhóm: `Models/Payment.py` (định nghĩa class Payment), `Storage/repositories.py` (đọc/ghi JSON), `Storage/json_handler.py` (ghi file atomic).

## Luồng hoạt động

Khi người dùng mở Tab 3, `PaymentManager.get_unpaid_bookings()` đọc `bookings.json`, lọc các đơn có `status = "Chờ thanh toán"` và loại các đơn đã có trong `payments.json`. UI hiển thị 2 cột: cột trái là danh sách đơn chờ, cột phải là chi tiết hóa đơn. Khi nhân viên chọn 1 đơn, `preview()` tính tiền tạm và UI cập nhật realtime. Nhân viên có thể nhập thêm phụ phí, mỗi lần nhập `preview()` được gọi lại để cập nhật tổng. Khi bấm "Thanh toán & In hóa đơn", hàm `pay()` thực hiện 6 bước: kiểm tra trùng qua Set `_paid_ids` (O(1)), tính tiền lần cuối, sinh mã hóa đơn tự động (INV01, INV02...), tạo object `Payment`, ghi vào `payments.json` bằng cơ chế atomic, và thêm `booking_id` vào Set `_paid_ids`. Sau đó UI hiển thị hóa đơn và gọi `st.rerun()` để đơn biến mất khỏi danh sách chờ.

## Cấu trúc dữ liệu

Module dùng 2 cấu trúc dữ liệu chính. Thứ nhất là **Hash Map (dict)** ở `PaymentManager._booking_by_id`, dùng để tra cứu booking theo `booking_id` với độ phức tạp O(1) thay vì O(n) nếu dùng list. Thứ hai là **Set** ở `PaymentManager._paid_ids`, dùng để kiểm tra đơn đã thanh toán hay chưa — kiểm tra `x in set` là O(1), còn `x in list` là O(n). Ngoài ra module còn dùng **List đã sort** ở `BookingRepository._sorted_cache` để phục vụ binary search.

## Thuật toán tự cài đặt

Binary Search được dùng trong `BookingRepository.find_by_name()` để tìm booking theo tên khách hàng với độ phức tạp O(log n). Cách hoạt động: duy trì đoạn `[left, right]` có thể chứa target, mỗi vòng lặp so sánh target với phần tử giữa `arr[mid]`, nếu bằng thì trả về index, nếu target nhỏ hơn thì tìm nửa trái (`right = mid - 1`), nếu lớn hơn thì tìm nửa phải (`left = mid + 1`). Mỗi bước giảm một nửa không gian tìm kiếm.
