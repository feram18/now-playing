import time

from api.data import Data
from constants import SLOW_REFRESH_RATE, SPOTIFY_CODE_URL
from model.user import User
from renderer.renderer import Renderer
from utils import align_text, Position, Color, load_image_url, get_background_color, is_background_light, rgb_to_hex, \
    align_image


class Profile(Renderer):
    def __init__(self, matrix, canvas, draw, layout, data):
        super().__init__(matrix, canvas, draw, layout)
        self.data: Data = data
        self.coords: dict = self.layout.coords['user']
        self.user: User = self.data.user

    def render(self):
        self.render_background()
        self.render_name()
        self.render_code()
        self.matrix.SetImage(self.canvas)

        while not self.data.is_playing:
            time.sleep(SLOW_REFRESH_RATE)
            self.data.update()

    def render_background(self):
        self.draw.rectangle(((0, 0), (self.matrix.width, self.matrix.height)), Color.BLACK)

    def render_name(self):
        x, y = align_text(self.font.getsize(self.user.name),
                          self.matrix.width, self.matrix.height,
                          Position[self.coords['name']['position']['x'].upper()],
                          Position[self.coords['name']['position']['y'].upper()])
        xo = self.coords['name']['offset']['x']
        yo = self.coords['name']['offset']['y']
        self.draw.text((x + xo, y + yo), self.user.name, Color.WHITE, self.font)

    def render_code(self):
        icon = load_image_url(self.user.icon_url, (64, 64))
        bg_color = get_background_color(icon)
        color = 'black' if is_background_light(bg_color) else 'white'

        url = SPOTIFY_CODE_URL.format(rgb_to_hex(bg_color), color, self.user.uri)
        width = self.coords['code']['size']['width']
        height = self.coords['code']['size']['height']
        code = load_image_url(url, (width, height))

        x, y = align_image(code,
                           self.matrix.width,
                           self.matrix.height,
                           Position[self.coords['code']['position']['x'].upper()],
                           Position[self.coords['code']['position']['y'].upper()])
        xo = self.coords['code']['offset']['x']
        yo = self.coords['code']['offset']['y']
        self.canvas.paste(code, (x + xo, y + yo))
