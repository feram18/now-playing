import logging
import time

from PIL import Image

from api.data import Data
from constants import RAPID_REFRESH_RATE
from model.track import Track
from renderer.renderer import Renderer
from utils import Color, load_image_url, off_screen, get_background_color, is_background_light, Position, align_image, \
    multiline_text


class NowPlaying(Renderer):
    """
    Now Playing Renderer

    Arguments:
        data (api.Data):                Data instance

    Attributes:
        track (model.Track):            Track instance
        coords (dict):                  Coordinates dictionary
        album_art (PIL.Image):          Album art image
        background (tuple):             Background color
        primary_color (tuple):          Primary text color
        secondary_color (tuple):        Secondary text color
        refresh (bool):                 Bool to indicate if canvas needs to refresh
    """
    def __init__(self, matrix, canvas, draw, layout, data):
        super().__init__(matrix, canvas, draw, layout)
        self.data: Data = data
        self.track: Track = self.data.track
        self.coords: dict = self.layout.coords['now_playing']
        self.album_art: Image = None
        self.background: tuple = Color.BLACK
        self.primary_color: tuple = Color.WHITE
        self.secondary_color: tuple = Color.GRAY
        self.refresh: bool = True

    def render(self):
        while self.data.is_playing:
            if self.refresh:
                self.setup()
                self.render_background()
                self.render_album_art()
                self.render_title()
                self.render_artist()
                self.matrix.SetImage(self.canvas)
            time.sleep(RAPID_REFRESH_RATE)
            self.refresh = self.data.update()
        self.scrolling = False

    def render_background(self):
        self.draw.rectangle(((0, 0), (self.matrix.width, self.matrix.height)), self.background)

    def render_album_art(self):
        x, y = align_image(self.album_art,
                           self.matrix.width,
                           self.matrix.height,
                           Position[self.coords['album_art']['position']['x'].upper()],
                           Position[self.coords['album_art']['position']['y'].upper()])
        xo = self.coords['album_art']['offset']['x']
        yo = self.coords['album_art']['offset']['y']
        self.canvas.paste(self.album_art, (x + xo, y + yo))

    def render_title(self):
        x = self.coords['title']['x']
        y = self.coords['title']['y']
        text_off_screen = off_screen((self.matrix.width - x), self.font.getsize(self.track.name)[0])
        if text_off_screen:
            self.scrolling = True
            self.scroll_text(self.track.name, self.primary_color, self.background, (x, y))
        else:
            self.draw.text((x, y), self.track.name, self.primary_color, self.font)

    def render_artist(self):
        x = self.coords['artist']['position']['x']
        y = self.coords['artist']['position']['y']
        artist = self.track.artist
        text_off_screen = off_screen((self.matrix.width - x),
                                     self.font.getsize(self.track.artist)[0])
        if text_off_screen:
            artist = multiline_text(artist, ((self.matrix.width - x - 2) // self.font.getsize('0')[0]))
        self.draw.text((x, y), artist, self.secondary_color, self.font, spacing=self.coords['artist']['line_spacing'])

    def setup(self):
        self.track = self.data.track
        self.scrolling = False
        time.sleep(2.5)
        self.album_art = load_image_url(self.track.album_art_url,
                                        (self.coords['album_art']['size']['width'],
                                         self.coords['album_art']['size']['height']))
        self.background = get_background_color(self.album_art)

        if is_background_light(self.background):
            self.primary_color = Color.DARK_PRIMARY
            self.secondary_color = Color.DARK_SECONDARY
        else:
            self.primary_color = Color.LIGHT_PRIMARY
            self.secondary_color = Color.LIGHT_SECONDARY

        logging.info(f'Now Playing: {self.track}')
