from bytes_packet import BytesPacket
from rtmp_packets import *


class RTMPPacketHeader:
    TYPE_MASK = 0b11000000

    packet_type_mapping = {
        0x1: SetChunkSizePacket,
        0x2: AbortPacket,
        0x3: AcknowledgementPacket,
        0x5: SetWindowAcknowledgementSize,
        0x6: SetClientBandwidth,
        0x12: MetaDataPacket,
        0x14: AMFCommandPacket
    }

    @staticmethod
    def get_packet_id(packet):
        for id, pack in RTMPPacketHeader.packet_type_mapping.items():
            if isinstance(packet, pack):
                return id
        raise PacketParseException("Packet {} is not implemented".format(packet))

    def __init__(self, chunk_type=0, stream_id=None, timestamp_delta=None, message_stream_id=0, packet=None):
        self.timestamp_delta = timestamp_delta
        self.packet_len = 0
        self.packet = packet
        self.chunk_type = chunk_type
        self.stream_id = stream_id
        self.message_type = 0
        self.message_stream_id = message_stream_id

    def write(self, buffer):
        first_byte = (self.chunk_type & self.TYPE_MASK) +(self.stream_id & ~self.TYPE_MASK)
        buffer.push_u8(first_byte)

        packet_buf = BytesPacket(bytearray())

        if self.chunk_type < 3:
            buffer.push_u28(self.timestamp_delta)
        if self.chunk_type < 2:
            self.packet.write(packet_buf)
            buffer.push_u28(len(packet_buf))
            buffer.push_u8(self.get_packet_id(self.packet))
        if self.chunk_type < 1:
            buffer.push_u32_little(self.message_stream_id)

        buffer.push_buffer(packet_buf)

    def read(self, data):
        self.chunk_type = (data[0] & self.TYPE_MASK) >> 6
        self.stream_id = data.pop()[0] & ~self.TYPE_MASK
        if self.chunk_type < 3:
            self.timestamp_delta = data.pop_u28()
        if self.chunk_type < 2:
            self.packet_len = data.pop_u28()
            self.message_type = data.pop_u8()
        if self.chunk_type < 1:
            self.message_stream_id = data.pop_u32_little()

        if self.message_type in self.packet_type_mapping:
            self.packet = self.packet_type_mapping[self.message_type]()
            print(self)
            print(len(data))
            print(data.pointer)
            print(self.packet_len)
            print("POP")
            self.packet.read(data.pop_packet(self.packet_len))
        else:
            raise PacketParseException("Packet id [{}] not implemented, received packet <{}>"
                                       .format(self.message_type, self))

    def __str__(self):
        return "type: {}; stream id: {}; timestamp: {}; packet length: {}; message type: {}; " \
               "message stream id {}; packet {}"\
            .format(self.chunk_type, self.stream_id, self.timestamp_delta, self.packet_len, self.message_type,
                    self.message_stream_id, self.packet)
