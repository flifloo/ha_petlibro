from typing import cast

from .feeder import Feeder


class GranaryFeeder(Feeder):
    @property
    def remaining_desiccant(self) -> str:
        return cast(str, self._data.get("remainingDesiccantDays"))
