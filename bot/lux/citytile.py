from .position import Position


class CityTile:
    def __init__(self, teamid, cityid, x, y, cooldown):
        self.cityid = cityid
        self.team = teamid
        self.pos = Position(x, y)
        self.cooldown = cooldown

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

    def activate_action(self, system, player):  # Player
        max_workers = (player.get_num_units() >= player.get_max_units())
        if self.can_act():
            if max_workers:
                action = self.research()
                system.actions.append(action)
            else:
                action = self.build_worker()
                system.actions.append(action)
                player.temp_extra_units += 1

    def get_closest_free_adjacent_position(self, pos, system):
        adjacent_positions = self.pos.get_adjacent_position(system)
        free_positions = [x for x in adjacent_positions if x.is_free(system)]
        return pos.get_closest_from_list(free_positions)
