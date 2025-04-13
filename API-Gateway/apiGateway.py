from flask import Flask, request, jsonify
from flask_cors import CORS

from asyncua.sync import Client, ua

import secrets
import settings

app = Flask(__name__)

if settings.DEBUG_MODE:
    CORS(app)                               # make cross-origin AJAX possible because of OPENAPI swagger


## generate a random secret key for session management
def generateToken():
    if settings.DEBUG_MODE:
        return "123456"                     # testing environment
    else:
        return secrets.token_urlsafe(64)    # production

## data of ppc_clients (PLCs)
opc_clients = []

## connect PLCs if possible at program start
def connect_plcs():
    for opcUser in settings.PLC_CONFIGS['opcUsers']:
        for plc in opcUser['plcs']:
            server_address = "opc.tcp://" + opcUser['username:password'] + '@' + plc['plc']['ip:port'] 
            security_string = plc['plc']['SECURITY_STRING']
            print(server_address, security_string)
            try:
                status = "online"
                client = Client(server_address, timeout=80)
                client.set_security_string(security_string)
                client.connect()
                opc_clients.append([opcUser['username:password'], plc['plc']['ip:port'], status, -1, client])   # i.e. ['opcUser:opcUser123', Client(opc.tcp://192.168.178.25:4840/), 'online', -1]
            except:
                status = "offline"
                opc_clients.append([opcUser['username:password'], plc['plc']['ip:port'], status, -1, client])   # i.e. ['opcUser:opcUser123', Client(opc.tcp://192.168.178.25:4840/), 'online', -1]
                client.disconnect()
    print(opc_clients)
                            
## read nodes of plc
def read_plc(client):
    try:
        MotorschützNode = client.get_node('ns=4;i=5')
        MotorschutzschalterNode = client.get_node('ns=4;i=6')
        Motorschütz = MotorschützNode.get_value()
        Motorschutzschalter = MotorschutzschalterNode.get_value()
        return { "Motorschütz": Motorschütz, "Motorschutzschalter": Motorschutzschalter }
    except:
        client.disconnect()

## write data to plc 
def write_plc(client, command):
    try:
        WebStartNode = client.get_node('ns=4;i=3')
        WebStopNode = client.get_node('ns=4;i=4')
        if command == "start":
            WebStartNode.write_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
        if command == "stop":
            WebStopNode.write_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
        return read_plc(client)
    except:
        client.disconnect()
  
## routes of flask webserver

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
            opc_clients[i][3] = -1             # put invalid token in opc client list
            print(opc_clients)
        if loggedON == False:
            return jsonify({"status": "success", "message": f"Byebye opcUser!"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid token"}), 403

## get info about which PLC of an user is registered and of online or not
@app.route('/info/<token>', methods=['GET'])
def info(token):  
    ## Check if the token exists in opc_clients
    user_opc_clients = []
    for opc_client in opc_clients:
        if token == opc_client[3]:
            user_opc_clients.append([opc_client[1],opc_client[2]])   # add opc_client to list
        if len(user_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": user_opc_clients}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid token"}), 403

## get info about status PLC(s) of an user
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

## give command to PLC(s)
@app.route('/control', methods=['POST'])
def control_plc():  
    data = request.get_json()
    print(data)
    # extract data from the request
    print(data.get('user_opc_clients'))
    user_opc_clients = eval(str(data.get('user_opc_clients'))) # create list
    print(user_opc_clients)
    command = data.get('command')
    token = data.get('token')
    # check user_opc_clients
    info_opc_clients = []
    for opc_client in opc_clients:
        print(opc_client)
        if token == opc_client[3] and opc_client[1] in user_opc_clients and opc_client[2] == "online":
            info_opc_clients.append([opc_client[1], write_plc(opc_client[4], command)])
        if len(info_opc_clients) > 0:
            return jsonify({"status": "success", "opc_clients": info_opc_clients})
        else:
            return jsonify({"status": "error", "message": "Invalid token, PLC(s) offline or incorrectly named"}), 403

## main program
if __name__ == "__main__":
    connect_plcs()
    app.run(port=5000, debug=False)