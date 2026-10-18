"""Tab 2 — Đặt sân & Hủy sân (Giao diện nâng cấp)."""

import inspect
import os
import sys
from datetime import date, datetime, time
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st

from Src.Core import BookingError, BookingManager


def main() -> None:
    st.set_page_config(page_title="Đặt sân / Hủy sân", layout="wide")
    render_tab_dat_san()


def _inject_booking_css() -> None:
    st.markdown(
        """
        <style>
        .slot-card {
            background-color: #f8fafc;
            border-left: 4px solid #0284c7;
            border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .slot-time {
            font-weight: 700;
            color: #0369a1;
            font-size: 0.98rem;
        }
        .slot-customer {
            font-size: 0.9rem;
            color: #334155;
            margin-top: 2px;
        }
        .field-summary-banner {
            background: linear-gradient(90deg, #eff6ff 0%, #f8fafc 100%);
            border: 1px solid #bfdbfe;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _show_feedback() -> None:
    feedback = st.session_state.pop("booking_tab_feedback", None)
    if feedback:
        kind, message = feedback
        if kind == "success":
            st.success(message)
        else:
            st.error(message)


def render_tab_dat_san(manager: Optional[BookingManager] = None) -> None:
    """Render the booking and cancellation tab for use from the app's main file."""
    manager = manager or BookingManager()
    _inject_booking_css()

    st.header("📅 Quản Lý Đặt Sân & Hủy Sân")
    st.caption(
        "Tra cứu lịch trống theo ngày, kiểm tra trùng giờ tự động (05:00 - 23:00) và quản lý phiếu đặt sân"
    )
    _show_feedback()

    fields = manager.list_fields()
    if not fields:
        st.warning("⚠️ Chưa có sân trong dữ liệu. Hãy thêm sân ở tab Quản lý sân bóng trước.")
        return

    fields_by_id = {field.field_id: field for field in fields}
    field_ids = list(fields_by_id)

    #select date and field to view bookings
    with st.container(border=True):
        col_date, col_field = st.columns([1, 2.2], gap="medium")
        with col_date:
            booking_date = st.date_input(
                "📆 Chọn ngày đặt sân",
                value=date.today(),
                key="booking_tab_date",
                format="DD/MM/YYYY",
            )
        with col_field:
            field_id = st.selectbox(
                "⚽ Chọn sân bóng",
                options=field_ids,
                format_func=lambda key: (
                    f"{fields_by_id[key].name} ({key}) — "
                    f"{getattr(fields_by_id[key], 'field_type', 'Sân bóng')} · "
                    f"{fields_by_id[key].price_per_hour:,.0f} đ/h [{fields_by_id[key].status}]"
                ),
                key="booking_tab_field",
            )

    selected_field = fields_by_id[field_id]
    bookings = manager.list_bookings(booking_date, field_id)
    is_maintenance = selected_field.status.strip().casefold() == "bảo trì"

    # show summary metrics for the selected date and field
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("📆 Ngày đang xem", booking_date.strftime("%d/%m/%Y"))
    with m2:
        with st.container(border=True):
            st.metric("🏟️ Sân đang chọn", f"{selected_field.name} ({field_id})")
    with m3:
        with st.container(border=True):
            st.metric("💵 Đơn giá thuê", f"{selected_field.price_per_hour:,.0f} đ/h")
    with m4:
        with st.container(border=True):
            st.metric("📋 Số ca đã đặt", f"{len(bookings)} ca")

    if is_maintenance:
        st.error(
            f"⛔ **{selected_field.name} ({field_id})** hiện đang ở trạng thái **Bảo trì**. "
            "Không thể tạo đơn đặt sân mới cho sân này."
        )

    st.write("")

    
    col_left, col_right = st.columns([1.05, 1.35], gap="large")

    # left column: create new booking
    with col_left:
        with st.container(border=True):
            st.subheader("➕ Tạo đơn đặt sân mới")

            st.markdown(
                f"""
                <div class="field-summary-banner">
                    <div>
                        <span style="font-size: 0.85rem; color: #475569;">Đặt lịch cho:</span><br>
                        <strong style="font-size: 1.05rem; color: #1e3a8a;">⚽ {selected_field.name} ({field_id})</strong>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.85rem; color: #475569;">Ngày đá:</span><br>
                        <strong style="font-size: 1.0rem; color: #0284c7;">{booking_date.strftime("%d/%m/%Y")}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            supports_deposit = (
                "deposit" in inspect.signature(manager.create_booking).parameters
            )

            with st.form("booking_tab_create_form", clear_on_submit=True):
                c_name, c_phone = st.columns(2)
                with c_name:
                    customer_name = st.text_input(
                        "👤 Tên khách hàng*",
                        placeholder="VD: Nguyễn Văn A...",
                    )
                with c_phone:
                    phone = st.text_input(
                        "📞 Số điện thoại*",
                        placeholder="VD: 0905123456 (10 số)...",
                    )

                c_start, c_end = st.columns(2)
                with c_start:
                    start_time = st.time_input(
                        "🕒 Giờ bắt đầu", value=time(17, 0), step=1800
                    )
                with c_end:
                    end_time = st.time_input(
                        "🕟 Giờ kết thúc", value=time(18, 30), step=1800
                    )

                if supports_deposit:
                    deposit = st.number_input(
                        "💰 Tiền đặt cọc trước (VNĐ - Không bắt buộc)",
                        min_value=0,
                        step=50000,
                        value=0,
                    )
                else:
                    deposit = 0

                #calculate and display estimated duration and fee
                duration_sec = (
                    datetime.combine(booking_date, end_time)
                    - datetime.combine(booking_date, start_time)
                ).total_seconds()
                if duration_sec > 0:
                    hours = duration_sec / 3600.0
                    est_fee = hours * selected_field.price_per_hour
                    st.caption(
                        f"⏱️ Thời lượng: **{hours:g} giờ** · "
                        f"💵 Tiền sân tạm tính: **{est_fee:,.0f} đ**"
                    )

                st.write("")
                submitted = st.form_submit_button(
                    "✅ Xác Nhận Đặt Sân",
                    type="primary",
                    use_container_width=True,
                    disabled=is_maintenance,
                )

            if submitted:
                try:
                    kwargs = {
                        "field_id": field_id,
                        "booking_date": booking_date,
                        "customer_name": customer_name,
                        "phone": phone,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                    if supports_deposit:
                        kwargs["deposit"] = float(deposit)

                    booking = manager.create_booking(**kwargs)
                except BookingError as error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state["booking_tab_feedback"] = (
                        "success",
                        f"✅ Đã tạo đơn đặt sân {booking.booking_id} thành công cho khách {booking.customer_name} ({booking.start_time} - {booking.end_time}).",
                    )
                    st.rerun()

    # right column: show existing bookings and allow cancellation
    with col_right:
        with st.container(border=True):
            st.subheader(
                f"📋 Lịch đặt sân ngày {booking_date.strftime('%d/%m/%Y')}"
            )

            if not bookings:
                st.info(
                    f"✨ **{selected_field.name}** hiện đang trống toàn bộ khung giờ (05:00 - 23:00) trong ngày {booking_date.strftime('%d/%m/%Y')}."
                )
            else:
                #show a list of existing bookings in a card format and also in a table
                st.caption("🕒 **Các ca đã có khách đặt:**")
                slot_cols = st.columns(min(len(bookings), 2))
                for idx, b in enumerate(bookings):
                    with slot_cols[idx % 2]:
                        st.markdown(
                            f"""
                            <div class="slot-card">
                                <div class="slot-time">⏰ {b.start_time} → {b.end_time} <span style="float:right; font-size:0.8rem; color:#64748b;">#{b.booking_id}</span></div>
                                <div class="slot-customer">👤 <strong>{b.customer_name}</strong> ({b.phone})</div>
                                <div style="font-size: 0.8rem; color: #059669; margin-top: 2px;">📌 {b.status}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                rows = [
                    {
                        "Mã đơn": b.booking_id,
                        "Tên khách": b.customer_name,
                        "Số điện thoại": b.phone,
                        "Khung giờ": f"{b.start_time} - {b.end_time}",
                        "Tiền cọc": f"{getattr(b, 'deposit', 0.0):,.0f} đ",
                        "Trạng thái": b.status,
                    }
                    for b in bookings
                ]
                st.dataframe(
                    pd.DataFrame(rows),
                    hide_index=True,
                    use_container_width=True,
                )

        st.write("")

        # cancel an existing booking
        with st.container(border=True):
            st.subheader("🗑️ Hủy đơn đặt sân")
            if not bookings:
                st.caption(
                    "Ngày và sân này hiện chưa có đơn đặt nào để thực hiện hủy."
                )
            else:
                bookings_by_id = {b.booking_id: b for b in bookings}
                with st.form("booking_tab_cancel_form"):
                    booking_id = st.selectbox(
                        "Chọn đơn cần hủy:",
                        options=list(bookings_by_id),
                        format_func=lambda key: (
                            f"🏷️ {key} — 👤 {bookings_by_id[key].customer_name} ({bookings_by_id[key].phone}) · "
                            f"🕒 {bookings_by_id[key].start_time} → {bookings_by_id[key].end_time}"
                        ),
                    )
                    cancel_submitted = st.form_submit_button(
                        "🗑️ Xác Nhận Hủy Đơn Này",
                        use_container_width=True,
                    )

                if cancel_submitted:
                    try:
                        cancelled = manager.cancel_booking(booking_id)
                    except BookingError as error:
                        st.error(f"❌ {error}")
                    else:
                        st.session_state["booking_tab_feedback"] = (
                            "success",
                            f"✅ Đã hủy đơn {cancelled.booking_id} thành công.",
                        )
                        st.rerun()


if __name__ == "__main__":
    main()