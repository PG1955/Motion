import pandas as pd
import numpy as np


# arr = np.random.rand(4,3)
#
# print(arr)
#
# columns = ['Column A', 'Column B', 'Column GGG']
#
# df = pd.DataFrame(data=arr, columns=columns)
#
# print(df)

def Rand(start, end, num):
    arr = np.array([])
    for j in range(num):
        arr = np.append(arr, int(np.random.randint(start, end)))
    return arr


# movements = Rand(20, 30, 40)
# print(movements)


movement_window = 10
movement_window_age = 5
trigger_point = 10
trigger_point_base = 5
movements = Rand(20, 50, 40)
print(movements)

new_move = np.array([])
cnt = 0
for movement in movements:
    cnt += 1
    if cnt < (movement_window + movement_window_age + 1):
        mean_movement = round(np.mean(movements[cnt:(movement_window + movement_window_age + 1)]))
        mean_trigger_point = mean_movement + trigger_point
        mean_trigger_point_base = mean_movement + trigger_point_base
        new_move = np.append(new_move, trigger_point)
        new_move = np.append(new_move, trigger_point_base)
        new_move = np.append(new_move, movement_window)
        new_move = np.append(new_move, movement_window_age)
        new_move = np.append(new_move, mean_movement)
        new_move = np.append(new_move, mean_trigger_point)
        new_move = np.append(new_move, mean_trigger_point_base)

print(new_move)
print(new_move.shape)

reshaped_arr = np.reshape(new_move, (-1, 7))

print(reshaped_arr)

columns = ['Trigger Point',
           'Trigger Point Base',
           'Movement Window',
           'Movement Window Age',
           'Mean Trigger Point',
           'Mean Trigger Point Base',
           'Mean Movement Level']

df = pd.DataFrame(data=reshaped_arr, columns=columns)
df.index.name = 'Frame'

print(df)

df.to_csv('foo.csv')