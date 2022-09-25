from dataclasses import dataclass


@dataclass
class User:
    name: str
    id: str
    followers: int
    icon_url: str
    uri: str
