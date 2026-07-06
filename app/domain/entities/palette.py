from dataclasses import dataclass
from datetime import datetime


@dataclass
class Palette:
    id: int | None
    user_id: int
    name: str
    description: str | None
    is_public: bool
    forked_from: int | None
    created_at: datetime | None
    updated_at: datetime | None
