from dataclasses import dataclass


@dataclass
class Track:
    id: str
    name: str
    artist: str
    album: str
    album_art_url: str
    explicit: bool
    length: int  # [ms]
