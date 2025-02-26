# copy it with your credentials to settings.py
import os

SERVER_ADDRESS = "opc.tcp://YOUR_OPC_USER:YOUR_OPC_PASSWORD@PLC_IP_ADDRESS:4840/"            # be careful

# Set Proxy environment variables to None to bypass system proxy
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""