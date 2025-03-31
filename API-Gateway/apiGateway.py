from flask import Flask, request, jsonify, session
from flask_cors import CORS
import ast

from opcua import *

import secrets
import settings

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

def connect_plcs():
    for opcUser in settings.PLC_CONFIGS['opcUsers']:
        for plc in opcUser['plcs']:
            status = "offline"
            server_address = "opc.tcp://" + opcUser['username:password'] + '@' + plc['plc']['ip:port'] 
            security_string = plc['plc']['SECURITY_STRING']
            print(server_address, security_string)
            client = Client(server_address, timeout=80)
            client.set_security_string(security_string)
            try:
                client.connect()
                status = "online"
                opc_clients.append([opcUser['username:password'], plc['plc']['ip:port'], status, -1, client])   # i.e. ['opcUser:opcUser123', Client(opc.tcp://192.168.178.25:4840/), 'online', -1]
            except:
                client.disconnect()
                            


def read_plc(client):
    try:
        MotorschützNode = client.get_node('ns=4;i=5')
        MotorschutzschalterNode = client.get_node('ns=4;i=6')
        Motorschütz = MotorschützNode.get_value()
        Motorschutzschalter = MotorschutzschalterNode.get_value()
        return { "Motorschütz": Motorschütz, "Motorschutzschalter": Motorschutzschalter }
    except:
        client.disconnect()


def write_plc(client, command):
    try:
        WebStartNode = client.get_node('ns=4;i=3')
        WebStopNode = client.get_node('ns=4;i=4')
        if command == "start":
            WebStartNode.set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
        if command == "stop":
            WebStopNode.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))  
        return read_plc(client)
    except:
        client.disconnect()
  

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
    ## Check user_opc_clients
    info_opc_clients = []
    for opc_client in opc_clients:
        if token == opc_client[3] and opc_client[1] in user_opc_clients and opc_client[2] == "online":
            info_opc_clients.append([opc_client[1], read_plc(opc_client[4])])
        if len(info_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": f"{info_opc_clients}"})
        else:
            return jsonify({"status": "error", "message": "Invalid token, PLC(s) offline or incorrectly named"}), 403

@app.route('/control', methods=['POST'])
def control_plc():  
    data = request.get_json()
    ## Extract data from the request
    user_opc_clients = ast.literal_eval(data.get('user_opc_clients')) # create list
    print(user_opc_clients)
    command = data.get('command')
    token = data.get('token')
    ## Check user_opc_clients
    info_opc_clients = []
    for opc_client in opc_clients:
        print(opc_client)
        if opc_client in user_opc_clients:
            print("xxxx")
        if token == opc_client[3] and opc_client[1] in user_opc_clients and opc_client[2] == "online":
            info_opc_clients.append([opc_client[1], write_plc(opc_client[4], command)])
        if len(info_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": f"{info_opc_clients}"})
        else:
            return jsonify({"status": "error", "message": "Invalid token, PLC(s) offline or incorrectly named"}), 403

if __name__ == "__main__":
    connect_plcs()
    app.run(port=5000, debug=False)