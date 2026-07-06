from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ColorCatalogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hex_code: str
    hue: int
    saturation: int
    lightness: int
    luminance: Decimal
    usage_count: int
    created_at: datetime | None
