import numpy as np


def Rand(start, end, num):
    arr = np.array([])
    for j in range(num):
        arr = np.append(arr, np.random.randint(start, end))
    return arr


movement_retard = 5
movement_window = 10
trigger_point = 10
trigger_point_base = 5

no_movement = Rand(20, 30, 40)
movement = Rand(40, 60, 10)
movements = np.append(no_movement, movement)
movements = np.append(movements, no_movement)
movement_flag = False

# print(movements)

# Get the average for the last movement_window + movement_retard.
# mean = np.mean(movements[(movement_window + movement_retard) * -1::])
# print(mean)

buffered_movement = np.array([])
for movement in movements:
    m = np.array([movement])
    buffered_movement = np.append(buffered_movement, m)
    buffered_movement = buffered_movement[(movement_window + movement_retard + 1) * -1::]
    # print(buffered_movement)
    mean_movement = round(np.mean(buffered_movement[:(movement_window + movement_retard + 1)]))
    mean_trigger_point = mean_movement + trigger_point
    mean_trigger_point_base = mean_movement + trigger_point_base
    if not movement_flag:
        if movement > mean_trigger_point:
            movement_flag = True
            print(f'Movement Triggered. movement:{movement} mean_trigger_point:{mean_trigger_point} ')
        # else:
        #     print(f'Movement Not Triggered. movement:{movement} mean_trigger_point:{mean_trigger_point} ')
    else:
        if movement <= mean_trigger_point_base:
            movement_flag = False
            print(f'Movement Ceased. movement:{movement} mean_trigger_point_base:{mean_trigger_point_base} ')


