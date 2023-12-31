import numpy as np
import pandas as pd

class TriggerCSV:
    """
    Creates a csv file that shows the detail of the trigger event.
    """

    def __init__(self, tc_trigger_point, tc_trigger_point_base, tc_movement_window, tc_movement_window_age):
        self.trigger_point = tc_trigger_point
        self.trigger_point_base = tc_trigger_point_base
        self.movement_window = tc_movement_window
        self.movement_window_age = tc_movement_window_age
        self.buffered_movement = None
        self.frame = 0
        self.filename = None
        self.df = None
        self.data = None
        self.mean_movement = None
        self.mean_trigger_point = None
        self.mean_trigger_point_base = None
        self.columns = ['Frame',
                        'Trigger Point',
                        'Trigger Point Base',
                        'Movement Window',
                        'Movement Window Age',
                        'Mean Trigger Point',
                        'Mean Trigger Point Base',
                        'Mean Movement Level',
                        'Movement Level']

    def write_trigger_data(self, tc_buffered_movement, filename='foo.csv'):
        self.buffered_movement = tc_buffered_movement
        self.filename = filename
        cnt = 0
        print(f'Buffered Movement array contains {self.buffered_movement.shape} items.')
        new_move = np.array([])
        for movement in self.buffered_movement:
            cnt += 1
            print(f'movement: {movement} cnt:{cnt} > movement_window {self.movement_window}' )
            if cnt > (self.movement_window + self.movement_window_age):
                print(f'self.buffered_movement[{cnt - self.movement_window_age}:{self.movement_window} ]')
                start = cnt - (self.movement_window_age + self.movement_window)
                end = cnt - self.movement_window_age
                start = cnt - (self.movement_window_age + self.movement_window)
                end = cnt - self.movement_window_age
                self.mean_movement = self.mean_movement = (round(np.mean(self.buffered_movement[start:end])))
                self.mean_trigger_point = self.mean_movement + self.trigger_point
                self.mean_trigger_point_base = self.mean_movement + self.trigger_point_base
                new_move = np.append(new_move, self.trigger_point)
                new_move = np.append(new_move, self.trigger_point_base)
                new_move = np.append(new_move, self.movement_window)
                new_move = np.append(new_move, self.movement_window_age)
                new_move = np.append(new_move, self.mean_movement)
                new_move = np.append(new_move, self.mean_trigger_point)
                new_move = np.append(new_move, self.mean_trigger_point_base)
                new_move = np.append(new_move, movement)


        reshaped_arr = np.reshape(new_move, (-1, 9))
        print(f'Shape: {reshaped_arr.shape}')

        columns = ['Trigger Point',
                   'Trigger Point Base',
                   'Movement Window',
                   'Movement Window Age',
                   'Mean Trigger Point',
                   'Mean Trigger Point Base',
                   'Mean Movement Level',
                   'Movement Level']
        df = pd.DataFrame(data=reshaped_arr, columns=columns)
        df.index.name = 'Frame'
        df.to_csv(self.filename)

trigger_point = 20
trigger_point_base = 10
movement_window = 20
movement_window_age = 10
# buffered_movement = np.array([621, 508, 503, 433, 425, 324, 304, 259, 237, 206, 228, 207, 217, 187, 181, 162, 163, 127,135, 132, 121, 124, 110, 111,  94, 101,  92,  97,  91,  88,  83,  86,  85,  76,  74, 77, 77, 77, 77, 76, 72, 75, 74,  66,  67,  70,  69, 115, 116, 213, 21])
# buffered_movement = np.random.rand(200)
# Create a array of 200 randowm numbers from 10 to 50
buffered_movement = np.random.randint(10,50, (200))
print(buffered_movement)


# Instantiate Trigger CSV class,
trcsv = TriggerCSV(trigger_point, trigger_point_base, movement_window, movement_window_age)

trcsv.write_trigger_data(buffered_movement)
