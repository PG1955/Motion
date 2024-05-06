import psutil

print(psutil.swap_memory())
process = psutil.Process()
print(f'Process name: {process.name()}')
_ = process.memory_info()
print(f'info {_}')

print(f'Percentage Free Memory: {psutil.virtual_memory().available * 100 / psutil.virtual_memory().total}')
print(f'Free Memory: {round(psutil.virtual_memory().available / 1024/ 1024)} Mb')
print(f'Shared Virtual : {psutil.virtual_memory().shared}')
print(f'Shared Memory: {psutil.Process().memory_info().shared / 1024}')

print(f'Virtual Memory: {psutil.virtual_memory()}')

print(f'Total Virtual Memory: {psutil.virtual_memory().total / 1024}')
print(f'Free Virtual Memory: {psutil.virtual_memory().free / 1024}')
print(f'Used Virtual Memory: {psutil.virtual_memory().used / 1024}')



