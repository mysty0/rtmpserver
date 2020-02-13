import asyncio

from bytes_packet import BytesPacket
from rtmp_packet_header import RTMPPacketHeader
from utils import *


class Protocol(asyncio.Protocol):
    PING_SIZE = 1536

    def __init__(self):
        self.state = 0
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.state = 0

    def data_received(self, data):
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
        pack = RTMPPacketHeader()
        pack.read(data)
        print(pack)

    @staticmethod
    def handshake_response(data):
        # send both data parts before reading next ping-size, to work with ffmpeg
        ndata = b'\x03' + b'\x00' * Protocol.PING_SIZE
        return ndata + data[1:]
