from typing import Final

class Drone:
    counter = 0
    def __init__(self):
        self.ID: Final[str] = "DR-" + self.counter
        self.where