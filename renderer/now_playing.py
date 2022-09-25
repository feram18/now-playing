import logging
import time

from PIL import Image

from api.data import Data
from model.track import Track
from renderer.renderer import Renderer
from utils import Color, load_image_url, off_screen, get_background_color, is_background_light, Position, align_image


class NowPlaying(Renderer):
    """
    Now Playing Renderer

    Arguments:
        data (api.Data):                    Data instance

    Attributes:
        track (model.Track):                Track instance
        coords (dict):                      Coordinates dictionary
        album_art (PIL.Image):              Album art image
        background (utils.Color):           Background color
        primary_color (utils.Color):        Primary text color
        secondary_color (utils.Color):      Secondary text color
        refresh (bool):                     Bool to indicate if canvas needs to refresh
    """
    def __init__(self, matrix, canvas, draw, layout, data):
        super().__init__(matrix, canvas, draw, layout)
        self.data: Data = data
        self.track: Track = self.data.track
        self.coords: dict = self.layout.coords['now_playing']
        self.album_art: Image = None
        self.background: Color = Color.BLACK
        self.primary_color: Color = Color.WHITE
        self.secondary_color: Color = Color.GRAY
        self.refresh: bool = True
        self.render()

    def render(self):
        while self.data.is_playing:
            if self.refresh:
                self.setup()
                self.render_background()
                self.render_album_art()
                self.render_title()
                self.render_artist()
                self.matrix.SetImage(self.canvas)
            self.refresh = self.data.update()

    def render_background(self):
        self.draw.rectangle(((0, 0), (self.matrix.width, self.matrix.height)), fill=self.background)

    def render_album_art(self):
        x, y = align_image(self.album_art,
                           self.matrix.width,
                           self.matrix.height,
                           Position[self.coords['album_art']['position']['x'].upper()],
                           Position[self.coords['album_art']['position']['y'].upper()])
        lo, to = self.coords['album_art']['offset']['left'], self.coords['album_art']['offset']['top']
        self.canvas.paste(self.album_art, (x + lo, y + to))

    def render_title(self):
        x, y = self.coords['title']['x'], \
               self.coords['title']['y']
        text_off_screen = off_screen((self.matrix.width - x), self.font.getsize(self.track.name)[0])
        if text_off_screen:
            self.scrolling = True
            self.scroll_text(self.track.name, self.primary_color, self.background, (x, y))
        else:
            self.draw.text((x, y), self.track.name, fill=self.primary_color, font=self.font)

    def render_artist(self):
        x, y = self.coords['artist']['x'], \
               self.coords['artist']['y']
        artist = self.track.artist
        text_off_screen = off_screen((self.matrix.width - x),
                                     self.font.getsize(self.track.artist)[0])
        if text_off_screen:
            # TODO: Smart Split OR Scroll
            artist = '\n'.join(artist.rsplit(' ', 1))
        self.draw.text((x, y), artist, fill=self.secondary_color, font=self.font, spacing=1)

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
