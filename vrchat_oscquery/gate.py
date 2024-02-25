import asyncio
import json

import aiohttp

import mdns


class VRChatOSCQueryGate:
    def __init__(self):
        self._mdns_cache_server = mdns.VRChatMDNSCacheServer()

    async def start(self):
        await self._mdns_cache_server.start_server()

    async def stop(self):
        await self._mdns_cache_server.stop_server()

    async def get_vrchat_osc_server_ip_port(self):
        result = await self._get_ip_port_from_mdns("_osc._udp.local")
        return result

    async def get_vrchat_oscquery_ip_port(self):
        result = await self._get_ip_port_from_mdns("_oscjson._tcp.local")
        return result

    async def get_all_parameter_list(self):
        host_info = await self.get_vrchat_oscquery_ip_port()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host_info[0]}:{host_info[1]}/") as response:
                html = await response.text()
                oscquery_result = json.loads(html)["CONTENTS"]
                stack = [oscquery_result]
                while stack:
                    current_level = stack.pop()
                    for key in current_level.keys():
                        if "CONTENTS" in current_level[key]:
                            current_level[key] = current_level[key]["CONTENTS"]
                            stack.append(current_level[key])
        return oscquery_result

    async def _get_ip_port_from_mdns(self, domain):
        while True:
            mdns_cache = await self._mdns_cache_server.get_mdns_cache_data()
            result = mdns_cache.get(domain)
            if result:
                break
            await asyncio.sleep(1)
        return result


async def main():
    vrc_oscquery_gate = VRChatOSCQueryGate()
    await vrc_oscquery_gate.start()
    test = await vrc_oscquery_gate.get_all_parameter_list()
    print(test)
    test = await vrc_oscquery_gate.get_vrchat_osc_server_ip_port()
    print(test)
    await vrc_oscquery_gate.stop()


if __name__ == "__main__":
    asyncio.run(main())
