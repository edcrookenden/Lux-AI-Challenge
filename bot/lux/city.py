from .citytile import CityTile


class City:
    def __init__(self, teamid, cityid, fuel, light_upkeep):
        self.cityid = cityid
        self.team = teamid
        self.fuel = fuel
        self.citytiles: list[CityTile] = []
        self.light_upkeep = light_upkeep

    def _add_city_tile(self, x, y, cooldown):
        ct = CityTile(self.team, self.cityid, x, y, cooldown)
        self.citytiles.append(ct)
        return ct

    def get_light_upkeep(self):
        return self.light_upkeep

    def activate_citytile_actions(self, system, player):
        for tile in self.citytiles:
            tile.activate_action(system, player)

    def get_closest_adjacent_cell(self, pos, system):
        citytiles = []
        for citytile in self.citytiles:
            citytiles.append(citytile.get_closest_free_adjacent_position(pos, system))
        return pos.get_closest_from_list(citytiles)
