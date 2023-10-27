from datetime import datetime


class KTimer:

    # frecuency: seconds
    def __init__(self, frecuency: float) -> None:
        self._frecuency = frecuency
        self._flag = False
        self._last: datetime = datetime.now()

    def update(self, now: datetime = None):
        nw = now
        if nw is None:
            nw = datetime.now()

        if (nw - self._last).total_seconds() > self._frecuency:
            self._last = nw
            self._flag = True
        else:
            self._flag = False

    @property
    def flag(self):
        return self._flag
