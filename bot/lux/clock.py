from .constants import Constants

TIME = Constants.TIME

class Clock:
    def __init__(self, turn):
        self.turn = turn

    def get_day_number(self):
        return self.turn // TIME.CYCLE_DURATION

    def get_time(self):
        return self.turn % TIME.CYCLE_DURATION

    def is_morning(self):
        return self.get_time() < TIME.MORNING_END

    def is_midday(self):
        return TIME.MORNING_END < self.get_time() < TIME.MIDDAY_END

    def is_afternoon(self):
        return TIME.MIDDAY_END < self.get_time() < TIME.AFTERNOON_END

    def is_night(self):
        return TIME.AFTERNOON_END < self.get_time() < TIME.NIGHT_END