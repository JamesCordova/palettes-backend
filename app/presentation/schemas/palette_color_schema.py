from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import HEX_CODE_PATTERN


class PaletteColorCreate(BaseModel):
    hex_code: str = Field(pattern=HEX_CODE_PATTERN)
    hue: int = Field(ge=0, le=360)
    saturation: int = Field(ge=0, le=100)
    lightness: int = Field(ge=0, le=100)
    luminance: float = Field(ge=0, le=255)
    position: int | None = None


class PaletteColorUpdate(BaseModel):
    hex_code: str = Field(pattern=HEX_CODE_PATTERN)


class ReorderPaletteColorsRequest(BaseModel):
    ordered_ids: list[int]


class PaletteColorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    palette_id: int
    hex_code: str
    name: str | None
    position: int
