import json
import logging
import os

from PIL import ImageFont


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
