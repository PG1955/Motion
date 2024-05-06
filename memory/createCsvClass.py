filename = 'meminfo.txt'
tab = 0
with open(filename, 'r') as f:
    contents = f.read().splitlines()

# for line in contents:
#     print(line)

print('class NewClass:')
tab += 4
print(f'{" " * tab}def __init__(self):')
print(f'{" " * tab}self.columns = ["Timestamp"', end="")
tab += 4
for line in contents:
    item = line.split(":")
    print(f',\n{" " * tab}\"{item[0]}\"', end="")
print(f']')
