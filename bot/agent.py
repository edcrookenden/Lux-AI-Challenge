import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate

DIRECTIONS = Constants.DIRECTIONS
game_state = None


def agent(observation, configuration):
    global game_state

    actions = setup(observation)

    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height

    resource_tiles = find_resource_tiles(game_state, height, width)

    max_units = sum([len(x.citytiles) for x in player.cities.values()])
    num_units = len(player.units)

    # City actions
    for cities in player.cities.values():
        for city_tile in cities.citytiles:
            max_workers = (num_units >= max_units)
            if city_tile.can_act():
                if max_workers:
                    action = city_tile.research()
                    actions.append(action)
                else:
                    action = city_tile.build_worker()
                    actions.append(action)
                    num_units += 1

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            expandable = can_build_city(player, unit)
            if expandable is not None:
                actions = build_city(unit, expandable, actions)
            else:
                if unit.get_cargo_space_left() > 0:
                    closest_resource_tile = get_closest_resource(player, resource_tiles, unit)
                    if closest_resource_tile is not None:
                        actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
                else:
                    if len(player.cities) > 0:
                        closest_city_tile = get_closest_city(player, unit)
                        if closest_city_tile is not None:
                            move_dir = unit.pos.direction_to(closest_city_tile.pos)
                            actions.append(unit.move(move_dir))

    # build new tile


    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions

def occupied_cells():
    pass
    # want this for collisions
    # Add opponent cities
    # add where are units are moving too
    # Can collide in out own city so these are an exception

def is_valid_cell_position(x, y):
    if 0 <= x < game_state.map.width and 0 <= y < game_state.map.height:
        return True
    return False


def get_adjacent_cells(city_tile):
    result = []
    xs = [city_tile.pos.x - 1, city_tile.pos.x + 1, city_tile.pos.x]
    ys = [city_tile.pos.y - 1, city_tile.pos.y + 1, city_tile.pos.y]
    for x in xs:
        for y in ys:
            if x == city_tile.pos.x and y == city_tile.pos.y:
                continue
            if is_valid_cell_position(x, y) and not game_state.map.get_cell(x, y).has_resource():
                result.append(game_state.map.get_cell(x, y))
    return result


def get_optimal_adjacent_cell(unit, city):
    optimal_cell = None
    distance = math.inf
    for city_tile in city.citytiles:
        adjacent_cells = get_adjacent_cells(city_tile)
        for cell in adjacent_cells:
            dis = cell.pos.distance_to(unit.pos)
            if dis == 0:
                return cell
            if dis < distance:
                optimal_cell = cell
                distance = dis
    return optimal_cell


def build_city(unit, city, action_list):
    destination = get_optimal_adjacent_cell(unit, city)
    if destination.pos.equals(unit.pos):
        action_list.append(unit.build_city())
        return action_list
    action_list.append(unit.move(unit.pos.direction_to(destination.pos)))
    return action_list


def get_city_to_expand(player, unit):
    for city in player.cities.values():
        if city.fuel > city.get_light_upkeep()*10:
            return city
    return None


def can_build_city(player, unit):
    expansion = get_city_to_expand(player, unit)
    if unit.get_cargo_space_left() == 0 and expansion is not None:   # Potentially optimise so we get rid of least amount of fuel
        return expansion
    return None


def get_closest_city(player, unit):
    closest_dist = math.inf
    closest_city_tile = None
    for k, city in player.cities.items():
        for city_tile in city.citytiles:
            dist = city_tile.pos.distance_to(unit.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_city_tile = city_tile
    return closest_city_tile


def get_closest_resource(player, resource_tiles, unit):
    closest_dist = math.inf
    closest_resource_tile = None
    for resource_tile in resource_tiles:
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
        dist = resource_tile.pos.distance_to(unit.pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_resource_tile = resource_tile
    return closest_resource_tile


def find_resource_tiles(state, height, width):
    '''

    :param state:
    :param height:
    :param width:
    :return:
    '''
    resource_tiles: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)
    return resource_tiles


def setup(observation):
    global game_state
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    actions = []
    return actions
