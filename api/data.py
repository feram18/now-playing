import time

from spotipy import Spotify

from auth import auth
from model.track import Track
from model.user import User

REFRESH_RATE = 20  # seconds


class Data:
    def __init__(self):
        self.sp: Spotify = Spotify(auth_manager=auth.oauth())
        self.user: User = self.user()
        self.is_playing: bool = False
        self.track: Track = self.now_playing()
        self.last_updated: float = time.time()

    def user(self):
        """
        Get user profile information
        :return: User
        """
        me = self.sp.me()
        return User(me['display_name'],
                    me['id'],
                    me['followers']['total'],
                    me['images'][0]['url'])

    def now_playing(self) -> Track:
        """
        Get user's currently playing track
        :return: Track
        """
        np = self.sp.currently_playing()
        return Track(np['item']['id'],
                     np['item']['name'],
                     np['item']['album']['artists'][0]['name'],
                     np['item']['album']['name'],
                     np['item']['album']['images'][0]['url'],
                     np['item']['explicit'],
                     np['item']['duration_ms'])

    def update(self) -> bool:
        """
        Update data attributes
        :return: bool to indicate if new data was fetched
        """
        if self.needs_update():
            last_track = self.track
            self.track = self.now_playing()
            self.last_updated = time.time()
            return last_track.id != self.track.id
        return False

    def needs_update(self) -> bool:
        """
        Determine if update is needed i.e. 20s have passed since last update
        :return: bool to indicate if update is needed
        """
        time_delta = time.time() - self.last_updated
        return time_delta >= REFRESH_RATE
