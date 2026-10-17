from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Base:
    """Lớp cơ sở chứa id và thông tin thời gian khởi tạo / cập nhật"""
    id: int = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
