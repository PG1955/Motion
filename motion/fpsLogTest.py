import random
import time

import psutil
from fpsLogCSV import FPSLogCSV

fps_log = FPSLogCSV(20, monitor_interval=10)

random_number = round(random.uniform(8.0, 30.0), 2)

fps_log.write(random_number)

print(f'Last Line is: {fps_log.read_last_line()}')

cnt = 0
while cnt < 30:
    repeat = 0
    while repeat < 15:
        repeat += 1
        fps_log.monitor_fps()
    cnt += 1
    time.sleep(1)

print(fps_log.get_fps())

