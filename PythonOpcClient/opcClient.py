from opcua import *
import os

# Setze Umgebungsvariablen für Proxy auf None, um den System-Proxy zu umgehen
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

#Benutzer verbinden
client = Client("opc.tcp://opcUser:asdUIZFD5367478!!@192.168.178.25:4840/",timeout=8)
print(client.application_uri) # urn anzeigen
client.set_security_string("Basic256Sha256,SignAndEncrypt,PLC-25OPCUA-Client_cert.pem,PLC-25OPCUA-Client_key.pem")

try:
    client.connect()
    print("Verbindung hergestellt")
    # Knoten über die Knoten-ID holen
    WebStartNode = client.get_node('ns=4;i=3')
    WebStopNode = client.get_node('ns=4;i=4')
    MotorschützNode = client.get_node('ns=4;i=5')
    MotorschutzschalterNode = client.get_node('ns=4;i=6')

    # Motorschütz EIN
    WebStartNode.set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
    # Motorschütz AUS
    #WebStopNode.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))  

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