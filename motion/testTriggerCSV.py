import numpy as np

from triggerCSV import TriggerCSV


def Rand(start, end, num):
    arr = np.array([])
    for j in range(num):
        arr = np.append(arr, np.random.randint(start, end))
    return arr

tcsv = TriggerCSV(40, 30, 10)

movement = Rand(20, 40, 100)

cnt = 0
for movement_level in movement:
    cnt += 1
    if cnt == 35:
        tcsv.movement_triggered()

    tcsv.log_movement(40,20,movement_level)

tcsv.write_csv('Motion/testTrigger.csv')

