import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import asyncio
import logging
from pathlib import Path

from asyncua import Client
from asyncua import ua

import secrets
import settings

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


app = Flask(__name__)

if settings.DEBUG_MODE:
    CORS(app)                               # make cross-origin AJAX possible because of OPENAPI swagger


## Generate a random secret key for session management
def generateToken():
    if settings.DEBUG_MODE:
        return "123456"                     # testing environment
    else:
        return secrets.token_urlsafe(64)    # production


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
                opc_clients.append([opcUser['username:password'], client, status, -1])   # i.e. ['opcUser:opcUser123', Client(opc.tcp://192.168.178.25:4840/), 'online', -1]
            

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(connect_plcs(loop))
    loop.close()
    print(opc_clients)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    ## Extract username and password from the request
    username = data.get('username')
    password = data.get('password')

    ## Check if the user exists and the password is correct
    for i in range(len(opc_clients)):
        loggedON = False
        token = generateToken()
        if username + ':' + password == opc_clients[i][0]:
            loggedON = True
            opc_clients[i][3] = token    # valid token in opc client list
            print(opc_clients)
        if loggedON:
            return jsonify({"status": "success", "message": f"Welcome {username}!", "token": f"{token}"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    
if __name__ == "__main__":
    main()
    app.run(port=5000, debug=True)
    print(opc_clients)