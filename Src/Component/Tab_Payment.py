"""Tab 3 — Thanh toán & Xuất hóa đơn (Giao diện nâng cấp)."""

import os
import sys
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st

from Src.Core.Payment_Manager import PaymentManager


def main() -> None:
    st.set_page_config(page_title="Thanh toán & Xuất hóa đơn", layout="wide")
    render_tab_payment()


def _inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .invoice-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-top: 10px;
            margin-bottom: 16px;
        }
        .invoice-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px dashed #cbd5e1;
            padding-bottom: 12px;
            margin-bottom: 14px;
        }
        .invoice-badge {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .invoice-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 0.96rem;
            color: #334155;
        }
        .invoice-divider {
            border-top: 1px solid #e2e8f0;
            margin: 10px 0;
        }
        .invoice-total {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 12px;
            font-weight: 700;
            font-size: 1.2rem;
            color: #1d4ed8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_tab_payment(pm: Optional[PaymentManager] = None) -> None:
    """Hàm public — main.py gọi."""
    pm = pm or PaymentManager()
    _inject_custom_css()

    st.header("💰 Quản Lý Thanh Toán & Xuất Hóa Đơn")
    st.caption("Tính tiền thuê sân tự động, cộng phụ phí, khấu trừ tiền cọc và xuất biên lai thanh toán")

    unpaid = pm.get_unpaid_bookings()
    paid_list = pm._payment_repo.get_all() if hasattr(pm, "_payment_repo") else []

    # show summary metrics at the top of the page
    total_revenue = sum(p.total_amount for p in paid_list)
    pending_estimated = sum(pm.preview(b)["total_amount"] for b in unpaid)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("⏳ Đơn chờ thanh toán", f"{len(unpaid)} đơn")
    with m2:
        with st.container(border=True):
            st.metric("💳 Dự kiến thu thêm", f"{pending_estimated:,.0f} đ")
    with m3:
        with st.container(border=True):
            st.metric("🧾 Hóa đơn đã xuất", f"{len(paid_list)} HĐ")
    with m4:
        with st.container(border=True):
            st.metric("📈 Tổng thực thu", f"{total_revenue:,.0f} đ")

    # show the last payment receipt if available
    last_receipt = st.session_state.pop("last_payment_receipt", None)
    if last_receipt:
        inv_id, receipt_text = last_receipt
        with st.container(border=True):
            col_msg, col_dl = st.columns([3, 1])
            with col_msg:
                st.success(f"✅ Đã thanh toán thành công — Mã hóa đơn: **{inv_id}**")
            with col_dl:
                st.download_button(
                    label=f"📥 Tải hóa đơn {inv_id} (.txt)",
                    data=receipt_text,
                    file_name=f"HoaDon_{inv_id}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            st.code(receipt_text, language="text")

    #quick search for bookings by customer name
    with st.expander("🔍 Tìm kiếm nhanh đơn đặt sân theo tên khách hàng"):
        col_kw, col_btn = st.columns([4, 1])
        with col_kw:
            kw = st.text_input(
                "Nhập tên khách hàng:",
                placeholder="Ví dụ: Nguyễn Văn A, mai xuan vu...",
                key="pay_search",
                label_visibility="collapsed",
            )
        with col_btn:
            search_clicked = st.button(
                "🔍 Tìm kiếm", key="pay_search_btn", use_container_width=True
            )

        if search_clicked:
            b = pm.find_booking_by_name(kw)
            if b:
                st.success(
                    f"**Mã đơn:** `{b.booking_id}` | **Khách:** {b.customer_name} ({getattr(b, 'phone', '')}) | "
                    f"**Sân:** {b.field_name} | **Khung giờ:** {b.start_time} - {b.end_time} | "
                    f"**Trạng thái:** `{b.status}`"
                )
            else:
                st.warning("Không tìm thấy đơn đặt sân nào khớp với tên khách hàng này.")

    st.write("")

    #pay an unpaid booking and generate a receipt
    if not unpaid:
        with st.container(border=True):
            st.info("🎉 Hiện tại tất cả các đơn đặt sân đều đã được thanh toán hoàn tất!")
    else:
        col_left, col_right = st.columns([1.05, 1.35], gap="large")

        with col_left:
            with st.container(border=True):
                st.subheader("📋 Danh sách chờ thanh toán")
                st.caption("Chọn một đơn đặt sân bên dưới để lập hóa đơn:")

                options = {
                    f"🏷️ {b.booking_id} · {b.field_name} — 👤 {b.customer_name} ({b.start_time}-{b.end_time})": b
                    for b in unpaid
                }
                choice = st.radio(
                    "Chọn đơn cần thanh toán:",
                    list(options.keys()),
                    label_visibility="collapsed",
                )
                booking = options[choice]

                st.divider()
                st.caption("📌 **Tóm tắt đơn đang chọn:**")
                summary_df = pd.DataFrame(
                    [
                        {
                            "Mã đơn": booking.booking_id,
                            "Sân": booking.field_name,
                            "Ngày đặt": getattr(booking, "booking_date", "Hôm nay"),
                            "Giờ đá": f"{booking.start_time} - {booking.end_time}",
                            "Đã cọc": f"{booking.deposit:,.0f} đ",
                        }
                    ]
                )
                st.dataframe(summary_df, hide_index=True, use_container_width=True)

        with col_right:
            with st.container(border=True):
                st.subheader("🧾 Chi tiết bảng kê & Thu tiền")

                surcharge = st.number_input(
                    "➕ Phụ phí phát sinh (nước uống, thuê bóng, đèn chiếu sáng... - VNĐ):",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                    format="%.0f",
                )

                info = pm.preview(booking, surcharge)
                booking_date_str = getattr(booking, "booking_date", "")
                phone_str = getattr(booking, "phone", "Chưa cập nhật")

                st.markdown(
                    f"""
                    <div class="invoice-box">
                        <div class="invoice-header">
                            <div>
                                <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">
                                    PHIẾU TẠM TÍNH — ĐƠN #{booking.booking_id}
                                </div>
                                <div style="font-size: 0.85rem; color: #64748b;">
                                    Ngày đá: {booking_date_str} | Khung giờ: {booking.start_time} → {booking.end_time}
                                </div>
                            </div>
                            <span class="invoice-badge">{booking.status}</span>
                        </div>
                        <div class="invoice-row">
                            <span>👤 Khách hàng:</span>
                            <strong>{booking.customer_name} ({phone_str})</strong>
                        </div>
                        <div class="invoice-row">
                            <span>⚽ Sân bóng:</span>
                            <strong>{booking.field_name}</strong>
                        </div>
                        <div class="invoice-row">
                            <span>⏱️ Thời lượng sử dụng:</span>
                            <strong>{info['duration_hours']} giờ</strong>
                        </div>
                        <div class="invoice-row">
                            <span>💵 Đơn giá thuê sân:</span>
                            <strong>{info['price_per_hour']:,.0f} đ / giờ</strong>
                        </div>
                        <div class="invoice-divider"></div>
                        <div class="invoice-row">
                            <span>Tiền thuê sân ({info['duration_hours']}h × {info['price_per_hour']:,.0f} đ):</span>
                            <strong>{info['rental_fee']:,.0f} đ</strong>
                        </div>
                        <div class="invoice-row">
                            <span>Phụ phí dịch vụ:</span>
                            <strong>+{info['surcharge']:,.0f} đ</strong>
                        </div>
                        <div class="invoice-row" style="color: #dc2626;">
                            <span>Khấu trừ tiền đã đặt cọc:</span>
                            <strong>-{info['deposit_deducted']:,.0f} đ</strong>
                        </div>
                        <div class="invoice-total">
                            <span>TỔNG CẦN THU:</span>
                            <span>{info['total_amount']:,.0f} VNĐ</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "✅ Xác Nhận Thanh Toán & Xuất Hóa Đơn",
                    type="primary",
                    use_container_width=True,
                ):
                    try:
                        p = pm.pay(booking, surcharge)
                        st.session_state["last_payment_receipt"] = (
                            p.invoice_id,
                            pm.format_receipt(p),
                        )
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

    # show a list of paid invoices in a table format
    if paid_list:
        st.write("")
        with st.expander(f"📜 Lịch sử hóa đơn đã thanh toán ({len(paid_list)} hóa đơn)", expanded=False):
            history_rows = [
                {
                    "Mã HĐ": p.invoice_id,
                    "Mã Đơn": p.booking_id,
                    "Khách Hàng": p.customer_name,
                    "Sân": p.field_name,
                    "Số Giờ": f"{p.duration_hours}h",
                    "Tiền Thuê": f"{p.rental_fee:,.0f} đ",
                    "Phụ Phí": f"{p.surcharge:,.0f} đ",
                    "Trừ Cọc": f"-{p.deposit_deducted:,.0f} đ",
                    "Thực Thu": f"{p.total_amount:,.0f} đ",
                    "Thời Gian Thanh Toán": p.payment_time,
                }
                for p in reversed(paid_list)
            ]
            st.dataframe(
                pd.DataFrame(history_rows),
                hide_index=True,
                use_container_width=True,
            )


if __name__ == "__main__":
    main()