import numpy as np

def rle_encode(data):
    compressed = []
    n = len(data)
    if n == 0:
        return compressed
    prev = data[0]
    count = 1
    for i in range(1, n):
        if data[i] == prev:
            count += 1
        else:
            if count == 1:
                compressed.append(prev)
            else:
                compressed.append(prev)
                compressed.append(- (count - 1))
            prev = data[i]
            count = 1
    # Handle the last run
    if count == 1:
        compressed.append(prev)
    else:
        compressed.append(prev)
        compressed.append(- (count - 1))
    return compressed
