import numpy as np

tp_buffer_size = 30
tp_buffer = np.zeros((tp_buffer_size, 4), np.dtype('uint16'))
print(tp_buffer.shape)

buffer_ptr = 0


for n in range(30):
    a = n + 1
    b =+ n
    c = 21
    # print(f'ptr:{buffer_ptr} size {np.size(buffer)}')
    if buffer_ptr > tp_buffer_size:
        buffer_ptr = 1
    else:
        buffer_ptr += 1

    tp_buffer[buffer_ptr - 1] = (a, b, c, n)

print(tp_buffer)

