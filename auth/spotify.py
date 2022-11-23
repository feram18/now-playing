import configparser
import logging
import sys

from spotipy.oauth2 import SpotifyOauthError, SpotifyPKCE

config = configparser.ConfigParser()
config.read('app.ini')
config = config['spotify']

CLIENT_ID = config.get('client_id')
CLIENT_SECRET = config.get('client_secret')
REDIRECT_URI = config.get('redirect_uri')
SCOPES = [
    'user-read-currently-playing',
    'user-read-private'
]


def valid() -> bool:
    """
    Verifies authentication fields were set on config file
    :return: boolean to indicate validity
    """
    if not CLIENT_ID:
        logging.error('Client ID has not been set')
        return False
    if not CLIENT_SECRET:
        logging.error('Client Secret has not been set')
        return False
    if not REDIRECT_URI:
        logging.error('Redirect URI has not been set')
        return False
    return True


def oauth() -> SpotifyPKCE:
    """
    Authorization Code Flow for Spotify's OAuth implementation.
    :return: SpotifyPKCE instance
    """
    if valid():
        try:
            return SpotifyPKCE(client_id=CLIENT_ID,
                               redirect_uri=REDIRECT_URI,
                               scope=','.join(SCOPES),
                               open_browser=False)
        except SpotifyOauthError:
            logging.exception('Authorization could not be completed')
            sys.exit(1)
