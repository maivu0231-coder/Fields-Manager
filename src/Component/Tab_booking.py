from datetime import date, time

import pandas as pd
import streamlit as st

from src.Core.Booking_Manager import BookingError, BookingManager


def _show_feedback() -> None:
    feedback = st.session_state.pop("booking_tab_feedback", None)
    if feedback:
        kind, message = feedback
        if kind == "success":
            st.success(message)
        else:
            st.error(message)


def render_tab_dat_san(manager: BookingManager | None = None) -> None:
    """Render the booking and cancellation tab for use from the app's main file."""
    manager = manager or BookingManager()
    st.header("Đặt sân / Hủy sân")
    _show_feedback()

    fields = manager.list_fields()
    if not fields:
        st.warning("Chưa có sân trong dữ liệu. Hãy thêm sân ở tab Sân bóng trước.")
        return

    fields_by_id = {field.field_id: field for field in fields}
    field_ids = list(fields_by_id)
    col_date, col_field = st.columns([1, 2])
    with col_date:
        booking_date = st.date_input(
            "Ngày đặt",
            value=date.today(),
            key="booking_tab_date",
            format="DD/MM/YYYY",
        )
    with col_field:
        field_id = st.selectbox(
            "Chọn sân",
            options=field_ids,
            format_func=lambda key: f"{fields_by_id[key].name} ({key})",
            key="booking_tab_field",
        )

    selected_field = fields_by_id[field_id]
    if selected_field.status.strip().casefold() == "bảo trì":
        st.warning("Sân này đang bảo trì. Không thể tạo đơn mới cho sân này.")

    bookings = manager.list_bookings(booking_date, field_id)
    st.subheader("Lịch đặt trong ngày")
    rows = [
        {
            "Mã đơn": booking.booking_id,
            "Tên khách": booking.customer_name,
            "Số điện thoại": booking.phone,
            "Bắt đầu": booking.start_time,
            "Kết thúc": booking.end_time,
            "Trạng thái": booking.status,
        }
        for booking in bookings
    ]
    st.dataframe(
        pd.DataFrame(
            rows,
            columns=[
                "Mã đơn",
                "Tên khách",
                "Số điện thoại",
                "Bắt đầu",
                "Kết thúc",
                "Trạng thái",
            ],
        ),
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Tạo đơn đặt sân", expanded=True):
        with st.form("booking_tab_create_form", clear_on_submit=True):
            customer_name = st.text_input("Tên khách")
            phone = st.text_input("Số điện thoại")
            col_start, col_end = st.columns(2)
            with col_start:
                start_time = st.time_input("Giờ bắt đầu", value=time(17, 0), step=1800)
            with col_end:
                end_time = st.time_input("Giờ kết thúc", value=time(18, 30), step=1800)
            submitted = st.form_submit_button("Xác nhận đặt sân", type="primary")

        if submitted:
            try:
                booking = manager.create_booking(
                    field_id=field_id,
                    booking_date=booking_date,
                    customer_name=customer_name,
                    phone=phone,
                    start_time=start_time,
                    end_time=end_time,
                )
            except BookingError as error:
                st.error(str(error))
            else:
                st.session_state["booking_tab_feedback"] = (
                    "success",
                    f"Đã tạo đơn {booking.booking_id}.",
                )
                st.rerun()

    st.subheader("Hủy đơn đặt sân")
    if not bookings:
        st.info("Ngày và sân này chưa có đơn đặt để hủy.")
        return

    bookings_by_id = {booking.booking_id: booking for booking in bookings}
    with st.form("booking_tab_cancel_form"):
        booking_id = st.selectbox(
            "Chọn đơn cần hủy",
            options=list(bookings_by_id),
            format_func=lambda key: (
                f"{key} · {bookings_by_id[key].customer_name} · "
                f"{bookings_by_id[key].start_time}-{bookings_by_id[key].end_time}"
            ),
        )
        cancel_submitted = st.form_submit_button("Hủy đơn")

    if cancel_submitted:
        try:
            cancelled = manager.cancel_booking(booking_id)
        except BookingError as error:
            st.error(str(error))
        else:
            st.session_state["booking_tab_feedback"] = (
                "success",
                f"Đã hủy đơn {cancelled.booking_id}.",
            )
            st.rerun()
