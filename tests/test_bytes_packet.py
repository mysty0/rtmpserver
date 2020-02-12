import struct

from bytes_packet import BytesPacket


def test_byte_pop():
    data = struct.pack('!B', 10)
    pack = BytesPacket(data)
    assert pack.pop_u8() == 10


def test_int_pop():
    data = struct.pack('!I', 10)
    pack = BytesPacket(data)
    assert pack.pop_u32() == 10


def test_long_pop():
    data = struct.pack('!Q', 10)
    pack = BytesPacket(data)
    assert pack.pop_u64() == 10


def test_get():
    data = bytearray([1, 2, 3])
    pack = BytesPacket(data)
    assert pack.pop_u8() == 1
    assert pack.get(0) == 2
