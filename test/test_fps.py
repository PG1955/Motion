import time

start = time.time()

while True:
    elapsed = time.time() - start
    print(round(elapsed))
    time.sleep(1)

