import os
import time
from datetime import datetime
import csv

"""
MovementsCSV class.
Writes a CSV file containing peak movements CSV file.

Version Date        Description
v1.10   16/11/2023  Add a new column for v3.20 of motion.
Phasing out with version v3.21b of motion.
"""

__author__ = "Peter Goodgame"
__name__ = "movementCSV"
__version__ = "v1.10"

class MovementCSV:
    def __init__(self, debug=False, interval=60):
        self.debug = debug
        self.interval = interval
        self.trigger_point = 0
        self.trigger_point_frames = 0
        self.subtraction_threshold = 0
        self.subtraction_history = 0
        self.motion_level = 0  # Current motion level.
        self.motion_highest = 0  # Maximum movement in the reporting period.
        self.movement_level = 0  # Current Movement level.
        self.movement_highest = 0  # Maximum movement in the reporting period.
        self.movement_average = 0  # Average movement based on mean movement.
        self.movement_total = 0  # Total movement
        self.movement_cnt = 0  # Number of frames.
        self.trigger_highest = 0  # value that triggered movement.
        self.trigger_point_base = 0  # value at which recording stops.
        self.movement_history_window = 0 # Number of past frames to Calculate the average movement level.
        self.movement_history_age = 0 # Number of frames gap between the movement history frames and the current one.
        self.variable_trigger_point = 0 # Variable trigger point = movement_average + trigger point
        self.last_write_time = datetime.now()  # Last write time.
        self.now = datetime.now()
        self.csv_file = "peakMovement.csv"
        self.columns = ['Timestamp',
                        'Trigger Point',
                        'Trigger Point Base',
                        'Movement History Window',
                        'Movement History Age',
                        'Subtraction Threshold',
                        'Subtraction History',
                        'Average',
                        'Variable Trigger Point',
                        'Variable Trigger Point Base',
                        'Highest Peak',
                        'Trigger Value']

        if not os.path.isfile(self.csv_file):
            self.create()

    def create(self):
        if self.debug:
            print('CSV:create')
        with open(self.csv_file, 'w', newline='') as file:
            # creating a csv dict writer object
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            _writer.writeheader()

    """
    Called after the parameters are read.
    """

    def update_parameters(self, _trigger_point,
                          _trigger_point_base,
                          _trigger_point_frames,
                          _subtraction_threshold,
                          _subtraction_history,
                          _movement_history_window,
                          _movement_history_age):
        if self.debug:
            print('CSV:update_parameters')
        self.trigger_point = _trigger_point
        self.trigger_point_base = _trigger_point_base
        self.trigger_point_frames = _trigger_point_frames
        self.subtraction_threshold = _subtraction_threshold
        self.subtraction_history = _subtraction_history
        self.movement_history_window = _movement_history_window
        self.movement_history_age = _movement_history_age
        if not os.path.isfile(self.csv_file):
            self.create()

    """
    Call this at every frame read.
    """

    def log_level(self, movement_level):
        if self.debug:
            print('CSV:update_movement')
        if not os.path.isfile(self.csv_file):
            self.create()
        if movement_level > 0:
            self.movement_cnt += 1
            self.movement_total += movement_level
        if movement_level > self.movement_highest:
            self.movement_highest = movement_level
        self.now = datetime.now()
        diff = self.now - self.last_write_time
        minutes = round((diff.total_seconds()), 2)
        # minutes = round((diff.total_seconds() / 60), 2)
        if minutes >= self.interval:
            if self.debug:
                print(f'round({self.movement_total} / {self.movement_cnt})')
            if self.movement_cnt > 0:
                self.movement_average = round(self.movement_total / self.movement_cnt)
            else:
                self.movement_average = 0
            self.write()
            self.last_write_time = self.now
            self.movement_total = 0
            self.movement_cnt = 0
            self.movement_highest = 0

    """
    To be called when motion is detected.
    if sighup is set to true a record is written with 
    values set temporarily set to 1.
    """

    def log_motion(self, _motion_level):
        if self.debug:
            print('CSV:log_motion')
        if not os.path.isfile(self.csv_file):
            self.create()
        if self.trigger_highest < _motion_level:
            self.trigger_highest = _motion_level

    """
    Call this after motion comes to an end.
    """

    def motion_write(self, sighup=False):
        if self.debug:
            print('CSV:motion_write')
        if not os.path.isfile(self.csv_file):
            self.create()
        if not sighup:
            with open(self.csv_file, 'a', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                timestamp = self.now.strftime("%Y-%m-%d %H:%M")
                _writer.writerow({"Timestamp": timestamp,
                                  'Trigger Point': self.trigger_point,
                                  'Trigger Point Base': self.trigger_point_base,
                                  'Movement History Window': self.movement_history_window,
                                  'Movement History Age': self.movement_history_age,
                                  'Subtraction Threshold': self.subtraction_threshold,
                                  'Subtraction History': self.subtraction_history,
                                  "Average": self.movement_average,
                                  "Highest Peak": self.movement_highest,
                                  "Trigger Value": self.trigger_highest,
                                  "Variable Trigger Point": self.movement_average + self.trigger_point,
                                  "Variable Trigger Point Base": self.movement_average + self.trigger_point_base})
            self.trigger_highest = 0
        else:
            with open(self.csv_file, 'a', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                timestamp = self.now.strftime("%Y-%m-%d %H:%M")
                _writer.writerow({"Timestamp": timestamp,
                                  'Trigger Point': 1,
                                  'Trigger Point Base': 1,
                                  'Movement History Window': self.movement_history_window,
                                  'Movement History Age': self.movement_history_age,
                                  'Subtraction Threshold': self.subtraction_threshold,
                                  'Subtraction History': self.subtraction_history,
                                  "Average": 1,
                                  "Highest Peak": 1,
                                  "Trigger Value": 1})

    """
    Called every minute.
    """

    def write(self):
        if self.debug:
            print('CSV:write')
        if not os.path.isfile(self.csv_file):
            self.create()
        with open(self.csv_file, 'a', newline='') as file:
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            timestamp = self.now.strftime("%Y-%m-%d %H:%M")
            return _writer.writerow({"Timestamp": timestamp,
                                     'Trigger Point': self.trigger_point,
                                     'Trigger Point Base': self.trigger_point_base,
                                     'Movement History Window': self.movement_history_window,
                                     'Movement History Age': self.movement_history_age,
                                     'Subtraction Threshold': self.subtraction_threshold,
                                     'Subtraction History': self.subtraction_history,
                                     "Average": self.movement_average,
                                     "Highest Peak": self.movement_highest,
                                     "Trigger Value": 0,
                                     "Variable Trigger Point": self.movement_average + self.trigger_point,
                                     "Variable Trigger Point Base": self.movement_average + self.trigger_point_base})
        self.movement_highest = 0
