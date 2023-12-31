import numpy as np
import pandas as pd
import subprocess


class TriggerCSV:
    """
    Creates a csv file that shows the detail of the trigger event.
    """

    def __init__(self, trigger_point_csv_window, window_size, window_size_age):
        self.post_movement_frames = None
        self.table = None
        self.trigger_point_csv_window = trigger_point_csv_window
        self.window_size = window_size
        self.window_size_age = window_size_age
        self.post_movement_frames_cnt = None
        self.filename = None
        self.data = np.array([])
        self.columns = ['Movement Window',
                        'Movement Window Age',
                        'Trigger Point',
                        'Trigger Point Base',
                        'Movement Level']

    def log_movement(self,
                     trigger_point,
                     trigger_point_base,
                     movement_level):
        """ Run this for every frame.
        """
        if self.trigger_point_csv_window:
            if not self.post_movement_frames or self.post_movement_frames_cnt > 0:
                self.data = np.append(self.data, self.window_size)
                self.data = np.append(self.data, self.window_size_age)
                self.data = np.append(self.data, trigger_point)
                self.data = np.append(self.data, trigger_point_base)
                self.data = np.append(self.data, movement_level)
                # Trim buffer
                self.data = self.data[(self.trigger_point_csv_window * 5) * -1::]
                if self.post_movement_frames:
                    self.post_movement_frames_cnt -= 1

    def movement_triggered(self):
        """
        Once movement is triggered set the save post frames and then stop storing data.
        """
        if self.trigger_point_csv_window:
            self.post_movement_frames = True
            self.post_movement_frames_cnt = self.trigger_point_csv_window / 2
            # self.movement_triggered = False

    def write_csv(self, filename='Motion/trigger.csv'):
        if self.trigger_point_csv_window:
            self.filename = filename
            # Reshape into a 5 column table
            # print(self.data.size)
            # print(self.data)
            self.table = np.reshape(self.data, (-1, 5))
            # print(f'Table contains {self.table.shape} rows')
            df = pd.DataFrame(data=self.table, columns=self.columns)
            df.index.name = 'Frame'
            df.to_csv(self.filename)

            # Create plot.
            subprocess.Popen(['python3', 'triggerPlot.py', '--filename', self.filename])
            self.post_movement_frames = False
