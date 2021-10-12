from typing import List, Optional, Set, Tuple

from .cell import Cell


class GameMap:
    # ----------------------------------- Public functions ------------------------------------- #

    def __init__(self, width, height):
        self.resource_tiles: List[Cell] = []
        self.opponent_city_tiles: Set[Tuple[int, int]] = set()
        self.player_city_tiles: Set[Tuple[int, int]] = set()
        self.future_no_go_tiles: Set[Tuple[int, int]] = set()
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

    def calculate_metrics(self, system):
        self.resource_tiles = self.__generate_resource_tiles()
        self.player_city_tiles = self.__generate_tile_set(system.player)
        self.opponent_city_tiles = self.__generate_tile_set(system.opponent)

    def get_resource_tiles(self) -> List[Cell]:
        return self.resource_tiles

    def get_opponent_city_tiles(self) -> Set[Tuple[int, int]]:
        return self.opponent_city_tiles

    def get_player_city_tiles(self) -> Set[Tuple[int, int]]:
        return self.player_city_tiles

    def add_future_no_go_tiles(self, position) -> None:
        self.future_no_go_tiles.add((position.x, position.y))

    def is_valid_position(self, x, y) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ---------------------------------- Private functions ------------------------------------- #

    def __generate_tile_set(self, player) -> Set[Tuple[int, int]]:
        tile_set = set()
        for city in player.cities.values():
            for city_tile in city.citytiles:
                tile_set.add((city_tile.pos.x, city_tile.pos.y))
        return tile_set

    def __generate_resource_tiles(self):
        resource_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles

    # --------------------------------------- Do not use --------------------------------------- #

    def _setResource(self, r_type, x, y, amount):
        """
        do not use this function, this is for internal tracking of state
        """
        cell = self.get_cell(x, y)
        cell.resource = Cell.Resource(r_type, amount)
