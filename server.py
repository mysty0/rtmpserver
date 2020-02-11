import struct
import asyncio
from utils import *


class RTMPServer:
    def run(self):
        asyncio.run(self.main())

    async def main(self):
        print("Starting server")
        HOST, PORT = "localhost", 1935

        loop = asyncio.get_running_loop()
        server = await loop.create_server(Protocol, HOST, PORT)
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        await server.serve_forever()

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


class BytesPacket:
    def __init__(self, bytes):
        self.pointer = 0
        self.bytes = bytes

    def __getitem__(self, key):
        return self.bytes[key]

    def is_empty(self):
        return len(self.bytes) == self.pointer

    def pop(self, len=1):
        self.pointer += len
        return bytearray([self.bytes[i] for i in range(self.pointer-len, self.pointer)])

    def pop_u8(self):
        return struct.unpack(">B", self.pop())

    def pop_u16(self):
        return struct.unpack(">H", self.pop(2))

    def pop_u32(self):
        return struct.unpack(">I", self.pop(4))

    def pop_u32_little(self):
        return struct.unpack("<I", self.pop(4))


class Packet:
    def __init__(self, data):
        self.timestamp_delta = None
        self.packet_len = None
        self.message_id = None

        self.chunk_type = data[0] & 0b11000000
        self.stream_id = data.pop()[0] & 0b00111111
        if self.chunk_type < 3:
            self.timestamp_delta = data.pop_u16()
        if self.chunk_type < 2:
            self.packet_len = data.pop_u16()
            self.message_type = data.pop_u8()
        if self.chunk_type < 1:
            self.message_stream_id = data.pop_u32_little()

    def __str__(self):
        return "type: {} stream id: {}, timestamp: {} packet length: {} message type: {} message stream id {}"\
            .format(self.chunk_type, self.stream_id, self.timestamp_delta, self.packet_len, self.message_type, self.message_stream_id)


class Protocol(asyncio.Protocol):
    PING_SIZE = 1536

    def __init__(self):
        self.state = 0
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.state = 0

    def data_received(self, data):
        #self.transport.write(data)
        #ip = transport.get_extra_info('peername')
        if self.state == 0:
            self.transport.write(Protocol.handshake_response(data))
            self.state = 1
            print("send")
        else:
            bpack = BytesPacket(data)
            if self.state == 1:
                bpack.pop(1536)
                self.state = 2

            if bpack.is_empty():
                return

            print_hex(data)
            self.parse_packet(bpack)

    @staticmethod
    def parse_packet(data):
        pack = Packet(data)
        print(pack)

    @staticmethod
    def handshake_response(data):
        # send both data parts before reading next ping-size, to work with ffmpeg
        ndata = b'\x03' + b'\x00' * Protocol.PING_SIZE
        return ndata + data[1:]
