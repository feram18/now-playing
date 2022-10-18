import time
from abc import ABC, abstractmethod
from typing import Tuple

import multitasking
from rgbmatrix import RGBMatrix
from PIL import Image, ImageDraw, ImageFont

from config.layout import Layout
from constants import SCROLL_SPEED
from utils import Direction


class Renderer(ABC):
    """
    Base Renderer abstract class

    Arguments:
        matrix (rgbmatrix.RGBMatrix):       RGBMatrix instance
        canvas (PIL.Image):                 Image canvas associated with matrix
        draw (PIL.ImageDraw):               ImageDraw instance
        layout (config.Layout):              Layout instance

    Attributes:
        scrolling (bool):                   Boolean to indicate if text is scrolling
    """

    def __init__(self, matrix, canvas, draw, layout):
        self.matrix: RGBMatrix = matrix
        self.canvas: Image = canvas
        self.draw: ImageDraw = draw
        self.layout: Layout = layout
        self.scrolling: bool = False

    @abstractmethod
    def render(self):
        pass

    @multitasking.task
    def scroll_text(self,
                    text: str,
                    text_color: tuple,
                    font: ImageFont,
                    bg_color: tuple,
                    start_pos: Tuple[int, int]):
        """
        Scroll string of text on canvas
        :param text: (str) text to scroll
        :param text_color: (tuple) text font color
        :param font: (ImageFont) font to render text
        :param bg_color: (tuple) text background color
        :param start_pos: (int) text starting x-position
        """
        end = (self.matrix.width, start_pos[1] + font.getsize(text)[1])
        shortened_text = text
        removed_chars = []
        direction = Direction.LEFT
        new_direction = True

        while self.scrolling is True:
            self.draw.rectangle((start_pos, end), bg_color)
            self.draw.text(start_pos, shortened_text, text_color, font)
            self.matrix.SetImage(self.canvas)

            length = font.getsize(shortened_text)[0] + start_pos[0]

            if length < self.matrix.width:  # Check if end of text is now visible
                direction = Direction.RIGHT
                new_direction = True
            elif shortened_text == text:  # Text is complete again
                direction = Direction.LEFT
                new_direction = True

            if direction is Direction.LEFT:
                removed_chars.append(shortened_text[0])  # Save character to remove
                shortened_text = shortened_text[1:]  # Remove character
            else:
                shortened_text = removed_chars[-1] + shortened_text  # Add last-removed character
                removed_chars.pop()  # Remove from saved characters

            if new_direction:
                time.sleep(2.5)
                new_direction = False
            else:
                time.sleep(SCROLL_SPEED)
