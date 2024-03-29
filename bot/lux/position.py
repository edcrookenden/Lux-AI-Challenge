import math
from typing import List, Optional

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS


class Position:
    def __init__(self, x, y):
        self.x: int = x
        self.y: int = y

    def __sub__(self, pos) -> int:
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def distance_to(self, pos) -> int:
        """
        Returns Manhattan (L1/grid) distance to pos
        """
        return self - pos

    def is_adjacent(self, pos) -> bool:
        return (self - pos) <= 1

    def __eq__(self, pos) -> bool:
        return self.x == pos.x and self.y == pos.y

    def equals(self, pos) -> bool:
        return self == pos

    def translate(self, direction, units) -> Optional['Position']:
        if direction == DIRECTIONS.NORTH:
            return Position(self.x, self.y - units)
        elif direction == DIRECTIONS.EAST:
            return Position(self.x + units, self.y)
        elif direction == DIRECTIONS.SOUTH:
            return Position(self.x, self.y + units)
        elif direction == DIRECTIONS.WEST:
            return Position(self.x - units, self.y)
        elif direction == DIRECTIONS.CENTER:
            return Position(self.x, self.y)
        return None

    def direction_to(self, target_pos: 'Position') -> DIRECTIONS:
        """
        Return closest position to target_pos from this position
        """
        check_dirs = [
            DIRECTIONS.NORTH,
            DIRECTIONS.EAST,
            DIRECTIONS.SOUTH,
            DIRECTIONS.WEST,
        ]
        closest_dist = self.distance_to(target_pos)
        closest_dir = DIRECTIONS.CENTER
        for direction in check_dirs:
            newpos = self.translate(direction, 1)
            dist = target_pos.distance_to(newpos)
            if dist < closest_dist:
                closest_dir = direction
                closest_dist = dist
        return closest_dir

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def get_adjacent_positions(self) -> List['Position']:
        result = []
        xs = [self.x - 1, self.x + 1]
        ys = [self.y - 1, self.y + 1]
        for x in xs:
            result.append(Position(x, self.y))
        for y in ys:
            result.append(Position(self.x, y))
        return result

    def get_closest_from_list(self, list_of_pos) -> Optional['Position']:
        closest_position = None
        distance = math.inf
        for position in list_of_pos:
            if position is None:
                return None
            temp_dist = position.distance_to(self)
            if temp_dist < distance:
                closest_position = position
                distance = temp_dist
        return closest_position
