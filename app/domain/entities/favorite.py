from dataclasses import dataclass
from datetime import datetime


@dataclass
class Favorite:
    user_id: int
    palette_id: int
    created_at: datetime | None
