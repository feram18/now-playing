import argparse
import json
import logging
import math
import os
from enum import Enum, auto
from io import BytesIO
from typing import Tuple

import numpy as np
import requests
from PIL import ImageFont, Image
from rgbmatrix import RGBMatrixOptions
from sklearn.cluster import KMeans


class Color:
    """Colors utility class (RGBA)"""
    RED = (171, 0, 3, 255)
    ORANGE = (128, 128, 128, 255)
    YELLOW = (239, 178, 30, 255)
    GREEN = (124, 252, 0, 255)
    BLUE = (0, 45, 114, 255)
    PURPLE = (170, 40, 203, 255)
    PINK = (255, 143, 255, 255)
    BROWN = (65, 29, 0, 255)
    GRAY = (112, 128, 144, 255)
    LIGHT_GRAY = (200, 200, 200, 255)
    BLACK = (0, 0, 0, 255)
    WHITE = (255, 255, 255, 255)

    DARK_PRIMARY = (21, 21, 21, 255)
    DARK_SECONDARY = (88, 88, 88, 255)
    LIGHT_PRIMARY = (250, 250, 250, 255)
    LIGHT_SECONDARY = (93, 93, 93, 255)


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


class Position(Enum):
    LEFT = auto()
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    CENTER = auto()


def read_json(filename: str) -> dict:
    """
    Read from JSON file and return it as a dictionary
    :param filename: (str) JSON file
    :return: json: (dict) JSON file as a dict
    """
    if os.path.isfile(filename):
        with open(filename, 'r') as json_file:
            logging.debug(f'Reading JSON file at {filename}')
            return json.load(json_file)
    logging.error(f"Couldn't find file at {filename}")


def load_font(filename: str) -> ImageFont:
    """
    Return ImageFont object from given path.
    :param filename: (str) Location of font file
    :return: font: (PIL.ImageFont) ImageFont object
    """
    if os.path.isfile(filename):
        return ImageFont.load(filename)
    logging.error(f"Couldn't find font {filename}")


def off_screen(canvas_width: int, text_size: int) -> bool:
    """
    Determines if text will go off-screen
    :param canvas_width: (int) Canvas width
    :param text_size: (int) Text size in pixels
    :return: off-screen: (bool)
    """
    return text_size > canvas_width


def load_image(filename: str,
               size: Tuple[int, int],
               background: tuple = Color.BLACK) -> Image:
    """
    Load Image file from local file's path
    :param filename: (str) Path to the image file
    :param size: (int, int) Image's maximum width and height
    :param background: (Color) Background color for PNG images
    :return: image: (PIL.Image) Image file
    """
    if os.path.isfile(filename):
        with Image.open(filename) as original:
            if '.png' in filename:
                original = original.crop(original.getbbox())  # Non-empty pixels
                image = Image.new('RGB',  # Background img
                                  original.size,
                                  background)
                image.paste(original)  # Paste original on background
                image.thumbnail(size)  # Resize
                return image
            else:  # Non-transparent images
                original.thumbnail(size)
                return original.convert('RGB')
    logging.error(f"Couldn't find image {filename}")


