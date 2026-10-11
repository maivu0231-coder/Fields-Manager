import sqlite3
import os
import sqlite3
import os
from pathlib import Path

# Lấy thư mục chứa chính file db.py này (chính là thư mục Database/)
DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "field_project.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def get_db_connection():
    # Tự động tạo thư mục chứa DB nếu chưa có
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    #fields table
    c.execute("""CREATE TABLE IF NOT EXISTS fields (
        field_id TEXT PRIMARY KEY, 
        name TEXT NOT NULL, 
        field_type TEXT NOT NULL, 
        price_per_hour REAL NOT NULL, 
        status TEXT DEFAULT 'Trống'
    )""")
    
    #bookings table
    c.execute("""CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY, 
        field_id TEXT NOT NULL, 
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL, 
        booking_date TEXT NOT NULL, 
        start_time TEXT NOT NULL, 
        end_time TEXT NOT NULL, 
        deposit REAL DEFAULT 0, 
        status TEXT DEFAULT 'Đã cọc'
    )""")
    
    #payments table
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        invoice_id TEXT PRIMARY KEY, 
        booking_id TEXT NOT NULL UNIQUE, 
        total_amount REAL NOT NULL, 
        payment_time TEXT NOT NULL
    )""")
    

    if c.execute("SELECT COUNT(*) FROM fields").fetchone()[0] == 0:
        c.executemany("INSERT INTO fields VALUES (?,?,?,?,?)", [
            ("S01", "Sân 5A", "Sân 5", 200000, "Trống"), 
            ("S02", "Sân 5B", "Sân 5", 200000, "Trống"),
            ("S03", "Sân 7A", "Sân 7", 350000, "Trống"), 
            ("S04", "Sân 7B", "Sân 7", 350000, "Bảo trì")
        ])
        
        c.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?)", [
            ("B01", "S01", "Nguyen Van A", "0123456789", "2023-10-01", "10:00", "11:00", 100000, "Đã cọc"),
            ("B02", "S02", "Tran Thi B", "0987654321", "2023-10-02", "14:00", "15:30", 150000, "Đã cọc")
        ])
        
        c.executemany("INSERT INTO payments VALUES (?,?,?,?)", [
            ("I01", "B01", 200000, "2023-10-01 10:30:00"), 
            ("I02", "B02", 300000, "2023-10-02 15:00:00")
        ])
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM fields")
    fields = c.fetchall()#list of sqlite3.Row objects
    for field in fields:
        print(dict(field)) #output:{'field_id': 'S01', 'name': 'Sân 5A', 'field_type': 'Sân 5', 'price_per_hour': 200000.0, 'status': 'Trống'}
        
    conn.close()
