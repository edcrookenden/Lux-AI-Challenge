import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import random

DIRECTIONS = Constants.DIRECTIONS
game_state = None

logfile = "agent.log"
open(logfile, "w")

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

    # Banned cells for collisions
    taken_tiles = set()
    for city in opponent.cities.values():
        for city_tile in city.citytiles:
            taken_tiles.add((city_tile.pos.x, city_tile.pos.y))

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            expandable = can_build_city(player, unit)
            if expandable is not None:
                with open(logfile, "a") as f:
                    f.write(f"{observation['step']}: {unit.id} trying to build a city\n")
                actions = build_city(unit, expandable, actions, taken_tiles)
            else:
                if unit.get_cargo_space_left() > 0:
                    with open(logfile, "a") as f:
                        f.write(f"{observation['step']}: {unit.id} trying to collect resources\n")
                    closest_resource_tile = get_closest_resource(player, resource_tiles, unit)
                    if closest_resource_tile is not None:
                        move_dir = unit.pos.direction_to(closest_resource_tile.pos)
                        while (unit.pos.translate(move_dir, 1).x, unit.pos.translate(move_dir, 1).y) in taken_tiles:
                            move_dir = rotate_90_degrees(move_dir)
                        taken_tiles.add((unit.pos.translate(move_dir, 1).x, unit.pos.translate(move_dir, 1).y))
                        actions.append(unit.move(move_dir))
                else:
                    if len(player.cities) > 0:
                        with open(logfile, "a") as f:
                            f.write(f"{observation['step']}: {unit.id} trying to deliver resources to city\n")
                        closest_city_tile = get_closest_city(player, unit)
                        if closest_city_tile is not None:
                            move_dir = unit.pos.direction_to(closest_city_tile.pos)
                            while (unit.pos.translate(move_dir, 1).x, unit.pos.translate(move_dir, 1).y) in taken_tiles:
                                move_dir = rotate_90_degrees(move_dir)
                            taken_tiles.add((unit.pos.translate(move_dir, 1).x, unit.pos.translate(move_dir, 1).y))
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
    adj_list = []
    xs = [city_tile.pos.x - 1, city_tile.pos.x + 1]
    ys = [city_tile.pos.y - 1, city_tile.pos.y + 1]
    for x in xs:
        if is_valid_cell_position(x, city_tile.pos.y) and not game_state.map.get_cell(x, city_tile.pos.y).has_resource():
            result.append(game_state.map.get_cell(x, city_tile.pos.y))
    for y in ys:
        if is_valid_cell_position(city_tile.pos.x, y) and not game_state.map.get_cell(city_tile.pos.x, y).has_resource():
            result.append(game_state.map.get_cell(city_tile.pos.x, y))
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


def calc_next_cell(state, source, direction):
    x = source.pos.x
    y = source.pos.y
    if direction == DIRECTIONS.CENTER:
        return source
    if direction == DIRECTIONS.NORTH:
        y = y + 1
    elif direction == DIRECTIONS.SOUTH:
        y = y - 1
    elif direction == DIRECTIONS.WEST:
        x = x - 1
    elif direction == DIRECTIONS.EAST:
        x = x + 1
    return state.map.get_cell(x, y)


def rotate_90_degrees(direction):
    dir_list = [DIRECTIONS.NORTH, DIRECTIONS.EAST, DIRECTIONS.SOUTH, DIRECTIONS.WEST]
    if direction == DIRECTIONS.CENTER:
        return random.choice(dir_list)
    return dir_list[(dir_list.index(direction) + 1) % 4]


def build_city(unit, city, action_list, taken_tiles):
    destination = get_optimal_adjacent_cell(unit, city)
    if destination.pos.equals(unit.pos):
        action_list.append(unit.build_city())
        return action_list
    for city_tile in city.citytiles:
        builder_taken_tiles = taken_tiles.copy()
        builder_taken_tiles.add((city_tile.pos.x, city_tile.pos.y))
    move_dir = unit.pos.direction_to(destination.pos)
    while (unit.pos.translate(move_dir, 1).x, unit.pos.translate(move_dir, 1).y) in builder_taken_tiles:
        move_dir = rotate_90_degrees(move_dir)
    action_list.append(unit.move(move_dir))
    return action_list


    #direction = unit.pos.direction_to(destination.pos)
    #next_cell = calc_next_cell(state, unit, direction)
    #while next_cell.citytile is not None:
    #    direction = rotate_90_degrees(direction)
    #    next_cell = calc_next_cell(state, unit, direction) # Edge case where it is trapped not dealt with
    #action_list.append(unit.move(unit.pos.direction_to(next_cell.pos)))
    #return action_list


def get_city_to_expand(player, unit):
    for city in player.cities.values():
        if city.fuel > city.get_light_upkeep()*20:
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
