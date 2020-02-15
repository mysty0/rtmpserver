import asyncio
import enum

from bytes_packet import BytesPacket
from rtmp_packet_header import RTMPPacketHeader
from rtmp_packets import *
from utils import *


class ConnectionState(enum.Enum):
    NOT_CONNECTED = 0,
    HANDSHAKE_INIT = 1,
    HANDSHAKE_FINISHED = 2,
    CONNECTED = 3,


class RTMPProtocol(asyncio.Protocol):
    PING_SIZE = 1536

    def __init__(self):
        self.state = ConnectionState.NOT_CONNECTED
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.state = ConnectionState.NOT_CONNECTED

    def data_received(self, data):
        #ip = transport.get_extra_info('peername')
        if self.state == ConnectionState.NOT_CONNECTED:
            self.transport.write(RTMPProtocol.handshake_response(data))
            self.state = ConnectionState.HANDSHAKE_INIT
            print("send")
        else:
            bpack = BytesPacket(data)
            if self.state == ConnectionState.HANDSHAKE_INIT:
                bpack.pop(1536)
                self.state = ConnectionState.HANDSHAKE_FINISHED
            if bpack.is_empty():
                return

            print_hex(data)
            while not bpack.is_empty():
                pack = self.parse_packet(bpack)
                self.process_packet(pack)

    def process_packet(self, header):
        packet = header.packet
        if self.state == ConnectionState.HANDSHAKE_FINISHED:
            self.send_packet(header, SetWindowAcknowledgementSize(5000000))
            self.send_packet(header, SetClientBandwidth(5000000, 2))
            self.send_packet(header, SetChunkSizePacket(60000))
            self.send_packet(header, AMFCommandPacket(["_result", packet[1], None, 1]))
            self.state = ConnectionState.CONNECTED
        elif self.state == ConnectionState.CONNECTED and packet[0] == "createStream":
            self.send_packet(header, AMFCommandPacket(["onStatus", 0, None, {"level": "status", "code": "NetStream.Publish.Start", "description": "some dec"}]))

    def send_packet(self, in_header, packet):
        header = RTMPPacketHeader(stream_id=in_header.stream_id, timestamp_delta=0,
                                              message_stream_id=in_header.message_stream_id, packet=packet)
        buffer = BytesPacket(bytearray())
        header.write(buffer)
        self.transport.write(buffer.bytes)
        print("send {}".format(packet))

    @staticmethod
    def parse_packet(data):
        pack = RTMPPacketHeader()
        pack.read(data)
        print("Receive packet {}".format(pack))
        return pack

    @staticmethod
    def handshake_response(data):
        # send both data parts before reading next ping-size, to work with ffmpeg
        ndata = b'\x03' + b'\x00' * RTMPProtocol.PING_SIZE
        return ndata + data[1:]
