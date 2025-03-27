# copy it with your credentials to settings.py
import os
PLC_CONFIGS= { 
    'opcUsers': [
        'opcUser':'YOUR_OPC_USER',
        'opcPassword':'YOUR_OPC_USER_PASSWORD'
        'plcs': [
            'plc': {
            'SECURITY_STRING':'Basic256Sha256,SignAndEncrypt,YOUR_CLIENT_CERT_FILE.pem,YOUR_CLIENT_KEY_FILE.pem',
            'ip:port': 'YOUR_PLC_IP:OPC_PORT'
            },
            'plc': {
            'SECURITY_STRING':'Basic256Sha256,SignAndEncrypt,YOUR_CLIENT_CERT_FILE2.pem,YOUR_CLIENT_KEY_FILE2.pem',
            'ip:port': 'YOUR_PLC_IP2:OPC_PORT2'
            }
        ],
        'opcUser':'YOUR_OPC_USER2',
        'opcPassword':'YOUR_OPC_USER_PASSWORD2'
        'plcs': [
            'plc': {
            'SECURITY_STRING':'',
            'ip:port': 'YOUR_PLC_IP3:OPC_PORT3'
            }
        ]
    ]
}             

# Set Proxy environment variables to None to bypass system proxy
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""