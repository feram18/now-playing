from dataclasses import dataclass, field

from PIL.ImageFont import FreeTypeFont

from constants import LAYOUT_FILE
from utils import read_json, load_font


@dataclass
class Layout:
    """Matrix Layout class"""
    width: int
    height: int
    json: dict = field(init=False)
    coords: dict = field(init=False)
    primary_font: FreeTypeFont = field(init=False)
    secondary_font: FreeTypeFont = field(init=False)

    def __post_init__(self):
        self.json = read_json(LAYOUT_FILE.format(self.width, self.height))
        self.coords = self.json['coords']
        self.primary_font = load_font(self.json['fonts']['primary']['path'],
                                      self.json['fonts']['primary']['size'])
        self.secondary_font = load_font(self.json['fonts']['secondary']['path'],
                                        self.json['fonts']['secondary']['size'])
