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


class GameSystem:
    def __init__(self):
        self.actions = []
        self.player = None
        self.opponent = None
        self.map = None
        self.logfile = "agent.log"
        self.step = 0

    def run(self):
        self.player.activate_city_actions(self)
        self.player.activate_unit_actions(self)
        return self.actions

    def setup(self, observation):
        global game_state
        if observation["step"] == 0:
            game_state = Game()
            game_state._initialize(observation["updates"])
            game_state._update(observation["updates"][2:])
            game_state.id = observation.player
        else:
            game_state._update(observation["updates"])
        self.player = game_state.players[observation.player]
        self.opponent = game_state.players[(observation.player + 1) % 2]
        self.map = game_state.map
        self.step = observation["step"]

    def rotate_90_degrees(self, direction):
        dir_list = [DIRECTIONS.NORTH, DIRECTIONS.EAST, DIRECTIONS.SOUTH, DIRECTIONS.WEST]
        if direction == DIRECTIONS.CENTER:
            return random.choice(dir_list)
        return dir_list[(dir_list.index(direction) + random.choice([1, -1])) % 4]


def agent(observation, configuration):
    system = GameSystem()
    system.setup(observation)
    return system.run()
