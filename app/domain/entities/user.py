from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    username: str
    email: str
    password_hash: str
    avatar_url: str | None
    created_at: datetime | None
