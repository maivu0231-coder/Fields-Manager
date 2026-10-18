"""Tab 1 — Quản lý danh sách sân bóng đá (Giao diện nâng cấp)."""

import os
import sys
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st

from Src.Core import FieldService
from Src.Models import FieldStatus, FieldType


def main() -> None:
    st.set_page_config(page_title="Quản lý sân bóng", layout="wide")
    render_tab_field()

# create a function to inject custom CSS for field cards
def _inject_field_css() -> None:
    st.markdown(
        """
        <style>
        .field-card {
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid #e2e8f0;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .field-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .field-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #0f172a;
        }
        .field-code {
            font-size: 0.8rem;
            color: #64748b;
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
        .badge-available {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-inuse {
            background-color: #dbeafe;
            color: #1e40af;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-maintenance {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .field-price {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0284c7;
            margin-top: 6px;
        }
        .field-meta {
            font-size: 0.85rem;
            color: #475569;
            margin-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

#get a status badge with color and icon based on the field status
def _get_status_badge(status: str) -> str:
    st_clean = status.strip()
    if st_clean == FieldStatus.AVAILABLE.value:
        return f'<span class="badge-available">🟢 {st_clean}</span>'
    if st_clean == FieldStatus.IN_USE.value:
        return f'<span class="badge-inuse">🔵 {st_clean}</span>'
    return f'<span class="badge-maintenance">🔴 {st_clean}</span>'


def _get_status_icon_text(status: str) -> str:
    st_clean = status.strip()
    if st_clean == FieldStatus.AVAILABLE.value:
        return f"🟢 {st_clean}"
    if st_clean == FieldStatus.IN_USE.value:
        return f"🔵 {st_clean}"
    return f"🔴 {st_clean}"


def _show_field_feedback() -> None:
    feedback = st.session_state.pop("field_tab_feedback", None)
    if feedback:
        kind, message = feedback
        if kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)


def render_tab_field(service: Optional[FieldService] = None) -> None:
    service = service or FieldService()
    _inject_field_css()

    all_fields = service.get_all()

    st.header("⚽ Quản Lý Danh Sách Sân Bóng Đá")
    st.caption(
        "Theo dõi trạng thái sân theo thời gian thực, tra cứu thông minh và quản lý danh mục sân bóng"
    )
    _show_field_feedback()


    total_cnt = len(all_fields)
    avail_cnt = sum(1 for f in all_fields if f.status == FieldStatus.AVAILABLE.value)
    inuse_cnt = sum(1 for f in all_fields if f.status == FieldStatus.IN_USE.value)
    maint_cnt = sum(1 for f in all_fields if f.status == FieldStatus.MAINTENANCE.value)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("🏟️ Tổng số sân", f"{total_cnt} sân")
    with m2:
        with st.container(border=True):
            st.metric("🟢 Sân đang trống", f"{avail_cnt} sân")
    with m3:
        with st.container(border=True):
            st.metric("🔵 Đang có khách", f"{inuse_cnt} sân")
    with m4:
        with st.container(border=True):
            st.metric("🔴 Đang bảo trì", f"{maint_cnt} sân")

    st.write("")

    with st.container(border=True):
        st.subheader("📋 Danh sách & Trạng thái sân bóng")

        col_s1, col_s2, col_s3 = st.columns([2.4, 1.2, 1.2])
        with col_s1:
            search_kw = st.text_input(
                "🔍 Tìm kiếm sân",
                placeholder="Nhập tên hoặc mã sân (hỗ trợ tiếng Việt không dấu)...",
            )
        with col_s2:
            status_opts = ["Tất cả"] + [s.value for s in FieldStatus]
            selected_st = st.selectbox("Lọc trạng thái", options=status_opts)
        with col_s3:
            type_opts = ["Tất cả"] + [t.value for t in FieldType]
            selected_type = st.selectbox("Lọc loại sân", options=type_opts)

        filtered = service.filter(
            status=selected_st, field_type=selected_type, search_term=search_kw
        )

        if filtered:
            st.markdown("##### 🏟️ Sơ đồ trạng thái nhanh")
            cols = st.columns(min(len(filtered), 4))
            for idx, f in enumerate(filtered):
                with cols[idx % 4]:
                    st.markdown(
                        f"""
                        <div class="field-card">
                            <div class="field-card-header">
                                <span class="field-title">⚽ {f.name}</span>
                                <span class="field-code">{f.field_id}</span>
                            </div>
                            <div>{_get_status_badge(f.status)}</div>
                            <div class="field-price">{f.price_per_hour:,.0f} đ / giờ</div>
                            <div class="field-meta">📐 Loại: <strong>{f.field_type}</strong></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with st.expander("📊 Xem dạng bảng chi tiết (Table View)", expanded=True):
                table_data = [
                    {
                        "Mã Sân": f.field_id,
                        "Tên Sân": f.name,
                        "Loại Sân": f.field_type,
                        "Giá Thuê/Giờ": f"{f.price_per_hour:,.0f} đ",
                        "Trạng Thái Hiện Tại": _get_status_icon_text(f.status),
                        "Cập Nhật Lần Cuối": f.updated_at,
                    }
                    for f in filtered
                ]
                st.dataframe(
                    pd.DataFrame(table_data),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning("⚠️ Không tìm thấy sân bóng nào phù hợp với bộ lọc hiện tại!")

    st.write("")

    with st.container(border=True):
        st.subheader("🛠️ Thao tác quản lý sân bóng")

        tab_edit, tab_combined, tab_reset = st.tabs(
            [
                "✏️ Cập Nhật Thông Tin Sân",
                "➕ 🗑️ Thêm Mới & Xóa Sân Bóng",
                "⚙️ Khôi Phục Dữ Liệu Gốc",
            ]
        )

        #tab1:update field info
        with tab_edit:
            if all_fields:
                col_select, col_form = st.columns([1, 1.8], gap="large")

                with col_select:
                    st.markdown("##### 🎯 Chọn sân cần chỉnh sửa")
                    code_list = [f.field_id for f in all_fields]
                    fields_map = {f.field_id: f for f in all_fields}

                    selected_code = st.selectbox(
                        "Mã sân bóng:",
                        options=code_list,
                        format_func=lambda code: f"{code} — {fields_map[code].name} ({fields_map[code].status})",
                        key="sb_edit_sel",
                    )
                    target = fields_map.get(selected_code)

                    if target:
                        st.markdown(
                            f"""
                            <div class="field-card" style="background-color: #f8fafc; margin-top: 12px;">
                                <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">ĐANG CHỌN SÂN</div>
                                <div class="field-card-header">
                                    <span class="field-title">{target.name}</span>
                                    <span class="field-code">{target.field_id}</span>
                                </div>
                                <div style="margin: 8px 0;">{_get_status_badge(target.status)}</div>
                                <div class="field-price">{target.price_per_hour:,.0f} đ / giờ</div>
                                <div class="field-meta">Loại sân: <strong>{target.field_type}</strong></div>
                                <div class="field-meta">Cập nhật: {target.updated_at}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                with col_form:
                    if target:
                        st.markdown(f"##### 📝 Thông tin cập nhật cho sân `{target.field_id}`")
                        with st.form("form_edit_field_edgecase"):
                            f_col1, f_col2 = st.columns(2)
                            with f_col1:
                                e_name = st.text_input("Tên sân bóng*", value=target.name)
                                e_price = st.number_input(
                                    "Giá thuê/giờ (VNĐ)*",
                                    min_value=0,
                                    step=50000,
                                    value=int(target.price_per_hour),
                                )
                            with f_col2:
                                type_list = [t.value for t in FieldType]
                                e_type = st.selectbox(
                                    "Loại sân*",
                                    options=type_list,
                                    index=type_list.index(target.field_type)
                                    if target.field_type in type_list
                                    else 0,
                                )
                                status_list = [s.value for s in FieldStatus]
                                e_status = st.selectbox(
                                    "Trạng thái hiện tại*",
                                    options=status_list,
                                    index=status_list.index(target.status)
                                    if target.status in status_list
                                    else 0,
                                )

                            st.write("")
                            if st.form_submit_button(
                                "💾 Lưu Thay Đổi Cập Nhật",
                                type="primary",
                                use_container_width=True,
                            ):
                                ok, msg = service.update(
                                    selected_code, e_name, e_type, e_price, e_status
                                )
                                if ok:
                                    st.session_state["field_tab_feedback"] = (
                                        "success",
                                        msg,
                                    )
                                    st.rerun()
                                else:
                                    st.error(msg)
            else:
                st.info("Hiện không có sân bóng nào để cập nhật.")

        #tab2:add or delete field
        with tab_combined:
            col_add, col_del = st.columns([1.3, 1], gap="large")

            with col_add:
                with st.container(border=True):
                    st.markdown("##### ➕ Thêm Sân Bóng Mới")
                    with st.form("form_add_combined", clear_on_submit=True):
                        a_col1, a_col2 = st.columns(2)
                        with a_col1:
                            f_code = st.text_input(
                                "Mã Sân (VD: S05)*", placeholder="Nhập mã viết hoa..."
                            )
                            f_type = st.selectbox(
                                "Loại Sân*", options=[t.value for t in FieldType]
                            )
                        with a_col2:
                            f_name = st.text_input(
                                "Tên Sân Bóng*", placeholder="VD: Sân 5C..."
                            )
                            f_status = st.selectbox(
                                "Trạng Thái Ban Đầu",
                                options=[s.value for s in FieldStatus],
                            )

                        f_price = st.number_input(
                            "Giá Thuê/Giờ (VNĐ)*",
                            min_value=0,
                            step=50000,
                            value=200000,
                        )

                        if st.form_submit_button(
                            "➕ Thêm Sân Mới Vào Hệ Thống",
                            type="primary",
                            use_container_width=True,
                        ):
                            ok, msg = service.add(
                                f_code, f_name, f_type, f_price, f_status
                            )
                            if ok:
                                st.session_state["field_tab_feedback"] = (
                                    "success",
                                    msg,
                                )
                                st.rerun()
                            else:
                                st.error(msg)

            with col_del:
                with st.container(border=True):
                    st.markdown("##### 🗑️ Xóa Sân Bóng")
                    st.caption(
                        "Lưu ý: Không thể xóa sân đang có khách đá hoặc còn đơn đặt sân chưa hủy."
                    )
                    if all_fields:
                        fields_map = {f.field_id: f for f in all_fields}
                        del_code = st.selectbox(
                            "Chọn sân cần xóa:",
                            options=list(fields_map.keys()),
                            format_func=lambda c: f"{c} — {fields_map[c].name} [{fields_map[c].status}]",
                            key="sb_del_combined",
                        )
                        del_target = fields_map[del_code]
                        st.info(
                            f"Sân đang chọn: **{del_target.name}** ({del_target.field_type}) — "
                            f"Giá: **{del_target.price_per_hour:,.0f} đ/h**"
                        )
                        if st.button(
                            "🗑️ Xác Nhận Xóa Sân Này",
                            type="primary",
                            use_container_width=True,
                        ):
                            ok, msg = service.delete(del_code)
                            if ok:
                                st.session_state["field_tab_feedback"] = (
                                    "success",
                                    msg,
                                )
                                st.rerun()
                            else:
                                st.warning(msg)
                    else:
                        st.info("Danh sách sân hiện đang rỗng.")

        #tab3:reset to default fields
        with tab_reset:
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                st.markdown("##### ⚙️ Khôi phục dữ liệu sân mặc định")
                st.caption(
                    "Thao tác này sẽ đưa danh sách sân bóng về 4 sân mặc định ban đầu (S01, S02, S03, S04)."
                )
            with col_r2:
                st.write("")
                if st.button(
                    "🔄 Khôi Phục Dữ Liệu Mẫu",
                    type="secondary",
                    use_container_width=True,
                ):
                    ok, msg = service.reset_to_default()
                    if ok:
                        st.session_state["field_tab_feedback"] = ("success", msg)
                        st.rerun()
                    else:
                        st.error(msg)


if __name__ == "__main__":
    main()