import random

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS


def rotate_90_degrees(direction) -> Constants.DIRECTIONS:
    dir_list = [Constants.DIRECTIONS.NORTH, Constants.DIRECTIONS.EAST, Constants.DIRECTIONS.SOUTH,
                Constants.DIRECTIONS.WEST]
    if direction == Constants.DIRECTIONS.CENTER:
        return random.choice(dir_list)
    return dir_list[(dir_list.index(direction) + random.choice([1, -1])) % 4]
