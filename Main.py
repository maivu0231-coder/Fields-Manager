import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from Src.Component.Tab_booking import render_tab_dat_san
from Src.Component.Tab_Field import render_tab_field
from Src.Component.Tab_Payment import render_tab_payment
from Src.Core.Booking_Manager import BookingManager
from Src.Core.Field_Manager import FieldService
from Src.Core.Payment_Manager import PaymentManager


def _inject_main_css() -> None:
    st.markdown(
        """
        <style>
        .main-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            color: white;
            padding: 20px 28px;
            border-radius: 14px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        }
        .main-banner-title {
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin: 0;
        }
        .main-banner-sub {
            font-size: 0.92rem;
            color: #cbd5e1;
            margin-top: 4px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            padding: 0 20px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # Cấu hình trang (Chỉ gọi duy nhất 1 lần ở đầu main.py)
    st.set_page_config(
        page_title="Fields Manager - Quản Lý Sân Bóng",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _inject_main_css()

    # Khởi tạo các tầng nghiệp vụ (Core Managers)
    field_service = FieldService()
    booking_manager = BookingManager()
    payment_manager = PaymentManager()

    # Đếm nhanh số liệu hiển thị trên thanh tiêu đề & nhãn Tab
    total_fields = len(field_service.get_all())
    unpaid_count = len(payment_manager.get_unpaid_bookings())

    # Banner tiêu đề chính của hệ thống
    st.markdown(
        f"""
        <div class="main-banner">
            <div>
                <div class="main-banner-title">🏟️ HỆ THỐNG QUẢN LÝ SÂN BÓNG MINI (FIELDS MANAGER)</div>
                <div class="main-banner-sub">Quản lý danh mục sân · Đặt lịch & Kiểm tra trùng giờ · Thanh toán & Xuất hóa đơn tự động</div>
            </div>
            <div style="text-align: right; font-size: 0.9rem; color: #e2e8f0;">
                <div>⚽ Tổng số sân: <strong>{total_fields} sân</strong></div>
                <div>⏳ Chờ thanh toán: <strong>{unpaid_count} đơn</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Gộp 3 chức năng vào 3 Tabs chính
    tab_fields, tab_bookings, tab_payments = st.tabs(
        [
            f"⚽ Quản Lý Sân Bóng ({total_fields})",
            "📅 Đặt Sân / Hủy Sân",
            f"💰 Thanh Toán & Hóa Đơn ({unpaid_count})",
        ]
    )

    with tab_fields:
        render_tab_field(service=field_service)

    with tab_bookings:
        render_tab_dat_san(manager=booking_manager)

    with tab_payments:
        render_tab_payment(pm=payment_manager)


if __name__ == "__main__":
    main()