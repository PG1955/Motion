a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25,26,27,28,29,30]



def get_average(_a):
    x = 0
    for n in _a[-9:-1]:
        x = x + n
    return x


print(a)

print(a[-9:-1])
print(a[-19:-10])


print(get_average(a))
