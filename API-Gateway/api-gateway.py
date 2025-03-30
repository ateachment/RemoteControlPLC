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

async def task_connect_plcs(loop):
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
            

def connect_plcs():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(task_connect_plcs(loop))
    loop.close()
    print(opc_clients)

async def task_read_plc(loop,opc_client):
    try:
        async with opc_client:
            objects = opc_client.nodes.objects
            Serverschnittstelle_1 = await objects.get_child("/3:ServerInterfaces/4:Server-Schnittstelle_1")
            Motorschuetz = await Serverschnittstelle_1.get_child("/4:Motorschütz")
            Motorschutzschalter = await Serverschnittstelle_1.get_child("/4:Motorschutzschalter")
            return (await Motorschuetz.get_value(), await Motorschutzschalter.get_value())
    except ua.UaError as exp:
        _logger.error(exp)
  
def read_plc(opc_client):
    info_plc = -1,-1
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(info_plc = task_read_plc(loop,opc_client))
    loop.close()
    print(info_plc)
    return info_plc





@app.route('/user/login', methods=['POST'])
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

@app.route('/user/logout/<token>', methods=['DELETE'])
def logout(token):
    ## Check if the token exists in opc_clients
    for i in range(len(opc_clients)):
        loggedON = True
        if token == opc_clients[i][3]:
            loggedON = False
            opc_clients[i][3] = -1    # put invalid token in opc client list
            print(opc_clients)
        if loggedON == False:
            return jsonify({"status": "success", "message": f"Byebye opcUser!"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid token"}), 403

@app.route('/info/<token>', methods=['GET'])
def info(token):  
    ## Check if the token exists in opc_clients
    user_opc_clients = []
    for opc_client in opc_clients:
        if token == opc_client[3]:
            user_opc_clients.append([opc_client[1],opc_client[2]])   # add opc_client to list
        if len(user_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": f"{user_opc_clients}"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid token"}), 403

@app.route('/info/<user_opc_clients>/<token>', methods=['GET'])
def info_plc(user_opc_clients,token):  
    temp_opc_clients = []
    for opc_client in user_opc_clients:
        temp_opc_clients.append("Client(opc.tcp://" + opc_client + '/')
    print(temp_opc_clients)
    ## Check if the token exists in opc_clients
    info_opc_clients = []
    for opc_client in opc_clients:
        if token == opc_client[3] and opc_client[1] in temp_opc_clients and opc_client[2] == "online":
            info_opc_clients.append = read_plc(opc_client)
        if len(info_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": f"{info_opc_clients}"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid token"}), 403


if __name__ == "__main__":
    connect_plcs()
    app.run(port=5000, debug=False)
    print(opc_clients)