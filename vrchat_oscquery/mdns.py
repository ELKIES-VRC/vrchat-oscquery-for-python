import socket
import struct
import asyncio
import dpkt


class VRChatMDNSProtocolFactory(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.vrchat_mdns_cache = {}

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport.close()

    def datagram_received(self, data, addr):
        dns_parsed = dpkt.dns.DNS(data)
        if dns_parsed.ar:
            if dns_parsed.ar[0].name.endswith("_osc._udp.local"):
                self.vrchat_mdns_cache["_osc._udp.local"] = ('.'.join([str(x) for x in dns_parsed.ar[2].ip]),
                                                             dns_parsed.ar[1].port)
            elif dns_parsed.ar[0].name.endswith("_oscjson._tcp.local"):
                self.vrchat_mdns_cache["_oscjson._tcp.local"] = ('.'.join([str(x) for x in dns_parsed.ar[2].ip]),
                                                                 dns_parsed.ar[1].port)


class VRChatMDNSCacheServer:

    def __init__(self):
        self.protocol = None
        self.transport = None
        self.sock = None

    async def _get_mdns_socket(self):
        mdns_ip = '224.0.0.251'
        mdns_port = 5353
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', mdns_port))
        mreq = struct.pack('4sl', socket.inet_aton(mdns_ip), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock = sock

    async def start_server(self):
        await self._get_mdns_socket()
        transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(VRChatMDNSProtocolFactory, sock=self.sock)
        self.transport = transport
        self.protocol = protocol

    async def stop_server(self):
        self.transport.close()

    async def get_mdns_cache_data(self):
        while not isinstance(self.protocol, VRChatMDNSProtocolFactory):
            await asyncio.sleep(1)
        return self.protocol.vrchat_mdns_cache


async def main():
    test_class = VRChatMDNSCacheServer()
    # await test_class.start_server()
    await asyncio.sleep(5)
    await test_class.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
