from dataclasses import dataclass


@dataclass
class CreatePaletteDTO:
    name: str
    description: str | None = None
    is_public: bool = True


@dataclass
class UpdatePaletteDTO:
    name: str
    description: str | None = None
    is_public: bool = True


@dataclass
class ForkPaletteDTO:
    name: str | None = None
