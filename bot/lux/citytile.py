from .position import Position


class CityTile:
    def __init__(self, teamid, cityid, x, y, cooldown):
        self.cityid: int = cityid
        self.team: int = teamid
        self.pos: Position = Position(x, y)
        self.cooldown: float = cooldown

    def can_act(self) -> bool:
        """
        Whether or not this unit can research or build
        """
        return self.cooldown < 1

    def research(self) -> str:
        """
        returns command to ask this tile to research this turn
        """
        return "r {} {}".format(self.pos.x, self.pos.y)

    def build_worker(self) -> str:
        """
        returns command to ask this tile to build a worker this turn
        """
        return "bw {} {}".format(self.pos.x, self.pos.y)

    def build_cart(self) -> str:
        """
        returns command to ask this tile to build a cart this turn
        """
        return "bc {} {}".format(self.pos.x, self.pos.y)

    def activate_action(self, system, player) -> None:  # Player
        max_workers = (player.units_plus_added_this_turn >= player.get_max_units())
        if self.can_act():
            if max_workers:
                system.add_action(self.research())
            else:
                system.add_action(self.build_worker())
                player.units_plus_added_this_turn += 1

    def get_closest_free_adjacent_position(self, pos, system) -> Position:
        adjacent_positions = self.pos.get_adjacent_positions(system) ############################################
        free_positions = [x for x in adjacent_positions if system.map.is_free(x)]
        return pos.get_closest_from_list(free_positions)
