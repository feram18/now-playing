import logging
import time

from api.data import Data
from constants import SLOW_REFRESH_RATE, SPOTIFY_CODE_URL, INACTIVITY_TIMEOUT
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
        self.inactivity: float = 0

    def render(self):
        self.inactivity = time.time()
        self.render_background()
        self.render_name()
        self.render_code()
        self.matrix.SetImage(self.canvas)

        while not self.data.is_playing and not self.timeout():
            time.sleep(SLOW_REFRESH_RATE)
            self.data.update()
        self.inactivity = 0

    def render_background(self):
        self.draw.rectangle(((0, 0), (self.matrix.width, self.matrix.height)), Color.BLACK)

    def render_name(self):
        x, y = align_text(self.layout.primary_font.getsize(self.user.name),
                          self.matrix.width, self.matrix.height,
                          Position(self.coords['name']['position']['x']),
                          Position(self.coords['name']['position']['y']))
        x += self.coords['name']['offset']['x']
        y += self.coords['name']['offset']['y']
        self.draw.text((x, y), self.user.name, Color.WHITE, self.layout.primary_font)

    def render_code(self):
        icon = load_image_url(self.user.icon_url, (64, 64))
        bg_color = get_background_color(icon)
        color = 'black' if is_background_light(bg_color) else 'white'

        url = SPOTIFY_CODE_URL.format(rgb_to_hex(bg_color), color, self.user.uri)
        code = load_image_url(url, self.coords['code']['size'])

        x, y = align_image(code,
                           self.matrix.width,
                           self.matrix.height,
                           Position(self.coords['code']['position']['x']),
                           Position(self.coords['code']['position']['y']))
        x += self.coords['code']['offset']['x']
        y += self.coords['code']['offset']['y']
        self.canvas.paste(code, (x, y))

    def timeout(self) -> bool:
        if self.inactivity > 0:
            if time.time() - self.inactivity >= INACTIVITY_TIMEOUT:
                logging.warning('Inactivity timeout')
                self.data.timeout = True
        return self.data.timeout
