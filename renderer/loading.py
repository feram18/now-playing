from renderer.renderer import Renderer
from utils import Color, load_image, align_text, Position, align_image
from version import __version__


class Loading(Renderer):
    """
    Loading Renderer

    Attributes:
        coords (dict):      Coordinates dictionary
    """
    def __init__(self, matrix, canvas, draw, layout):
        super().__init__(matrix, canvas, draw, layout)
        self.coords: dict = self.layout.coords['loading']
        self.render()

    def render(self):
        self.render_logo()
        self.render_version()
        self.matrix.SetImage(self.canvas)

    def render_version(self):
        x, y = align_text(self.font.getsize(__version__),
                          self.matrix.width,
                          self.matrix.height,
                          Position.CENTER,
                          Position.BOTTOM)
        self.draw.text((x, y), __version__, fill=Color.ORANGE, font=self.font)

    def render_logo(self):
        logo = load_image('assets/img/spotify.png',
                          (self.coords['image']['size']['width'],
                           self.coords['image']['size']['height']))
        x, y = align_image(logo,
                           self.matrix.width,
                           self.matrix.height)
        self.canvas.paste(logo, (x, y))
