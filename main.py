import logging

from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix

from utils import led_matrix_options, args
from version import __version__


def main():
    print(f'\U0001F3B5 Now-Playing - v{__version__} ({matrix.width}x{matrix.height})')


if __name__ == '__main__':
    matrix = RGBMatrix(options=led_matrix_options(args()))
    canvas = Image.new('RGB', (matrix.width, matrix.height))
    draw = ImageDraw.Draw(canvas)

    try:
        main()
    except Exception as e:
        logging.exception(SystemExit(e))
    finally:
        matrix.Clear()
