import re
from typing import Optional

from .constants import Constants
from .gamesetup.game_constants import GAME_CONSTANTS
from .position import Position
from .constants_helpers import rotate_90_degrees, random_direction

UNIT_TYPES = Constants.UNIT_TYPES
DIRECTIONS = Constants.DIRECTIONS


class Unit:
    class Cargo:
        def __init__(self):
            self.wood: int = 0
            self.coal: int = 0
            self.uranium: int = 0

        def __str__(self) -> str:
            return f"Cargo | Wood: {self.wood}, Coal: {self.coal}, Uranium: {self.uranium}"

    def __init__(self, teamid, u_type, unitid, x, y, cooldown, wood, coal, uranium):
        self.pos: Position = Position(x, y)
        self.team: int = teamid
        self.id: str = unitid
        self.type: UNIT_TYPES = u_type
        self.cooldown: int = cooldown
        self.cargo: Unit.Cargo = Unit.Cargo()
        self.cargo.wood = wood
        self.cargo.coal = coal
        self.cargo.uranium = uranium

    def is_worker(self) -> bool:
        return self.type == UNIT_TYPES.WORKER

    def is_cart(self) -> bool:
        return self.type == UNIT_TYPES.CART

    def get_cargo_space_left(self) -> int:
        """
        get cargo space left in this unit
        """
        spaceused = self.cargo.wood + self.cargo.coal + self.cargo.uranium
        if self.type == UNIT_TYPES.WORKER:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["WORKER"] - spaceused
        else:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["CART"] - spaceused

    def can_build(self, game_map) -> bool:
        """
        whether or not the unit can build where it is right now, checks that cell does not have resource and unit can
        act and unit has enough resources DOESN'T CHECK IF CITY IS ALREADY HERE
        """
        cell = game_map.get_cell_by_pos(self.pos)
        if not cell.has_resource() and self.can_act() and (self.cargo.wood + self.cargo.coal + self.cargo.uranium) >= \
                GAME_CONSTANTS["PARAMETERS"]["CITY_BUILD_COST"]:
            return True
        return False

    def can_act(self) -> bool:
        """
        whether or not the unit can move or not. This does not check for potential collisions into other units or enemy cities
        """
        return self.cooldown < 1

    def move(self, dir) -> str:
        """
        return the command to move unit in the given direction
        """
        return "m {} {}".format(self.id, dir)

    def transfer(self, dest_id, resourceType, amount) -> str:
        """
        return the command to transfer a resource from a source unit to a destination unit as specified by their ids
        """
        return "t {} {} {} {}".format(self.id, dest_id, resourceType, amount)

    def build_city(self) -> str:
        """
        return the command to build a city right under the worker
        """
        return "bcity {}".format(self.id)

    def pillage(self) -> str:
        """
        return the command to pillage whatever is underneath the worker
        """
        return "p {}".format(self.id)

    def activate_actions(self, system, player) -> None:
        if self.can_act():
            if system.clock.is_night():
                return None
            if system.player.cities == 0 and self.can_build(system.map):
                self.__build_city_here(system)
            elif self.get_cargo_space_left() == 0 and player.has_cities_to_expand():
                self.__try_to_build(system)
            elif self.get_cargo_space_left() > 0:
                self.__collect_resources(system)
            else:
                self.__deposit_resources_in_city(system)

    def __build_city_here(self, system) -> None:
        system.add_action(self.build_city())
        system.map.add_future_no_go_positions(self.pos)

    def __try_to_build(self, system) -> None:
        destination = system.map.get_optimal_position_to_expand(self.pos, system)
        if (destination is None) or system.map.city_is_too_far(destination, self.pos):
            destination = system.map.get_optimal_position_to_build_new_city(self.pos, system)
        self.try_to_build_at(destination, system)

    def try_to_build_at(self, pos, system) -> None:
        if pos is None:
            self.__safe_move(random_direction(), system)
        elif pos.equals(self.pos):
            self.__build_city_here(system)
        else:
            direction = self.__direction_without_collision(pos, system.map.is_city_tile)
            self.__safe_move(direction, system)

    def __move_towards_closest(self, get_closest_tile_function, system):
        closest_tile = get_closest_tile_function(self.pos, system)
        direction = self.__direction_without_collision(closest_tile, system.map.is_collision_tile)
        self.__safe_move(direction, system)

    def __collect_resources(self, system) -> None:
        self.__move_towards_closest(system.map.get_closest_resource_position, system)

    def __deposit_resources_in_city(self, system) -> None:
        self.__move_towards_closest(system.map.get_closest_city_tile, system)

    def __direction_without_collision(self, destination, collision_function) -> Optional[DIRECTIONS]:
        if destination is not None:
            move_direction = self.pos.direction_to(destination)
            c = 0
            new_position = self.pos.translate(move_direction, 1)
            while collision_function(new_position) and c < 5:
                move_direction = rotate_90_degrees(move_direction)
                new_position = self.pos.translate(move_direction, 1)
                c += 1
            return move_direction
        return None

    def __safe_move(self, direction, system) -> None:
        system.add_action(self.move(direction))
        system.map.add_future_no_go_positions(self.pos.translate(direction, 1))

    def get_id_value(self):
        number_string = re.findall(r'\d+', self.id)
        return int(number_string[0])

    # ------------------- Optional functions to set roles ---------------------------

    def activate_roles_based_actions(self, system, player) -> None:
        if self.can_act():
            if system.player.cities == 0 and self.can_build(system.map):
                self.__build_city_here(system)
            elif player.get_num_units_at_turn_start() < 2:
                self.activate_actions(system, player)
            elif self.get_id_value() % 4 == 0:
                self.activate_maintainer_actions(system)
            else:
                self.activate_builder_actions(system, player)

    def activate_builder_actions(self, system, player):
        if self.get_cargo_space_left() > 0:
            self.__collect_resources(system)
        elif player.has_cities_to_expand():
            self.__try_to_build(system)
        else:
            self.activate_maintainer_actions(system)

    def activate_maintainer_actions(self, system):
        if self.get_cargo_space_left() > 0:
            self.__collect_resources(system)
        else:
            self.__deposit_resources_in_city(system)