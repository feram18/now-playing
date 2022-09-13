import configparser
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser()
config.read('app.ini')
config = config['spotify']

CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
REDIRECT_URI = config['redirect_uri']
SCOPE = 'user-read-currently-playing'


def oauth() -> SpotifyOAuth:
    """
    Authorization Code Flow for Spotify's OAuth implementation
    :return: SpotifyOAuth
    """
    return SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE,
                        open_browser=False)
