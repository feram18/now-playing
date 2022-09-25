import configparser
import logging

from spotipy.oauth2 import SpotifyOAuth

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


def oauth() -> SpotifyOAuth:
    """
    Authorization Code Flow for Spotify's OAuth implementation.
    Raises a SystemError if authentication variables are not valid
    :return: SpotifyOAuth
    """
    if valid():
        return SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=','.join(SCOPES),
                            open_browser=False)
    raise SystemError('Authorization could not be completed')