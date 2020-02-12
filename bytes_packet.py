import struct


class BytesPacket:
    def __init__(self, bytes):
        self.pointer = 0
        self.bytes = bytes

    def __getitem__(self, key):
        return self.bytes[key]

    def __len__(self):
        return len(self.bytes)

    def get(self, index):
        return self.bytes[self.pointer+index]

    def is_empty(self):
        return len(self.bytes) == self.pointer

    def pop(self, len=1):
        self.pointer += len
        return bytearray([self.bytes[i] for i in range(self.pointer-len, self.pointer)])

    def pop_packet(self, len=1):
        return BytesPacket(self.pop(len))

    def pop_u8(self):
        return struct.unpack(">B", self.pop())[0]

    def pop_u16(self):
        return struct.unpack(">H", self.pop(2))[0]

    def pop_u28(self):
        return struct.unpack(">I", bytearray([0])+self.pop(3))[0]

    def pop_u32(self):
        return struct.unpack(">I", self.pop(4))[0]

    def pop_u32_little(self):
        return struct.unpack("<I", self.pop(4))[0]

    def pop_u64(self):
        return struct.unpack(">Q", self.pop(8))[0]
