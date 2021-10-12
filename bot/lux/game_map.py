from typing import List, Optional, Set, Tuple

from .cell import Cell
from .position import Position


class GameMap:
    # ----------------------------------- Public functions ------------------------------------- #

    def __init__(self, width, height):
        self.resource_cells: List[Cell] = []
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

    def calculate_metrics(self, system) -> None:
        self.resource_cells = self.__generate_resource_cells()
        self.player_city_tiles = self.__generate_tile_set(system.player)
        self.opponent_city_tiles = self.__generate_tile_set(system.opponent)

    def get_resource_cells(self) -> List[Cell]:
        return self.resource_cells

    def get_opponent_city_positions(self) -> List[Position]:
        return [Position(a[0], a[1]) for a in self.opponent_city_tiles]

    def get_player_city_positions(self) -> List[Position]:
        return [Position(a[0], a[1]) for a in self.player_city_tiles]

    def get_future_no_go_positions(self) -> List[Position]:
        return [Position(a[0], a[1]) for a in self.future_no_go_tiles]

    def add_future_no_go_positions(self, position) -> None:
        if position is not None:
            self.future_no_go_tiles.add((position.x, position.y))

    def is_on_board(self, pos) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_city_tile(self, pos) -> bool:
        return ((pos.x, pos.y) in self.opponent_city_tiles) or ((pos.x, pos.y) in self.player_city_tiles)

    def is_collision_tile(self, pos) -> bool:
        return ((pos.x, pos.y) in self.opponent_city_tiles) or ((pos.x, pos.y) in self.future_no_go_tiles)

    def get_closest_resource_position(self, pos) -> Position:
        return pos.get_closest_from_list([a.pos for a in self.resource_cells])

    def get_closest_city_tile(self, pos) -> Position:
        return pos.get_closest_from_list(self.get_player_city_positions())

    def get_closest_safe_tile(self, pos) -> Position:
        safe_tiles = [a.pos for a in self.resource_cells] + self.get_player_city_positions()
        return pos.get_closest_from_list(safe_tiles)

    def get_distance_to_safe_tile(self, pos) -> int:
        return pos.distance_to(self.get_closest_safe_tile(pos))

    def get_optimal_build_position(self, pos, closest_function) -> Optional[Position]:
        closest = closest_function(pos)
        if closest is None: return None
        adjacent_positions = closest.get_adjacent_positions()
        build_positions = self.filter_position_list(adjacent_positions, self.is_on_board)
        build_positions = self.filter_position_list(build_positions, self.is_free)
        return pos.get_closest_from_list(build_positions)

    def get_optimal_position_to_expand(self, pos) -> Position:
        return self.get_optimal_build_position(pos, self.get_closest_city_tile)

    def get_optimal_position_to_build_new_city(self, pos) -> Position:
        return self.get_optimal_build_position(pos, self.get_closest_resource_position)

    def is_free(self, pos) -> bool:
        cell = self.get_cell_by_pos(pos)
        return cell.resource is None and cell.citytile is None

    def filter_position_list(self, positions, filter_function) -> List[Position]:
        return [a for a in positions if filter_function(a)]

    def city_is_too_far(self, city_pos, unit_pos):
        return city_pos.distance_to(unit_pos) > 2


    # ---------------------------------- Private functions ------------------------------------- #

    def __generate_tile_set(self, player) -> Set[Tuple[int, int]]:
        tile_set = set()
        for city in player.cities.values():
            for city_tile in city.citytiles:
                tile_set.add((city_tile.pos.x, city_tile.pos.y))
        return tile_set

    def __generate_resource_cells(self):
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
