import sys
import os 

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from Core.Payment_Manager import PaymentManager
from Component.Tab_Payment import render_tab_payment

st.set_page_config(page_title="Quản lí sân bóng", layout="wide")
st.title("⚽ Hệ thống quản lý sân bóng")

pm = PaymentManager()
tab1, tab2, tab3 = st.tabs([
    "Tab 1: Sân bóng",
    "Tab 2: Lịch đặt sân",
    "Tab 3: Thanh toán"
])
with tab1:
    st.info("(Thành viên khác phụ trách)")

with tab2:
    st.info("(Thành viên khác phụ trách)")

with tab3:
    render_tab_payment(pm)
