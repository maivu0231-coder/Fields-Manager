import streamlit as st

from src.Component.Tab_booking import render_tab_dat_san


def main() -> None:
    st.set_page_config(page_title="Quản lý sân bóng đá", layout="wide")
    st.title("Quản lý sân bóng đá")

    tab_fields, tab_bookings, tab_payments = st.tabs(
        ["Sân bóng", "Đặt sân / Hủy sân", "Thanh toán"]
    )
    with tab_fields:
        st.info("Tab quản lý danh sách sân sẽ được tích hợp tại đây.")
    with tab_bookings:
        render_tab_dat_san()
    with tab_payments:
        st.info("Tab thanh toán sẽ được tích hợp tại đây.")


if __name__ == "__main__":
    main()
