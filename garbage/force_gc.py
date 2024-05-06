import gc

# Create some objects
obj1 = [1, 2, 3]
obj2 = {"a": 1, "b": 2}
obj3 = "Hello, world!"

# Delete references to objects
del obj1
del obj2
del obj3

# Force a garbage collection
gc.collect()