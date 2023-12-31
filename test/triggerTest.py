import numpy as np
import pandas as pd

df = pd.read_csv('peakMovement.csv')

df1 = df[(df['Trigger Value'] > 0)]

buffered_movement = np.array([])

movement_flag_cnt = 0
movement_flag = False
movement_trigger_csv = None
movement_trigger_csv_counter = None

for index, row in df1.iterrows():

    movement_level = row['Trigger Value']
    # trigger_point = row['Trigger Point']
    # trigger_point_base = row['Trigger Point Base']

    trigger_point = 2
    trigger_point_base = 1
    movement_window = row['Movement History Window']
    # movement_window_age = row['Movement History Age']
    movement_window_age = 10

    buffered_movement = np.append(buffered_movement, movement_level)

    # Do not do any processing until the buffer is fully populated.
    if np.size(buffered_movement) < (movement_window + movement_window_age):
        continue


    # Trim the movement buffer.
    buffered_movement = buffered_movement[((movement_window + movement_window_age) + 1) * -1::]

    # Get the average movement over the movement window using movement_window_age.
    mean_movement = round(np.mean(buffered_movement[-movement_window:]))
    old_mean_movement = round(np.mean(buffered_movement[-(movement_window + movement_window_age):-(movement_window_age - 1)]))
    # mean_trigger_point = mean_movement + trigger_point
    # mean_trigger_point_base = mean_movement + trigger_point_base

    # Check for movement. Compare the mean movement level with this movement level.
    # Do this after the movement buffer is complete.
    if movement_window_age > 0:
        if movement_flag:
            movement_triggered = False
            movement_ended = True
            # if movement_level < mean_trigger_point_base:
            print(f'if {mean_movement} < {old_mean_movement + trigger_point_base}:')
            if mean_movement < old_mean_movement + trigger_point_base:
                print('False')
                movement_flag = False
                movement_ended = True
        else:
            # When movement_flag is not set.
            # if movement_level > mean_trigger_point:
            print(f'if {mean_movement} > {old_mean_movement - trigger_point}:')
            if mean_movement > old_mean_movement + trigger_point:
                print('True')
                movement_flag = True
                movement_triggered = True
                if not movement_trigger_csv:
                    movement_trigger_csv = True
                    movement_trigger_csv_counter = movement_window_age
    else:
        if movement_flag:
            movement_triggered = False
            movement_ended = True
            if movement_level < trigger_point_base:
                movement_flag = False
                movement_ended = True
        else:
            if movement_level > trigger_point:
                movement_flag = True
                movement_triggered = True
                if not movement_trigger_csv:
                    movement_trigger_csv = True
                    movement_trigger_csv_counter = movement_window_age

    if movement_flag:
        movement_flag_cnt += 1
    # print(f'movement_flag: {movement_flag} movement_level: {movement_level} > mean_trigger_point: {mean_trigger_point}')

print(f'Number of movements triggered: {movement_flag_cnt}')