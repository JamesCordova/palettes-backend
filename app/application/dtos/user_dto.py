from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    username: str
    email: str
    password: str
    avatar_url: str | None = None


@dataclass
class UpdateUserDTO:
    username: str
    email: str
    avatar_url: str | None = None
