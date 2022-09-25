import logging
import time
from dataclasses import dataclass, field

from spotipy import Spotify

from auth import spotify
from model.track import Track
from model.user import User

RAPID_REFRESH_RATE = 10  # seconds
SLOW_REFRESH_RATE = 60  # seconds


@dataclass
class Data:
    """
    Data class to fetch Spotify data

    Attributes:
        sp (spotipy.Spotify):           Spotify instance
        user (model.User):              User instance
        is_playing (bool):              Bool to indicate if user is currently active
        track (model.Track):            Track currently playing
        prev_track (model.Track):       Previously played track
        last_updated (float):           Time data was last updated
        refresh_rate (int):             Data refresh rate (in seconds)
        new_data (bool):                Bool to indicate if new data was fetched
    """
    def __init__(self):
        self.sp: Spotify = Spotify(auth_manager=spotify.oauth())
        self.user: User = field(init=False)
        self.is_playing: bool = field(init=False)
        self.track: Track = None
        self.prev_track: Track = None
        self.last_updated: float = field(init=False)
        self.refresh_rate: int = RAPID_REFRESH_RATE  # change based on activity
        self.new_data: bool = self.update(True)  # force to initialize

    def update(self, force: bool = False) -> bool:
        """
        Update data attributes
        :param force: (bool) force update
        :return: bool to indicate if new data was fetched
        """
        if force or self.needs_update():
            logging.debug('Checking for new data...')

            self.get_user()
            data = self.sp.currently_playing()

            try:
                self.is_playing = bool(data['is_playing'])
                self.prev_track = self.track
                self.now_playing(data['item'])
                if self.prev_track:
                    return self.prev_track.id != self.track.id  # new data
            except TypeError:
                self.is_playing = False
                logging.warning('User currently not playing')
            self.refresh_rate = RAPID_REFRESH_RATE if self.is_playing else SLOW_REFRESH_RATE
            self.last_updated = time.time()
            return True  # just initialized
        return False  # no new data

    def get_user(self):
        """
        Get user profile information
        """
        me = self.sp.me()
        self.user = User(me['display_name'],
                         me['id'],
                         me['followers']['total'],
                         me['images'][0]['url'],
                         me['uri'])

    def now_playing(self, track: dict):
        """
        Get user's currently playing track
        :param track: (dict) data dictionary
        """
        self.track = Track(track['id'],
                           track['name'],
                           track['album']['artists'][0]['name'],
                           track['album']['name'],
                           track['album']['images'][0]['url'],
                           track['duration_ms'],
                           track['uri'])

    def needs_update(self) -> bool:
        """
        Determine if update is needed i.e. 20s have passed since last update
        :return: bool to indicate if update is needed
        """
        time_delta = time.time() - self.last_updated
        return time_delta >= self.refresh_rate
