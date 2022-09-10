from dataclasses import dataclass, field

from PIL import ImageFont

from utils import read_json, load_font

LAYOUT_FILE = 'config/w{}h{}.json'


@dataclass
class Layout:
    """Matrix Layout class"""
    width: int
    height: int
    json: dict = field(init=False)
    coords: dict = field(init=False)
    font: ImageFont = field(init=False)

    def __post_init__(self):
        self.json = read_json(LAYOUT_FILE.format(self.width, self.height))
        self.coords = self.json['coords']
        self.font = load_font(self.json['defaults']['font'])
