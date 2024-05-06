import gc

gc.set_threshold(500, 5, 5)
print("Garbage collector thresholds set")

# Get the current garbage collector thresholds
thresholds = gc.get_threshold()
print("Current thresholds:", thresholds)