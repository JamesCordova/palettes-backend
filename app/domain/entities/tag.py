from dataclasses import dataclass


@dataclass
class Tag:
    id: int | None
    name: str
