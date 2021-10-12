from .citytile import CityTile
from .position import Position


class City:
    def __init__(self, teamid, cityid, fuel, light_upkeep):
        self.cityid: int = cityid
        self.team: int = teamid
        self.fuel: float = fuel
        self.citytiles: list[CityTile] = []
        self.light_upkeep: float = light_upkeep

    def _add_city_tile(self, x, y, cooldown):
        ct = CityTile(self.team, self.cityid, x, y, cooldown)
        self.citytiles.append(ct)
        return ct

    def get_light_upkeep(self) -> float:
        return self.light_upkeep

    def activate_citytile_actions(self, system, player):
        for tile in self.citytiles:
            tile.activate_action(system, player)

    def get_closest_adjacent_cell(self, pos, system) -> Position:
        citytiles = []
        for citytile in self.citytiles:
            citytiles.append(citytile.get_closest_free_adjacent_position(pos, system))
        return pos.get_closest_from_list(citytiles)
