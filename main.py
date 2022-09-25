import logging
import signal
import sys
from logging.handlers import RotatingFileHandler

import multitasking
from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix

from api.data import Data
from config.layout import Layout
from renderer.loading import Loading
from renderer.now_playing import NowPlaying
from utils import led_matrix_options, args
from version import __version__


def main():
    print(f'\U0001F3B5 Now-Playing - v{__version__} ({matrix.width}x{matrix.height})')

    layout = Layout(matrix.width, matrix.height)
    Loading(matrix, canvas, draw, layout)
    data = Data()
    NowPlaying(matrix, canvas, draw, layout, data)


if __name__ == '__main__':
    if '--debug' in sys.argv:
        LOG_LEVEL = logging.DEBUG
        sys.argv.remove('--debug')
    else:
        LOG_LEVEL = logging.INFO

    logger = logging.getLogger('')
    logger.setLevel(LOG_LEVEL)
    handler = RotatingFileHandler(filename='now-playing.log',
                                  maxBytes=5 * 1024 * 1024,  # 5MB
                                  backupCount=4)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                                           datefmt='%m/%d/%Y %I:%M:%S %p'))
    logger.addHandler(handler)

    matrix = RGBMatrix(options=led_matrix_options(args()))
    canvas = Image.new('RGB', (matrix.width, matrix.height))
    draw = ImageDraw.Draw(canvas)
    matrix.SetImage(canvas)

    try:
        main()
    except Exception as e:
        logging.exception(SystemExit(e))
    finally:
        signal.signal(signal.SIGINT, multitasking.killall)
        matrix.Clear()
