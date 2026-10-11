# Cách khởi tạo môi trường ảo trên terminal
python -m venv venv
# Cách kích hoạt môi trường ảo 
.venv\Scripts\Activate.ps1
# code mẫu truy vấn database
from Database import get_db_connection, init_db
def get_all_fields():
    with get_db_connection as conn:
        c=conn.cursor()
        c.execute("select * from fields")
        return [dict(row) for row in c.fetchall()]#trả về 1 list gồm các dict trong đó dict bao gồm key là tên cột value là giá trị
# Xây dựng logic nghiệp vụ ta viết vào folder core 
# xây dựng giao diện ta viết vào folder components
# dùng trực tiếp các class trong models
