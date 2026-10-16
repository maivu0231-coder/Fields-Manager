import streamlit as st
from Src.Component.Tab_Field import render_tab_field

st.set_page_config(
    page_title="Hệ Thống Quản Lý Sân Bóng Đá (File-Based Persistence)",
    page_icon="⚽",
    layout="wide"
)

render_tab_field()
