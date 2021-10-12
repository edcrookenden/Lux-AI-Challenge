import random

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS


def rotate_90_degrees(direction) -> Constants.DIRECTIONS:
    if direction == Constants.DIRECTIONS.CENTER:
        return random_direction()
    return DIRECTIONS.DIR_LIST[(DIRECTIONS.DIR_LIST.index(direction) + random.choice([1, -1])) % 4]


def random_direction() -> Constants.DIRECTIONS:
    return random.choice(DIRECTIONS.DIR_LIST)