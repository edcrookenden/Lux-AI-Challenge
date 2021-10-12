from typing import List, Optional, Set, Tuple

from .cell import Cell


class GameMap:
    opponent_city_tiles: Set[Tuple[int, int]] = None
    player_city_tiles: Set[Tuple[int, int]] = None

    def __init__(self, width, height):
        self.height: int = height
        self.width: int = width
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
        cell.resource = Cell.Resource(r_type, amount)

    def get_resource_tiles(self) -> List[Cell]:
        resource_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles

    def get_opponent_city_tiles(self, opponent) -> Set[Tuple[int, int]]:
        if self.opponent_city_tiles is None:
            self.opponent_city_tiles = self.generate_tile_set(opponent)
        return self.opponent_city_tiles

    def get_player_city_tiles(self, player) -> Set[Tuple[int, int]]:
        if self.player_city_tiles is None:
            self.player_city_tiles = self.generate_tile_set(player)
        return self.player_city_tiles

    def generate_tile_set(self, player) -> Set[Tuple[int, int]]:
        tile_set = set()
        for city in player.cities.values():
            for city_tile in city.citytiles:
                tile_set.add((city_tile.pos.x, city_tile.pos.y))
        return tile_set

    def add_future_unit_positions(self, position, system) -> None:
        self.get_opponent_city_tiles(system.opponent)
        self.opponent_city_tiles.add((position.x, position.y))

    def is_valid_position(self, x, y) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


