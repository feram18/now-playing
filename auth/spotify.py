import configparser

from spotipy import Spotify, SpotifyOAuth

from constants import CONFIG_FILE

config = configparser.ConfigParser()
config.read(CONFIG_FILE)
config = config['spotify']

CLIENT_ID = config.get('client_id')
CLIENT_SECRET = config.get('client_secret')
REDIRECT_URI = config.get('redirect_uri')
SCOPES = [
    'user-read-currently-playing',
    'user-read-private'
]


def oauth() -> Spotify:
    """
    Create Spotify instance with Spotify's OAuth manager.
    :return: Spotify instance
    """
    return Spotify(oauth_manager=SpotifyOAuth(client_id=config.get('client_id'),
                                              client_secret=config.get('client_secret'),
                                              redirect_uri=config.get('redirect_uri'),
                                              scope=','.join(SCOPES),
                                              open_browser=False))
