import time

from api.data import Data
from constants import INACTIVITY_TIMEOUT
from renderer.now_playing import NowPlaying
from renderer.profile import Profile
from renderer.renderer import Renderer


class MainRenderer(Renderer):
    def __init__(self, matrix, canvas, draw, layout, data):
        super().__init__(matrix, canvas, draw, layout)
        self.data: Data = data
        self.np: NowPlaying = NowPlaying(self.matrix, self.canvas, self.draw, self.layout, self.data)
        self.profile: Profile = Profile(self.matrix, self.canvas, self.draw, self.layout, self.data)
        self.render()

    def render(self):
        while not self.timeout(self.data.inactivity):
            self.render_now_playing()
            self.render_profile()

    def render_now_playing(self):
        self.np.render()

    def render_profile(self):
        self.profile.render()

    @staticmethod
    def timeout(inactivity: float) -> bool:
        if inactivity > 0:
            return time.time() - inactivity >= INACTIVITY_TIMEOUT
        return False
