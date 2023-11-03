


class KLongPlan:
    def __init__(self, speeds, accels):
        self._speeds = speeds
        self._accels = accels

    @property
    def speeds(self):
        return self._speeds

    @property
    def accels(self):
        return self._accels

