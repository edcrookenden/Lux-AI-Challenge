import math
from typing import List

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES


class Resource:
    def __init__(self, r_type: str, amount: int):
        self.type = r_type
        self.amount = amount


class Cell:
    def __init__(self, x, y):
        self.pos = Position(x, y)
        self.resource: Resource = None
        self.citytile = None
        self.road = 0

    def has_resource(self):
        return self.resource is not None and self.resource.amount > 0


class GameMap:
    opponent_city_tiles = None
    player_city_tiles = None

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map: List[List[Cell]] = [None] * height
        for y in range(0, self.height):
            self.map[y] = [None] * width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y)

    def get_cell_by_pos(self, pos) -> Cell:
        return self.map[pos.y][pos.x]

    def get_cell(self, x, y) -> Cell:
        return self.map[y][x]

    def _setResource(self, r_type, x, y, amount):
        """
        do not use this function, this is for internal tracking of state
        """
        cell = self.get_cell(x, y)
        cell.resource = Resource(r_type, amount)

    def get_resource_tiles(self):
        resource_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles

    def get_opponent_city_tiles(self, opponent):
        if self.opponent_city_tiles is None:
            self.opponent_city_tiles = self.generate_tile_set(opponent)
        return self.opponent_city_tiles

    def get_player_city_tiles(self, player):
        if self.player_city_tiles is None:
            self.player_city_tiles = self.generate_tile_set(player)
        return self.player_city_tiles

    def generate_tile_set(self, player):
        tile_set = set()
        for city in player.cities.values():
            for city_tile in city.citytiles:
                tile_set.add((city_tile.pos.x, city_tile.pos.y))
        return tile_set

    def add_future_unit_positions(self, position, system):
        self.get_opponent_city_tiles(system.opponent)
        self.opponent_city_tiles.add((position.x, position.y))

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, pos) -> int:
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def distance_to(self, pos):
        """
        Returns Manhattan (L1/grid) distance to pos
        """
        return self - pos

    def is_adjacent(self, pos):
        return (self - pos) <= 1

    def __eq__(self, pos) -> bool:
        return self.x == pos.x and self.y == pos.y

    def equals(self, pos):
        return self == pos

    def translate(self, direction, units) -> 'Position':
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

    def get_adjacent_position(self, system):
        result = []
        xs = [self.x - 1, self.x + 1]
        ys = [self.y - 1, self.y + 1]
        for x in xs:
            if system.map.is_valid_position(x, self.y):
                result.append(Position(x, self.y))
        for y in ys:
            if system.map.is_valid_position(self.x, y):
                result.append(Position(self.x, y))
        return result

    def is_free(self, system):
        cell = system.map.get_cell_by_pos(self)
        return cell.resource == None and cell.citytile == None

    def get_closest_from_list(self, list_of_pos):
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