def load_image_url(url: str, size: Tuple[int, int]) -> Image:
    """
    Load Image file from URL
    :param url: (str) URL to image
    :param size: (int, int) Image's maximum width and height
    :return: image: (PIL.Image) Image file
    """
    response = requests.get(url)
    if response.ok:
        with Image.open(BytesIO(response.content)) as img:
            img.thumbnail(size)
            return img.convert('RGB')
    logging.error(f'Could not get image at {url}')


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert RGB to HEX
    :param rgb: (tuple) RGB value
    :return: (str) HEX value
    """
    return '%02x%02x%02x' % rgb


def get_background_color(img: Image) -> tuple:
    """
    Get best matching background color based on album cover

    Adapted from https://github.com/davidkrantz/Colorfy
    :param img: (PIL.Image) Album cover image
    :return: (tuple) RGB values
    """
    img = np.asarray(img.resize((100, 100), Image.BILINEAR))
    img = img.reshape((img.shape[0] * img.shape[1], 3))

    clt = KMeans(n_clusters=8)
    clt.fit(img)
    centroids = clt.cluster_centers_

    cf = [colorfulness(color[0], color[1], color[2]) for color in centroids]
    max_colorful = np.max(cf)
    rgb = centroids[np.argmax(cf)]

    if max_colorful < 10:  # Colorfulness tolerance
        return Color.LIGHT_GRAY  # Not colorful enough
    return tuple(int(math.ceil(value)) for value in rgb)


def colorfulness(r: int, g: int, b: int) -> float:
    """
    Returns a colorfulness index of given RGB combination.
    Implementation of the colorfulness metric proposed by Hasler and Süsstrunk (2003)
    in https://infoscience.epfl.ch/record/33994/files/HaslerS03.pdf.

    Adapted from https://github.com/davidkrantz/Colorfy
    :param r: (int) RED value
    :param g: (int) GREEN value
    :param b: (int) BLUE value
    :return: (float) colorfulness metric
    """
    rg = np.absolute(r - g)
    yb = np.absolute(0.5 * (r + g) - b)

    # Compute the mean and standard deviation of both `rg` and `yb`
    rg_mean, rg_std = (np.mean(rg), np.std(rg))
    yb_mean, yb_std = (np.mean(yb), np.std(yb))

    # Combine the mean and standard deviations
    std_root = np.sqrt((rg_std ** 2) + (yb_std ** 2))
    mean_root = np.sqrt((rg_mean ** 2) + (yb_mean ** 2))
    return std_root + (0.3 * mean_root)


def is_background_light(bg_color: tuple) -> bool:
    """
    Determine if the background color is light or dark, based on luminance
    :param bg_color: (tuple) background color RGB values
    :return: bool to indicate if background color is light
    """
    return ((bg_color[0] * 0.299) + (bg_color[1] * 0.587) + (bg_color[2] * 0.114)) / 255 > 0.5


def multiline_text(text: str, max_len: int) -> str:
    """
    Split a string of text into multiple lines based on a max character length value.
    :param text: (str) text to split
    :param max_len: (int) maximum line length
    :return: (str) multi-lined string
    """
    words = iter(text.split())
    lines, current = '', next(words)
    for word in words:
        if len(current) + 1 + len(word) > max_len:  # add new line
            lines += current + '\n'
            current = word
        else:  # add to current line
            current += " " + word
    lines += current  # add last line
    return lines


def align_text(text_size: Tuple[int, int],
               col_width: int = 0, col_height: int = 0,
               x: Position = Position.CENTER, y: Position = Position.CENTER) -> (int, int):
    """
    Calculate x, y coords to align text on canvas
    :param text_size:
    :param x: Text's horizontal position
    :param y: Text's vertical position
    :param col_width: Column's width
    :param col_height: Column's height
    :return: x, y: Coordinates
    """

    # x: horizontal position
    if x == Position.RIGHT:
        x = col_width - text_size[0]
    elif x == Position.CENTER:
        x = abs(col_width//2 - text_size[0]//2)
    elif x == Position.LEFT:
        x = 0

    # y: vertical position
    if y == Position.CENTER:
        y = abs(col_height//2 - text_size[1]//2)
    elif y == Position.BOTTOM:
        y = col_height - text_size[1]
    elif y == Position.TOP:
        y = 0

    return x, y


def align_image(image: Image,
                col_width: int = 0, col_height: int = 0,
                x: Position = Position.CENTER, y: Position = Position.CENTER) -> (int, int):
    """
    Calculate the x, y offsets to align image on canvas
    :param image: Image to align
    :param x: Image horizontal position
    :param y: Image vertical position
    :param col_width: Column's width
    :param col_height: Column's height
    :return: x, y: Coordinate offsets
    """

    if x == Position.RIGHT:
        x = col_width - image.width
    elif x == Position.CENTER:
        x = abs(col_width//2 - image.width//2)
    elif x == Position.LEFT:
        x = 0

    if y == Position.CENTER:
        y = abs(col_height//2 - image.height//2)
    elif y == Position.BOTTOM:
        y = col_height - image.height
    elif y == Position.TOP:
        y = 0

    return x, y


def args() -> argparse.Namespace:
    """
    CLI argument parser to configure matrix.
    :return: arguments: (argsparse.Namespace) Argument parser
    """
    parser = argparse.ArgumentParser(prog='Now-Playing')

    parser.add_argument('--led-rows',
                        action='store',
                        help='Display rows. 16 for 16x32, 32 for 32x64, etc. (Default: 32)',
                        type=int,
                        default=32)
    parser.add_argument('--led-cols',
                        action='store',
                        help='Display columns. 32 for 16x32, 64 for 32x62, etc. (Default: 64)',
                        type=int,
                        default=64)
    parser.add_argument('--led-multiplexing',
                        action='store',
                        help='Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; '
                             '5 = ZnMirrorZStripe; 6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)',
                        type=int,
                        choices=range(9),
                        default=0)
    parser.add_argument('--led-row-addr-type',
                        action='store',
                        help='Addressing of rows: 0 = default; 1 = AB-addressed panels; 2 = direct row select; '
                             '3 = ABC-addressed panels. (Default: 0)',
                        type=int,
                        choices=range(4),
                        default=0)
    parser.add_argument('--led-panel-type',
                        action='store',
                        help='Chipset of the panel. Supported panel types: FM6126A; FM6127.',
                        type=str,
                        choices=['FM6126A', 'FM6127'],
                        default='')
    parser.add_argument('--led-gpio-mapping',
                        help='Name of GPIO mapping used: regular, adafruit-hat, adafruit-hat-pwm, compute-module',
                        type=str,
                        choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm', 'compute-module'],
                        default='regular')
    parser.add_argument('--led-slowdown-gpio',
                        action='store',
                        help="Slow down writing to GPIO. Needed for faster Pi's and/or slower panels. Range: 0..4. "
                             '(Default: 1)',
                        type=int,
                        choices=range(5),
                        default=1)
    parser.add_argument('--led-chain',
                        action='store',
                        help='Number of daisy-chained boards. (Default: 1)',
                        type=int,
                        default=1)
    parser.add_argument('--led-parallel',
                        action='store',
                        help='For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)',
                        type=int,
                        default=1)
    parser.add_argument('--led-pixel-mapper',
                        action='store',
                        help='Apply pixel mappers: '
                             'Mirror (Horizontal) = \"Mirror:H\"; '
                             'Mirror (Vertical) = \"Mirror:V\"; '
                             'Rotate (Degrees) = eg. \"Rotate: 90\"; '
                             'U-Mapper = \"U-mapper\"',
                        type=str,
                        default='')
    parser.add_argument('--led-brightness',
                        action='store',
                        help='Brightness level. Range: 1..100. (Default: 100)',
                        type=int,
                        choices=range(101),
                        default=100)
    parser.add_argument('--led-pwm-bits',
                        action='store',
                        help='Bits used for PWM. Range 1..11. (Default: 11)',
                        type=int,
                        choices=range(12),
                        default=11)
    parser.add_argument('--led-show-refresh',
                        action='store_true',
                        help='Shows the current refresh rate of the LED panel.')
    parser.add_argument('--led-limit-refresh',
                        action='store',
                        help='Limit refresh rate to this frequency in Hz. Useful to keep a constant refresh rate on '
                             'loaded system. 0=no limit. (Default: 0)',
                        type=int,
                        default=0)
    parser.add_argument('--led-scan-mode',
                        action='store',
                        help='Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)',
                        type=int,
                        choices=range(2),
                        default=1)
    parser.add_argument('--led-pwm-lsb-nanoseconds',
                        action='store',
                        help='Base time-unit for the on-time in the lowest significant bit in nanoseconds. '
                             '(Default: 130)',
                        type=int,
                        default=130)
    parser.add_argument('--led-pwm-dither-bits',
                        action='store',
                        help='Time dithering of lower bits (Default: 0)',
                        type=int,
                        default=0)
    parser.add_argument('--led-no-hardware-pulse',
                        action='store',
                        help="Don't use hardware pin-pulse generation.")
    parser.add_argument('--led-inverse',
                        action='store',
                        help='Switch if your matrix has inverse colors on.')
    parser.add_argument('--led-rgb-sequence',
                        action='store',
                        help='Switch if your matrix has led colors swapped. (Default: RGB)',
                        type=str,
                        default='RGB')

    return parser.parse_args()


def led_matrix_options(args_: argparse.Namespace) -> RGBMatrixOptions:
    """
    Set RGBMatrixOptions from parsed arguments.
    :param args_: (argsparse.Namespace) Parsed arguments from CLI
    :return: options: (rgbmatrix.RGBMatrixOptions) RGBMatrixOptions instance
    :exception AttributeError: If attribute is not found
    """
    options = RGBMatrixOptions()

    options.rows = args_.led_rows
    options.cols = args_.led_cols
    options.multiplexing = args_.led_multiplexing
    options.row_address_type = args_.led_row_addr_type

    if args_.led_panel_type is not None:
        options.panel_type = args_.led_panel_type

    if args_.led_gpio_mapping is not None:
        options.hardware_mapping = args_.led_gpio_mapping

    if args_.led_slowdown_gpio is not None:
        options.gpio_slowdown = args_.led_slowdown_gpio

    options.chain_length = args_.led_chain
    options.parallel = args_.led_parallel
    options.pixel_mapper_config = args_.led_pixel_mapper
    options.brightness = args_.led_brightness
    options.pwm_bits = args_.led_pwm_bits

    if args_.led_show_refresh:
        options.show_refresh_rate = 1

    options.limit_refresh_rate_hz = args_.led_limit_refresh
    options.scan_mode = args_.led_scan_mode
    options.pwm_lsb_nanoseconds = args_.led_pwm_lsb_nanoseconds
    options.pwm_dither_bits = args_.led_pwm_dither_bits

    if args_.led_no_hardware_pulse:
        options.disable_hardware_pulsing = True

    if args_.led_inverse:
        options.inverse_colors = args_.led_inverse

    options.led_rgb_sequence = args_.led_rgb_sequence

    return options
