from typing import Optional

from .citytile import CityTile
from .position import Position


class Cell:
    class Resource:
        def __init__(self, r_type: str, amount: int):
            self.type: str = r_type
            self.amount: int = amount

    def __init__(self, x, y):
        self.pos: Position = Position(x, y)
        self.resource: Optional[Cell.Resource] = None
        self.citytile: Optional[CityTile] = None
        self.road: float = 0

    def has_resource(self) -> bool:
        return self.resource is not None and self.resource.amount > 0
