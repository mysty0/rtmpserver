from enum import Enum
from abc import ABC, abstractmethod


class PacketParseException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class RTMPPacket(ABC):
    @abstractmethod
    def read(self, data):
        pass

    @abstractmethod
    def write(self, buffer):
        pass


class SetChunkSizePacket(RTMPPacket):
    def __init__(self, size=0):
        self.size = size

    def read(self, data):
        self.size = data.pop_u32()
        if self.size >> 31:
            raise Exception("The most significant bit should be zero")

    def write(self, buffer):
        buffer.push_u32(self.size)


class AbortPacket(RTMPPacket):
    def __init__(self):
        self.stream_id = 0

    def read(self, data):
        self.stream_id = data.pop_u32()

    def write(self, buffer):
        buffer.push_u32(self.stream_id)


class AcknowledgementPacket(RTMPPacket):
    def __init__(self):
        self.sequence_number = 0

    def read(self, data):
        self.sequence_number = data.pop_u32()

    def write(self, buffer):
        buffer.push_u32(self.sequence_number)


class SetWindowAcknowledgementSize(RTMPPacket):
    def __init__(self, acknowledgement_size=0):
        self.acknowledgement_size = acknowledgement_size

    def read(self, data):
        self.acknowledgement_size = data.pop_u32()

    def write(self, buffer):
        buffer.push_u32(self.acknowledgement_size)


class SetClientBandwidth (RTMPPacket):
    def __init__(self, bandwidth=0, limit_type=0):
        self.bandwidth = bandwidth
        self.limit_type = limit_type
        """
        0 - Hard: The peer SHOULD limit its output bandwidth to the
        indicated window size.
        1 - Soft: The peer SHOULD limit its output bandwidth to the the
        window indicated in this message or the limit already in effect,
        whichever is smaller.
        2 - Dynamic: If the previous Limit Type was Hard, treat this message
        as though it was marked Hard, otherwise ignore this message.
        """

    def read(self, data):
        self.bandwidth = data.pop_u32()
        self.limit_type = data.pop_u8()

    def write(self, buffer):
        buffer.push_u32(self.bandwidth)
        buffer.push_u8(self.limit_type)


class AMFCommandPacket(RTMPPacket):
    def __init__(self, fields=None):
        if fields is None:
            fields = []

        self.fields = fields

    def __getitem__(self, key):
        return self.fields[key]

    def read(self, data):
        while not data.is_empty():
            self.fields.append(self.parse_field(data))

    def write(self, buffer):
        for field in self.fields:
            self.write_field(buffer, field)

    @staticmethod
    def write_property(buffer, name, val):
        buffer.push_string(name)
        AMFCommandPacket.write_field(buffer, val)

    @staticmethod
    def write_field(buffer, field):
        if isinstance(field, int):
            buffer.push_u8(0)
            buffer.push_u64(field)
        elif isinstance(field, bool):
            buffer.push_u8(1)
            buffer.push_u8(0 if not field else 1)
        elif isinstance(field, str):
            buffer.push_u8(2)
            buffer.push_string(field)
        elif isinstance(field, dict):
            buffer.push_u8(3)
            for name, val in field.items():
                print(name, val)
                AMFCommandPacket.write_property(buffer, name, val)
            # write object end
            buffer.push_u8(0)
            buffer.push_u8(0)
            buffer.push_u8(9)
        elif field is None:
            buffer.push_u8(5)
        elif isinstance(field, list):
            buffer.push_u8(8)
            buffer.push_u32(len(field))
            for item in field:
                AMFCommandPacket.write_property(buffer, item[0], item[1])
        else:
            raise PacketParseException("Packet field type {} not implemented".format(type(field)))

    @staticmethod
    def is_object_end(data):
        return data.get(0) == 0 and data.get(1) == 0 and data.get(2) == 9

    @staticmethod
    def parse_property(data):
        name = data.pop_string()
        val = AMFCommandPacket.parse_field(data)
        return name, val

    @staticmethod
    def parse_field(data):
        ptype = data.pop_u8()
        if ptype == 0:
            field = data.pop_u64()
        elif ptype == 1:
            field = False if data.pop_u8() == 0 else True
        elif ptype == 2:
            field = data.pop_string()
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
                field.append((name, val))
        else:
            raise PacketParseException("Packet field type not implemented")

        return field

    def __str__(self):
        return "fields: {}".format(self.fields)
