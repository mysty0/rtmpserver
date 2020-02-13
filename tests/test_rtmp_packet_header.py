import struct

from bytes_packet import BytesPacket
from rtmp_packet_header import RTMPPacketHeader, AMFCommandPacket


def test_header_parse():
    data = struct.pack('!bbhbhb', 3, 0, 123, 0, 4, 1)
    data += struct.pack('<i', 321)
    data += struct.pack('!i', 123)
    pack = RTMPPacketHeader()
    pack.read(BytesPacket(data))
    assert pack.chunk_type == 0 and pack.timestamp_delta == 123 and pack.packet_len == 4 and pack.message_type == 1\
           and pack.message_stream_id == 321 and pack.packet.size == 123


def test_header_write():
    amf_pack = AMFCommandPacket([[("123", 123)]])
    pack = RTMPPacketHeader(chunk_type=0, stream_id=20, timestamp_delta=123, message_stream_id=321, packet=amf_pack)
    buf = BytesPacket(bytearray())
    pack.write(buf)
    pack_parsed = RTMPPacketHeader()
    pack_parsed.read(buf)
    assert pack_parsed.stream_id == 20 and pack_parsed.timestamp_delta == 123 and pack_parsed.message_stream_id == 321\
           and pack_parsed.packet.fields[0] == [("123", 123)]
