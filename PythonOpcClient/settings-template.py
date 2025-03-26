# copy it with your credentials to settings.py
import os

SERVER_ADDRESS = "opc.tcp://YOUR_OPC_USER:YOUR_OPC_PASSWORD@PLC_IP_ADDRESS:4840/"            # be careful
SECURITY_STRING = "Basic256Sha256,SignAndEncrypt,YOUR_CERT_FILE.pem,YOUR_KEY_FILE.pem"

# Set Proxy environment variables to None to bypass system proxy
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""