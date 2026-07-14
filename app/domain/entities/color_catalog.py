from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class ColorCatalog:
    hex_code: str
    hue: int
    saturation: int
    lightness: int
    luminance: Decimal
    usage_count: int
    created_at: datetime | None
    name: str | None = None
