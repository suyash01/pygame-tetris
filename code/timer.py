from settings import *


class Timer:
    def __init__(self, duration, repeated=False, func=None) -> None:
        self.repeated = repeated
        self.func = func
        self.duration = duration

        self.start_time = 0
        self.active = False

    def activate(self) -> None:
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self) -> None:
        self.active = False
        self.start_time = 0

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration and self.active:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()
            if self.repeated:
                self.activate()
