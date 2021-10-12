from typing import Dict

from .city import City
from .constants import Constants
from .gamesetup.game_constants import GAME_CONSTANTS
from .position import Position
from .unit import Unit

UNIT_TYPES = Constants.UNIT_TYPES


class Player:
    def __init__(self, team):
        self.team = team
        self.research_points = 0
        self.units: list[Unit] = []
        self.cities: Dict[str, City] = {}
        self.city_tile_count = 0
        self.units_plus_added_this_turn = 0

    def researched_coal(self) -> bool:
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["COAL"]

    def researched_uranium(self) -> bool:
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["URANIUM"]

    def get_max_units(self) -> int:
        return sum([len(x.citytiles) for x in self.cities.values()])

    def get_num_units_at_turn_start(self) -> int:
        return len(self.units)

    def activate_city_actions(self, system) -> None:
        self.units_plus_added_this_turn = self.get_num_units_at_turn_start()
        for city in self.cities.values():
            city.activate_citytile_actions(system, self)

    def activate_unit_actions(self, system) -> None:
        for unit in self.units:
            unit.activate_actions(system, self)

    def has_cities_to_expand(self) -> bool:
        expandable = False
        for city in self.cities.values():
            expandable = expandable or city.can_expand()
        return expandable

    # def get_optimal_new_build_cell(self, pos, system) -> Position:
    #     closest_from_each_city = []
    #     for city in self.cities.values():
    #         closest_from_each_city.append(city.get_closest_adjacent_cell(pos, system))
    #     return pos.get_closest_from_list(closest_from_each_city)


