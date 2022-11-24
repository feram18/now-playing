import logging
import time
from dataclasses import dataclass, field

from spotipy import Spotify

from constants import RAPID_REFRESH_RATE, SLOW_REFRESH_RATE
from model.track import Track
from model.user import User


@dataclass
class Data:
    sp: Spotify
    user: User = field(init=False)
    is_playing: bool = False
    track: Track = None
    prev_track: Track = None
    last_updated: float = None
    refresh_rate: int = RAPID_REFRESH_RATE  # change based on activity
    new_data: bool = False
    timeout: bool = False

    def __post_init__(self):
        logging.debug('Initializing data...')
        self.user = self.get_user()
        self.new_data = self.update(True)  # force to initialize

    def update(self, force: bool = False) -> bool:
        """
        Update data attributes
        :param force: (bool) force update
        :return: bool to indicate if new data was fetched
        """
        if force or self.needs_update():
            self.last_updated = time.time()
            logging.debug('Checking for new data...')

            data = self.sp.currently_playing()

            try:
                self.is_playing = bool(data['is_playing'])
                self.prev_track = self.track
                self.now_playing(data['item'])
                if self.prev_track:
                    return self.prev_track.id != self.track.id  # new data
            except TypeError:
                self.is_playing = False
                logging.warning('Stopped playback')
            self.refresh_rate = RAPID_REFRESH_RATE if self.is_playing else SLOW_REFRESH_RATE
            return True  # just initialized
        return False  # no new data

    def get_user(self) -> User:
        """
        Get user profile information
        :return: User instance
        """
        me = self.sp.me()
        return User(me['display_name'],
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
