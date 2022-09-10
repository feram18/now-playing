from abc import ABC, abstractmethod
from rgbmatrix import RGBMatrix
from PIL import Image, ImageDraw, ImageFont

from config.layout import Layout


class Renderer(ABC):
    """
    Base Renderer abstract class

    Arguments:
        matrix (rgbmatrix.RGBMatrix):       RGBMatrix instance
        canvas (PIL.Image):                 Image canvas associated with matrix
        draw (PIL.ImageDraw):               ImageDraw instance
        layout (config.Layout):             Layout instance

    Attributes:
        font (PIL.ImageFont):               Default font
    """

    def __init__(self, matrix, canvas, draw, layout):
        self.matrix: RGBMatrix = matrix
        self.canvas: Image = canvas
        self.draw: ImageDraw = draw
        self.layout: Layout = layout
        self.font: ImageFont = self.layout.font

    @abstractmethod
    def render(self):
        pass
