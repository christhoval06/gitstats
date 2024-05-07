import time

from singleton import SingletonMeta


class Locals(metaclass=SingletonMeta):

    def __init__(self) -> None:
        self.exectime_internal = 0.0
        self.exectime_external = 0.0
        self.time_start = time.time()


locals = Locals()
