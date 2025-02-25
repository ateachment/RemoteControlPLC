import asyncio
import logging
import sys
import socket
from pathlib import Path

from asyncua import Client
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from asyncua import ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Definiere den Dateipfad für Zertifikat und privaten Schlüssel
cert_path = Path("PLC-25OPCUA-Client_cert.pem")
private_key_path = Path("PLC-25OPCUA-Client_key.pem")


async def task(loop):
    url = "opc.tcp://opcUser:asdUIZFD5367478!!@192.168.178.25:4840/"

    client = Client(url=url,timeout=8)
    #client.application_uri = client_app_uri
    await client.set_security_string("Basic256Sha256,SignAndEncrypt,PLC-25OPCUA-Client_cert.pem,PLC-25OPCUA-Client_key.pem")
    """
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=str(cert_path),  # Zertifikat-Dateipfad
        private_key=str(private_key_path),  # Privater Schlüssel-Dateipfad
        server_certificate=str(cert_path)  # Serverzertifikat (kann gleich wie Client-Zertifikat sein)
    )
    """

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