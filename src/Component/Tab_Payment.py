"""Tab 3 — Thanh toán & Xuất hóa đơn. Chỉ render UI."""

import streamlit as st
from Core.Payment_Manager import PaymentManager


def render_tab_payment(pm: PaymentManager):
    """Hàm public — main.py gọi."""
    st.subheader("💰 Thanh toán & Xuất hóa đơn")
    with st.expander("🔍 Tìm kiếm đơn"):
        kw = st.text_input("Nhập tên khách hàng:", key="pay_search")
        if st.button("Tìm", key="pay_search_btn"):
            b = pm.find_booking_by_name(kw)
            if b:
                st.success(
                    f"Tìm thấy: **{b.booking_id}** — {b.customer_name} "
                    f"({b.field_name})"
                )
            else:
                st.warning("Không tìm thấy.")

    st.divider()

    unpaid = pm.get_unpaid_bookings()
    if not unpaid:
        st.info("Không có đơn nào chờ thanh toán.")
        return

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown("### 📋 Danh sách chờ thanh toán")
        options = {
            f"{b.booking_id} | {b.field_name} | {b.customer_name}": b
            for b in unpaid
        }
        choice = st.radio(
            "Chọn đơn:", list(options.keys()),
            label_visibility="collapsed"
        )
        booking = options[choice]

    with col_right:
        st.markdown("### 🧾 Chi tiết hóa đơn")
        surcharge = st.number_input(
            "Phụ phí (nước uống, bóng, đèn...):",
            min_value=0.0, value=0.0, step=10000.0
        )

        info = pm.preview(booking, surcharge)

        st.write(f"**Mã đơn:** {booking.booking_id}")
        st.write(f"**Khách:** {booking.customer_name}")
        st.write(f"**Sân:** {booking.field_name}")
        st.write(f"**Thời gian:** {booking.start_time} → "
                 f"{booking.end_time} ({info['duration_hours']}h)")
        st.write(f"**Đơn giá:** {info['price_per_hour']:,.0f} đ/h")
        st.write(f"**Tiền thuê:** {info['rental_fee']:,.0f} đ")
        st.write(f"**Phụ phí:** {info['surcharge']:,.0f} đ")
        st.write(f"**Tiền cọc:** -{info['deposit_deducted']:,.0f} đ")
        st.markdown(f"## TỔNG: **{info['total_amount']:,.0f} đ**")

        if st.button(
            "✅ Thanh toán & In hóa đơn",
            type="primary",
            use_container_width=True
        ):
            try:
                p = pm.pay(booking, surcharge)
                st.success(f"Đã thanh toán — HĐ {p.invoice_id}")
                st.code(pm.format_receipt(p), language="text")
                st.rerun()
            except ValueError as e:
                st.error(str(e))