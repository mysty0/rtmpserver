import struct
import asyncio

from bytes_packet import BytesPacket
from rtmp_packet import RTMPPacketHeader
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
        pack = RTMPPacketHeader(data)
        print(pack)

    @staticmethod
    def handshake_response(data):
        # send both data parts before reading next ping-size, to work with ffmpeg
        ndata = b'\x03' + b'\x00' * Protocol.PING_SIZE
        return ndata + data[1:]
