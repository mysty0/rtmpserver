from enum import Enum
from abc import ABC, abstractmethod

from utils import print_hex


class PacketParseException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class RTMPPacket(ABC):
    @abstractmethod
    def __init__(self, data):
        pass


class SetChunkSizePacket(RTMPPacket):
    def __init__(self, data):
        super().__init__(data)
        self.size = data.pop_u32()
        if self.size >> 31:
            raise Exception("The most significant bit should be zero")


class AbortPacket(RTMPPacket):
    def __init__(self, data):
        super().__init__(data)
        self.stream_id = data.pop_u32()


class AcknowledgementPacket(RTMPPacket):
    def __init__(self, data):
        super().__init__(data)
        self.sequence_number = data.pop_u32()


class SetServerBandwidth(RTMPPacket):
    def __init__(self, data):
        super().__init__(data)
        self.bandwidth = data.pop_u32()


class SetClientBandwidth (RTMPPacket):
    def __init__(self, data):
        super().__init__(data)
        self.bandwidth = data.pop_u32()
        self.limit_type = data.pop_u8()
        """
        0 - Hard: The peer SHOULD limit its output bandwidth to the
        indicated window size.
        1 - Soft: The peer SHOULD limit its output bandwidth to the the
        window indicated in this message or the limit already in effect,
        whichever is smaller.
        2 - Dynamic: If the previous Limit Type was Hard, treat this message
        as though it was marked Hard, otherwise ignore this message.
        """


class AMFCommandPacket(RTMPPacket):
    @staticmethod
    def is_object_end(data):
        return data.get(0) == 0 and data.get(1) == 0 and data.get(2) == 9

    def __init__(self, data):
        super().__init__(data)
        self.fields = []
        while not data.is_empty():
            self.fields.append(self.parse_field(data))

    @staticmethod
    def parse_property(data):
        length = data.pop_u16()
        name = data.pop(length).decode('utf-8')
        val = AMFCommandPacket.parse_field(data)
        return name, val

    @staticmethod
    def parse_field(data):
        #field = None
        ptype = data.pop_u8()
        if ptype == 0:
            field = data.pop_u64()
        elif ptype == 1:
            field = False if data.pop_u8() == 0 else True
        elif ptype == 2:
            length = data.pop_u16()
            string = data.pop(length).decode('utf-8')
            field = string
        elif ptype == 3:
            field = {}
            while not AMFCommandPacket.is_object_end(data):
                name, val = AMFCommandPacket.parse_property(data)
                field[name] = val

            # delete object end
            data.pop(3)
        elif ptype == 5:
            field = None
        elif ptype == 8:
            length = data.pop_u32()
            field = []
            for _ in range(length):
                name, val = AMFCommandPacket.parse_property(data)
                field[name] = val
        else:
            raise PacketParseException("Packet field type not implemented")

        return field

    def __str__(self):
        return "fields: {}".format(self.fields)


class RTMPPacketHeader:
    packet_type_mapping = {
        0x1: SetChunkSizePacket,
        0x2: AbortPacket,
        0x3: AcknowledgementPacket,
        0x5: SetServerBandwidth,
        0x6: SetClientBandwidth,
        0x14: AMFCommandPacket
    }

    def __init__(self, data):
        self.timestamp_delta = None
        self.packet_len = None
        self.message_id = None
        self.packet = None

        self.chunk_type = data[0] & 0b11000000
        self.stream_id = data.pop()[0] & 0b00111111
        if self.chunk_type < 3:
            self.timestamp_delta = data.pop_u28()
        if self.chunk_type < 2:
            self.packet_len = data.pop_u28()
            self.message_type = data.pop_u8()
        if self.chunk_type < 1:
            self.message_stream_id = data.pop_u32_little()

        if self.message_type in self.packet_type_mapping:
            self.packet = self.packet_type_mapping[self.message_type](data.pop_packet(self.packet_len))
        else:
            raise PacketParseException("Packet id not implemented")

    def __str__(self):
        return "type: {} stream id: {}, timestamp: {} packet length: {} message type: {} message stream id {} packet {}"\
            .format(self.chunk_type, self.stream_id, self.timestamp_delta, self.packet_len, self.message_type, self.message_stream_id, self.packet)



