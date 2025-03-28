import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import asyncio
import logging
from pathlib import Path

from asyncua import Client
from asyncua import ua
import settings

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


app = Flask(__name__)
## Generate a random secret key for session management
if settings.DEBUG:
    CORS(app)                               # make cross-origin AJAX possible because of OPENAPI swagger
    app.secret_key = 'abc'
else:
    app.secret_key = os.urandom(24)



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


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    ## Extract username and password from the request
    username = data.get('username')
    password = data.get('password')

    ## Check if the user exists and the password is correct
    for opc_client in opc_clients:
        if username + ':' + password == opc_client[0]:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({"status": "success", "message": f"Welcome {username}!"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401


if __name__ == "__main__":
    main()
    app.run(port=8080, debug=True)
    print(opc_clients)