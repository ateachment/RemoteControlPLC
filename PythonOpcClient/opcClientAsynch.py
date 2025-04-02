import asyncio
import logging
from pathlib import Path

from asyncua import Client
from asyncua import ua
import settings

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# file paths for the certificate and private key
cert_path = Path("PLC-25OPCUA-Client_cert.pem")
private_key_path = Path("PLC-25OPCUA-Client_key.pem")

async def task(loop):
    client = Client(settings.SERVER_ADDRESS, timeout=20)
    await client.set_security_string(settings.SECURITY_STRING)
    try:
        async with client:
            objects = client.nodes.objects
            Serverschnittstelle_1 = await objects.get_child("/3:ServerInterfaces/4:Server-Schnittstelle_1")
            Datenbaustein_Motorschaltung = await Serverschnittstelle_1.get_child("/4:Datenbaustein_Motorschaltung")
            WebStart = await Datenbaustein_Motorschaltung.get_child("/4:WebStart")
            WebStop = await Datenbaustein_Motorschaltung.get_child("/4:WebStop")
            Motorschuetz = await Serverschnittstelle_1.get_child("/4:Motorschütz")
            Motorschutzschalter = await Serverschnittstelle_1.get_child("/4:Motorschutzschalter")
            print(await Motorschuetz.get_value())
            await WebStart.set_value(ua.DataValue(True))  # einschalten
            print(await Motorschuetz.get_value())
    except ua.UaError as exp:
        _logger.error(exp)

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(task(loop))
    loop.close()


if __name__ == "__main__":
    main()