import math
from typing import Dict

from .constants import Constants
from .game_map import Position
from .game_constants import GAME_CONSTANTS

UNIT_TYPES = Constants.UNIT_TYPES


class Player:
    temp_extra_units = 0

    def __init__(self, team):
        self.team = team
        self.research_points = 0
        self.units: list[Unit] = []
        self.cities: Dict[str, City] = {}
        self.city_tile_count = 0

    def researched_coal(self) -> bool:
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["COAL"]

    def researched_uranium(self) -> bool:
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["URANIUM"]

    def get_max_units(self):
        return sum([len(x.citytiles) for x in self.cities.values()])

    def get_num_units(self):
        return len(self.units)

    def activate_city_actions(self, system):
        self.temp_extra_units = self.get_num_units()
        for city in self.cities.values():
            city.activate_citytile_actions(system, self)

    def activate_unit_actions(self, system):
        for unit in self.units:
            unit.activate_actions(system, self)

    def has_cities_to_expand(self):
        for city in self.cities.values():
            # If final day, just return True
            if city.fuel > city.get_light_upkeep() * 20:
                return True
        return False

    def get_optimal_new_build_cell(self, pos, system):
        closest_from_each_city = []
        for city in self.cities.values():
            closest_from_each_city.append(city.get_closest_adjacent_cell(pos, system))
        return pos.get_closest_from_list(closest_from_each_city)


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


class Cargo:
    def __init__(self):
        self.wood = 0
        self.coal = 0
        self.uranium = 0

    def __str__(self) -> str:
        return f"Cargo | Wood: {self.wood}, Coal: {self.coal}, Uranium: {self.uranium}"


class Unit:
    def __init__(self, teamid, u_type, unitid, x, y, cooldown, wood, coal, uranium):
        self.pos = Position(x, y)
        self.team = teamid
        self.id = unitid
        self.type = u_type
        self.cooldown = cooldown
        self.cargo = Cargo()
        self.cargo.wood = wood
        self.cargo.coal = coal
        self.cargo.uranium = uranium

    def is_worker(self) -> bool:
        return self.type == UNIT_TYPES.WORKER

    def is_cart(self) -> bool:
        return self.type == UNIT_TYPES.CART

    def get_cargo_space_left(self):
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
        whether or not the unit can build where it is right now
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

    def activate_actions(self, system, player):
        if self.can_act():
            if system.player.cities == 0 and self.can_build(system.map):
                # with open("agent.log", "a") as f:
                #     f.write(f"{system.step}: {self.id} trying to build emergency city\n")
                self.build_city_here(system)
            elif self.get_cargo_space_left() == 0 and player.has_cities_to_expand():
                # with open("agent.log", "a") as f:
                #     f.write(f"{system.step}: {self.id} trying to build city\n")
                self.try_to_build_city(system, player)
            elif self.get_cargo_space_left() > 0:
                # with open("agent.log", "a") as f:
                #     f.write(f"{system.step}: {self.id} trying to collect resources\n")
                self.collect_resources(system)
            else:
                # with open("agent.log", "a") as f:
                #     f.write(f"{system.step}: {self.id} trying to deposit resources\n")
                self.deposit_resources_in_city(system)

    def build_city_here(self, system):
        system.actions.append(self.build_city())
        system.map.add_future_unit_positions(self.pos, system)

    def try_to_build_city(self, system, player):
        destination = player.get_optimal_new_build_cell(self.pos, system)
        if destination is None:
            return
        if destination.equals(self.pos):
            self.build_city_here(system)
        else:
            no_go_tiles = system.map.get_opponent_city_tiles(system.opponent).union(system.map.get_player_city_tiles(
                system.player))
            self.move_without_collision(destination, no_go_tiles, system)

    def move_without_collision(self, destination, no_go_tiles, system):
        if destination is not None:
            move_direction = self.pos.direction_to(destination)
            c = 0
            new_position = self.pos.translate(move_direction, 1)
            while (new_position.x, new_position.y) in no_go_tiles and c < 5:
                move_direction = system.rotate_90_degrees(move_direction)
                new_position = self.pos.translate(move_direction, 1)
                c += 1
            system.actions.append(self.move(move_direction))
            system.map.add_future_unit_positions(self.pos.translate(move_direction, 1), system)

    def collect_resources(self, system):
        resources = system.map.get_resource_tiles()
        no_go_tiles = system.map.get_opponent_city_tiles(system.opponent)
        closest_resource_position = self.pos.get_closest_from_list([x.pos for x in resources])
        with open("agent.log", "a") as f:
            f.write(f"{system.step}: {self.id} closest resource: {closest_resource_position}\n")
        self.move_without_collision(closest_resource_position, no_go_tiles, system)

    def deposit_resources_in_city(self, system):
        citytiles = system.map.get_player_city_tiles(system.player)
        no_go_tiles = system.map.get_opponent_city_tiles(system.opponent)
        closest_citytile_position = self.pos.get_closest_from_list([Position(x[0], x[1]) for x in citytiles])
        self.move_without_collision(closest_citytile_position, no_go_tiles, system)
