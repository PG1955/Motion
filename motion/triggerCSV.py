import numpy as np
import pandas as pd
import subprocess

__author__ = "Peter Goodgame"
__name__ = "triggerCSV"
__version__ = "v1.2"


class TriggerCSV:
    """
    Creates a csv file that shows the detail of the trigger event.
    """
    def __init__(self, trigger_point, trigger_point_base, trigger_point_csv_window, window_size, window_size_age):
        self.frames_required = None
        self.finalise = None
        # self.post_movement_frames = None
        self.table = None
        self.trigger_point_csv_window = trigger_point_csv_window
        self.trigger_point = trigger_point
        self.trigger_point_base = trigger_point_base
        self.window_size = window_size
        self.window_size_age = window_size_age
        # self.post_movement_frames_cnt = None
        self.filename = None
        self.data = np.array([],dtype=np.int16)
        self.columns = [
            'Trigger Point',
            'Trigger Point Base',
            'Movement Window',
            'Movement Window Age',
            'Event Trigger Point',
            'Event Trigger Point Base',
            'Movement Level',
            'Trigger']

    def add_row(self,
                event_trigger_point,
                event_trigger_point_base,
                movement_level):
        if self.trigger_point_csv_window > 0:
            self.data = np.append(self.data, self.trigger_point)
            self.data = np.append(self.data, self.trigger_point_base)
            self.data = np.append(self.data, self.window_size)
            self.data = np.append(self.data, self.window_size_age)
            self.data = np.append(self.data, event_trigger_point)
            self.data = np.append(self.data, event_trigger_point_base)
            self.data = np.append(self.data, movement_level)
            self.data = np.append(self.data, False)
            # Trim buffer
            self.data = self.data[(self.trigger_point_csv_window * 8) * -1::]
            # print(self.data.size)


    def log_movement(self,
                     event_trigger_point,
                     event_trigger_point_base,
                     movement_level):
        """ Run this for every frame.
        """

        if self.finalise:
            self.frames_required -= 1
            if self.frames_required > 0:
                self.add_row(event_trigger_point,
                             event_trigger_point_base,
                             movement_level)
        else:
            self.add_row(event_trigger_point,
                         event_trigger_point_base,
                         movement_level)

            # def log_movement(self,

    def movement_triggered(self):
        """
        Once movement is triggered set the save post frames and then stop storing data.
        """
        if self.trigger_point_csv_window:
            if not self.finalise:
                self.finalise = True
                self.frames_required = round(self.trigger_point_csv_window / 2)
                self.data[-1] = True

    def write_csv(self, filename='Motion/trigger.csv'):
        if self.trigger_point_csv_window:
            self.filename = filename
            # Reshape into a 5 column table
            self.table = np.reshape(self.data, (-1, 8))
            df = pd.DataFrame(data=self.table, columns=self.columns)
            df.index.name = 'Frame'
            df.to_csv(self.filename)

            # Create plot.
            subprocess.Popen(['python3', 'triggerPlot.py', '--filename', self.filename])

            # As the file has been written start collecting data again.
            self.finalise = False
