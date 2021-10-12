import random
from typing import List, Optional

from lux.gamesetup.game import GameMap
from lux.player import Player
from lux.constants import Constants
from lux.gamesetup.game import Game

DIRECTIONS = Constants.DIRECTIONS
game_state = None

logfile = "agent.log"
open(logfile, "w")


class GameSystem:
    """
    A class to control the game progression

    ...

    Attributes
    ----------
    actions : List[str]
        instructions to feed to the next round
    player : Player
        the current player
    opponent : Player
        the current opponent
    map : GameMap
        the map of the game
    step : int
        the turn of the game (0 - 360)

    Methods
    -------
    setup(observation: Observation) -> None:
        initiates the game state for the new turn
    run() -> List[str]:
        activates city and unit actions and returns a record of them
    rotate_90_degrees(direction: DIRECTIONS) -> DIRECTIONS: @staticmethod
        returns a random cardinal directions 90 degrees from the input direction
    """

    def __init__(self) -> None:
        self.actions: List[str] = []
        self.player: Optional[Player] = None
        self.opponent: Optional[Player] = None
        self.map: Optional[GameMap] = None
        self.step: int = 0

    def setup(self, observation) -> None:
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

    def run(self) -> List[str]:
        self.player.activate_city_actions(self)
        self.player.activate_unit_actions(self)
        return self.actions


def agent(observation, configuration):
    system = GameSystem()
    system.setup(observation)
    return system.run()
