import struct

from bytes_packet import BytesPacket
from rtmp_packets import AMFCommandPacket, MetaDataPacket
from utils import print_hex


def test_int_parse():
    data = struct.pack('!bd', 0, 100.0)
    pack = AMFCommandPacket()
    pack.read(BytesPacket(data))
    assert pack.fields[0] == 100.0


def test_bool_parse():
    data = struct.pack('!bb', 1, 1)
    pack = AMFCommandPacket()
    pack.read(BytesPacket(data))
    assert pack.fields[0] == True


def test_string_parse():
    data = struct.pack('!bh11s', 2, 11, 'Hello world'.encode('UTF-8'))
    pack = AMFCommandPacket()
    pack.read(BytesPacket(data))
    assert pack.fields[0] == "Hello world"


def test_object_end():
    data = struct.pack('!bbb', 0, 0, 9)
    assert AMFCommandPacket.is_object_end(BytesPacket(data))


def test_object_parse():
    data = struct.pack('!bh4sbh4sbbb', 3, 4, 'test'.encode('UTF-8'), 2, 4, 'test'.encode('UTF-8'), 0, 0, 9)
    pack = AMFCommandPacket()
    pack.read(BytesPacket(data))
    assert "test" in pack.fields[0] and pack.fields[0]["test"] == "test"


def test_object_parse_long():
    data = struct.pack('!bh4sbh4s', 3, 4, 'test'.encode('UTF-8'), 2, 4, 'test'.encode('UTF-8'))
    data += struct.pack('!h4sbh4s', 4, 'tset'.encode('UTF-8'), 2, 4, 'tset'.encode('UTF-8'))
    data += struct.pack('!bbb', 0, 0, 9)
    pack = AMFCommandPacket()
    pack.read(BytesPacket(data))
    assert "test" in pack.fields[0] and pack.fields[0]["test"] == "test" and pack.fields[0]["tset"] == "tset"


def test_set_dataframe_parse():
    bstr = """
    02 00 0d 40 73 65 74 44 61 74 61 46 72 61 6d 65
    02 00 0a 6f 6e 4d 65 74 61 44 61 74 61 08 00 00
    00 08 00 08 64 75 72 61 74 69 6f 6e 00 00 00 00
    00 00 00 00 00 00 05 77 69 64 74 68 00 40 94 00
    00 00 00 00 00 00 06 68 65 69 67 68 74 00 40 8e
    00 00 00 00 00 00 00 0d 76 69 64 65 6f 64 61 74
    61 72 61 74 65 00 00 00 00 00 00 00 00 00 00 09
    66 72 61 6d 65 72 61 74 65 00 40 3e 00 00 00 00
    00 00 00 0c 76 69 64 65 6f 63 6f 64 65 63 69 64
    00 40 1c 00 00 00 00 00 00 00 07 65 6e 63 6f 64
    65 72 02 00 0d 4c 61 76 66 35 38 2e 32 30 2e 31
    30 30 00 08 66 69 6c 65 73 69 7a 65 00 00 00 00
    00 00 00 00 00 00 00 09 """.split()
    pack_bytes = [int(b, 16) for b in bstr]
    print(pack_bytes)
    pack = MetaDataPacket()
    pack.read(BytesPacket(bytearray(pack_bytes)))
    print(pack)
    assert pack[0] == "@setDataFrame" and pack[1] == "onMetaData"
    assert pack[2] == [("duration", 0.0), ("width", 1280.0), ("height", 960.0), ("videodatarate", 0.0),
                       ("framerate", 30.0), ("videocodecid", 7.0), ("encoder", "Lavf58.20.100"), ("filesize", 0.0)]


def test_int_write():
    pack = AMFCommandPacket([12.0])
    buf = BytesPacket(bytearray())
    pack.write(buf)
    tp, num = buf.pop_u8(), buf.pop_double()
    assert tp == 0 and num == 12.0