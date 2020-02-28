def insert_in_pos(str, pos, ins):
    return str[:pos] + ins + str[pos:]


def num_to_hex(num):
    return hex(num)[2:].zfill(2)


def data_to_str(data, i):
    return ' '.join(["{}: ".format(str(i).zfill(4))] + [num_to_hex(b).ljust(2) for b in data])


def clean_char(string):
    return ''.join(c if c.isalpha() or c.isdigit() else '.' for c in string)


def print_hex(data):
    n = 16
    chunks = [data[i:i + n] for i in range(0, len(data), n)]
    strs = [data_to_str(chunks[i], num_to_hex(i*n))+" | "+clean_char((''.join(chunks[i].decode('utf-8', 'replace'))).replace(u'\ufffd', '.')) for i in range(len(chunks))]
    strs = [insert_in_pos(string, 31, ' ') for string in strs]
    [print(string) for string in strs]
