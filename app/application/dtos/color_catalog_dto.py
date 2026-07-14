from dataclasses import dataclass


@dataclass
class UpdateColorNameDTO:
    name: str | None
