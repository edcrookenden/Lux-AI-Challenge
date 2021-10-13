class Constants:
    class INPUT_CONSTANTS:
        RESEARCH_POINTS = "rp"
        RESOURCES = "r"
        UNITS = "u"
        CITY = "c"
        CITY_TILES = "ct"
        ROADS = "ccd"
        DONE = "D_DONE"

    class DIRECTIONS:
        NORTH = "n"
        WEST = "w"
        SOUTH = "s"
        EAST = "e"
        CENTER = "c"
        DIR_LIST = [NORTH, EAST, SOUTH, WEST]

    class UNIT_TYPES:
        WORKER = 0
        CART = 1

    class RESOURCE_TYPES:
        WOOD = "wood"
        URANIUM = "uranium"
        COAL = "coal"

    class TIME:
        NIGHT_END = 40
        AFTERNOON_END = 30
        MIDDAY_END = 20
        MORNING_END = 10
        CYCLE_DURATION = 40
        DAY_DURATION = 30
        NIGHT_DURATION = 10
        TOTAL_CYCLES = 9

    class GAME_PARAMETERS:
        NUMBER_OF_NIGHTS_BACKUP = 2
        MAX_DISTANCES = {12: 3, 16: 5, 24: 7, 32: 8}