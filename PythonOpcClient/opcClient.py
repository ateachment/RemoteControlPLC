#from opcua import *
from asyncua.sync import Client, ua
import settings

#Benutzer verbinden
client = Client(settings.SERVER_ADDRESS,timeout=20)
client.set_security_string(settings.SECURITY_STRING)

try:
    client.connect()
    print("Verbindung hergestellt")
    # Knoten über die Knoten-ID holen
    WebStartNode = client.get_node('ns=4;i=3')
    WebStopNode = client.get_node('ns=4;i=4')
    MotorschützNode = client.get_node('ns=4;i=5')
    MotorschutzschalterNode = client.get_node('ns=4;i=6')

    # Deklaration von Unified Architekture - Variablen
    on = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
    off = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
    
    # Motorschütz EIN
    WebStartNode.write_value(on)
    # Motorschütz AUS
    WebStopNode.write_value(off)

    WebStart = WebStartNode.get_value()
    WebStop = WebStopNode.get_value()
    Motorschutzschalter = MotorschutzschalterNode.get_value()
    Motorschütz = MotorschützNode.get_value()
    print("WebStart: " + str(WebStart))
    print("WebStop: " + str(WebStop))
    print("Motorschütz: " + str(Motorschütz))
    print("Motorschutzschalter: " + str(Motorschutzschalter))
finally:
    client.disconnect()