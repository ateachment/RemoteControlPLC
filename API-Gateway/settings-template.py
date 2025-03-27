# copy it with your credentials to settings.py
import os
PLC_CONFIGS={'SERVER_ADDRESS':'opc.tcp://opcUser:asdUIZFD5367478!!@192.168.178.25:4840/',
             'SECURITY_STRING':'Basic256Sha256,SignAndEncrypt,PLC-25OPCUA-Client_cert.pem,PLC-25OPCUA-Client_key.pem'}

# Set Proxy environment variables to None to bypass system proxy
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""