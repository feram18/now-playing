import time
from abc import ABC, abstractmethod
from typing import Tuple

import multitasking
from rgbmatrix import RGBMatrix
from PIL import Image, ImageDraw, ImageFont

from config.layout import Layout
from utils import Color, Direction

SCROLL_SPEED = 0.5


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
        refresh (bool):                     Bool to indicate if canvas is to be refreshed
    """

    def __init__(self, matrix, canvas, draw, layout):
        self.matrix: RGBMatrix = matrix
        self.canvas: Image = canvas
        self.draw: ImageDraw = draw
        self.layout: Layout = layout
        self.font: ImageFont = self.layout.font
        self.refresh: bool = True

    @abstractmethod
    def render(self):
        pass

    @multitasking.task
    def scroll_text(self, text: str, text_color: Color, bg_color: Color, start_pos: Tuple[int, int]):
        self.refresh = False
        short_text = text
        removed_chars = []
        direction = Direction.LEFT
        new_direction = True

        while not self.refresh:
            end = (self.matrix.width, start_pos[1] + self.font.getsize(text)[1])

            self.draw.rectangle((start_pos, end), fill=bg_color)
            self.draw.text(start_pos, short_text, fill=text_color, font=self.font)

            right_end = self.font.getsize(short_text)[0] + start_pos[0]

            if right_end < self.matrix.width:  # Check if end of text is now visible
                direction = Direction.RIGHT
                new_direction = True
            elif short_text == text:  # Text is complete again
                direction = Direction.LEFT
                new_direction = True

            if direction is Direction.LEFT:
                removed_chars.append(short_text[0])  # Save character to remove
                short_text = short_text[1:]  # Remove character
            else:
                short_text = removed_chars[-1] + short_text  # Add last-removed character
                removed_chars.pop()  # Remove from saved characters

            self.matrix.SetImage(self.canvas)

            if new_direction:
                time.sleep(1.5)
                new_direction = False
            else:
                time.sleep(SCROLL_SPEED)
