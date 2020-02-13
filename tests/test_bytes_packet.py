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


def test_string_pop():
    data = struct.pack('!h4s', 4, 'test'.encode('utf-8'))
    pack = BytesPacket(data)
    assert pack.pop_string() == 'test'


def test_write_u8():
    pack = BytesPacket(bytearray())
    pack.push_u8(23)
    assert len(pack) == 1
    assert pack.pop_u8() == 23


def test_write_u16():
    pack = BytesPacket(bytearray())
    pack.push_u16(23)
    assert len(pack) == 2
    assert pack.pop_u16() == 23


def test_write_u28():
    pack = BytesPacket(bytearray())
    pack.push_u28(23)
    assert len(pack) == 3
    assert pack.pop_u28() == 23


def test_write_u32():
    pack = BytesPacket(bytearray())
    pack.push_u32(23)
    assert len(pack) == 4
    assert pack.pop_u32() == 23


def test_write_u64():
    pack = BytesPacket(bytearray())
    pack.push_u64(23)
    assert len(pack) == 8
    assert pack.pop_u64() == 23


def test_write_string():
    pack = BytesPacket(bytearray())
    pack.push_string('testtest')
    assert pack.pop_string() == 'testtest'
