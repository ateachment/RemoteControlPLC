import asyncio
import logging
from pathlib import Path

from asyncua import Client
from asyncua import ua
import settings

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

opc_clients = []

async def connect_plcs(loop):
    for opcUser in settings.PLC_CONFIGS['opcUsers']:
        for plc in opcUser['plcs']:
            status = "offline"
            server_address = "opc.tcp://" + opcUser['username:password'] + '@' + plc['plc']['ip:port'] + '/'
            security_string = plc['plc']['SECURITY_STRING']
            print(server_address, security_string)
            client = Client(server_address, timeout=80)
            await client.set_security_string(security_string)
            try:
                async with client:
                    objects = client.nodes.objects
                    status = "online"
            except ua.UaError as exp:
                _logger.error(exp)
            finally:
                opc_clients.append([opcUser['username:password'], client, status])
            

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(connect_plcs(loop))
    loop.close()
    print(opc_clients)


if __name__ == "__main__":
    main()