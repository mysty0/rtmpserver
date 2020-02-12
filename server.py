import asyncio

from rtmp_protocol import Protocol


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



