import argparse
import json
import logging
import os

from PIL import ImageFont
from rgbmatrix import RGBMatrixOptions


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


def args() -> argparse.Namespace:
    """
    CLI argument parser to configure matrix.
    :return: arguments: (argsparse.Namespace) Argument parser
    """
    parser = argparse.ArgumentParser(prog='LED-Stock-Ticker')

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
