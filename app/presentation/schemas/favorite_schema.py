from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    palette_id: int
    created_at: datetime | None
