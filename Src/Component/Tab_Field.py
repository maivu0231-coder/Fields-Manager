import streamlit as st
import pandas as pd
from Src.Core.Field_Manager import FieldService
from Src.Models.Fields import FieldStatus, FieldType

def render_tab_field() -> None:
    service = FieldService()
    all_fields = service.get_all()

    st.title("⚽ QUẢN LÝ DANH SÁCH SÂN BÓNG ĐÁ")
    st.caption("Chế độ: Đọc/Ghi dữ liệu trực tiếp File JSON (Lưu trữ bền vững) + Xử lý Edge Cases")

    # --- THANH TÌM KIẾM VÀ BỘ LỌC thông minh ---
    st.subheader("DANH SÁCH SÂN BÓNG (ListView - Report Mode)")
    
    col_s1, col_s2, col_s3 = st.columns([2.5, 1.2, 1.2])
    with col_s1:
        search_kw = st.text_input("🔍 Tìm kiếm sân", placeholder="Nhập tên hoặc mã sân (hỗ trợ tiếng Việt không dấu)...")
    with col_s2:
        status_opts = ["Tất cả"] + [s.value for s in FieldStatus]
        selected_st = st.selectbox("Lọc trạng thái", options=status_opts)
    with col_s3:
        type_opts = ["Tất cả"] + [t.value for t in FieldType]
        selected_type = st.selectbox("Lọc loại sân", options=type_opts)

    filtered = service.filter(status=selected_st, field_type=selected_type, search_term=search_kw)

    if filtered:
        table_data = [{
            "Mã Sân": f.field_code,
            "Tên Sân": f.field_name,
            "Loại Sân": f.field_type,
            "Giá Thuê/Giờ": f"{f.price_per_hour:,.0f} đ",
            "Trạng Thái Hiện Tại": f.status,
            "Cập Nhật": f.updated_at
        } for f in filtered]

        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Không tìm thấy sân bóng nào phù hợp với bộ lọc hiện tại!")
        if st.button("⏪ Hiển thị lại tất cả sân bóng"):
            st.rerun()

    st.markdown("---")

    # --- KHU VỰC THAO TÁC QUẢN LÝ GỘP ---
    st.write("#### 🛠️ THAO TÁC QUẢN LÝ SÂN BÓNG")

    tab_edit, tab_combined, tab_reset = st.tabs([
        "✏️ Cập Nhật Thông Tin Sân",
        "➕ 🗑️ Gộp: Thêm Mới & Xóa Sân Bóng",
        "⚙️ Khôi Phục Dữ Liệu Gốc"
    ])

    # TAB 1: CẬP NHẬT
    with tab_edit:
        st.write("##### Chỉnh sửa thông tin sân bóng")
        if all_fields:
            code_list = [f.field_code for f in all_fields]
            selected_code = st.selectbox("Chọn mã sân cần sửa:", options=code_list, key="sb_edit_sel")
            target = next((f for f in all_fields if f.field_code == selected_code), None)

            if target:
                with st.form("form_edit_field_edgecase"):
                    e_name = st.text_input("Tên sân bóng", value=target.field_name)
                    
                    type_opts = [t.value for t in FieldType]
                    e_type = st.selectbox("Loại sân", options=type_opts, index=type_opts.index(target.field_type) if target.field_type in type_opts else 0)
                    
                    e_price = st.number_input("Giá thuê/giờ (VNĐ)", min_value=0, step=50000, value=int(target.price_per_hour))
                    
                    status_opts = [s.value for s in FieldStatus]
                    e_status = st.selectbox("Trạng thái hiện tại", options=status_opts, index=status_opts.index(target.status) if target.status in status_opts else 0)

                    if st.form_submit_button("Xác Nhận Cập Nhật", type="primary", use_container_width=True):
                        ok, msg = service.update(selected_code, e_name, e_type, e_price, e_status)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Hiện không có sân bóng nào để cập nhật.")

    # TAB 2: GỘP THÊM & XÓA
    with tab_combined:
        col_add, col_del = st.columns(2)

        with col_add:
            st.write("##### ➕ Thêm Sân Bóng Mới")
            with st.form("form_add_combined", clear_on_submit=True):
                f_code = st.text_input("Mã Sân (VD: S05)*", placeholder="Mã sân viết hoa...")
                f_name = st.text_input("Tên Sân Bóng*", placeholder="Tên hiển thị sân...")
                f_type = st.selectbox("Loại Sân*", options=[t.value for t in FieldType])
                f_price = st.number_input("Giá Thuê/Giờ (VNĐ)*", min_value=0, step=50000, value=200000)
                f_status = st.selectbox("Trạng Thái Ban Đầu", options=[s.value for s in FieldStatus])

                if st.form_submit_button("Lưu Vào File JSON", type="primary", use_container_width=True):
                    ok, msg = service.add(f_code, f_name, f_type, f_price, f_status)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col_del:
            st.write("##### 🗑️ Xóa Sân Bóng")
            if all_fields:
                code_list = [f.field_code for f in all_fields]
                del_code = st.selectbox("Chọn mã sân cần xóa:", options=code_list, key="sb_del_combined")
                st.write("")
                if st.button("Xác Nhận Xóa Sân", type="primary", use_container_width=True):
                    ok, msg = service.delete(del_code)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning(msg)
            else:
                st.info("Danh sách sân hiện đang rỗng.")

    # TAB 3: KHÔI PHỤC
    with tab_reset:
        st.write("##### Khôi phục dữ liệu ban đầu")
        st.caption("Nếu bạn lỡ xóa nhầm hết sân, nhấn nút bên dưới để khôi phục lại dữ liệu mẫu ban đầu.")
        if st.button("⚙️ Khôi Phục Dữ Liệu Mẫu", type="secondary"):
            ok, msg = service.reset_to_default()
            if ok:
                st.success(msg)
                st.rerun()
