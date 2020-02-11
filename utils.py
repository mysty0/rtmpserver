def print_hex(data):
    n = 20
    [print(' '.join(hex(b) for b in data[i:i + n])) for i in range(0, len(data), n)]